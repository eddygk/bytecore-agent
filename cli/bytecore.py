#!/usr/bin/env python3
"""
ByteCore CLI - Command-line interface for ByteCore Agent

Provides a rich CLI experience for interacting with the agent,
executing tasks, and managing skills.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import uuid
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.panel import Panel
from rich.logging import RichHandler

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.task_runner import TaskRunner, Task
from core.context_manager import ContextManager
from core.memory_adapter import YAMLMemoryAdapter, JSONMemoryAdapter
from core.skill_loader import SkillLoader

# Initialize CLI app
app = typer.Typer(
    name="bytecore",
    help="ByteCore Agent CLI - Your intelligent automation assistant",
    add_completion=True,
)

console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)
logger = logging.getLogger("bytecore")


class ByteCoreAgent:
    """Main agent class coordinating all components."""

    def __init__(self, memory_backend: str = "yaml"):
        """Initialize the agent with specified memory backend."""
        # Initialize memory adapter
        if memory_backend == "yaml":
            self.memory = YAMLMemoryAdapter()
        elif memory_backend == "json":
            self.memory = JSONMemoryAdapter()
        else:
            raise ValueError(f"Unknown memory backend: {memory_backend}")

        # Initialize components
        self.context = ContextManager(self.memory)
        self.skills = SkillLoader()
        self.runner = TaskRunner(self.context, self.skills)

        # Create or load session
        session_id = str(uuid.uuid4())
        self.context.create_session(session_id)

        logger.info(f"ByteCore Agent initialized with {memory_backend} backend")

    async def execute_task(self, skill: str, action: str, **params) -> Any:
        """Execute a task using specified skill and action."""
        task = Task(
            id=str(uuid.uuid4()),
            name=f"{skill}.{action}",
            skill=skill,
            parameters={"action": action, **params},
        )

        return await self.runner.execute_task(task)

    def list_skills(self) -> List[Dict[str, Any]]:
        """List all available skills."""
        return self.skills.list_skills()

    def get_skill_info(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a skill."""
        for skill in self.list_skills():
            if skill["name"] == skill_name:
                return skill
        return None


# Global agent instance
agent: Optional[ByteCoreAgent] = None


def get_agent() -> ByteCoreAgent:
    """Get or create agent instance."""
    global agent
    if agent is None:
        agent = ByteCoreAgent()
    return agent


