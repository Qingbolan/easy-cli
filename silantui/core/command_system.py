"""
Enhanced Command System - Convenient command registration and management system
"""

from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


@dataclass
class CommandInfo:
    """Command information"""
    name: str
    handler: Callable
    description: str
    usage: str = ""
    aliases: List[str] = None
    category: str = "General"
    requires_args: bool = False
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []


class CommandRegistry:
    """
    Command Registry - Convenient command management system

    Example:
        >>> registry = CommandRegistry()
        >>>
        >>> @registry.command("greet", description="Say hello")
        >>> def greet_command(app, args: str):
        >>>     app.logger.info(f"Hello {args}!")
        >>>
        >>> registry.execute("greet", app, "World")
    """
    
    def __init__(self):
        self.commands: Dict[str, CommandInfo] = {}
        self.categories: Dict[str, List[str]] = {}
        
    def command(
        self,
        name: str,
        description: str = "",
        usage: str = "",
        aliases: List[str] = None,
        category: str = "General",
        requires_args: bool = False
    ):
        """
        Decorator: register command

        Example:
            >>> @registry.command("hello", description="Say hello")
            >>> def hello_cmd(app, args):
            >>>     print("Hello!")
        """
        def decorator(func: Callable):
            cmd_info = CommandInfo(
                name=name,
                handler=func,
                description=description,
                usage=usage or f"/{name} [args]",
                aliases=aliases or [],
                category=category,
                requires_args=requires_args
            )
            self.register(cmd_info)
            return func
        return decorator
    
    def register(self, cmd_info: CommandInfo) -> None:
        """Register command"""
        # Register main command
        self.commands[cmd_info.name] = cmd_info

        # Register aliases
        for alias in cmd_info.aliases:
            self.commands[alias] = cmd_info

        # Category management
        if cmd_info.category not in self.categories:
            self.categories[cmd_info.category] = []
        if cmd_info.name not in self.categories[cmd_info.category]:
            self.categories[cmd_info.category].append(cmd_info.name)

    def unregister(self, name: str) -> bool:
        """Unregister command"""
        if name in self.commands:
            cmd_info = self.commands[name]
            # Delete main command and all aliases
            del self.commands[name]
            for alias in cmd_info.aliases:
                if alias in self.commands:
                    del self.commands[alias]
            # Remove from category
            if cmd_info.category in self.categories:
                if cmd_info.name in self.categories[cmd_info.category]:
                    self.categories[cmd_info.category].remove(cmd_info.name)
            return True
        return False

    def get(self, name: str) -> Optional[CommandInfo]:
        """Get command information"""
        return self.commands.get(name)

    def exists(self, name: str) -> bool:
        """Check if command exists"""
        return name in self.commands

    def execute(self, name: str, app: Any, args: str = "") -> Any:
        """Execute command"""
        cmd_info = self.get(name)
        if not cmd_info:
            raise ValueError(f"Unknown command: {name}")
        
        if cmd_info.requires_args and not args:
            raise ValueError(f"Command '{name}' requires arguments")
        
        return cmd_info.handler(app, args)
    
    def list_commands(self, category: Optional[str] = None) -> List[CommandInfo]:
        """List all commands"""
        if category:
            cmd_names = self.categories.get(category, [])
            return [self.commands[name] for name in cmd_names]

        # Return all main commands (excluding aliases)
        seen = set()
        result = []
        for cmd_info in self.commands.values():
            if cmd_info.name not in seen:
                seen.add(cmd_info.name)
                result.append(cmd_info)
        return result

    def list_categories(self) -> List[str]:
        """List all categories"""
        return list(self.categories.keys())

    def show_help(
        self,
        console: Console,
        command_name: Optional[str] = None,
        table_factory: Optional[Callable[[str], Table]] = None,
    ):
        """Display help information"""
        if command_name:
            # Show help for single command
            cmd_info = self.get(command_name)
            if not cmd_info:
                console.print(f"[red]Unknown command: {command_name}[/red]")
                return

            panel = Panel(
                f"[bold]{cmd_info.description}[/bold]\n\n"
                f"Usage: [cyan]{cmd_info.usage}[/cyan]\n"
                f"Aliases: [yellow]{', '.join(cmd_info.aliases) if cmd_info.aliases else 'None'}[/yellow]\n"
                f"Category: [green]{cmd_info.category}[/green]",
                title=f"Command: /{cmd_info.name}",
                border_style="cyan"
            )
            console.print(panel)
        else:
            # Show all commands
            for category in sorted(self.list_categories()):
                title = f"📚 {category} Commands"
                if table_factory:
                    table = table_factory(title)
                else:
                    table = Table(
                        title=title,
                        show_header=True,
                        header_style="bold cyan"
                    )
                table.add_column("Command", style="bold yellow", width=20)
                table.add_column("Description", style="white")
                table.add_column("Aliases", style="dim", width=15)

                for cmd_info in self.list_commands(category):
                    aliases = ", ".join(cmd_info.aliases) if cmd_info.aliases else "-"
                    table.add_row(
                        f"/{cmd_info.name}",
                        cmd_info.description,
                        aliases
                    )

                console.print()
                console.print(table)

    def show_command_list(self, console: Console):
        """Show a compact command list (autocomplete style when typing /)"""
        all_commands = self.list_commands()

        # Sort commands by name
        all_commands.sort(key=lambda x: x.name)

        # Calculate max command length for alignment
        max_cmd_len = max(len(cmd.name) for cmd in all_commands)

        console.print()
        for cmd in all_commands:
            # Format: /command (aliases)  Description
            cmd_name = f"/{cmd.name}"

            # Add aliases if any
            aliases_str = ""
            if cmd.aliases:
                aliases_str = f" ({', '.join(cmd.aliases)})"

            # Pad for alignment
            padding = " " * (max_cmd_len - len(cmd.name) + 2)

            # Print command line
            console.print(
                f"[cyan]{cmd_name}[/cyan][dim]{aliases_str}[/dim]{padding}{cmd.description}"
            )


