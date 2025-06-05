import asyncio
from unittest.mock import patch, MagicMock

import pytest

from skills.github_agent import GitHubAgentSkill
from core.context_manager import ContextManager
from core.memory_adapter import YAMLMemoryAdapter


@pytest.mark.asyncio
async def test_list_issues():
    context = ContextManager(YAMLMemoryAdapter())
    skill = GitHubAgentSkill(context)

    with (
        patch("skills.github_agent.Github", create=True) as MockGithub,
        patch("skills.github_agent.GithubException", create=True),
    ):
        # force module availability
        from skills import github_agent

        github_agent.GITHUB_AVAILABLE = True
        mock_issue = MagicMock()
        mock_issue.number = 1
        mock_issue.title = "Test"
        mock_issue.state = "open"
        mock_issue.user.login = "alice"
        mock_issue.created_at.isoformat.return_value = "2024-01-01"
        mock_issue.labels = []
        mock_issue.comments = 0

        mock_repo = MagicMock()
        issue_list = MagicMock()
        issue_list.__iter__.return_value = [mock_issue].__iter__()
        issue_list.__getitem__.return_value = [mock_issue]
        issue_list.totalCount = 1
        mock_repo.get_issues.return_value = issue_list

        mock_client = MagicMock()
        mock_client.get_repo.return_value = mock_repo
        mock_client.get_user.return_value.login = "alice"
        MockGithub.return_value = mock_client

        result = await skill.execute("list_issues", repo="owner/repo", token="tkn")

    assert result["total_count"] == 1
    assert result["issues"][0]["number"] == 1
