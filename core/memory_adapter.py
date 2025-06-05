"""
Memory Adapter - Abstract interface for memory persistence

This module provides an abstract base class for memory backends,
allowing ByteCore to work with different storage systems.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path
import yaml


class MemoryAdapter(ABC):
    """
    Abstract base class for memory persistence backends.
    
    Implementations can use YAML, JSON, databases, or any other
    storage mechanism to persist agent memory and context.
    """
    
    @abstractmethod
    def save(self, key: str, data: Any) -> bool:
        """
        Save data to the memory backend.
        
        Args:
            key: Unique identifier for the data
            data: Data to persist
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[Any]:
        """
        Load data from the memory backend.
        
        Args:
            key: Unique identifier for the data
            
        Returns:
            Loaded data or None if not found
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete data from the memory backend.
        
        Args:
            key: Unique identifier for the data
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the memory backend.
        
        Args:
            key: Unique identifier to check
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def list_keys(self) -> list[str]:
        """
        List all keys in the memory backend.
        
        Returns:
            List of all keys
        """
        pass


class YAMLMemoryAdapter(MemoryAdapter):
    """
    YAML-based memory adapter for file system persistence.
    """
    
    def __init__(self, base_path: str = "./memory"):
        """Initialize with base directory for YAML files."""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def _get_file_path(self, key: str) -> Path:
        """Convert key to file path."""
        # Sanitize key for filesystem
        safe_key = key.replace("/", "_").replace("\\", "_")
        return self.base_path / f"{safe_key}.yaml"
    
    def save(self, key: str, data: Any) -> bool:
        """Save data as YAML file."""
        try:
            file_path = self._get_file_path(key)
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save {key}: {e}")
            return False
    
    def load(self, key: str) -> Optional[Any]:
        """Load data from YAML file."""
        try:
            file_path = self._get_file_path(key)
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return yaml.safe_load(f)
            return None
        except Exception as e:
            self.logger.error(f"Failed to load {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete YAML file."""
        try:
            file_path = self._get_file_path(key)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if YAML file exists."""
        return self._get_file_path(key).exists()
    
    def list_keys(self) -> list[str]:
        """List all YAML files."""
        try:
            files = self.base_path.glob("*.yaml")
            return [f.stem for f in files]
        except Exception as e:
            self.logger.error(f"Failed to list keys: {e}")
            return []


class JSONMemoryAdapter(MemoryAdapter):
    """
    JSON-based memory adapter for file system persistence.
    """
    
    def __init__(self, file_path: str = "./memory/bytecore_memory.json"):
        """Initialize with JSON file path."""
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self._data: Dict[str, Any] = {}
        self._load_all()
    
    def _load_all(self) -> None:
        """Load entire JSON file into memory."""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as f:
                    self._data = json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load JSON: {e}")
                self._data = {}
    
    def _save_all(self) -> bool:
        """Save entire memory to JSON file."""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self._data, f, indent=2, default=str)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save JSON: {e}")
            return False
    
    def save(self, key: str, data: Any) -> bool:
        """Save data to JSON memory."""
        self._data[key] = data
        return self._save_all()
    
    def load(self, key: str) -> Optional[Any]:
        """Load data from JSON memory."""
        return self._data.get(key)
    
    def delete(self, key: str) -> bool:
        """Delete data from JSON memory."""
        if key in self._data:
            del self._data[key]
            return self._save_all()
        return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in JSON memory."""
        return key in self._data
    
    def list_keys(self) -> list[str]:
        """List all keys in JSON memory."""
        return list(self._data.keys())


# Placeholder for future Neo4j adapter
class Neo4jMemoryAdapter(MemoryAdapter):
    """
    Neo4j graph database memory adapter.
    
    TODO: Implement graph-based memory storage for complex relationships.
    """
    
    def __init__(self, uri: str, username: str, password: str):
        """Initialize Neo4j connection."""
        self.logger = logging.getLogger(__name__)
        self.logger.warning("Neo4j adapter not yet implemented")
        # TODO: Implement Neo4j driver connection
    
    def save(self, key: str, data: Any) -> bool:
        """Save to Neo4j graph."""
        # TODO: Implement graph storage
        raise NotImplementedError("Neo4j adapter coming soon")
    
    def load(self, key: str) -> Optional[Any]:
        """Load from Neo4j graph."""
        # TODO: Implement graph retrieval
        raise NotImplementedError("Neo4j adapter coming soon")
    
    def delete(self, key: str) -> bool:
        """Delete from Neo4j graph."""
        # TODO: Implement graph deletion
        raise NotImplementedError("Neo4j adapter coming soon")
    
    def exists(self, key: str) -> bool:
        """Check existence in Neo4j graph."""
        # TODO: Implement existence check
        raise NotImplementedError("Neo4j adapter coming soon")
    
    def list_keys(self) -> list[str]:
        """List keys in Neo4j graph."""
        # TODO: Implement key listing
        raise NotImplementedError("Neo4j adapter coming soon")