# Create global registry
default_registry = CommandRegistry()


def register_builtin_commands(registry: CommandRegistry, app: Any):
    """Register built-in commands"""

    @registry.command(
        "help",
        description="Display help information",
        usage="/help [command]",
        aliases=["h", "?"],
        category="System"
    )
    def cmd_help(app, args: str):
        table_factory = lambda title: app.logger.table(title=title)
        if args:
            registry.show_help(app.logger.console, args, table_factory=table_factory)
        else:
            registry.show_help(app.logger.console, table_factory=table_factory)

    @registry.command(
        "exit",
        description="Exit program",
        aliases=["quit", "q"],
        category="System"
    )
    def cmd_exit(app, args: str):
        if app.ui.confirm("Are you sure you want to exit?"):
            app.logger.console.print("\n[bold green]👋 Goodbye![/bold green]\n")
            app.running = False

    @registry.command(
        "bye",
        description="Exit program (shortcut)",
        category="System"
    )
    def cmd_bye(app, args: str):
        app.logger.console.print("\n[bold green]👋 Goodbye![/bold green]\n")
        app.running = False

    @registry.command(
        "clear",
        description="Clear current session",
        aliases=["cls", "reset"],
        category="Session"
    )
    def cmd_clear(app, args: str):
        if app.ui.confirm("Clear current session?"):
            from .session import ChatSession
            app.current_session = ChatSession()
            app.logger.console.clear()
            app.ui.show_success("Session cleared")

    @registry.command(
        "new",
        description="Create new session",
        aliases=["n"],
        category="Session"
    )
    def cmd_new(app, args: str):
        from .session import ChatSession
        app.current_session = ChatSession()
        app.logger.console.clear()
        app.ui.show_success(f"New session: {app.current_session.session_id}")

    @registry.command(
        "save",
        description="Save current session",
        aliases=["s"],
        category="Session"
    )
    def cmd_save(app, args: str):
        path = app.session_manager.save(app.current_session)
        app.ui.show_success(f"Saved: {path}")

    @registry.command(
        "load",
        description="Load session",
        usage="/load <session_id>",
        aliases=["l"],
        category="Session",
        requires_args=True
    )
    def cmd_load(app, args: str):
        session = app.session_manager.load(args)
        if session:
            app.current_session = session
            app.logger.console.clear()
            app.ui.show_success(f"Loaded: {args}")
        else:
            app.ui.show_error(f"Session not found: {args}")

    @registry.command(
        "list",
        description="List all sessions",
        aliases=["ls"],
        category="Session"
    )
    def cmd_list(app, args: str):
        sessions = app.session_manager.list_sessions(limit=20)
        app.ui.show_sessions(sessions)

    @registry.command(
        "export",
        description="Export as Markdown",
        aliases=["exp"],
        category="Session"
    )
    def cmd_export(app, args: str):
        path = app.session_manager.export_markdown(app.current_session.session_id)
        if path:
            app.logger.file_saved(str(path), "Markdown export")
        else:
            app.ui.show_error("Export failed")

    @registry.command(
        "model",
        description="Switch AI model",
        usage="/model [model_name]",
        aliases=["m"],
        category="Settings"
    )
    def cmd_model(app, args: str):
        if not args:
            app.ui.show_info("Current model", app.client.model)
        else:
            app.client.model = args
            app.ui.show_success(f"Model switched: {args}")

    @registry.command(
        "system",
        description="Set system prompt",
        usage="/system [prompt]",
        aliases=["sys"],
        category="Settings"
    )
    def cmd_system(app, args: str):
        if not args:
            if app.system_prompt:
                app.ui.show_info("Current system prompt", app.system_prompt)
            else:
                app.ui.show_info("System prompt", "Not set")
        else:
            app.system_prompt = args
            app.ui.show_success("System prompt updated")

    @registry.command(
        "alias",
        description="Manage command aliases",
        usage="/alias [list|add|remove]",
        category="Settings"
    )
    def cmd_alias(app, args: str):
        app.show_alias_menu()

    @registry.command(
        "commands",
        description="List all available commands",
        aliases=["cmd", "cmds"],
        category="System"
    )
    def cmd_commands(app, args: str):
        table_factory = lambda title: app.logger.table(title=title)
        registry.show_help(app.logger.console, table_factory=table_factory)


