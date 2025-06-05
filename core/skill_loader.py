"""
Skill Loader - Dynamic module loading system for agent skills

This module handles the discovery, loading, and management of
modular skills that extend ByteCore's capabilities.
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
from abc import ABC, abstractmethod
import asyncio


class BaseSkill(ABC):
    """
    Abstract base class for all ByteCore skills.

    Skills are self-contained modules that provide specific capabilities
    to the agent. Each skill must implement the execute method.
    """

    def __init__(self, context):
        """Initialize skill with execution context."""
        self.context = context
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Execute the skill's primary function.

        Args:
            **kwargs: Skill-specific parameters

        Returns:
            Skill execution result
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the skill's unique name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of the skill's capabilities."""
        pass

    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Return skill metadata for MCP compatibility.

        Override in subclasses to provide additional metadata.
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": getattr(self, "version", "0.1.0"),
            "author": getattr(self, "author", "ByteCore"),
            "parameters": self.get_parameters(),
        }

    def get_parameters(self) -> Dict[str, Any]:
        """Extract parameter information from execute method."""
        sig = inspect.signature(self.execute)
        params = {}

        for name, param in sig.parameters.items():
            if name == "self" or name == "kwargs":
                continue

            param_info = {
                "type": (
                    str(param.annotation) if param.annotation != param.empty else "Any"
                ),
                "required": param.default == param.empty,
                "default": None if param.default == param.empty else param.default,
            }
            params[name] = param_info

        return params

    async def validate_parameters(self, **kwargs) -> bool:
        """
        Validate input parameters before execution.

        Override in subclasses for custom validation.
        """
        return True


class SkillLoader:
    """
    Dynamic skill loading and management system.

    Discovers and loads skills from the skills directory,
    managing their lifecycle and providing access to the agent.
    """

    def __init__(self, skills_path: str = "./skills", hot_reload: bool = False):
        """
        Initialize the skill loader.

        Args:
            skills_path: Directory containing skill modules
        """
        self.skills_path = Path(skills_path)
        self.hot_reload = hot_reload
        self.loaded_skills: Dict[str, Type[BaseSkill]] = {}
        self.skill_instances: Dict[str, BaseSkill] = {}
        self.logger = logging.getLogger(__name__)

        # Ensure skills directory exists
        self.skills_path.mkdir(parents=True, exist_ok=True)

        # Auto-load skills on initialization
        self.discover_skills()

    def discover_skills(self) -> None:
        """Discover and load all available skills."""
        self.logger.info(f"Discovering skills in {self.skills_path}")

        # Add skills directory to Python path
        import sys

        if str(self.skills_path.parent) not in sys.path:
            sys.path.insert(0, str(self.skills_path.parent))

        # Find all Python files in skills directory
        skill_files = self.skills_path.glob("*.py")

        for skill_file in skill_files:
            if skill_file.name.startswith("_"):
                continue  # Skip private modules

            try:
                # Import the module
                module_name = f"skills.{skill_file.stem}"
                module = importlib.import_module(module_name)

                # Find skill classes in the module
                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, BaseSkill)
                        and obj != BaseSkill
                    ):
                        if not inspect.iscoroutinefunction(obj.execute):
                            self.logger.warning(
                                f"Skill {obj.__name__} execute() is not async-compatible"
                            )
                            continue

                        skill_instance = obj(None)  # Temporary instance for metadata
                        skill_name = skill_instance.name

                        self.loaded_skills[skill_name] = obj
                        self.logger.info(f"Loaded skill: {skill_name}")

            except Exception as e:
                self.logger.error(f"Failed to load skill from {skill_file}: {e}")

    async def get_skill(self, skill_name: str) -> Optional[Type[BaseSkill]]:
        """
        Get a skill class by name.

        Args:
            skill_name: Name of the skill to retrieve

        Returns:
            Skill class or None if not found
        """
        return self.loaded_skills.get(skill_name)

    def list_skills(self) -> List[Dict[str, Any]]:
        """
        List all available skills with their metadata.

        Returns:
            List of skill metadata dictionaries
        """
        skills_info = []

        for skill_name, skill_class in self.loaded_skills.items():
            try:
                # Create temporary instance to get metadata
                temp_instance = skill_class(None)
                skills_info.append(temp_instance.metadata)
            except Exception as e:
                self.logger.error(f"Failed to get metadata for {skill_name}: {e}")

        return skills_info

    def reload_skill(self, skill_name: str) -> bool:
        """
        Reload a specific skill module.

        Useful for development when skills are being modified.

        Args:
            skill_name: Name of the skill to reload

        Returns:
            True if successful, False otherwise
        """
        if not self.hot_reload:
            self.logger.warning("Hot reload attempted while disabled")
            return False

        try:
            # Find the module containing the skill
            for module_name, skill_class in list(self.loaded_skills.items()):
                if module_name == skill_name:
                    # Get the module
                    module = inspect.getmodule(skill_class)

                    # Reload the module
                    importlib.reload(module)

                    # Re-discover skills from this module
                    for name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, BaseSkill)
                            and obj != BaseSkill
                        ):
                            skill_instance = obj(None)
                            if skill_instance.name == skill_name:
                                self.loaded_skills[skill_name] = obj
                                self.logger.info(f"Reloaded skill: {skill_name}")
                                return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to reload skill {skill_name}: {e}")
            return False

    def get_skill_parameters(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Get parameter information for a specific skill."""
        skill_class = self.loaded_skills.get(skill_name)
        if skill_class:
            temp_instance = skill_class(None)
            return temp_instance.get_parameters()
        return None
