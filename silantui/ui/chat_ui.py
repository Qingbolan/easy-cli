"""
Textual-based UI components for the chat interface.

This is the modern replacement for the Rich-based chat_ui.py
"""

from typing import Optional, List
from datetime import datetime

from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, Label
from textual.containers import Container, ScrollableContainer
from textual.binding import Binding
from textual.reactive import reactive
from rich.text import Text
from rich.markdown import Markdown

from ..logging.modern import ModernLogger
from ..core.session import ChatSession


class ChatMessage(Static):
    """A single chat message widget"""

    def __init__(self, role: str, content: str, timestamp: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.role = role
        self.content = content
        self.timestamp = timestamp

    def compose(self) -> ComposeResult:
        """Compose the message display"""
        # Create header
        if self.role == "user":
            icon = "👤"
            name = "You"
            style = "bold blue"
        else:
            icon = "🤖"
            name = "Assistant"
            style = "bold magenta"

        header = Text()
        header.append(f"{icon} ", style=style)
        header.append(name, style=style)

        if self.timestamp:
            time_str = datetime.fromisoformat(self.timestamp).strftime("%H:%M:%S")
            header.append(f" · {time_str}", style="dim")

        yield Label(header)

        # Create content
        if self.role == "user":
            # User message with background
            msg_text = Text(f"> {self.content}", style="black on grey93")
            yield Static(msg_text)
        else:
            # Assistant message with markdown
            try:
                yield Static(Markdown(self.content, code_theme="monokai"))
            except:
                yield Static(Text(self.content))


class ChatDisplay(ScrollableContainer):
    """Scrollable chat message display"""

    DEFAULT_CSS = """
    ChatDisplay {
        height: 1fr;
        border: solid cyan;
        background: $surface;
        padding: 1;
    }

    ChatMessage {
        margin: 1 0;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages: List[ChatMessage] = []

    def add_message(self, role: str, content: str, timestamp: Optional[str] = None):
        """Add a message to the chat display"""
        msg = ChatMessage(role, content, timestamp)
        self.mount(msg)
        self.messages.append(msg)
        # Auto-scroll to bottom
        self.scroll_end(animate=False)

    def clear_messages(self):
        """Clear all messages"""
        for msg in self.messages:
            msg.remove()
        self.messages.clear()


class ChatHeader(Static):
    """Chat header with session info"""

    DEFAULT_CSS = """
    ChatHeader {
        dock: top;
        height: 3;
        content-align: center middle;
        background: $primary;
        color: $text;
        border: solid cyan;
    }
    """

    session_id = reactive("")
    message_count = reactive(0)
    model = reactive("claude-sonnet-4")

    def render(self) -> Text:
        """Render the header"""
        header = Text()
        header.append("🤖 ", style="bold cyan")
        header.append("AI Chat", style="bold white")
        header.append(" | ", style="dim")
        header.append("Session: ", style="dim")
        header.append(self.session_id[:8] if self.session_id else "N/A", style="bold yellow")
        header.append(" | ", style="dim")
        header.append("Messages: ", style="dim")
        header.append(str(self.message_count), style="bold green")
        header.append(" | ", style="dim")
        header.append("Model: ", style="dim")
        header.append(self.model, style="bold magenta")
        return header


class ChatUIApp(App):
    """
    Main Textual Chat UI Application

    Modern replacement for Rich-based ChatUI
    """

    CSS = """
    Screen {
        background: $background;
    }

    #welcome {
        height: 100%;
        content-align: center middle;
        padding: 2;
    }

    #chat-container {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+n", "new_chat", "New Chat", show=True),
        Binding("ctrl+h", "show_help", "Help", show=True),
    ]

    def __init__(self, session: Optional[ChatSession] = None, logger: Optional[ModernLogger] = None, **kwargs):
        super().__init__(**kwargs)
        self.session = session
        self.logger = logger or ModernLogger(name="chat-ui", level="info")

    def compose(self) -> ComposeResult:
        """Build the UI"""
        # Header with session info
        self.header_widget = ChatHeader(id="chat-header")
        if self.session:
            self.header_widget.session_id = self.session.session_id
            self.header_widget.message_count = len(self.session.messages)
        yield self.header_widget

        # Main chat display
        with Container(id="chat-container"):
            self.chat_display = ChatDisplay(id="chat-display")
            yield self.chat_display

        # Footer
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts"""
        self.title = "SilanTui - AI Chat Interface"
        self.sub_title = "Powered by Textual"

        # Show welcome or existing conversation
        if self.session and self.session.messages:
            self.show_conversation()
        else:
            self.show_welcome()

    def show_welcome(self):
        """Show welcome message"""
        welcome = Text()
        welcome.append("👋 ", style="bold")
        welcome.append("Welcome! Start a conversation by typing a message.\n\n", style="green")
        welcome.append("💡 ", style="dim")
        welcome.append("Tips:\n", style="bold cyan")
        welcome.append("  • Type ", style="white")
        welcome.append("/help", style="bold yellow")
        welcome.append(" to see all commands\n", style="white")
        welcome.append("  • Type ", style="white")
        welcome.append("/exit", style="bold red")
        welcome.append(" to quit\n", style="white")

        self.chat_display.mount(Static(welcome, id="welcome"))

    def show_conversation(self):
        """Display entire conversation from session"""
        if not self.session or not self.session.messages:
            self.show_welcome()
            return

        for msg in self.session.messages:
            self.chat_display.add_message(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
                timestamp=msg.get("timestamp")
            )

    def add_message(self, role: str, content: str, timestamp: Optional[str] = None):
        """Add a message to the display"""
        # Remove welcome if present
        try:
            welcome = self.query_one("#welcome")
            welcome.remove()
        except:
            pass

        # Add message
        self.chat_display.add_message(role, content, timestamp)

        # Update header
        self.header_widget.message_count += 1

    def action_new_chat(self):
        """Start a new chat"""
        self.chat_display.clear_messages()
        self.header_widget.message_count = 0
        self.show_welcome()

        if self.session:
            self.session.messages.clear()

    def action_show_help(self):
        """Show help message"""
        help_text = Text.from_markup(
            "[bold cyan]Available Commands:[/bold cyan]\n"
            "  /help - Show this help\n"
            "  /new - Start new conversation\n"
            "  /exit - Exit application\n"
            "  /clear - Clear screen\n"
            "  Ctrl+N - New chat\n"
            "  Ctrl+H - Show help\n"
            "  Ctrl+C - Quit\n"
        )
        self.chat_display.mount(Static(help_text))

    def action_quit(self):
        """Quit the application"""
        self.exit()


class ChatUI:
    """
    Wrapper class for compatibility with existing code

    Provides same interface as Rich-based ChatUI but uses Textual
    """

    def __init__(self, logger: Optional[ModernLogger] = None):
        self.logger = logger or ModernLogger(name="chat-ui", level="info")
        self.app: Optional[ChatUIApp] = None

    def run(self, session: Optional[ChatSession] = None):
        """Run the Textual chat UI"""
        self.app = ChatUIApp(session=session, logger=self.logger)
        self.app.run()

    def show_welcome(self, app_name: str = "SilanTui"):
        """Display welcome banner (compatibility method)"""
        self.logger.banner(
            project_name=app_name,
            title="Modern AI Chat Interface",
            description="A beautiful terminal interface for AI conversations\n"
                       "Built with Textual • Powered by LLM",
            font="slant"
        )

    def show_message(self, role: str, content: str, timestamp: Optional[str] = None):
        """Display a single message (compatibility method)"""
        if self.app and hasattr(self.app, 'chat_display'):
            self.app.add_message(role, content, timestamp)
        else:
            # Fallback to console output
            if role == "user":
                self.logger.console.print(f"\nYou: {content}")
            else:
                self.logger.console.print(f"\nAssistant:")
                self.logger.console.print(Markdown(content))

    def show_conversation(self, session: ChatSession):
        """Display entire conversation (compatibility method)"""
        if self.app:
            self.app.session = session
            self.app.show_conversation()


__all__ = ["ChatUI", "ChatUIApp", "ChatDisplay", "ChatHeader", "ChatMessage"]
