"""
Rich-based UI components for the chat interface.
"""

from typing import Optional, List, Dict
from datetime import datetime

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.box import ROUNDED

from ..logging.modern import ModernLogger
from ..core.session import ChatSession


class ChatUI:
    """UI components for displaying chat conversations."""
    
    def __init__(self, logger: Optional[ModernLogger] = None):
        self.logger = logger or ModernLogger(name="chat-ui", level="info")
        self.console = self.logger.console
    
    def show_welcome(self, app_name: str = "SilanTui") -> None:
        """Display welcome banner."""
        self.logger.banner(
            project_name=app_name,
            title="Modern AI Chat Interface",
            description="A beautiful terminal interface for AI conversations\n"
                       "Built with Rich • Powered by LLM",
            font="slant"
        )
    
    def show_header(
        self,
        session_id: str,
        message_count: int,
        model: str = "claude-sonnet-4"
    ) -> Panel:
        """Create header panel."""
        header = Text()
        header.append("🤖 ", style="bold cyan")
        header.append("AI Chat", style="bold white")
        header.append(" | ", style="dim")
        header.append("Session: ", style="dim")
        header.append(session_id[:8], style="bold yellow")
        header.append(" | ", style="dim")
        header.append("Messages: ", style="dim")
        header.append(str(message_count), style="bold green")
        header.append(" | ", style="dim")
        header.append("Model: ", style="dim")
        header.append(model, style="bold magenta")
        
        return Panel(
            header,
            box=ROUNDED,
            style="cyan",
            padding=(0, 2)
        )
    
    def show_message(self, role: str, content: str, timestamp: Optional[str] = None) -> None:
        """Display a single message."""
        if role == "user":
            header = Text()
            header.append("👤 You", style="bold blue")
            if timestamp:
                time_str = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")
                header.append(f" · {time_str}", style="dim")
            
            self.console.print()
            self.console.print(header)
            self.console.print(Text(content, style="white"))
            
        else:  # assistant
            header = Text()
            header.append("🤖 LLM", style="bold magenta")
            if timestamp:
                time_str = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")
                header.append(f" · {time_str}", style="dim")
            
            self.console.print()
            self.console.print(header)
            self.console.print(Markdown(content))
    
    def show_conversation(self, session: ChatSession) -> None:
        """Display entire conversation."""
        if not session.messages:
            welcome = Text()
            welcome.append("👋 ", style="bold")
            welcome.append("Welcome! Start a conversation by typing a message.\n", style="green")
            welcome.append("\n💡 ", style="dim")
            welcome.append("Tips:\n", style="bold cyan")
            welcome.append("  • Type ", style="white")
            welcome.append("/help", style="bold yellow")
            welcome.append(" to see all commands\n", style="white")
            welcome.append("  • Type ", style="white")
            welcome.append("/exit", style="bold red")
            welcome.append(" to quit\n", style="white")
            
            panel = Panel(
                welcome,
                box=ROUNDED,
                border_style="green",
                padding=(1, 2)
            )
            self.console.print(panel)
            return
        
        for msg in session.messages:
            self.show_message(
                msg["role"],
                msg["content"],
                msg.get("timestamp")
            )
        
        self.console.print()
    
    def show_input_prompt(self) -> Panel:
        """Create input prompt panel."""
        text = Text()
        text.append("> ", style="bold yellow")
        text.append("Type your message", style="white")
        text.append(" | ", style="dim")
        text.append("/help", style="cyan")
        text.append(" for commands | ", style="dim")
        text.append("/exit", style="red")
        text.append(" to quit", style="dim")
        
        return Panel(
            text,
            box=ROUNDED,
            style="yellow",
            padding=(0, 2)
        )
    
    def show_help(self) -> None:
        """Display help information."""
        table = Table(
            title="📖 Available Commands",
            box=ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("Command", style="bold yellow", width=20)
        table.add_column("Description", style="white")
        
        commands = [
            ("/help", "Show this help message"),
            ("/new", "Start a new conversation"),
            ("/clear", "Clear current conversation"),
            ("/save", "Save current conversation"),
            ("/load <id>", "Load a saved conversation"),
            ("/list", "List all saved conversations"),
            ("/export", "Export conversation as Markdown"),
            ("/model <name>", "Change the AI model"),
            ("/system <prompt>", "Set system prompt"),
            ("/exit or /quit", "Exit the application"),
            ("/commands", "Manage custom commands"),
        ]
        
        for cmd, desc in commands:
            table.add_row(cmd, desc)
        
        self.console.print()
        self.console.print(table)
        self.console.print()
        self.console.print(
            "[dim]💡 Tip: All conversations are automatically saved[/dim]\n"
        )
    
    def show_sessions(self, sessions: List[Dict]) -> None:
        """Display list of sessions."""
        if not sessions:
            self.console.print("[yellow]📭 No saved sessions found[/yellow]\n")
            return
        
        table = Table(
            title="📚 Saved Conversations",
            box=ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("Session ID", style="bold yellow", width=20)
        table.add_column("Messages", justify="right", style="green", width=10)
        table.add_column("Created", style="blue", width=20)
        table.add_column("Updated", style="magenta", width=20)
        
        for session in sessions:
            session_id = session["id"][:16] + "..."
            messages = str(session["messages"])
            created = datetime.fromisoformat(session["created_at"]).strftime("%Y-%m-%d %H:%M")
            updated = datetime.fromisoformat(session["updated_at"]).strftime("%Y-%m-%d %H:%M")
            table.add_row(session_id, messages, created, updated)
        
        self.console.print()
        self.console.print(table)
        self.console.print()
        self.console.print("[dim]💡 Use /load <id> to load a session[/dim]\n")
    
    def show_error(self, message: str) -> None:
        """Display error message."""
        self.logger.error_box(message)
    
    def show_success(self, message: str) -> None:
        """Display success message."""
        self.logger.success(message)
    
    def show_info(self, title: str, message: str) -> None:
        """Display info panel."""
        self.logger.info_panel(title, message)
    
    def confirm(self, message: str) -> bool:
        """Show confirmation prompt."""
        from rich.prompt import Confirm
        return Confirm.ask(f"\n[yellow]{message}[/yellow]")
