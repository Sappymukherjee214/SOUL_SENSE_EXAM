import httpx
import time
import asyncio
from typing import Dict, Any, List, Optional
from backend.fastapi.app.config import get_settings_instance

class GitHubService:
    def __init__(self):
        self.settings = get_settings_instance()
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "SoulSense-Contributions-Dashboard"
        }
        if self.settings.github_token:
            self.headers["Authorization"] = f"token {self.settings.github_token}"
        
        self.owner = self.settings.github_repo_owner
        self.repo = self.settings.github_repo_name
        
        # Simple in-memory cache: {key: (data, timestamp)}
        self._cache: Dict[str, tuple[Any, float]] = {}
        self.CACHE_TTL = 3600  # 1 hour cache

    async def _get(self, endpoint: str, params: Dict = None) -> Any:
        # Check cache
        cache_key = f"{endpoint}:{str(params)}"
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.CACHE_TTL:
                return data

        async with httpx.AsyncClient() as client:
            try:
                url = f"{self.base_url}{endpoint}"
                response = await client.get(url, headers=self.headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    # Update cache
                    self._cache[cache_key] = (data, time.time())
                    return data
                elif response.status_code == 403:
                    print(f"❌ GitHub API Rate Limit Exceeded or Forbidden: {response.text}")
                    return None
                else:
                    print(f"⚠️ GitHub API Error ({response.status_code}): {response.text}")
                    return None
            except Exception as e:
                print(f"❌ GitHub Request Failed: {e}")
                return None

    async def get_repo_stats(self) -> Dict[str, Any]:
        """Fetch general repository statistics."""
        data = await self._get(f"/repos/{self.owner}/{self.repo}")
        if not data:
            return {
                "stars": 0,
                "forks": 0,
                "open_issues": 0,
                "watchers": 0,
                "description": "Unavailable",
                "html_url": f"https://github.com/{self.owner}/{self.repo}"
            }
            
        return {
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "watchers": data.get("watchers_count", 0),
            "description": data.get("description", ""),
            "html_url": data.get("html_url", "")
        }

    async def get_contributors(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch top contributors."""
        # By default gets top 100
        data = await self._get(f"/repos/{self.owner}/{self.repo}/contributors", params={"per_page": limit})
        if not data:
            return []
            
        contributors = []
        for contributor in data:
            contributors.append({
                "login": contributor.get("login"),
                "avatar_url": contributor.get("avatar_url"),
                "html_url": contributor.get("html_url"),
                "contributions": contributor.get("contributions"),
                "type": contributor.get("type")
            })
        return contributors

    async def get_pull_requests(self) -> Dict[str, int]:
        """Fetch basic PR stats (Merged vs Open)."""
        # Note: This is a simplification. Accurate counts for large repos need search API.
        # Open PRs
        open_prs_data = await self._get(f"/repos/{self.owner}/{self.repo}/pulls", params={"state": "open", "per_page": 1})
        # This only returns the list. We need to check search API for accurate counts or just count page 1 (limited).
        # Better approach: Use the /search/issues endpoint for accurate counts
        
        # Search Open PRs
        open_search = await self._get("/search/issues", params={"q": f"repo:{self.owner}/{self.repo} is:pr is:open"})
        open_count = open_search.get("total_count", 0) if open_search else 0

        # Search Merged PRs
        merged_search = await self._get("/search/issues", params={"q": f"repo:{self.owner}/{self.repo} is:pr is:merged"})
        merged_count = merged_search.get("total_count", 0) if merged_search else 0
        
        return {
            "open": open_count,
            "merged": merged_count,
            "total": open_count + merged_count
        }

    async def get_activity(self) -> List[Dict[str, Any]]:
        """Fetch commit activity for the last year (weekly)."""
        # Returns [ { total, week, days: [] } ... ]
        data = await self._get(f"/repos/{self.owner}/{self.repo}/stats/commit_activity")
        if not data:
            return []
        
        # Filter 0 activity weeks if desired, or return all
        return data

# Singleton instance
github_service = GitHubService()
