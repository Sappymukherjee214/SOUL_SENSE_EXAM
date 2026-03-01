"""API router for Team Vision collaborative document management."""
import logging
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional, Annotated

from ..services.db_service import get_db
from ..models import TeamVisionDocument, User
from .auth import get_current_user
from ..utils.redlock import redlock_service
from ..schemas.team import (
    TeamVisionResponse, TeamVisionCreate, TeamVisionUpdate, 
    LockAcquireResponse, LockReleaseRequest
)

logger = logging.getLogger("api.routers.team_vision")

router = APIRouter(tags=["Team EI - Vision Documents"])

@router.get("/{document_id}", response_model=TeamVisionResponse)
async def get_team_vision(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[User, Depends(get_current_user)] = None
):
    """Fetches a document and shows its current lock status (Read-Only detection)."""
    stmt = select(TeamVisionDocument).filter(TeamVisionDocument.id == document_id)
    res = await db.execute(stmt)
    doc = res.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Team Vision Document not found")
        
    lock_info = await redlock_service.get_lock_info(str(document_id))
    
    response_dict = doc.to_dict()
    response_dict["lock_status"] = lock_info # Tells and UI if it's currently locked
    
    return TeamVisionResponse(**response_dict)

@router.post("/{document_id}/lock", response_model=LockAcquireResponse)
async def hold_vision_lock(
    document_id: int,
    ttl_seconds: int = 30,
    current_user: Annotated[User, Depends(get_current_user)] = None
):
    """
    Acquires an exclusive edit lock (Redlock) for the document.
    Returns the 'lock_value' which must be passed in the PUT update.
    """
    success, lock_val = await redlock_service.acquire_lock(
        str(document_id), current_user.id, ttl_seconds
    )
    
    if not success:
        return LockAcquireResponse(
            success=False, 
            message="Document is already being edited by another user.",
            expires_in=0
        )
        
    return LockAcquireResponse(
        success=True,
        lock_value=lock_val,
        message="Lock acquired successfully.",
        expires_in=ttl_seconds
    )

@router.post("/{document_id}/unlock")
async def release_vision_lock(
    document_id: int,
    req: LockReleaseRequest,
    current_user: Annotated[User, Depends(get_current_user)] = None
):
    """Releases the lock prematurely if the user finished editing."""
    success = await redlock_service.release_lock(str(document_id), req.lock_value)
    if not success:
        raise HTTPException(
            status_code=403, 
            detail="Failed to release lock. It might have expired or you don't own it."
        )
    return {"message": "Lock released."}

@router.put("/{document_id}", response_model=TeamVisionResponse)
async def update_team_vision(
    document_id: int,
    update_data: TeamVisionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[User, Depends(get_current_user)] = None
):
    """
    Saves changes to the Team Vision document.
    Enforces BOTH:
    1. Distributed Lock (Ownership verification)
    2. Fencing Token (Monotonic version check)
    """
    # 1. Ownership Check (Redlock)
    lock_info = await redlock_service.get_lock_info(str(document_id))
    if not lock_info or lock_info["user_id"] != current_user.id:
         raise HTTPException(
            status_code=423, # Locked
            detail="You do not hold the edit lock for this document."
        )

    # 2. Fetch current record
    stmt = select(TeamVisionDocument).filter(TeamVisionDocument.id == document_id)
    res = await db.execute(stmt)
    doc = res.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # 3. Fencing Token Check (Prevent stale writes if someone bypassed lock)
    if doc.version != update_data.version:
         raise HTTPException(
            status_code=409, # Conflict
            detail=f"Stale Update Rejected. Database version is {doc.version}, you sent {update_data.version}. "
                   "Refreshing your window is required."
        )

    # 4. Perform Update and INCREMENT version (The Fencing Token)
    doc.title = update_data.title
    doc.content = update_data.content
    doc.version += 1 # Monotonic increase
    doc.last_modified_by_id = current_user.id
    
    await db.commit()
    await db.refresh(doc)
    
    return TeamVisionResponse(**doc.to_dict())

@router.post("/", response_model=TeamVisionResponse)
async def create_team_vision(
    data: TeamVisionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Annotated[User, Depends(get_current_user)] = None
):
    """Standard creation of a new group document."""
    doc = TeamVisionDocument(
        team_id=data.team_id,
        title=data.title,
        content=data.content,
        version=1,
        last_modified_by_id=current_user.id
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return TeamVisionResponse(**doc.to_dict())
