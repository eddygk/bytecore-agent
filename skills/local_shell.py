"""
Local Shell Skill - System command execution capabilities

Provides controlled shell command execution for system automation
and local environment interaction.
"""

import asyncio
import os
import platform
import subprocess
import shlex
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import psutil

from core.skill_loader import BaseSkill


class LocalShellSkill(BaseSkill):
    """
    Local shell execution skill for system automation.

    Capabilities:
    - Execute shell commands with safety controls
    - File system operations
    - Process management
    - System information gathering
    """

    def __init__(self, context):
        """Initialize shell skill."""
        super().__init__(context)
        self.platform = platform.system().lower()
        self.shell = self._get_default_shell()

        # Safety: Define allowed command prefixes
        self.allowed_commands = [
            "ls",
            "dir",
            "pwd",
            "cd",
            "echo",
            "cat",
            "type",
            "grep",
            "find",
            "wc",
            "head",
            "tail",
            "sort",
            "git",
            "python",
            "pip",
            "node",
            "npm",
            "curl",
            "ps",
            "top",
            "df",
            "du",
            "whoami",
            "date",
        ]

        # Safety: Define blocked patterns
        self.blocked_patterns = [
            "rm -rf",
            "del /f",
            "format",
            "fdisk",
            "sudo",
            "su",
            "chmod 777",
            "mkfs",
        ]

    @property
    def name(self) -> str:
        """Return skill name."""
        return "local_shell"

    @property
    def description(self) -> str:
        """Return skill description."""
        return "Local shell command execution and system automation"

    @property
    def version(self) -> str:
        """Return skill version."""
        return "0.1.0"

    def _get_default_shell(self) -> str:
        """Determine the default shell based on platform."""
        if self.platform == "windows":
            return "cmd.exe"
        else:
            return os.environ.get("SHELL", "/bin/bash")

    def _is_command_allowed(self, command: str) -> bool:
        """
        Check if a command is allowed based on safety rules.

        Args:
            command: Command to validate

        Returns:
            True if allowed, False otherwise
        """
        # Check for blocked patterns
        command_lower = command.lower()
        for pattern in self.blocked_patterns:
            if pattern in command_lower:
                return False

        # Check if command starts with allowed prefix
        first_word = command.split()[0] if command.split() else ""
        base_command = os.path.basename(first_word)

        # Check against allowed commands
        for allowed in self.allowed_commands:
            if base_command.startswith(allowed):
                return True

        # Check if it's a safe mode override from context
        if self.context and self.context.get_context("shell_unrestricted", "global"):
            return True

        return False

    async def execute(
        self, action: str, command: Optional[str] = None, **kwargs
    ) -> Any:
        """
        Execute shell operations.

        Args:
            action: Action to perform (run, list_processes, system_info, etc.)
            command: Shell command to execute (for 'run' action)
            **kwargs: Additional action-specific parameters

        Returns:
            Action-specific results
        """
        # Route to appropriate action handler
        action_handlers = {
            "run": self._run_command,
            "list_processes": self._list_processes,
            "system_info": self._get_system_info,
            "file_operations": self._file_operations,
            "check_command": self._check_command_availability,
        }

        handler = action_handlers.get(action)
        if not handler:
            return {"error": f"Unknown action: {action}"}

        # Execute action
        try:
            if action == "run":
                result = await handler(command, **kwargs)
            else:
                result = await handler(**kwargs)
            return result
        except Exception as e:
            self.logger.error(f"Action {action} failed: {e}")
            return {"error": str(e)}

    async def _run_command(
        self,
        command: str,
        timeout: int = 30,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Execute a shell command with safety checks."""
        if not command:
            return {"error": "No command provided"}

        # Safety check
        if not self._is_command_allowed(command):
            return {
                "error": "Command blocked by safety rules",
                "allowed_commands": self.allowed_commands,
            }

        # Prepare environment
        cmd_env = os.environ.copy()
        if env:
            cmd_env.update(env)

        # Execute command
        try:
            # Use shell=True carefully with safety checks already done
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=cmd_env,
            )

            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "error": f"Command timed out after {timeout} seconds",
                    "partial_output": "",
                }

            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "command": command,
            }

        except Exception as e:
            return {"error": f"Command execution failed: {e}"}

    async def _list_processes(self, **kwargs) -> Dict[str, Any]:
        """List running processes with details."""
        processes = []

        for proc in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent"]
        ):
            try:
                proc_info = proc.info
                processes.append(
                    {
                        "pid": proc_info["pid"],
                        "name": proc_info["name"],
                        "cpu_percent": proc_info["cpu_percent"],
                        "memory_percent": round(proc_info["memory_percent"], 2),
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage
        processes.sort(key=lambda x: x["cpu_percent"] or 0, reverse=True)

        return {
            "process_count": len(processes),
            "processes": processes[:50],  # Top 50 processes
        }

    async def _get_system_info(self, **kwargs) -> Dict[str, Any]:
        """Gather comprehensive system information."""
        # CPU info
        cpu_info = {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
        }

        # Memory info
        memory = psutil.virtual_memory()
        memory_info = {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free,
        }

        # Disk info
        disk_info = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent,
                    }
                )
            except PermissionError:
                continue

        # Network info
        network_info = psutil.net_if_addrs()

        return {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
            },
            "cpu": cpu_info,
            "memory": memory_info,
            "disk": disk_info,
            "network_interfaces": list(network_info.keys()),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
        }

    async def _file_operations(
        self, operation: str, path: str, **kwargs
    ) -> Dict[str, Any]:
        """Perform safe file system operations."""
        path_obj = Path(path)

        operations = {
            "list": self._list_directory,
            "read": self._read_file,
            "info": self._file_info,
            "find": self._find_files,
        }

        handler = operations.get(operation)
        if not handler:
            return {"error": f"Unknown file operation: {operation}"}

        return await handler(path_obj, **kwargs)

    async def _list_directory(self, path: Path, **kwargs) -> Dict[str, Any]:
        """List directory contents."""
        if not path.exists():
            return {"error": f"Path does not exist: {path}"}

        if not path.is_dir():
            return {"error": f"Path is not a directory: {path}"}

        items = []
        for item in path.iterdir():
            items.append(
                {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(
                        item.stat().st_mtime
                    ).isoformat(),
                }
            )

        return {
            "path": str(path),
            "item_count": len(items),
            "items": sorted(items, key=lambda x: (x["type"] != "directory", x["name"])),
        }

    async def _read_file(
        self, path: Path, lines: Optional[int] = None, encoding: str = "utf-8", **kwargs
    ) -> Dict[str, Any]:
        """Read file contents safely."""
        if not path.exists():
            return {"error": f"File does not exist: {path}"}

        if not path.is_file():
            return {"error": f"Path is not a file: {path}"}

        # Size limit for safety (10MB)
        if path.stat().st_size > 10 * 1024 * 1024:
            return {"error": "File too large (>10MB)"}

        try:
            with open(path, "r", encoding=encoding) as f:
                if lines:
                    content = "".join(f.readlines()[:lines])
                else:
                    content = f.read()

            return {
                "path": str(path),
                "size": path.stat().st_size,
                "encoding": encoding,
                "content": content,
                "truncated": lines is not None,
            }
        except Exception as e:
            return {"error": f"Failed to read file: {e}"}

    async def _file_info(self, path: Path, **kwargs) -> Dict[str, Any]:
        """Get detailed file information."""
        if not path.exists():
            return {"error": f"Path does not exist: {path}"}

        stat = path.stat()

        return {
            "path": str(path),
            "name": path.name,
            "type": "directory" if path.is_dir() else "file",
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "permissions": oct(stat.st_mode)[-3:],
            "owner_uid": stat.st_uid if hasattr(stat, "st_uid") else None,
            "group_gid": stat.st_gid if hasattr(stat, "st_gid") else None,
        }

    async def _find_files(
        self, path: Path, pattern: str = "*", recursive: bool = True, **kwargs
    ) -> Dict[str, Any]:
        """Find files matching a pattern."""
        if not path.exists():
            return {"error": f"Path does not exist: {path}"}

        matches = []

        if recursive:
            for match in path.rglob(pattern):
                matches.append(str(match))
        else:
            for match in path.glob(pattern):
                matches.append(str(match))

        return {
            "base_path": str(path),
            "pattern": pattern,
            "recursive": recursive,
            "match_count": len(matches),
            "matches": matches[:100],  # Limit to 100 results
        }

    async def _check_command_availability(
        self, commands: List[str], **kwargs
    ) -> Dict[str, Any]:
        """Check if commands are available in the system."""
        results = {}

        for command in commands:
            # Use 'which' on Unix-like systems, 'where' on Windows
            check_cmd = "where" if self.platform == "windows" else "which"

            try:
                result = await self._run_command(f"{check_cmd} {command}")
                results[command] = {
                    "available": result.get("success", False),
                    "path": (
                        result.get("stdout", "").strip()
                        if result.get("success")
                        else None
                    ),
                }
            except Exception:
                results[command] = {"available": False, "path": None}

        return {"commands": results}
