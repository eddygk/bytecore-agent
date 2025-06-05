import pytest
from core.skill_loader import SkillLoader


def test_discover_skills():
    loader = SkillLoader(skills_path="skills")
    skill_names = [s["name"] for s in loader.list_skills()]
    assert "github_agent" in skill_names
    assert "local_shell" in skill_names
