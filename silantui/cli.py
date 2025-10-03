#!/usr/bin/env python3
"""
SilanTui - Main CLI application with enhanced UI and Markdown support.
"""

import sys
import os
from typing import Optional
from pathlib import Path
from types import SimpleNamespace
import time

from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.text import Text
from pyfiglet import Figlet

from .logging.modern import ModernLogger
from .core.session import ChatSession, SessionManager
from .ui.chat_ui import ChatUI
from .core.command_manager import CommandManager
from .core.command_system import CommandRegistry, register_builtin_commands
from .ui.builder import UIBuilder, QuickUI
from .ui.chat_display import LiveChatDisplay
from .integrations.AIClient import AIClient

class ChatApplication:
    """Main chat application with enhanced UI."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        log_level: str = "info",
        use_live_display: bool = True,
        input_mode: str = None,
        input_label: str = None,
        input_tips: str = None,
        footer_offset: int = None,
        input_reserved_lines: int = None,
        locked: bool = None,
    ):
        self.logger = ModernLogger(
            name="silantui",
            level=log_level,
            log_file=str(Path.home() / ".silantui" / "app.log")
        )
        
        self.client = AIClient(
            api_key=api_key,
            model=model,
            logger=self.logger
        )
        
        self.session_manager = SessionManager(
            base_dir=Path.home() / ".silantui" / "sessions"
        )
        self.current_session = ChatSession()
        self.ui = ChatUI(logger=self.logger)
        self.command_manager = CommandManager()
        
        # Enhanced UI components
        self.command_registry = CommandRegistry()
        self.ui_builder = UIBuilder(console=self.logger.console)
        self.quick_ui = QuickUI(console=self.logger.console)

        # Live chat display
        self.use_live_display = use_live_display
        self.locked = bool(locked if locked is not None else os.getenv("EASYCLI_LOCKED"))
        # Input UI defaults - use multiline mode for best IME support
        self.input_mode = input_mode or os.getenv("EASYCLI_INPUT_MODE", "multiline")
        self.input_label = input_label or os.getenv("EASYCLI_INPUT_LABEL", "chat")
        self.input_tips = input_tips or os.getenv("EASYCLI_INPUT_TIPS", "Type / for commands")
        self.footer_offset = int(footer_offset or int(os.getenv("EASYCLI_FOOTER_OFFSET", "2")))
        self.input_reserved_lines = int(input_reserved_lines or int(os.getenv("EASYCLI_INPUT_RESERVE", "2")))
        if use_live_display:
            self.chat_display = LiveChatDisplay(
                console=self.logger.console,
                mode=self.input_label,
                left_label=self.input_label,
                tips=self.input_tips,
                footer_offset=self.footer_offset,
                input_reserved_lines=self.input_reserved_lines,
            )
        
        # Register built-in commands
        register_builtin_commands(self.command_registry, self)
        
        self.system_prompt: Optional[str] = None
        self.running = True
    
    def run(self) -> None:
        """Main application loop with enhanced UI."""
        try:
            # Show welcome message
            self.logger.console.clear()
            self.ui.show_welcome("SilanTui")
            
            self.logger.info("Application started")
            self.logger.info(f"Model: {self.client.model}")
            
            # Prompt user about display mode
            if self.use_live_display:
                self.logger.console.print(
                    "\n[cyan]Using live display mode - Fixed bottom input box, full Markdown support[/cyan]"
                )
                self.logger.console.print(
                    "[dim]Tip: Type /help to see all commands[/dim]\n"
                )
                time.sleep(1)

                # Start live display
                self.logger.console.clear()
                self.run_with_live_display()
            else:
                self.run_traditional()
                
        finally:
            self.cleanup()
    
    def run_with_live_display(self) -> None:
        """Run with live display mode with IME-friendly footer input"""
        # Use main screen (no alt screen) for best IME compatibility
        self.chat_display.start()

        try:
            while self.running:
                try:
                    # Use footer mode for best IME support (Chinese, Japanese, Korean)
                    user_input = self.chat_display.read_input(mode=self.input_mode)

                    if not user_input:
                        continue

                    # Show command list if user just types /
                    if user_input == "/":
                        with self.chat_display.pause():
                            self.command_registry.show_command_list(self.logger.console)
                            input("\n[dim]Press Enter to continue...[/dim]")
                        continue

                    # Handle commands
                    if user_input.startswith('/'):
                        self.handle_command(user_input)
                        continue

                    # Add user message to display
                    self.chat_display.add_user_message(user_input)

                    # Add to session
                    self.current_session.add_message("user", user_input)

                    # Start AI response
                    self.chat_display.start_assistant_message()

                    # Stream response
                    full_response = ""
                    for chunk in self.client.chat_stream(
                        message=user_input,
                        system=self.system_prompt,
                        conversation_history=self.current_session.get_messages()[:-1]
                    ):
                        full_response += chunk
                        self.chat_display.append_streaming(chunk)
                        time.sleep(0.01)  # Control refresh rate

                    # Finish response
                    self.chat_display.finish_assistant_message()

                    # Add to session
                    self.current_session.add_message("assistant", full_response)

                    # Auto-save
                    self.session_manager.save(self.current_session)
                    
                except KeyboardInterrupt:
                    self.chat_display.stop()
                    self.logger.console.print(
                        "\n\n[yellow]⚠️  Use /exit to quit the program[/yellow]\n"
                    )
                    time.sleep(1)
                    self.chat_display.start()
                    continue
                
                except Exception as e:
                    self.chat_display.show_error(str(e))
                    self.logger.error(f"Error: {e}")
                    time.sleep(2)
                    continue
        
        finally:
            self.chat_display.stop()
    
    def run_traditional(self) -> None:
        """Traditional display mode"""
        self.logger.print()
        
        while self.running:
            try:
                # Get user input with command highlighting
                user_input = Prompt.ask(
                    "\n[bold yellow]> You[/bold yellow] [dim](type [cyan]/[/cyan] to see commands)[/dim]"
                ).strip()

                if not user_input:
                    continue

                # Show command list if user just types /
                if user_input == "/":
                    self.command_registry.show_command_list(self.logger.console)
                    input("\n[dim]Press Enter to continue...[/dim]")
                    continue

                # Handle commands
                if user_input.startswith('/'):
                    self.handle_command(user_input)
                    continue

                # Add user message
                self.current_session.add_message("user", user_input)

                # Display user message
                self.logger.console.print()
                self.logger.console.print(
                    f"[bold blue]👤 You:[/bold blue] {user_input}"
                )
                self.logger.console.print()

                # Get AI response (streaming, with Markdown rendering)
                self.logger.console.print("[bold green]🤖 LLM:[/bold green]")

                response = self.client.chat_stream_with_logger(
                    message=user_input,
                    system=self.system_prompt,
                    conversation_history=self.current_session.get_messages()[:-1],
                    stream_title=None,  # Don't show title
                    render_markdown=True  # Enable Markdown rendering
                )

                # Add response to session
                self.current_session.add_message("assistant", response)

                # Auto-save
                self.session_manager.save(self.current_session)
                
                self.logger.print()
                
            except KeyboardInterrupt:
                self.logger.console.print(
                    "\n\n[yellow]⚠️  Use /exit to quit the program[/yellow]\n"
                )
                continue
            
            except Exception as e:
                self.logger.error(f"Error: {e}")
                self.ui.show_error(str(e))
                continue
    
    def handle_command(self, command: str) -> None:
        """Handle slash commands using the command registry."""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lstrip('/').lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Special handling: some commands need to stop display in live mode
        if self.use_live_display and hasattr(self, 'chat_display'):
            if cmd in ['help', 'list', 'alias']:
                self.chat_display.stop()

        # Use command registration system
        if self.command_registry.exists(cmd):
            try:
                self.command_registry.execute(cmd, self, args)
            except ValueError as e:
                if self.use_live_display:
                    self.chat_display.show_error(str(e))
                else:
                    self.ui.show_error(str(e))
            except Exception as e:
                self.logger.error(f"Command execution failed: {e}")
                if self.use_live_display:
                    self.chat_display.show_error(f"Error executing command: {e}")
                else:
                    self.ui.show_error(f"Error executing command: {e}")
        else:
            if self.use_live_display:
                self.chat_display.show_error(f"Unknown command: /{cmd}")
            else:
                self.ui.show_error(f"Unknown command: /{cmd}")
            self.logger.console.print("[dim]Type /help to see all available commands[/dim]\n")

        # Restart display
        if self.use_live_display and hasattr(self, 'chat_display'):
            if cmd in ['help', 'list', 'alias']:
                input("\nPress Enter to continue...")
                self.chat_display.start()
    
    def show_alias_menu(self) -> None:
        """Show alias management menu"""
        from rich.table import Table

        aliases = self.command_manager.list_aliases()

        if aliases:
            table = Table(
                title="🔧 Command Aliases",
                show_header=True,
                header_style="bold cyan"
            )
            table.add_column("Alias", style="yellow", width=15)
            table.add_column("Command", style="green")
            
            for alias, command in aliases.items():
                table.add_row(alias, command)
            
            self.logger.console.print()
            self.logger.console.print(table)
            self.logger.console.print()
        else:
            self.logger.console.print("\n[yellow]No aliases configured[/yellow]\n")

        self.logger.console.print("[bold]Alias Management:[/bold]")
        self.logger.console.print("  • Add alias: silantui --add-alias <name> <command>")
        self.logger.console.print("  • Remove alias: silantui --remove-alias <name>")
        self.logger.console.print("  • Setup aliases: silantui --setup-aliases")
        self.logger.console.print()
    
    def cleanup(self) -> None:
        """Cleanup before exit."""
        # Stop live display and show previous terminal history
        if self.use_live_display and hasattr(self, 'chat_display'):
            self.chat_display.stop()

        # Auto-save current session
        if self.current_session.messages:
            self.session_manager.save(self.current_session)

        self.logger.info("Application stopped")


def main() -> None:
    """Entry point for the CLI application."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="SilanTui - Modern terminal interface for AI conversations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  silantui                           # Start chat interface (live display)
  silantui --traditional             # Use traditional display mode
  silantui --model claude-opus-4     # Use specific model
  silantui --setup-aliases           # Setup command aliases