class CommandBuilder:
    """
    Command Builder - Convenient command creation tool

    Example:
        >>> builder = CommandBuilder("greet")
        >>> builder.description("Say hello")
        >>> builder.usage("/greet <name>")
        >>> builder.aliases(["hi", "hello"])
        >>> builder.category("Social")
        >>> builder.handler(lambda app, args: print(f"Hello {args}!"))
        >>> cmd = builder.build()
    """
    
    def __init__(self, name: str):
        self._name = name
        self._description = ""
        self._usage = ""
        self._aliases = []
        self._category = "General"
        self._requires_args = False
        self._handler = None
    
    def description(self, desc: str) -> 'CommandBuilder':
        """Set description"""
        self._description = desc
        return self

    def usage(self, usage: str) -> 'CommandBuilder':
        """Set usage instructions"""
        self._usage = usage
        return self

    def aliases(self, aliases: List[str]) -> 'CommandBuilder':
        """Set aliases"""
        self._aliases = aliases
        return self

    def category(self, category: str) -> 'CommandBuilder':
        """Set category"""
        self._category = category
        return self

    def requires_args(self, required: bool = True) -> 'CommandBuilder':
        """Set whether arguments are required"""
        self._requires_args = required
        return self

    def handler(self, func: Callable) -> 'CommandBuilder':
        """Set handler function"""
        self._handler = func
        return self

    def build(self) -> CommandInfo:
        """Build command"""
        if not self._handler:
            raise ValueError("Command handler is required")
        
        return CommandInfo(
            name=self._name,
            handler=self._handler,
            description=self._description,
            usage=self._usage or f"/{self._name}",
            aliases=self._aliases,
            category=self._category,
            requires_args=self._requires_args
        )


# Convenient command registration function
def quick_command(
    registry: CommandRegistry,
    name: str,
    handler: Callable,
    description: str = "",
    **kwargs
):
    """
    Quick command registration

    Example:
        >>> quick_command(
        >>>     registry,
        >>>     "greet",
        >>>     lambda app, args: print(f"Hello {args}!"),
        >>>     description="Say hello",
        >>>     aliases=["hi"]
        >>> )
    """
    cmd_info = CommandInfo(
        name=name,
        handler=handler,
        description=description,
        usage=kwargs.get("usage", f"/{name}"),
        aliases=kwargs.get("aliases", []),
        category=kwargs.get("category", "Custom"),
        requires_args=kwargs.get("requires_args", False)
    )
    registry.register(cmd_info)
    return cmd_info
