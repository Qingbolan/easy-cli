"""
Command Manager - Manage custom command aliases
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import sys


class CommandManager:
    """
    Command manager that supports creating independent executable commands.

    Example:
        >>> cm = CommandManager()
        >>> cm.add_command("chat", model="claude-sonnet-4-20250514")
        >>> cm.add_command("code", system="You are a coding assistant")
        >>> cm.create_executables()
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or (Path.home() / ".silantui")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.commands_file = self.config_dir / "commands.json"
        self.commands: Dict[str, Dict] = {}
        self.load_commands()
    
    def load_commands(self) -> None:
        """Load command configurations from config file."""
        if self.commands_file.exists():
            try:
                with open(self.commands_file, 'r', encoding='utf-8') as f:
                    self.commands = json.load(f)
            except Exception:
                self.commands = {}
        else:
            # Default commands
            self.commands = {
                "chat": {
                    "description": "Quick chat with LLM",
                },
                "ai": {
                    "description": "AI assistant",
                },
            }
    
    def save_commands(self) -> None:
        """Save command configurations to file."""
        with open(self.commands_file, 'w', encoding='utf-8') as f:
            json.dump(self.commands, f, indent=2, ensure_ascii=False)
    
    def add_command(
        self,
        name: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        log_level: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Add a custom command.

        Args:
            name: Command name (e.g. "chat", "code")
            model: Optional model name
            system: Optional system prompt
            log_level: Optional log level
            description: Command description
        """
        config = {}
        if model:
            config["model"] = model
        if system:
            config["system"] = system
        if log_level:
            config["log_level"] = log_level
        if description:
            config["description"] = description
        
        self.commands[name] = config
        self.save_commands()
    
    def remove_command(self, name: str) -> bool:
        """
        Remove command configuration.

        Args:
            name: Name of the command to remove

        Returns:
            Whether deletion was successful
        """
        if name in self.commands:
            del self.commands[name]
            self.save_commands()
            return True
        return False
    
    def get_command(self, name: str) -> Optional[Dict]:
        """
        Get command configuration.

        Args:
            name: Command name

        Returns:
            Command configuration dictionary, or None if not found
        """
        return self.commands.get(name)
    
    def list_commands(self) -> Dict[str, Dict]:
        """Return all command configurations."""
        return self.commands.copy()
    
    def create_executables(self) -> List[Path]:
        """
        Create executable commands in system PATH.

        Returns:
            List of created executable file paths
        """
        # Use user's bin directory
        bin_dir = Path.home() / ".local" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        
        for cmd_name, config in self.commands.items():
            # Skip silantui itself
            if cmd_name == "silantui":
                continue

            script_path = bin_dir / cmd_name

            # Build Python startup script
            model = config.get("model", "")
            system = config.get("system", "")
            log_level = config.get("log_level", "")
            
            # Create Python script
            script_content = f'''#!/usr/bin/env python3
"""
{cmd_name} - Custom SilanTui command
{config.get("description", "")}
"""

import sys
import os

# Configuration
CONFIG = {{
    "model": {repr(model)},
    "system": {repr(system)},
    "log_level": {repr(log_level)},
}}

def main():
    from silantui.cli import ChatApplication

    # Get API key
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        print("Error: API key required. Set LLM_API_KEY environment variable")
        print("\nVisit the project homepage for setup guidance: https://github.com/Qingbolan/silan-tui")
        sys.exit(1)

    # Create app instance with configuration
    app = ChatApplication(
        api_key=api_key,
        model=CONFIG["model"] or "claude-sonnet-4-20250514",
        log_level=CONFIG["log_level"] or "info",
    )

    # Set system prompt
    if CONFIG["system"]:
        app.system_prompt = CONFIG["system"]

    # Run application
    try:
        app.run()
    except Exception as e:
        print(f"Fatal error: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)

            # Set executable permissions
            script_path.chmod(0o755)
            created_files.append(script_path)
        
        return created_files
    
    def remove_executables(self) -> List[Path]:
        """
        Remove created executable files.

        Returns:
            List of removed file paths
        """
        bin_dir = Path.home() / ".local" / "bin"
        removed_files = []
        
        for cmd_name in self.commands.keys():
            if cmd_name == "silantui":
                continue
            
            script_path = bin_dir / cmd_name
            if script_path.exists():
                script_path.unlink()
                removed_files.append(script_path)
        
        return removed_files


def setup_commands_interactive():
    """Interactive setup for custom commands."""
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich.panel import Panel
    
    console = Console()
    cm = CommandManager()

    console.print("\n[bold cyan]🚀 SilanTui Custom Command Setup[/bold cyan]\n")

    # Display current commands
    if cm.commands:
        table = Table(title="Current Custom Commands", show_header=True)
        table.add_column("Command", style="yellow", width=15)
        table.add_column("Model", style="green", width=25)
        table.add_column("System Prompt", style="cyan")
        table.add_column("Description", style="white")
        
        for name, config in cm.commands.items():
            model = config.get("model", "Default")
            system = config.get("system", "-")
            if len(system) > 30:
                system = system[:27] + "..."
            desc = config.get("description", "-")
            table.add_row(name, model, system, desc)
        
        console.print(table)
        console.print()
    
    # Main menu
    while True:
        console.print("[bold]Choose an operation:[/bold]")
        console.print("1. Add/Modify command")
        console.print("2. Delete command")
        console.print("3. Create executables")
        console.print("4. Remove executables")
        console.print("5. View examples")
        console.print("6. Exit")

        choice = Prompt.ask("\nChoice", choices=["1", "2", "3", "4", "5", "6"], default="6")
        
        if choice == "1":
            # Add command
            console.print("\n[bold cyan]Add Custom Command[/bold cyan]")
            name = Prompt.ask("[yellow]Command name[/yellow]", default="mychat")

            model = Prompt.ask(
                "[green]Model (leave empty for default)[/green]",
                default=""
            )

            system = Prompt.ask(
                "[cyan]System prompt (leave empty for none)[/cyan]",
                default=""
            )

            log_level = Prompt.ask(
                "[magenta]Log level (leave empty for default)[/magenta]",
                default=""
            )

            description = Prompt.ask(
                "[white]Description (optional)[/white]",
                default=""
            )
            
            cm.add_command(
                name=name,
                model=model or None,
                system=system or None,
                log_level=log_level or None,
                description=description or None,
            )
            console.print(f"\n[green]✅ Command added: {name}[/green]\n")

        elif choice == "2":
            # Delete command
            if not cm.commands:
                console.print("\n[yellow]⚠️  No commands to delete[/yellow]\n")
                continue

            name = Prompt.ask("\n[yellow]Command name to delete[/yellow]")
            if cm.remove_command(name):
                console.print(f"\n[green]✅ Command deleted: {name}[/green]\n")
            else:
                console.print(f"\n[red]❌ Command not found: {name}[/red]\n")

        elif choice == "3":
            # Create executables
            try:
                created = cm.create_executables()
                console.print(f"\n[green]✅ Created {len(created)} executable commands[/green]")
                console.print("[dim]Location: ~/.local/bin/[/dim]\n")

                for path in created:
                    console.print(f"  • {path.name}")

                console.print("\n[bold cyan]Usage:[/bold cyan]")
                console.print("[dim]1. Ensure ~/.local/bin is in PATH:[/dim]")
                console.print('[yellow]   export PATH="$HOME/.local/bin:$PATH"[/yellow]')
                console.print("[dim]2. Then use the command directly:[/dim]")
                for path in created:
                    console.print(f"[green]   {path.name}[/green]")
                console.print()
            except Exception as e:
                console.print(f"\n[red]❌ Creation failed: {e}[/red]\n")

        elif choice == "4":
            # Remove executables
            try:
                removed = cm.remove_executables()
                if removed:
                    console.print(f"\n[green]✅ Removed {len(removed)} executable files[/green]\n")
                    for path in removed:
                        console.print(f"  • {path}")
                    console.print()
                else:
                    console.print("\n[yellow]⚠️  No executable files found[/yellow]\n")
            except Exception as e:
                console.print(f"\n[red]❌ Removal failed: {e}[/red]\n")

        elif choice == "5":
            # Display examples
            console.print("\n[bold cyan]📝 Command Configuration Examples[/bold cyan]\n")
            
            examples = [
                {
                    "name": "chat",
                    "desc": "Quick chat",
                    "config": {"description": "Quick chat"}
                },
                {
                    "name": "sonnet",
                    "desc": "Use Sonnet model",
                    "config": {
                        "model": "claude-sonnet-4-20250514",
                        "description": "LLM Sonnet model"
                    }
                },
                {
                    "name": "opus",
                    "desc": "Use Opus model",
                    "config": {
                        "model": "claude-opus-4-20250514",
                        "description": "LLM Opus model"
                    }
                },
                {
                    "name": "code",
                    "desc": "Coding assistant",
                    "config": {
                        "system": "You are an expert coding assistant",
                        "description": "Coding assistant"
                    }
                },
                {
                    "name": "writer",
                    "desc": "Writing assistant",
                    "config": {
                        "system": "You are a creative writing assistant",
                        "description": "Writing assistant"
                    }
                },
            ]

            for ex in examples:
                panel = Panel(
                    f"[yellow]Command:[/yellow] {ex['name']}\n"
                    f"[cyan]Description:[/cyan] {ex['desc']}\n"
                    f"[green]Config:[/green] {json.dumps(ex['config'], indent=2, ensure_ascii=False)}",
                    title=f"[bold]{ex['name']}[/bold]",
                    border_style="blue"
                )
                console.print(panel)
            console.print()

        elif choice == "6":
            console.print("\n[green]👋 Goodbye![/green]\n")
            break


if __name__ == "__main__":
    setup_commands_interactive()
