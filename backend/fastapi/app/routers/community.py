from fastapi import APIRouter, HTTPException
from backend.fastapi.app.services.github_service import github_service

router = APIRouter(tags=["Community Dashboard"])

@router.get("/stats")
async def get_community_stats():
    """Get aggregated repository statistics."""
    repo_stats = await github_service.get_repo_stats()
    pr_stats = await github_service.get_pull_requests()
    
    return {
        "repository": repo_stats,
        "pull_requests": pr_stats
    }

@router.get("/contributors")
async def get_contributors(limit: int = 100):
    """Get list of top contributors."""
    contributors = await github_service.get_contributors(limit)
    return contributors

@router.get("/activity")
async def get_activity():
    """Get weekly commit activity for the past year."""
    activity = await github_service.get_activity()
    return activity
