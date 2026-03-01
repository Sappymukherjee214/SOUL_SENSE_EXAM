import logging
import uuid
from datetime import datetime, UTC
from typing import List, Tuple
from sqlalchemy.orm import Session
from ..schemas import ExamResponseCreate, ExamResultCreate
from ..models import User, Score, Response
from .db_service import get_db
from .gamification_service import GamificationService
from ..utils.db_transaction import transactional, retry_on_transient
try:
    from .crypto import EncryptionManager
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

logger = logging.getLogger("api.exam")

class ExamService:
    """
    Service for handling Exam write operations via API.
    Uses 'Storage-First' approach: Client calculates, API validates and saves.
    """

    @staticmethod
    def start_exam(db: Session, user: User):
        """Standardizes session initiation and returns a new session_id."""
        session_id = str(uuid.uuid4())
        logger.info(f"Exam session started", extra={
            "user_id": user.id,
            "session_id": session_id
        })
        return session_id

    @staticmethod
    def save_response(db: Session, user: User, session_id: str, data: ExamResponseCreate):
        """Saves a single question response linked to the user and session."""
        try:
            new_response = Response(
                username=user.username,
                user_id=user.id,
                question_id=data.question_id,
                response_value=data.value,
                age_group=data.age_group,
                session_id=session_id,
                timestamp=datetime.now(UTC).isoformat()
            )
            db.add(new_response)
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save response", extra={
                "user_id": user.id,
                "session_id": session_id,
                "question_id": data.question_id,
                "error": str(e)
            }, exc_info=True)
            db.rollback()
            raise e

    @staticmethod
    @retry_on_transient(retries=3)
    def save_score(db: Session, user: User, session_id: str, data: ExamResultCreate):
        """
        Saves the final exam score atomically together with gamification updates.
        Encrypts reflection_text if crypto is available.

        The Score row and all GamificationService side-effects are committed in
        a single transaction so that a partial failure cannot leave the database
        in an inconsistent state (e.g. score saved but XP not awarded, or vice-versa).
        """
        try:
            # Encrypt reflection text for privacy (before the transaction)
            reflection = data.reflection_text
            if CRYPTO_AVAILABLE and reflection:
                try:
                    reflection = EncryptionManager.encrypt(reflection)
                except Exception as ce:
                    logger.error(f"Encryption failed for reflection: {ce}")
                    # Fall back to plain text – do not block submission

            # ── ATOMIC WRITE ─────────────────────────────────────────────────
            # Score write + all GamificationService mutations must succeed
            # atomically.  If gamification raises an exception the score row
            # is also rolled back, preventing orphan/inconsistent records.
            with transactional(db):
                new_score = Score(
                    username=user.username,
                    user_id=user.id,
                    age=data.age,
                    total_score=data.total_score,
                    sentiment_score=data.sentiment_score,
                    reflection_text=reflection,
                    is_rushed=data.is_rushed,
                    is_inconsistent=data.is_inconsistent,
                    timestamp=datetime.now(UTC).isoformat(),
                    detailed_age_group=data.detailed_age_group,
                    session_id=session_id
                )
                db.add(new_score)
                db.flush()  # Assign new_score.id before gamification

                GamificationService.award_xp(db, user.id, 100, "Assessment completion")
                GamificationService.update_streak(db, user.id, "assessment")
                GamificationService.check_achievements(db, user.id, "assessment")
            # ─────────────────────────────────────────────────────────────────

            db.refresh(new_score)

            logger.info(f"Exam saved successfully", extra={
                "user_id": user.id,
                "session_id": session_id,
                "score": data.total_score,
                "sentiment_score": data.sentiment_score
            })
            return new_score

        except Exception as e:
            logger.error(f"Failed to save exam score", extra={
                "user_id": user.id,
                "session_id": session_id,
                "error": str(e)
            }, exc_info=True)
            raise e

    @staticmethod
    def get_history(db: Session, user: User, skip: int = 0, limit: int = 10) -> Tuple[List[Score], int]:
        """Retrieves paginated exam history for the specified user."""
        limit = min(limit, 100)  # Guard: cap at 100 to prevent unbounded queries
        query = db.query(Score).filter(Score.user_id == user.id)
        total = query.count()
        results = query.order_by(Score.timestamp.desc()).offset(skip).limit(limit).all()
        return results, total
