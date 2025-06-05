"""
Task Runner - Central execution engine for ByteCore Agent

This module coordinates the execution of agent tasks, managing the lifecycle
of skill invocations and maintaining execution context.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .context_manager import ContextManager
from .skill_loader import SkillLoader


class TaskStatus(Enum):
    """Enumeration of possible task states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents a single executable task."""
    id: str
    name: str
    skill: str
    parameters: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class TaskRunner:
    """
    Central task execution engine for ByteCore Agent.
    
    Manages task lifecycle, skill invocation, and result handling.
    Supports both synchronous and asynchronous task execution.
    """
    
    def __init__(
        self,
        context_manager: ContextManager,
        skill_loader: SkillLoader,
        max_concurrent_tasks: int = 5
    ):
        """
        Initialize the TaskRunner.
        
        Args:
            context_manager: Instance managing execution context
            skill_loader: Instance for loading and managing skills
            max_concurrent_tasks: Maximum number of tasks to run concurrently
        """
        self.context = context_manager
        self.skills = skill_loader
        self.max_concurrent = max_concurrent_tasks
        self.active_tasks: Dict[str, Task] = {}
        self.task_history: List[Task] = []
        self.logger = logging.getLogger(__name__)
        
    async def execute_task(self, task: Task) -> Any:
        """
        Execute a single task asynchronously.
        
        Args:
            task: Task instance to execute
            
        Returns:
            Task execution result
            
        Raises:
            Exception: If task execution fails
        """
        self.logger.info(f"Starting task {task.id}: {task.name}")
        
        # Update task status
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        self.active_tasks[task.id] = task
        
        try:
            # Load the required skill
            skill_class = await self.skills.get_skill(task.skill)
            if not skill_class:
                raise ValueError(f"Skill '{task.skill}' not found")
            
            # Initialize skill with current context
            skill_instance = skill_class(self.context)
            
            # Execute the skill
            result = await skill_instance.execute(**task.parameters)
            
            # Update task with results
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow()
            
            self.logger.info(f"Task {task.id} completed successfully")
            return result
            
        except Exception as e:
            # Handle task failure
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            
            self.logger.error(f"Task {task.id} failed: {e}")
            raise
            
        finally:
            # Clean up
            self.active_tasks.pop(task.id, None)
            self.task_history.append(task)
    
    async def run_task_batch(self, tasks: List[Task]) -> List[Any]:
        """
        Execute multiple tasks with concurrency control.
        
        Args:
            tasks: List of tasks to execute
            
        Returns:
            List of task results
        """
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def run_with_semaphore(task: Task):
            async with semaphore:
                return await self.execute_task(task)
        
        # Create coroutines for all tasks
        coroutines = [run_with_semaphore(task) for task in tasks]
        
        # Execute with gather to handle exceptions
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        return results
    
    def get_active_tasks(self) -> List[Task]:
        """Get list of currently running tasks."""
        return list(self.active_tasks.values())
    
    def get_task_history(self, limit: Optional[int] = None) -> List[Task]:
        """Get historical task execution records."""
        if limit:
            return self.task_history[-limit:]
        return self.task_history.copy()
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task.
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            True if task was cancelled, False otherwise
        """
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.utcnow()
            # TODO: Implement actual task cancellation logic
            return True
        return False