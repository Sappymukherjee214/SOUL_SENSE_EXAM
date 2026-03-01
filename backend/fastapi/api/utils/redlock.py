import uuid
import logging
import asyncio
from typing import Optional, Tuple
from datetime import datetime, UTC
from ..services.cache_service import cache_service

logger = logging.getLogger("api.utils.redlock")

class RedlockService:
    """
    Distributed Locking Mechanism using the Redlock algorithm principle in Redis (#1178).
    Prevents Lost Updates by ensuring only one user can edit a resource at a time.
    """

    def __init__(self):
        self._lock_prefix = "lock:team_vision:"

    async def acquire_lock(self, resource_id: str, user_id: int, ttl_seconds: int = 30) -> Tuple[bool, Optional[str]]:
        """
        Acquires a lease on a resource.
        Returns (success_boolean, lock_value_or_none).
        """
        await cache_service.connect()
        lock_key = f"{self._lock_prefix}{resource_id}"
        lock_value = f"{user_id}:{uuid.uuid4()}" # Ownership + Unique ID
        
        # NX: Only set if it doesn't exist
        # EX: Set expiration in seconds
        success = await cache_service.redis.set(
            lock_key, 
            lock_value, 
            nx=True, 
            ex=ttl_seconds
        )
        
        if success:
            logger.info(f"[Redlock] Lock ACQUIRED for resource={resource_id} by user={user_id}")
            return True, lock_value
        
        # Check if we already own it (idempotency)
        current_val = await cache_service.redis.get(lock_key)
        if current_val and current_val.startswith(f"{user_id}:"):
            # Already owned, extend it
            await cache_service.redis.expire(lock_key, ttl_seconds)
            return True, current_val
            
        logger.warning(f"[Redlock] Lock DENIED for resource={resource_id} - already held by {current_val}")
        return False, None

    async def release_lock(self, resource_id: str, lock_value: str) -> bool:
        """
        Releases a lease only if the lock_value matches (proving ownership).
        Uses Lua script for atomicity.
        """
        await cache_service.connect()
        lock_key = f"{self._lock_prefix}{resource_id}"
        
        # Lua script to release lock safely
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        result = await cache_service.redis.eval(lua_script, 1, lock_key, lock_value)
        if result == 1:
            logger.info(f"[Redlock] Lock RELEASED for resource={resource_id}")
            return True
            
        logger.error(f"[Redlock] Release FAILED for resource={resource_id} - invalid value or expired")
        return False

    async def get_lock_info(self, resource_id: str) -> Optional[dict]:
        """Returns details about who currently holds the lock."""
        await cache_service.connect()
        lock_key = f"{self._lock_prefix}{resource_id}"
        val = await cache_service.redis.get(lock_key)
        if not val:
            return None
            
        user_id, _ = val.split(":", 1)
        ttl = await cache_service.redis.ttl(lock_key)
        
        return {
            "user_id": int(user_id),
            "expires_in": ttl
        }

redlock_service = RedlockService()