@app.command()
def list_skills():
    """List all available skills and their capabilities."""
    agent = get_agent()
    skills = agent.list_skills()

    if not skills:
        console.print("[yellow]No skills found[/yellow]")
        return

    table = Table(title="Available Skills", show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Description", style="white")
    table.add_column("Author", style="blue")

    for skill in skills:
        table.add_row(
            skill["name"], skill["version"], skill["description"], skill["author"]
        )

    console.print(table)


@app.command()
def skill_info(skill_name: str):
    """Show detailed information about a specific skill."""
    agent = get_agent()
    skill = agent.get_skill_info(skill_name)

    if not skill:
        console.print(f"[red]Skill '{skill_name}' not found[/red]")
        return

    # Create info panel
    info = f"""
[bold cyan]{skill['name']}[/bold cyan] v{skill['version']}
[italic]{skill['description']}[/italic]

Author: {skill['author']}
"""

    console.print(Panel(info, title="Skill Information", border_style="green"))

    # Show parameters
    if skill.get("parameters"):
        param_table = Table(title="Parameters", show_header=True)
        param_table.add_column("Name", style="cyan")
        param_table.add_column("Type", style="yellow")
        param_table.add_column("Required", style="red")
        param_table.add_column("Default", style="green")

        for name, info in skill["parameters"].items():
            param_table.add_row(
                name,
                info["type"],
                "Yes" if info["required"] else "No",
                str(info.get("default", "None")),
            )

        console.print(param_table)


@app.command()
def run(
    task: str = typer.Argument(..., help="Task description or command"),
    skill: Optional[str] = typer.Option(
        None, "--skill", "-s", help="Specific skill to use"
    ),
    params: Optional[str] = typer.Option(
        None, "--params", "-p", help="JSON parameters"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output format: json, text"
    ),
):
    """Execute a task using natural language or specific skill."""
    agent = get_agent()

    # Parse parameters if provided
    task_params = {}
    if params:
        try:
            task_params = json.loads(params)
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON parameters[/red]")
            return

    # Determine skill and action from task
    if skill:
        # Direct skill invocation
        if ":" in task:
            action = task.split(":", 1)[1]
        else:
            action = task

        asyncio.run(_execute_skill_task(agent, skill, action, task_params, output))
    else:
        # Natural language task processing
        console.print(
            "[yellow]Natural language task processing not yet implemented[/yellow]"
        )
        console.print("Please specify a skill with --skill option")


async def _execute_skill_task(
    agent: ByteCoreAgent,
    skill: str,
    action: str,
    params: Dict[str, Any],
    output_format: Optional[str],
):
    """Execute a skill-based task."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task_id = progress.add_task(f"Executing {skill}.{action}...", total=None)

        try:
            result = await agent.execute_task(skill, action, **params)
            progress.update(task_id, completed=True)

            # Format output
            if output_format == "json":
                console.print_json(json.dumps(result, indent=2, default=str))
            else:
                _print_result(result)

        except Exception as e:
            progress.update(task_id, completed=True)
            console.print(f"[red]Task failed: {e}[/red]")
            logger.exception("Task execution failed")


def _print_result(result: Any):
    """Pretty print task result."""
    if isinstance(result, dict):
        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
        elif "success" in result and result["success"]:
            console.print("[green]Task completed successfully![/green]")
            if "stdout" in result:
                console.print("\nOutput:")
                console.print(Syntax(result["stdout"], "text"))
        else:
            # Generic dict output
            for key, value in result.items():
                if isinstance(value, (list, dict)):
                    console.print(f"\n[bold]{key}:[/bold]")
                    console.print_json(json.dumps(value, indent=2, default=str))
                else:
                    console.print(f"[bold]{key}:[/bold] {value}")
    else:
        console.print(str(result))


@app.command(name="github-close-issues")
def github_close_issues(
    repo: str = typer.Argument(..., help="Repository in format owner/name"),
    labels: Optional[List[str]] = typer.Option(
        None, "--label", "-l", help="Filter by labels"
    ),
    token: Optional[str] = typer.Option(None, "--token", "-t", help="GitHub token"),
):
    """Close GitHub issues based on criteria."""
    agent = get_agent()

    params = {"repo": repo}
    if labels:
        params["labels"] = labels
    if token:
        params["token"] = token

    asyncio.run(
        _execute_skill_task(agent, "github_agent", "close_issues", params, "text")
    )


@app.command(name="shell")
def shell_command(
    command: str = typer.Argument(..., help="Shell command to execute"),
    timeout: int = typer.Option(
        30, "--timeout", "-t", help="Command timeout in seconds"
    ),
    cwd: Optional[str] = typer.Option(None, "--cwd", "-c", help="Working directory"),
):
    """Execute a shell command safely."""
    agent = get_agent()

    params = {"command": command, "timeout": timeout}
    if cwd:
        params["cwd"] = cwd

    asyncio.run(_execute_skill_task(agent, "local_shell", "run", params, "text"))


@app.command()
def system_info():
    """Display system information."""
    agent = get_agent()
    asyncio.run(_execute_skill_task(agent, "local_shell", "system_info", {}, "text"))


@app.command()
def processes(
    top: int = typer.Option(20, "--top", "-t", help="Number of top processes to show")
):
    """List running processes."""
    agent = get_agent()
    asyncio.run(
        _execute_skill_task(
            agent, "local_shell", "list_processes", {"top": top}, "text"
        )
    )


@app.command()
def interactive():
    """Start interactive mode for continuous task execution."""
    console.print(
        Panel(
            "[bold cyan]ByteCore Interactive Mode[/bold cyan]\n"
            "Type 'help' for commands, 'exit' to quit",
            border_style="cyan",
        )
    )

    agent = get_agent()

    while True:
        try:
            command = console.input("\n[bold green]bytecore>[/bold green] ")

            if command.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Goodbye![/yellow]")
                break
            elif command.lower() == "help":
                _show_interactive_help()
            elif command.lower() == "skills":
                list_skills()
            elif command.startswith("skill "):
                parts = command.split(" ", 2)
                if len(parts) >= 3:
                    skill_name = parts[1]
                    action = parts[2]
                    asyncio.run(
                        _execute_skill_task(agent, skill_name, action, {}, "text")
                    )
                else:
                    console.print("[red]Usage: skill <name> <action>[/red]")
            else:
                console.print(
                    "[yellow]Unknown command. Type 'help' for available commands.[/yellow]"
                )

        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' to quit[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


def _show_interactive_help():
    """Show help for interactive mode."""
    help_text = """
[bold]Available Commands:[/bold]

  help              Show this help message
  skills            List available skills
  skill <name> <action>  Execute a skill action
  exit/quit/q       Exit interactive mode

[bold]Examples:[/bold]

  skill github_agent analyze --repo owner/name
  skill local_shell system_info
  skill local_shell run "ls -la"
"""
    console.print(Panel(help_text, title="Interactive Mode Help", border_style="blue"))


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
    memory: str = typer.Option(
        "yaml", "--memory", "-m", help="Memory backend: yaml, json"
    ),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging"),
    task: Optional[str] = typer.Option(
        None,
        "--task",
        help="Execute a task in the format skill:action",
    ),
    params: Optional[str] = typer.Option(
        None,
        "--params",
        help="JSON string of parameters for --task",
    ),
):
    """ByteCore Agent CLI - Your intelligent automation assistant."""
    if version:
        console.print("[bold cyan]ByteCore Agent[/bold cyan] v0.1.0")
        raise typer.Exit(0)

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize agent with specified backend
    global agent
    agent = ByteCoreAgent(memory_backend=memory)

    if task:
        if ":" not in task:
            console.print("[red]Task must be in format skill:action[/red]")
            raise typer.Exit(1)

        skill, action = task.split(":", 1)
        task_params = {}
        if params:
            try:
                task_params = json.loads(params)
            except json.JSONDecodeError:
                console.print("[red]Invalid JSON for --params[/red]")
                raise typer.Exit(1)

        asyncio.run(_execute_skill_task(agent, skill, action, task_params, None))
        raise typer.Exit()


if __name__ == "__main__":
    app()
