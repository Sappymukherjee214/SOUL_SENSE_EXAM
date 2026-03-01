import logging
import uuid
from datetime import datetime, UTC, timedelta
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from fastapi import status
from ..schemas import ExamResponseCreate, ExamResultCreate
from ..models import User, Score, Response, ExamSession, Question
from ..exceptions import APIException
from ..constants.errors import ErrorCode
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
    Service for handling Exam write operations via API with strict business logic validation.
    """

    EXAM_DURATION_MINUTES = 60  # Maximum time allowed for an exam

    @staticmethod
    def start_exam(db: Session, user: User) -> str:
        """
        Initiates a new exam session, persists it to DB, and returns session_id.
        Prevents multiple active sessions if necessary (policy decision).
        """
        # 1. Check for existing active sessions to prevent 'multiple attempts' bypass
        # (Optional: allow resumed sessions if they haven't expired)
        active_session = db.query(ExamSession).filter(
            ExamSession.user_id == user.id,
            ExamSession.status.in_(['STARTED', 'IN_PROGRESS']),
            ExamSession.expires_at > datetime.now(UTC)
        ).first()

        if active_session:
             logger.info(f"User resumed existing exam session", extra={
                 "user_id": user.id,
                 "session_id": active_session.session_id
             })
             return active_session.session_id

        # 2. Create new session
        session_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        expires_at = now + timedelta(minutes=ExamService.EXAM_DURATION_MINUTES)
        
        new_session = ExamSession(
            session_id=session_id,
            user_id=user.id,
            status='STARTED',
            started_at=now,
            expires_at=expires_at
        )
        
        try:
            db.add(new_session)
            db.commit()
            logger.info(f"New exam session created", extra={
                "user_id": user.id,
                "session_id": session_id,
                "expires_at": expires_at.isoformat()
            })
            return session_id
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create exam session: {e}")
            raise APIException(ErrorCode.INTERNAL_SERVER_ERROR, "Failed to initiate exam")

    @staticmethod
    def _get_valid_session(db: Session, user_id: int, session_id: str, allowed_statuses: List[str]) -> ExamSession:
        """Helper to fetch and validate an exam session."""
        session = db.query(ExamSession).filter(
            ExamSession.session_id == session_id
        ).first()

        if not session:
            logger.warning(f"Exam session not found: {session_id}", extra={"user_id": user_id})
            raise APIException(
                ErrorCode.WFK_SESSION_NOT_FOUND, 
                "Exam session does not exist",
                status_code=status.HTTP_404_NOT_FOUND
            )

        if session.user_id != user_id:
            logger.warning(f"Access denied for session {session_id}", extra={"user_id": user_id, "owner_id": session.user_id})
            raise APIException(
                ErrorCode.WFK_ACCESS_DENIED, 
                "You do not have access to this session",
                status_code=status.HTTP_403_FORBIDDEN
            )

        if session.status not in allowed_statuses:
            logger.warning(f"Invalid state transition for session {session_id}: {session.status} -> {allowed_statuses}", 
                        extra={"user_id": user_id, "current_status": session.status})
            raise APIException(
                ErrorCode.WFK_INVALID_STATE, 
                f"Invalid workflow sequence. Current status: {session.status}"
            )

        # Check for expiration (Workflow validation)
        if session.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
            logger.warning(f"Exam session expired: {session_id}", extra={"user_id": user_id})
            session.status = 'ABANDONED'
            db.commit()
            raise APIException(
                ErrorCode.WFK_SESSION_EXPIRED, 
                "Exam session has expired. Please start a new one."
            )

        return session

    @staticmethod
    def save_response(db: Session, user: User, session_id: str, data: ExamResponseCreate):
        """Saves a single question response with session state validation."""
        # 1. Validate session state
        session = ExamService._get_valid_session(db, user.id, session_id, ['STARTED', 'IN_PROGRESS'])

        try:
            # 2. Update session status to IN_PROGRESS if it was STARTED
            if session.status == 'STARTED':
                session.status = 'IN_PROGRESS'

            # 3. Save the response
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
        Saves the final exam score with strict state checking.
        Requires session to be in 'SUBMITTED' state (via /api/v1/exams/submit).
        """
        # 1. Validate session state (Must be SUBMITTED before scoring allowed)
        session = ExamService._get_valid_session(db, user.id, session_id, ['SUBMITTED'])

        try:
            # Check for Replay Attack (Already completed)
            if session.completed_at:
                raise APIException(ErrorCode.WFK_REPLAY_ATTACK, "Exam score already recorded")

            # Encrypt reflection text for privacy
            reflection = data.reflection_text
            if CRYPTO_AVAILABLE and reflection:
                try:
                    reflection = EncryptionManager.encrypt(reflection)
                except Exception as ce:
                    logger.error(f"Encryption failed for reflection: {ce}")

            # ── ATOMIC WRITE ─────────────────────────────────────────────────
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
                db.flush()

                # Update session state
                session.status = 'COMPLETED'
                session.completed_at = datetime.now(UTC)

                GamificationService.award_xp(db, user.id, 100, "Assessment completion")
                GamificationService.update_streak(db, user.id, "assessment")
                GamificationService.check_achievements(db, user.id, "assessment")
            # ─────────────────────────────────────────────────────────────────

            db.refresh(new_score)

            logger.info(f"Exam completed successfully", extra={
                "user_id": user.id,
                "session_id": session_id,
                "score": data.total_score
            })
            return new_score

        except Exception as e:
            if not isinstance(e, APIException):
                logger.error(f"Failed to save exam score", extra={
                    "user_id": user.id,
                    "session_id": session_id,
                    "error": str(e)
                }, exc_info=True)
            raise e

    @staticmethod
    def mark_as_submitted(db: Session, user_id: int, session_id: str):
        """Transitions a session to SUBMITTED state."""
        session = ExamService._get_valid_session(db, user_id, session_id, ['STARTED', 'IN_PROGRESS'])
        session.status = 'SUBMITTED'
        session.submitted_at = datetime.now(UTC)
        db.commit()
        logger.info(f"Exam session marked as SUBMITTED", extra={"user_id": user_id, "session_id": session_id})

    @staticmethod
    def get_history(db: Session, user: User, skip: int = 0, limit: int = 10) -> Tuple[List[Score], int]:
        """Retrieves paginated exam history for the specified user."""
        limit = min(limit, 100)
        query = db.query(Score).filter(Score.user_id == user.id)
        total = query.count()
        results = query.order_by(Score.timestamp.desc()).offset(skip).limit(limit).all()
        return results, total