More info: https://github.com/yourusername/silantui
        """
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        help="Anthropic API key (or set LLM_API_KEY environment variable)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="claude-sonnet-4-20250514",
        help="LLM model (default: claude-sonnet-4-20250514)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Log level (default: info)"
    )
    parser.add_argument(
        "--traditional",
        action="store_true",
        help="Use traditional display mode (no live display)"
    )
    parser.add_argument(
        "--setup-aliases",
        action="store_true",
        help="Interactive alias setup"
    )
    parser.add_argument(
        "--list-aliases",
        action="store_true",
        help="List configured aliases"
    )
    parser.add_argument(
        "--add-alias",
        nargs=2,
        metavar=("NAME", "COMMAND"),
        help="Add command alias"
    )
    parser.add_argument(
        "--remove-alias",
        type=str,
        metavar="NAME",
        help="Remove command alias"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="SilanTui v0.2.0"
    )
    parser.add_argument(
        "--locked",
        action="store_true",
        help="Lock terminal to UI (alternate screen, no scrollback)"
    )
    # Input UI options
    parser.add_argument(
        "--input-mode",
        type=str,
        choices=["multiline", "prompt"],
        default=os.getenv("EASYCLI_INPUT_MODE", "multiline"),
        help="Input mode: multiline (IME-friendly, Shift+Enter for newline), or prompt"
    )
    parser.add_argument(
        "--footer-offset",
        type=int,
        default=int(os.getenv("EASYCLI_FOOTER_OFFSET", "2")),
        help="Footer input row offset (lines to move up to input line)"
    )
    parser.add_argument(
        "--input-label",
        type=str,
        default=os.getenv("EASYCLI_INPUT_LABEL", "chat"),
        help="Left label on footer bottom row"
    )
    parser.add_argument(
        "--input-tips",
        type=str,
        default=os.getenv("EASYCLI_INPUT_TIPS", "Type / for commands"),
        help="Right tips text on footer bottom row"
    )

    parser.add_argument(
        "--input-reserve-lines",
        type=int,
        default=int(os.getenv("EASYCLI_INPUT_RESERVE", "2")),
        help="Reserved lines for input area when active (prevents overlap)"
    )
    
    shell_help = False
    slash_args: list[str] = []
    argv: list[str] = []
    for arg in sys.argv[1:]:
        if arg == "/help":
            shell_help = True
        elif arg.startswith('/'):
            slash_args.append(arg)
        else:
            argv.append(arg)

    args = parser.parse_args(argv)

    if shell_help:
        logger = ModernLogger(name="silantui", level=args.log_level)
        fig = Figlet(font="slant")
        for line in fig.renderText("SilanTui").splitlines():
            logger.console.print(logger._create_gradient_text(line))

        logger.console.print()
        registry = CommandRegistry()
        register_builtin_commands(registry, SimpleNamespace())
        registry.show_help(
            logger.console,
            table_factory=lambda title: logger.table(title=title),
        )
        logger.console.print(
            "\n[dim]Tip: launch `silantui` and type `/help` inside the session for interactive commands.\n"
            "Use `silantui --help` to see CLI flags.[/dim]\n"
        )
        return

    if slash_args:
        logger = ModernLogger(name="silantui", level=args.log_level)
        unique_cmds = ", ".join(f"`{cmd}`" for cmd in sorted(set(slash_args)))
        message = (
            "Slash commands such as {cmds} are available after the chat UI starts.\n"
            "Launch SilanTui first (and provide an API key), then type them inside the session."
        ).format(cmds=unique_cmds)
        logger.console.print(Markdown(message))
        logger.console.print(
            "\n[dim]Hint: use `/help` inside the app to browse all commands.[/dim]\n"
        )
        return

    # Handle alias management commands
    if args.setup_aliases:
        from .core.command_manager import setup_aliases_interactive
        setup_aliases_interactive()
        return
    
    if args.list_aliases:
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        cm = CommandManager()
        aliases = cm.list_aliases()

        if aliases:
            table = Table(title="Command Aliases", show_header=True)
            table.add_column("Alias", style="yellow")
            table.add_column("Command", style="green")
            
            for alias, command in aliases.items():
                table.add_row(alias, command)
            
            console.print()
            console.print(table)
            console.print()
        else:
            console.print("\n[yellow]No aliases configured[/yellow]\n")
        return
    
    if args.add_alias:
        from rich.console import Console
        
        console = Console()
        cm = CommandManager()
        alias_name, alias_command = args.add_alias
        cm.add_alias(alias_name, alias_command)
        console.print(f"\n[green]✅ Alias added: {alias_name} -> {alias_command}[/green]\n")
        return
    
    if args.remove_alias:
        from rich.console import Console
        
        console = Console()
        cm = CommandManager()
        if cm.remove_alias(args.remove_alias):
            console.print(f"\n[green]✅ Alias removed: {args.remove_alias}[/green]\n")
        else:
            console.print(f"\n[red]❌ Alias does not exist: {args.remove_alias}[/red]\n")
        return
    
    # Get API key
    api_key = args.api_key or os.getenv("LLM_API_KEY")
    if not api_key:
        logger = ModernLogger(name="silantui", level=args.log_level)
        fig = Figlet(font="slant")
        for line in fig.renderText("SilanTui").splitlines():
            logger.console.print(logger._create_gradient_text(line))

        logger.console.print()
        welcome_table = logger.table(title="Welcome to SilanTui")
        welcome_table.add_column("Highlights", style="white")
        welcome_table.add_row(
            Text.from_markup(
                "[green]•[/green] Modern terminal experience for AI conversations\n"
                "[green]•[/green] Live streaming output with a rich command palette\n"
                "[green]•[/green] IME-friendly input without relying on the alternate screen"
            )
        )
        logger.console.print(welcome_table)

        logger.console.print()
        quick_table = logger.table(title="Quick Start")
        quick_table.add_column("#", style="cyan", justify="right", width=2)
        quick_table.add_column("Instruction", style="white")
        quick_table.add_row(
            "1",
            Text.from_markup(
                "Set your API key: [cyan]export LLM_API_KEY=<your-key>[/cyan] or run "
                "[cyan]silantui --api-key <your-key>[/cyan]"
            ),
        )
        quick_table.add_row(
            "2",
            "Launch the interface with [cyan]silantui[/cyan]",
        )
        quick_table.add_row(
            "3",
            "Inspect CLI options with [cyan]silantui --help[/cyan]",
        )
        quick_table.add_row(
            "4",
            "Inside the app, type [cyan]/help[/cyan] to open the command palette",
        )
        logger.console.print(quick_table)

        logger.console.print()
        flags_table = logger.table(title="Helpful CLI Flags")
        flags_table.add_column("Flag", style="cyan", no_wrap=True)
        flags_table.add_column("Purpose", style="white")
        flags_table.add_row("--api-key <key>", "Provide an API key at launch")
        flags_table.add_row(
            "--model <name>",
            "Pick the default model (default: claude-sonnet-4-20250514)",
        )
        flags_table.add_row(
            "--traditional",
            "Disable the live display for a legacy prompt loop",
        )
        flags_table.add_row(
            "--log-level {…}",
            "Adjust logging verbosity",
        )
        flags_table.add_row(
            "--input-mode {…}",
            "Choose the input editor style",
        )
        flags_table.add_row("--setup-aliases", "Open the alias setup wizard")
        flags_table.add_row("--list-aliases", "Print configured aliases")
        flags_table.add_row("--add-alias <name> <command>", "Create a new alias")
        flags_table.add_row("--remove-alias <name>", "Delete an alias")
        flags_table.add_row(
            "--locked",
            "Keep the UI in a locked, no-scroll mode",
        )
        logger.console.print(flags_table)

        logger.console.print()
        footer = Text.from_markup(
            "[dim]More docs: README.md / QUICKSTART.md\n"
            "Project: https://github.com/Qingbolan/silan-tui[/dim]"
        )
        logger.console.print(footer)
        sys.exit(0)
    
    try:
        app = ChatApplication(
            api_key=api_key,
            model=args.model,
            log_level=args.log_level,
            use_live_display=not args.traditional,
            input_mode=args.input_mode,
            input_label=args.input_label,
            input_tips=args.input_tips,
            footer_offset=args.footer_offset,
            input_reserved_lines=args.input_reserve_lines,
            locked=args.locked,
        )
        app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
