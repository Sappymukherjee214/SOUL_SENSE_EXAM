import logging
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from ..root_models import AuditLog

logger = logging.getLogger("api.audit")

class AuditService:
    """Async Audit Service for FastAPI backend."""
    
    ALLOWED_DETAIL_FIELDS = {
        "status", "reason", "method", "device", "location", "changed_field", "old_value"
    }

    @classmethod
    async def log_event(cls, user_id: int, action: str, 
                        ip_address: Optional[str] = "SYSTEM", 
                        user_agent: Optional[str] = None, 
                        details: Optional[Dict[str, Any]] = None,
                        db_session: Optional[AsyncSession] = None) -> bool:
        """
        Log a security-critical event (Async).
        """
        if not db_session:
            logger.warning(f"Audit log skipped for user {user_id} - no db_session provided")
            return False
            
        try:
            # 1. Sanitize Inputs
            safe_ua = (user_agent[:250] + "...") if user_agent and len(user_agent) > 250 else user_agent
            
            # Filter Details
            safe_details = "{}"
            if details:
                filtered = {k: v for k, v in details.items() if k in cls.ALLOWED_DETAIL_FIELDS}
                try:
                    safe_details = json.dumps(filtered)
                except Exception as e:
                    logger.warning(f"Failed to serialize audit details: {e}")
            
            # 2. Create Record
            log_entry = AuditLog(
                user_id=user_id,
                action=action,
                ip_address=ip_address,
                user_agent=safe_ua,
                details=safe_details,
                timestamp=datetime.now(timezone.utc)
            )
            
            db_session.add(log_entry)
            # We don't commit here if it's part of a larger transaction, 
            # but auth_service awaits it directly. 
            # Better to commit if we want it to be persistent.
            await db_session.commit()
            
            logger.info(f"AUDIT LOG: User {user_id} performed {action} from {ip_address}")
            return True
            
        except Exception as e:
            logger.error(f"AUDIT LOG FAILURE: User {user_id} performed {action}. Error: {e}")
            await db_session.rollback()
            return False
