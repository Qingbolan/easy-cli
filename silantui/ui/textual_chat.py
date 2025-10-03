"""
Textual-based Chat Interface - Modern TUI with full interactivity

- Automatic scrolling with mouse and keyboard
- True interactive input without stop/start cycles
- Better layout management
- Native event handling
"""

from typing import Optional, List
from dataclasses import dataclass
import time
import asyncio

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog
from textual.containers import Container
from textual.binding import Binding
from textual.reactive import reactive
from textual import on
from rich.text import Text
from rich.markdown import Markdown


@dataclass
class ChatMessage:
    """Represents a single chat message"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: float = None
    duration: Optional[float] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class ChatHistory(RichLog):
    """
    Scrollable chat history widget

    Features:
    - Auto-scroll to bottom on new messages
    - Mouse wheel scrolling
    - Keyboard navigation (arrows, page up/down)
    - Markdown rendering for assistant messages
    """

    DEFAULT_CSS = """
    ChatHistory {
        height: 1fr;
        border: none;
        background: $background;
        padding: 1 2;
    }

    ChatHistory:focus {
        border: none;
        background: $background;
    }
    """

    can_focus = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auto_scroll: bool = True
        # streaming state
        self._streaming_start: Optional[float] = None
        self._streaming_full_content: str = ""
        self._streaming_buffer: str = ""

    def _maybe_scroll_end(self) -> None:
        if self.auto_scroll:
            # no animation avoids jitter during fast updates
            self.scroll_end(animate=False)

    def add_user_message(self, content: str):
        """Add a user message with simple > prefix"""
        user_text = Text.assemble(("> ", "bold cyan"), (content, ""))
        self.write(user_text)
        self._maybe_scroll_end()

    def add_assistant_message(self, content: str, role: str = "Assistant", duration: Optional[float] = None):
        """Add an assistant message with markdown"""
        header = Text.assemble(("* ", "bold green"), (role, "green"))
        self.write(header)

        try:
            md = Markdown(content, code_theme="monokai")
            self.write(md)
        except Exception as e:
            fallback = Text(f"[markdown render failed: {e}] {content}")
            self.write(fallback)

        if duration is not None:
            meta = Text.assemble(("· ", "dim"), (f"{duration:.2f}s", "dim"))
            self.write(meta)

        self._maybe_scroll_end()

    def start_streaming(self, role: str = "Assistant"):
        """Start streaming indicator"""
        self._streaming_start = time.time()
        self._streaming_full_content = ""
        self._streaming_buffer = ""

        header = Text.assemble(("* ", "bold green"), (role, "green"))
        self.write(header)
        self._maybe_scroll_end()

    def update_streaming(self, chunk: str):
        """Update streaming content in real-time"""
        if self._streaming_start is None:
            # Safety hatch if someone忘了先 start_streaming
            self.start_streaming()

        self._streaming_full_content += chunk
        self._streaming_buffer += chunk

        # Natural chunking for a smoother typing effect
        if chunk in (' ', '\n', '.', '!', '?', ',', ';', ':') or len(self._streaming_buffer) > 40:
            piece = self._streaming_buffer
            self._streaming_buffer = ""
            if piece.strip():
                self.write(piece)
                self._maybe_scroll_end()

    def finish_streaming(self, role: str = "Assistant"):
        """Finish streaming - flush buffer and render formatted Markdown"""
        # Flush remaining buffer
        if self._streaming_buffer.strip():
            self.write(self._streaming_buffer.strip())
            self._streaming_buffer = ""

        # Separator and formatted block
        self.write("")  # spacing
        self.write("──────")
        header = Text.assemble(("* ", "bold green"), (f"{role} (formatted)", "green dim"))
        self.write(header)

        try:
            md = Markdown(self._streaming_full_content, code_theme="monokai")
            self.write(md)
        except Exception as e:
            self.write(Text(f"[markdown render failed: {e}] {self._streaming_full_content}"))

        self.write("")  # spacing
        self._maybe_scroll_end()

        # Reset streaming state
        self._streaming_start = None
        self._streaming_full_content = ""
        self._streaming_buffer = ""


class ChatInput(Input):
    """Simple chat input widget"""

    DEFAULT_CSS = """
    ChatInput {
        height: 3;
        border-top: tall $primary;
        border-bottom: none;
        background: $background;
        padding: 0 2;
    }

    ChatInput:focus {
        border-top: tall $accent;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(placeholder="Type your message...", **kwargs)


class ChatApp(App):
    """
    Main Textual Chat Application

    Features:
    - Full-screen TUI with header/footer
    - Scrollable chat history
    - Interactive input
    - Keyboard shortcuts
    """

    CSS = """
    Screen {
        background: $background;
    }

    Header {
        background: $primary;
        color: $text;
        text-style: bold;
    }

    Footer {
        background: $panel;
    }

    #chat-container {
        height: 1fr;
        background: $background;
    }

    #chat-input {
        dock: bottom;
    }

    .hidden {
        display: none;
        height: 0;
        visibility: hidden;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+n", "new_chat", "New Chat", show=True),
        Binding("escape", "focus_input", "To Input", show=True),
        Binding("ctrl+k", "focus_history", "To History", show=True),
        Binding("ctrl+j", "toggle_autoscroll", "AutoScroll", show=True),
    ]

    status = reactive("Ready")
    message_count = reactive(0)

    def __init__(self, role: str = "Assistant", **kwargs):
        super().__init__(**kwargs)
        self.role = role
        self.messages: List[ChatMessage] = []
        self.streaming_start_time: Optional[float] = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="chat-container"):
            yield ChatHistory(id="chat-history")
        yield ChatInput(id="chat-input")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "SilanTui - Intelligent Chat Assistant"
        self.sub_title = f"{self.role} • {self.status}"

        chat_history = self.query_one("#chat-history", ChatHistory)
        welcome = Text()
        welcome.append("Welcome to SilanTui!\n\n", style="bold cyan")
        welcome.append("• Type to chat\n", style="green")
        welcome.append("• /help for commands\n", style="white")
        welcome.append("• /new to reset\n", style="white")
        welcome.append("• /exit to quit\n", style="white")
        chat_history.write(welcome)

        self.query_one("#chat-input", ChatInput).focus()

    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        message = event.value.strip()
        chat_input = self.query_one("#chat-input", ChatInput)

        if not message:
            return

        # clear early so UI不残留上一条
        chat_input.value = ""

        if message.startswith("/"):
            self.handle_command(message)
            return

        self.add_user_message(message)

        # Hide input during response
        chat_input.add_class("hidden")

        # Allow scrolling while waiting
        self.query_one("#chat-history", ChatHistory).focus()

        # async simulated response (replace with real API)
        self.run_worker(self.simulate_response(message), exclusive=True)

    def handle_command(self, command: str):
        cmd = command.lower().strip()
        chat_history = self.query_one("#chat-history", ChatHistory)

        handlers = {
            "/help": self.show_help,
            "/new": self.action_new_chat,
            "/clear": self.action_new_chat,
            "/exit": self.action_quit,
            "/quit": self.action_quit,
            "/autoscroll": self.action_toggle_autoscroll,
            "/": self.show_help,
        }
        action = handlers.get(cmd)
        if action:
            action()
        else:
            chat_history.write(Text(f"Unknown command: {command}", style="yellow"))

    def show_help(self):
        chat_history = self.query_one("#chat-history", ChatHistory)
        help_text = Text.from_markup(
            "[bold cyan]Available Commands:[/bold cyan]\n"
            "  /help - Show this help\n"
            "  /new  - Clear chat history\n"
            "  /autoscroll - Toggle auto scroll\n"
            "  Ctrl+N - New chat\n"
            "  Ctrl+C - Quit\n"
        )
        chat_history.write(help_text)

    def add_user_message(self, content: str):
        msg = ChatMessage(role="user", content=content)
        self.messages.append(msg)
        self.message_count += 1
        self.query_one("#chat-history", ChatHistory).add_user_message(content)

    def add_assistant_message(self, content: str, duration: Optional[float] = None):
        msg = ChatMessage(role="assistant", content=content, duration=duration)
        self.messages.append(msg)
        self.message_count += 1
        self.query_one("#chat-history", ChatHistory).add_assistant_message(content, self.role, duration)

    def start_streaming(self):
        self.streaming_start_time = time.time()
        self.status = "Typing..."
        self.sub_title = f"{self.role} • {self.status}"
        chat_input = self.query_one("#chat-input", ChatInput)
        chat_input.add_class("hidden")
        self.query_one("#chat-history", ChatHistory).start_streaming(role=self.role)

    def append_streaming(self, chunk: str):
        self.query_one("#chat-history", ChatHistory).update_streaming(chunk)

    def finish_streaming(self):
        """Finish streaming response"""
        duration = time.time() - self.streaming_start_time if self.streaming_start_time else None

        chat_history = self.query_one("#chat-history", ChatHistory)
        chat_history.finish_streaming(role=self.role)

        if duration is not None:
            chat_history.write(Text(f"· {duration:.2f}s", style="dim"))

        self.status = "Ready"
        self.sub_title = f"{self.role} • {self.status}"
        self.streaming_start_time = None

        chat_input = self.query_one("#chat-input", ChatInput)
        chat_input.remove_class("hidden")
        chat_input.focus()

    async def simulate_response(self, user_message: str):
        """Simulate an AI response (placeholder)"""
        await asyncio.sleep(0.2)
        self.start_streaming()

        # pretend to stream token-by-token
        for ch in f"Echo: {user_message}":
            self.append_streaming(ch)
            await asyncio.sleep(0.01)

        self.finish_streaming()

    def action_new_chat(self):
        self.messages.clear()
        self.message_count = 0
        chat_history = self.query_one("#chat-history", ChatHistory)
        chat_history.clear()
        welcome = Text.from_markup(
            "[bold cyan]Chat cleared![/bold cyan]\n\nStart a new conversation...\n"
        )
        chat_history.write(welcome)
        self.action_focus_input()

    def action_focus_input(self):
        self.query_one("#chat-input", ChatInput).focus()

    def action_focus_history(self):
        self.query_one("#chat-history", ChatHistory).focus()

    def action_quit(self):
        self.exit()

    def action_toggle_autoscroll(self):
        self.query_one("#chat-history", ChatHistory).auto_scroll = (
            not self.query_one("#chat-history", ChatHistory).auto_scroll
        )
        state = "ON" if self.query_one("#chat-history", ChatHistory).auto_scroll else "OFF"
        self.query_one("#chat-history", ChatHistory).write(Text(f"[AutoScroll {state}]", style="dim"))

    # for /autoscroll command path
    def action_toggle_autoscroll_command(self):
        self.action_toggle_autoscroll()


def run_chat_app(role: str = "Assistant"):
    app = ChatApp(role=role)
    app.run()


__all__ = ["ChatApp", "ChatHistory", "ChatInput", "ChatMessage", "run_chat_app"]
