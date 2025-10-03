"""
Enhanced Chat UI - Improved chat interface with fixed input box and Markdown rendering
"""

from typing import Optional, List, Any, Dict
from contextlib import contextmanager
from dataclasses import dataclass, field
import time

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich.text import Text
from rich.box import ROUNDED
from rich.padding import Padding
from rich.align import Align
from rich.rule import Rule

from .input_box import InputBox
from .input_field import InputField


# -------------------- helpers --------------------

@dataclass
class ChatMsg:
    role: str
    content: str
    duration: Optional[float] = None
    # Cache rendered objects to avoid repeated Markdown parsing and flicker
    _render_cache: Optional[RenderableType] = field(default=None, repr=False)


def _safe_markdown(src: str) -> RenderableType:
    try:
        return Markdown(src, code_theme="monokai")
    except Exception:
        return Text(src)


# -------------------- Simple version: non-Live layout --------------------

class ChatDisplay:
    """
    Chat Display Component - Fixed bottom input box with Markdown support

    Features:
        - Fixed bottom input box (static rendering)
        - Auto-scrolling chat history (simplified: one-time output)
        - Full Markdown rendering
        - Simple streaming (no Live)
    """

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.messages: List[Dict[str, Any]] = []
        self.current_streaming = ""
        self.layout = Layout()
        self._setup_layout()

    def _setup_layout(self):
        """Setup layout: top=title, middle=chat, bottom=input"""
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="chat", ratio=1),
            Layout(name="input", size=3),
        )

        # Setup title
        self.layout["header"].update(
            Panel(
                "[bold cyan]SilanTui Chat[/bold cyan] - Type message or /help for commands",
                style="cyan",
                box=ROUNDED
            )
        )

        # Setup input prompt
        self.layout["input"].update(
            Panel(
                "> [yellow]Type message...[/yellow] (Press Enter to send, /help for commands)",
                style="yellow",
                box=ROUNDED
            )
        )

    def render_message(self, role: str, content: str, streaming: bool = False) -> Panel:
        if role == "user":
            message_text = Text(content)
            return Panel(
                message_text,
                title="[bold blue]You[/bold blue]",
                border_style="blue",
                box=ROUNDED,
                title_align="left",
            )
        else:
            if streaming:
                message_text = Text(content)
                title = "[bold green]LLM[/bold green] [dim](typing...)[/dim]"
            else:
                message_text = _safe_markdown(content)
                title = "[bold green]LLM[/bold green]"
            return Panel(
                message_text,
                title=title,
                border_style="green",
                box=ROUNDED,
                title_align="left",
            )

    def render_chat_history(self) -> RenderableType:
        if not self.messages and not self.current_streaming:
            return Panel(
                Padding(
                    "[dim]No messages yet. Start chatting![/dim]",
                    (4, 2)
                ),
                style="dim",
                box=ROUNDED
            )

        rendered: List[RenderableType] = []
        for msg in self.messages:
            rendered.append(self.render_message(msg["role"], msg["content"]))
            rendered.append(Rule(style="dim"))
        if self.current_streaming:
            rendered.append(self.render_message("assistant", self.current_streaming, streaming=True))
        return Group(*rendered)

    def update_display(self):
        chat_content = self.render_chat_history()
        self.layout["chat"].update(chat_content)

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})
        self.update_display()

    def start_assistant_message(self):
        self.current_streaming = ""
        self.update_display()

    def append_streaming(self, chunk: str):
        self.current_streaming += chunk
        self.update_display()

    def finish_assistant_message(self):
        if self.current_streaming:
            self.messages.append({"role": "assistant", "content": self.current_streaming})
            self.current_streaming = ""
        self.update_display()

    def clear_messages(self):
        self.messages.clear()
        self.current_streaming = ""
        self.update_display()

    def show(self):
        self.console.print(self.layout)

    def get_input(self, prompt_text: str = "> You") -> str:
        self.console.print()
        return self.console.input(f"[bold yellow]{prompt_text}[/bold yellow] ").strip()


# -------------------- Live version: stable fixed bottom input with full frame redraw --------------------

