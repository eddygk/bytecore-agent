"""
Context Manager - Maintains state and conversation context

This module manages the execution context for ByteCore Agent, including
conversation history, user preferences, and session state.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path

from .memory_adapter import MemoryAdapter


@dataclass
class Message:
    """Represents a single message in the conversation."""

    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    """Represents an agent session with conversation history."""

    id: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    messages: List[Message] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    active: bool = True


class ContextManager:
    """
    Manages execution context and conversation state for ByteCore Agent.

    Handles session management, message history, and context persistence
    across agent restarts using the configured memory adapter.
    """

    def __init__(
        self,
        memory_adapter: MemoryAdapter,
        max_history_length: int = 100,
        context_window: int = 10,
    ):
        """
        Initialize the ContextManager.

        Args:
            memory_adapter: Memory backend for persistence
            max_history_length: Maximum messages to retain in history
            context_window: Number of recent messages for context
        """
        self.memory = memory_adapter
        self.max_history = max_history_length
        self.context_window = context_window
        self.current_session: Optional[Session] = None
        self.sessions: Dict[str, Session] = {}
        self.global_context: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)

        # Load persisted context
        self._load_context()

    def _load_context(self) -> None:
        """Load persisted context from memory adapter."""
        try:
            # Load global context
            global_data = self.memory.load("global_context")
            if global_data:
                self.global_context = global_data

            # Load active sessions
            sessions_data = self.memory.load("sessions")
            if sessions_data:
                # Reconstruct session objects
                for session_id, session_data in sessions_data.items():
                    session = Session(
                        id=session_data["id"],
                        started_at=datetime.fromisoformat(session_data["started_at"]),
                        messages=[
                            Message(
                                role=msg["role"],
                                content=msg["content"],
                                timestamp=datetime.fromisoformat(msg["timestamp"]),
                                metadata=msg.get("metadata", {}),
                            )
                            for msg in session_data["messages"]
                        ],
                        context=session_data.get("context", {}),
                        active=session_data.get("active", True),
                    )
                    self.sessions[session_id] = session

            self.logger.info("Context loaded successfully")

        except Exception as e:
            self.logger.error(f"Failed to load context: {e}")

    def _save_context(self) -> None:
        """Persist current context to memory adapter."""
        try:
            # Save global context
            self.memory.save("global_context", self.global_context)

            # Serialize sessions
            sessions_data = {}
            for session_id, session in self.sessions.items():
                sessions_data[session_id] = {
                    "id": session.id,
                    "started_at": session.started_at.isoformat(),
                    "messages": [
                        {
                            "role": msg.role,
                            "content": msg.content,
                            "timestamp": msg.timestamp.isoformat(),
                            "metadata": msg.metadata,
                        }
                        for msg in session.messages[-self.max_history :]
                    ],
                    "context": session.context,
                    "active": session.active,
                }

            self.memory.save("sessions", sessions_data)
            self.logger.debug("Context saved successfully")

        except Exception as e:
            self.logger.error(f"Failed to save context: {e}")

    def create_session(self, session_id: str) -> Session:
        """Create a new conversation session."""
        session = Session(id=session_id)
        self.sessions[session_id] = session
        self.current_session = session
        self._save_context()
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve a session by ID."""
        return self.sessions.get(session_id)

    def set_current_session(self, session_id: str) -> bool:
        """Set the active session for context operations."""
        if session_id in self.sessions:
            self.current_session = self.sessions[session_id]
            return True
        return False

    def add_message(
        self, role: str, content: str, metadata: Optional[Dict] = None
    ) -> None:
        """
        Add a message to the current session.

        Args:
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional metadata dictionary
        """
        if not self.current_session:
            raise ValueError("No active session")

        message = Message(role=role, content=content, metadata=metadata or {})
        self.current_session.messages.append(message)

        # Trim history if needed
        if len(self.current_session.messages) > self.max_history:
            self.current_session.messages = self.current_session.messages[
                -self.max_history :
            ]

        self._save_context()

    def get_recent_messages(self, count: Optional[int] = None) -> List[Message]:
        """Get recent messages from current session."""
        if not self.current_session:
            return []

        count = count or self.context_window
        return self.current_session.messages[-count:]

    def update_context(self, key: str, value: Any, scope: str = "session") -> None:
        """
        Update context variables.

        Args:
            key: Context key
            value: Context value
            scope: 'session' or 'global'
        """
        if scope == "global":
            self.global_context[key] = value
        elif scope == "session" and self.current_session:
            self.current_session.context[key] = value
        else:
            raise ValueError(f"Invalid scope '{scope}' or no active session")

        self._save_context()

    def get_context(self, key: str, scope: str = "session") -> Any:
        """Retrieve a context variable."""
        if scope == "global":
            return self.global_context.get(key)
        elif scope == "session" and self.current_session:
            return self.current_session.context.get(key)
        return None

    def get_full_context(self) -> Dict[str, Any]:
        """Get combined global and session context."""
        context = self.global_context.copy()
        if self.current_session:
            context.update(self.current_session.context)
        return context

    def clear_session(self, session_id: str) -> bool:
        """Clear a session's history and context."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.messages.clear()
            session.context.clear()
            session.active = False
            self._save_context()
            return True
        return False
