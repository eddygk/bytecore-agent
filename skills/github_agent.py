"""
GitHub Agent Skill - Repository management and automation

Provides GitHub integration capabilities for ByteCore Agent,
enabling repository analysis, issue management, and automation.
"""

import asyncio
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from github import Github, GithubException
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

from core.skill_loader import BaseSkill


class GitHubAgentSkill(BaseSkill):
    """
    GitHub integration skill for repository management.
    
    Capabilities:
    - Repository analysis and statistics
    - Issue and PR management
    - Automated workflows
    - Code review assistance
    """
    
    def __init__(self, context):
        """Initialize GitHub skill."""
        super().__init__(context)
        self.github_client = None
        self.current_repo = None
    
    @property
    def name(self) -> str:
        """Return skill name."""
        return "github_agent"
    
    @property
    def description(self) -> str:
        """Return skill description."""
        return "GitHub repository management and automation capabilities"
    
    @property
    def version(self) -> str:
        """Return skill version."""
        return "0.1.0"
    
    @property
    def author(self) -> str:
        """Return skill author."""
        return "ByteCore Team"
    
    def _initialize_client(self, token: Optional[str] = None) -> bool:
        """
        Initialize GitHub client with authentication.
        
        Args:
            token: GitHub personal access token
            
        Returns:
            True if successful, False otherwise
        """
        if not GITHUB_AVAILABLE:
            self.logger.error("PyGithub not installed. Run: pip install PyGithub")
            return False
        
        # Try to get token from context or environment
        if not token:
            token = self.context.get_context("github_token", "global")
        if not token:
            token = os.environ.get("GITHUB_TOKEN")
        
        if not token:
            self.logger.error("No GitHub token found")
            return False
        
        try:
            self.github_client = Github(token)
            # Test authentication
            self.github_client.get_user().login
            return True
        except Exception as e:
            self.logger.error(f"Failed to authenticate with GitHub: {e}")
            return False
    
    async def execute(
        self,
        action: str,
        repo: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Execute GitHub operations.
        
        Args:
            action: Action to perform (analyze, close_issues, create_pr, etc.)
            repo: Repository in format 'owner/name'
            **kwargs: Additional action-specific parameters
            
        Returns:
            Action-specific results
        """
        # Initialize client if needed
        if not self.github_client:
            if not self._initialize_client(kwargs.get("token")):
                return {"error": "Failed to initialize GitHub client"}
        
        # Set current repository if provided
        if repo:
            try:
                self.current_repo = self.github_client.get_repo(repo)
            except GithubException as e:
                return {"error": f"Failed to access repository {repo}: {e}"}
        
        # Route to appropriate action handler
        action_handlers = {
            "analyze": self._analyze_repository,
            "close_issues": self._close_issues,
            "list_issues": self._list_issues,
            "create_issue": self._create_issue,
            "get_stats": self._get_repository_stats,
            "list_prs": self._list_pull_requests,
        }
        
        handler = action_handlers.get(action)
        if not handler:
            return {"error": f"Unknown action: {action}"}
        
        # Execute action
        try:
            result = await handler(**kwargs)
            return result
        except Exception as e:
            self.logger.error(f"Action {action} failed: {e}")
            return {"error": str(e)}
    
    async def _analyze_repository(self, **kwargs) -> Dict[str, Any]:
        """Analyze repository structure and provide insights."""
        if not self.current_repo:
            return {"error": "No repository specified"}
        
        analysis = {
            "name": self.current_repo.full_name,
            "description": self.current_repo.description,
            "language": self.current_repo.language,
            "stars": self.current_repo.stargazers_count,
            "forks": self.current_repo.forks_count,
            "open_issues": self.current_repo.open_issues_count,
            "created_at": self.current_repo.created_at.isoformat(),
            "updated_at": self.current_repo.updated_at.isoformat(),
            "topics": self.current_repo.get_topics(),
            "default_branch": self.current_repo.default_branch,
        }
        
        # Get language breakdown
        languages = self.current_repo.get_languages()
        analysis["languages"] = dict(languages)
        
        # Get recent activity
        commits = list(self.current_repo.get_commits()[:10])
        analysis["recent_commits"] = [
            {
                "sha": c.sha[:7],
                "message": c.commit.message.split('\n')[0],
                "author": c.commit.author.name,
                "date": c.commit.author.date.isoformat()
            }
            for c in commits
        ]
        
        return {"analysis": analysis}
    
    async def _list_issues(self, state: str = "open", **kwargs) -> Dict[str, Any]:
        """List repository issues."""
        if not self.current_repo:
            return {"error": "No repository specified"}
        
        issues = self.current_repo.get_issues(state=state)
        issue_list = []
        
        for issue in issues[:20]:  # Limit to 20 issues
            issue_list.append({
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "author": issue.user.login,
                "created_at": issue.created_at.isoformat(),
                "labels": [label.name for label in issue.labels],
                "comments": issue.comments
            })
        
        return {
            "issues": issue_list,
            "total_count": issues.totalCount
        }
    
    async def _close_issues(self, labels: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """Close issues based on criteria."""
        if not self.current_repo:
            return {"error": "No repository specified"}
        
        closed_count = 0
        closed_issues = []
        
        # Get open issues
        issues = self.current_repo.get_issues(state="open")
        
        for issue in issues:
            # Check if issue matches criteria
            should_close = False
            
            if labels:
                issue_labels = [label.name for label in issue.labels]
                if any(label in issue_labels for label in labels):
                    should_close = True
            
            if should_close:
                try:
                    issue.edit(state="closed")
                    closed_count += 1
                    closed_issues.append({
                        "number": issue.number,
                        "title": issue.title
                    })
                except Exception as e:
                    self.logger.error(f"Failed to close issue #{issue.number}: {e}")
        
        return {
            "closed_count": closed_count,
            "closed_issues": closed_issues
        }
    
    async def _create_issue(self, title: str, body: str, labels: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """Create a new issue."""
        if not self.current_repo:
            return {"error": "No repository specified"}
        
        try:
            issue = self.current_repo.create_issue(
                title=title,
                body=body,
                labels=labels or []
            )
            
            return {
                "created": True,
                "issue": {
                    "number": issue.number,
                    "title": issue.title,
                    "url": issue.html_url
                }
            }
        except Exception as e:
            return {"error": f"Failed to create issue: {e}"}
    
    async def _get_repository_stats(self, **kwargs) -> Dict[str, Any]:
        """Get detailed repository statistics."""
        if not self.current_repo:
            return {"error": "No repository specified"}
        
        stats = {
            "contributors": self.current_repo.get_contributors().totalCount,
            "commits": self.current_repo.get_commits().totalCount,
            "branches": self.current_repo.get_branches().totalCount,
            "tags": self.current_repo.get_tags().totalCount,
            "releases": self.current_repo.get_releases().totalCount,
            "watchers": self.current_repo.watchers_count,
            "network_count": self.current_repo.network_count,
            "size_kb": self.current_repo.size,
        }
        
        # Get pull request stats
        open_prs = self.current_repo.get_pulls(state="open").totalCount
        closed_prs = self.current_repo.get_pulls(state="closed").totalCount
        stats["pull_requests"] = {
            "open": open_prs,
            "closed": closed_prs,
            "total": open_prs + closed_prs
        }
        
        return {"stats": stats}
    
    async def _list_pull_requests(self, state: str = "open", **kwargs) -> Dict[str, Any]:
        """List repository pull requests."""
        if not self.current_repo:
            return {"error": "No repository specified"}
        
        prs = self.current_repo.get_pulls(state=state)
        pr_list = []
        
        for pr in prs[:20]:  # Limit to 20 PRs
            pr_list.append({
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "author": pr.user.login,
                "created_at": pr.created_at.isoformat(),
                "draft": pr.draft,
                "mergeable": pr.mergeable,
                "additions": pr.additions,
                "deletions": pr.deletions,
                "changed_files": pr.changed_files
            })
        
        return {
            "pull_requests": pr_list,
            "total_count": prs.totalCount
        }