class LiveChatDisplay:
    """
    Real-time Chat Display - Uses Rich Live for truly fixed layout

    Features:
        - Fixed bottom input (alt-screen global persist)
        - Full frame manual redraw, no flicker
        - History messages bottom-aligned viewport, clipped by height
        - Markdown render cache
        - Pause input without exiting alt-screen
    """

    def __init__(
        self,
        console: Optional[Console] = None,
        role: Optional[str] = None,
        mode: str = "chat",
        *,
        left_label: Optional[str] = None,
        tips: Optional[str] = None,
        footer_offset: int = 2,
        input_reserved_lines: int = 2,
    ):
        self.console = console or Console()
        self.messages: List[ChatMsg] = []
        self.current_streaming: str = ""
        self.current_streaming_start_time: Optional[float] = None
        self.layout: Optional[Layout] = None

        # Live
        self.live: Optional[Live] = None

        self.role = role
        self.mode = mode
        self.status = "ready"

        self._alt_screen = True
        self.input_reserved_lines = max(1, int(input_reserved_lines))
        self.clear_on_refresh = False

        self.input_box = InputBox(
            left_label=left_label or self.mode,
            tips=tips or "Type / for commands",
            footer_offset=footer_offset,
        )

        # Interactive input field
        self.input_field = InputField(
            console=self.console,
            prompt="> ",
            placeholder="Type your message... (Enter to send, / for commands)",
        )

        self._setup_layout()

    # -------------------- layout --------------------
    def _setup_layout(self):
        self.layout = Layout()
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="chat", ratio=1),
            Layout(name="footer", size=3),
        )
        # Only draw header once during initialization
        self.layout["header"].update(
            Panel(
                "[bold cyan]SilanTui - Intelligent Chat Assistant[/bold cyan]",
                style="cyan on black",
                box=ROUNDED,
            )
        )
        self._update_footer()
        self._update_chat()

    def _update_footer(self, status: str = "ready"):
        self.status = status
        # Fixed height, let InputBox handle internal line wrapping to avoid footer jitter
        self.layout["footer"].size = 3
        self.layout["footer"].update(self.input_box.render(status))

    def _render_cached(self, msg: ChatMsg) -> RenderableType:
        if msg._render_cache is not None:
            return msg._render_cache
        if msg.role == "user":
            # User message: > prefix included in light background
            user_text = Text(f"> {msg.content}", style="black on grey93")
            r: RenderableType = user_text
        else:
            # Assistant message: metadata header + markdown body
            header = Text()
            header.append("* ", style="bold green")
            meta = []
            if self.role:
                meta.append(self.role)
            meta.append(time.strftime("%H:%M:%S"))
            if msg.duration is not None:
                meta.append(f"{msg.duration:.1f}s")
            header.append(f"「{'/'.join(meta)}」", style="dim")
            body = _safe_markdown(msg.content)
            r = Group(header, body)
        msg._render_cache = r
        return r

    def _render_streaming(self) -> RenderableType:
        # Lightweight animation to avoid flashy effects causing jitter
        tick = int(time.time() * 4) % 4
        dots = "…"[:tick] if tick else ""
        header = Text()
        header.append("• ", style="bold green")
        header.append("typing", style="dim")
        header.append(dots, style="dim")
        body = Text(self.current_streaming + "▌")
        return Group(header, body)

    def _update_chat(self):
        # Empty state
        if not self.messages and not self.current_streaming:
            welcome = Panel(
                Padding(
                    Text.from_markup(
                        "[bold cyan]Welcome to SilanTui![/bold cyan]\n\n"
                        "• Type to chat\n"
                        "• /help for commands\n"
                        "• /new to reset\n"
                        "• /exit to quit\n"
                    ),
                    (2, 4),
                ),
                style="cyan dim",
                box=ROUNDED,
            )
            self.layout["chat"].update(welcome)
            return

        # Bottom-aligned viewport: fill from bottom to top by height
        term_w = self.console.size.width
        term_h = self.console.size.height
        header_h = self.layout["header"].size or 0
        footer_h = self.layout["footer"].size or 0
        chat_h = max(3, term_h - header_h - footer_h)

        opts = self.console.options.update(width=term_w)
        visible: List[RenderableType] = []
        used = 0

        # First add streaming
        if self.current_streaming:
            streaming_r = self._render_streaming()
            h = max(1, len(self.console.render_lines(streaming_r, opts)))
            if used + h <= chat_h:
                visible.insert(0, streaming_r)
                used += h

        # Then fill from history in reverse order
        for msg in reversed(self.messages):
            r = self._render_cached(msg)
            rh = max(1, len(self.console.render_lines(r, opts)))
            # Add spacing between messages (1 blank line)
            spacing_h = 1
            if used + rh + spacing_h > chat_h:
                break
            visible.insert(0, r)
            used += rh
            # Add blank line for spacing
            if used + spacing_h <= chat_h:
                visible.insert(0, Text(""))
                used += spacing_h

        self.layout["chat"].update(Align(Group(*visible), vertical="bottom"))

    # -------------------- Live lifecycle --------------------
    def start(self, use_alt_screen: bool = True):
        if self.live:
            return

        self.live = Live(
            self.layout,
            console=self.console,
            refresh_per_second=12,
            screen=True,        # Must be True: full screen redraw, prevents append/scroll
            auto_refresh=False, # Manual refresh to prevent jitter
            transient=False,
            redirect_stdout=False,
            redirect_stderr=False,
        )
        self.live.start()

    def stop(self):
        if self.live:
            try:
                self.live.stop()
            finally:
                self.live = None

    def _full_redraw(self):
        if not self.live:
            return
        # Don't update header - only drawn once in _setup_layout()
        self._update_footer(self.status)
        self._update_chat()
        self.live.update(self.layout, refresh=True)

    def refresh(self):
        self._full_redraw()

    @contextmanager
    def pause(self):
        """Pause rendering without leaving alt-screen."""
        if not self.live:
            yield
            return
        # Temporarily stop auto-refresh, but keep Live active
        was_running = self.live.is_started
        try:
            if was_running:
                self.live.stop()
            yield
        finally:
            if was_running:
                self.live.start(refresh=True)

    # -------------------- Chat operations --------------------
    def add_user_message(self, content: str):
        self.messages.append(ChatMsg(role="user", content=content))
        self._full_redraw()

    def start_assistant_message(self):
        self.current_streaming = ""
        self.current_streaming_start_time = time.time()
        self._update_footer("typing")
        self._full_redraw()

    def append_streaming(self, chunk: str):
        if not chunk:
            return
        self.current_streaming += chunk
        # Partial update of chat to reduce full frame cost
        self._update_chat()
        if self.live:
            self.live.update(self.layout, refresh=True)

    def finish_assistant_message(self):
        if self.current_streaming:
            dur = time.time() - self.current_streaming_start_time if self.current_streaming_start_time else None
            self.messages.append(ChatMsg(role="assistant", content=self.current_streaming, duration=dur))
            self.current_streaming = ""
            self.current_streaming_start_time = None
        self._update_footer("ready")
        self._full_redraw()

    def clear_messages(self):
        self.messages.clear()
        self.current_streaming = ""
        self._full_redraw()

    def show_error(self, message: str):
        self._update_footer(f"[bold red]❌ {message}[/bold red]")
        self._full_redraw()

    def show_success(self, message: str):
        self._update_footer(f"[bold green]✅ {message}[/bold green]")
        self._full_redraw()

    def notify(self, message: str, style: str = "cyan"):
        self._update_footer(f"[bold {style}]{message}[/bold {style}]")
        self._full_redraw()

    def show(self):
        # NEVER print layout during Live mode - causes frame append/stacking
        if self.live:
            return
        self.console.print(self.layout)

    def read_input(self, prompt: str = "> ") -> str:
        """
        Read input using integrated input field
        - No need to stop/pause Live
        - Real-time character input with cursor
        - Works seamlessly within alt-screen
        """
        if not self.live:
            self.start()

        # Update footer to show input field
        self.input_field.clear()
        self.input_field._active = True
        self.layout["footer"].update(self.input_field.render("ready"))
        self.live.update(self.layout, refresh=True)

        # Read input character by character
        try:
            while True:
                char = self.input_field.read_char()
                if char is None:
                    continue

                # Process the key
                should_submit = self.input_field.process_key(char)

                # Update display
                self.layout["footer"].update(self.input_field.render("typing"))
                self.live.update(self.layout, refresh=True)

                if should_submit:
                    break

            # Get the final value
            value = self.input_field.get_value()
            self.input_field._active = False

            # Restore footer to status display
            self._update_footer("ready")
            self.live.update(self.layout, refresh=True)

            return value.strip()

        except (KeyboardInterrupt, EOFError):
            self.input_field._active = False
            self._update_footer("ready")
            self.live.update(self.layout, refresh=True)
            raise


__all__ = ["ChatDisplay", "LiveChatDisplay"]
