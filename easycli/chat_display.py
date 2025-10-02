"""
Enhanced Chat UI - Improved chat interface with fixed input box and Markdown rendering
"""

from typing import Optional, List
from contextlib import contextmanager

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich.text import Text
from rich.box import ROUNDED
from rich.prompt import Prompt
from rich.padding import Padding

from .input_box import InputBox


class ChatDisplay:
    """
    Chat Display Component - Fixed bottom input box with Markdown support

    Features:
        - Fixed bottom input box
        - Auto-scrolling chat history
        - Full Markdown rendering
        - Beautiful message bubbles
        - Real-time streaming display
    """
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.messages: List[dict] = []
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
                "[bold cyan]EasyCli Chat[/bold cyan] - Type message or /help for commands",
                style="cyan"
            )
        )

        # Setup input prompt
        self.layout["input"].update(
            Panel(
                "💬 [yellow]Type message...[/yellow] (Press Enter to send, /help for commands)",
                style="yellow"
            )
        )
    
    def render_message(self, role: str, content: str, streaming: bool = False) -> Panel:
        """
        Render a single message

        Args:
            role: user or assistant
            content: Message content
            streaming: Whether streaming display
        """
        if role == "user":
            # User message - right-aligned, blue
            message_text = Text(content, style="white")
            return Panel(
                message_text,
                title="[bold blue]👤 You[/bold blue]",
                border_style="blue",
                box=ROUNDED,
                title_align="left"
            )
        else:
            # AI message - left-aligned, green, Markdown rendering
            if streaming:
                # Streaming display: use plain text
                message_text = Text(content, style="white")
                title = "[bold green]🤖 LLM[/bold green] [dim](typing...)[/dim]"
            else:
                # Complete message: render Markdown
                try:
                    message_text = Markdown(content)
                except Exception:
                    # Markdown parsing failed, use plain text
                    message_text = Text(content, style="white")
                title = "[bold green]🤖 LLM[/bold green]"
            
            return Panel(
                message_text,
                title=title,
                border_style="green",
                box=ROUNDED,
                title_align="left"
            )
    
    def render_chat_history(self):
        """Render chat history"""
        if not self.messages and not self.current_streaming:
            # Empty chat
            return Panel(
                Padding(
                    "[dim]No messages yet. Start chatting![/dim]",
                    (10, 2)
                ),
                style="dim"
            )

        # Render all messages
        rendered = []

        for msg in self.messages:
            panel = self.render_message(msg["role"], msg["content"])
            rendered.append(panel)
            rendered.append("")  # Empty line separator

        # Add currently streaming message
        if self.current_streaming:
            panel = self.render_message("assistant", self.current_streaming, streaming=True)
            rendered.append(panel)

        # Combine all messages
        from rich.console import Group
        return Group(*rendered)
    
    def update_display(self):
        """Update display"""
        chat_content = self.render_chat_history()
        self.layout["chat"].update(chat_content)

    def add_user_message(self, content: str):
        """Add user message"""
        self.messages.append({"role": "user", "content": content})
        self.update_display()

    def start_assistant_message(self):
        """Start AI streaming response"""
        self.current_streaming = ""
        self.update_display()

    def append_streaming(self, chunk: str):
        """Append streaming content"""
        self.current_streaming += chunk
        self.update_display()

    def finish_assistant_message(self):
        """Finish AI response"""
        if self.current_streaming:
            self.messages.append({"role": "assistant", "content": self.current_streaming})
            self.current_streaming = ""
        self.update_display()

    def clear_messages(self):
        """Clear messages"""
        self.messages = []
        self.current_streaming = ""
        self.update_display()

    def show(self):
        """Show layout"""
        self.console.print(self.layout)

    def get_input(self, prompt_text: str = "💬 You") -> str:
        """
        Get user input

        Note: This temporarily breaks layout because Rich's Prompt doesn't support Layout
        Solution: Use input() and manually format
        """
        # Option 1: Use standard input (more stable)
        self.console.print()
        user_input = Prompt.ask(f"[bold yellow]{prompt_text}[/bold yellow]")
        return user_input.strip()


class LiveChatDisplay:
    """
    Real-time Chat Display - Uses Rich Live for truly fixed layout

    Features:
        - Truly fixed bottom input box
        - Real-time updates without flickering
        - Full Markdown support
        - Smooth streaming display
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
        self.messages: List[dict] = []
        self.current_streaming = ""
        self.current_streaming_start_time = None
        self.layout: Optional[Layout] = None

        # Live & screen context
        self.live: Optional[Live] = None
        self._screen_cm = None            # console.screen() context manager handle

        self.role = role  # Optional role name
        self.mode = mode  # Display mode
        self.status = "ready"  # Current status

        self._alt_screen = True                 # keep alt-screen the whole session
        self.input_reserved_lines = max(1, int(input_reserved_lines))
        self._default_reserved_lines = self.input_reserved_lines
        self.clear_on_refresh = False           # no clear on refresh

        # Footer input component (polymorphic)
        self.input_box = InputBox(
            left_label=left_label or self.mode,
            tips=tips or "Type / for commands",
            footer_offset=footer_offset,
        )
        self._setup_layout()
    
    # -------------------- layout --------------------
    def _setup_layout(self):
        """Setup three-section layout"""
        self.layout = Layout()
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="chat", ratio=1),
            Layout(name="footer", size=5),  # status/input/tips area
        )
        self._update_header()
        self._update_footer()
        self._update_chat()
    
    def _update_header(self):
        """Update header bar"""
        self.layout["header"].update(
            Panel(
                "[bold cyan]EasyCli - Intelligent Chat Assistant[/bold cyan]",
                style="cyan on black",
                box=ROUNDED
            )
        )
    
    def _update_footer(self, status: str = "ready", user_input: str = "", input_mode: bool = False):
        """Update footer using the InputBox component, stable height."""
        self.status = status
        self.layout["footer"].size = 3
        renderable = self.input_box.render(status)
        self.layout["footer"].update(renderable)

    def _update_chat(self):
        """Update chat area with bottom-aligned visible window."""
        if not self.messages and not self.current_streaming:
            welcome = Panel(
                Padding(
                    Text.from_markup(
                        "[bold cyan]Welcome to EasyCli![/bold cyan]\n\n"
                        "This is an intelligent AI chat assistant.\n"
                        "You can:\n"
                        "  • Type message to chat with AI\n"
                        "  • Use /help to view all commands\n"
                        "  • Use /new to start a new conversation\n"
                        "  • Use /exit to quit the program\n\n"
                        "[dim]Start typing your first message![/dim]"
                    ),
                    (2, 4)
                ),
                style="cyan dim",
                box=ROUNDED
            )
            self.layout["chat"].update(welcome)
            return

        from rich.console import Group
        from rich.align import Align
        import time

        term_h = self.console.size.height
        header_h = self.layout["header"].size or 0
        footer_h = self.layout["footer"].size or 0
        chat_h = max(3, term_h - header_h - footer_h)

        visible: List = []
        used = 0
        width = self.console.size.width
        opts = self.console.options.update(width=width)

        if self.current_streaming:
            current_duration = None
            if self.current_streaming_start_time:
                current_duration = time.time() - self.current_streaming_start_time
            last = self._render_message("assistant", self.current_streaming, streaming=True, duration=current_duration)
            lines = self.console.render_lines(last, opts)
            h = max(1, len(lines))
            if used + h <= chat_h:
                visible.insert(0, last)
                used += h

        for msg in reversed(self.messages):
            duration = msg.get("duration")
            r = self._render_message(msg["role"], msg["content"], duration=duration)
            lines = self.console.render_lines(r, opts)
            h = max(1, len(lines))
            if used + h > chat_h:
                break
            visible.insert(0, r)
            used += h

        self.layout["chat"].update(Align(Group(*visible), vertical="bottom"))

    def _render_message(self, role: str, content: str, streaming: bool = False, duration: Optional[float] = None):
        """Render message in minimalist style (no emoji, minimal chrome)"""
        if role == "user":
            return Text(f"> {content}", style="black on white")
        else:
            from datetime import datetime as _dt
            from rich.console import Group as _Group
            import time as _t

            timestamp = _dt.now().strftime("%H:%M:%S")
            parts = []
            if self.role:
                parts.append(self.role)
            parts.append(timestamp)
            if duration is not None:
                parts.append(f"{duration:.1f}s")
            meta = "/".join(parts)

            if streaming:
                cycle = int(_t.time() * 3) % 3
                star = "*" if cycle == 0 else ("✦" if cycle == 1 else "✧")
                header = Text()
                header.append(f"{star} ", style="bold green blink")
                header.append(f"「{meta}」", style="dim")
                header.append(" ●", style="blink green")
                body = Text(content + "▌", style="white")
                return _Group(header, body)
            else:
                header = Text()
                header.append("* ", style="bold green")
                header.append(f"「{meta}」", style="dim")
                try:
                    body = Markdown(content)
                except Exception:
                    body = Text(content, style="white")
                from rich.console import Group as _Group2
                return _Group2(header, body)
    
    # -------------------- Live lifecycle & screen --------------------
    def start(self, use_alt_screen: bool = True):
        """
        Enter alternate screen once and keep it for the whole session.
        Live runs with screen=False so stopping Live won't exit alt-screen.
        """
        if self.live:
            return
        # Enter alt-screen via console.screen() context and keep it open
        if self._screen_cm is None and use_alt_screen:
            self._screen_cm = self.console.screen()
            self._screen_cm.__enter__()

        # Create Live without taking control of screen
        self.live = Live(
            self.layout,
            console=self.console,
            refresh_per_second=10,
            screen=False,           # important: don't toggle screen here
            auto_refresh=False,     # we do full-frame manual updates
        )
        self.live.start()
        # First full-frame draw
        self._update_header()
        self._update_footer(self.status)
        self._update_chat()
        self.live.update(self.layout, refresh=True)
    
    def stop(self):
        """Stop Live and exit alt-screen. Call only when quitting the app."""
        if self.live:
            try:
                self.live.stop()
            finally:
                self.live = None
        if self._screen_cm is not None:
            try:
                self._screen_cm.__exit__(None, None, None)
            finally:
                self._screen_cm = None

    def _full_redraw(self):
        """Full-frame redraw: header/footer/chat then update(refresh=True)."""
        if not self.live:
            return
        self._update_header()
        self._update_footer(self.status)
        self._update_chat()
        self.live.update(self.layout, refresh=True)

    def refresh(self):
        self._full_redraw()

    @contextmanager
    def pause(self):
        """
        Temporarily stop Live to perform blocking IO (e.g., input) while
        staying in the same alt-screen. Live(screen=False) ensures that
        stopping Live doesn't exit alt-screen.
        """
        was_running = bool(self.live)
        try:
            if was_running:
                self.live.stop()
            yield
        finally:
            if was_running:
                # restart Live and redraw a full frame
                self.live.start()
                self._full_redraw()
    
    # -------------------- Chat operations --------------------
    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})
        self._full_redraw()
    
    def start_assistant_message(self):
        import time
        self.current_streaming = ""
        self.current_streaming_start_time = time.time()
        self._update_footer("typing")
        self._full_redraw()

    def append_streaming(self, chunk: str):
        self.current_streaming += chunk
        self._update_chat()
        if self.live:
            self.live.update(self.layout, refresh=True)

    def finish_assistant_message(self):
        import time
        if self.current_streaming:
            duration = time.time() - self.current_streaming_start_time if self.current_streaming_start_time else None
            self.messages.append({
                "role": "assistant",
                "content": self.current_streaming,
                "duration": duration
            })
            self.current_streaming = ""
            self.current_streaming_start_time = None
        self._update_footer("ready")
        self._full_redraw()
    
    def clear_messages(self):
        self.messages = []
        self.current_streaming = ""
        self._full_redraw()
    
    def show_error(self, message: str):
        self._update_footer(f"❌ [bold red]{message}[/bold red]")
        self._full_redraw()
    
    def show_success(self, message: str):
        self._update_footer(f"✅ [bold green]{message}[/bold green]")
        self._full_redraw()

    def notify(self, message: str, style: str = "cyan"):
        try:
            self._update_footer(f"[bold {style}]{message}[/bold {style}]")
            self._full_redraw()
        except Exception:
            pass

    def read_input(self, mode: str = "multiline") -> str:
        """
        Read input while staying in alt-screen:
        - do not leave alt-screen
        - stop Live temporarily, read input on the same screen
        - resume Live and full-frame redraw
        """
        if not self.live:
            self.start(use_alt_screen=True)

        # show typing state before input
        self._update_footer("typing")
        if self.live:
            self.live.update(self.layout, refresh=True)

        with self.pause():
            try:
                text = self.console.input("> ")
            except Exception:
                text = input("> ")

        # restore ready state
        self._update_footer("ready")
        if self.live:
            self.live.update(self.layout, refresh=True)

        return text.strip()


# Export
__all__ = ['ChatDisplay', 'LiveChatDisplay']
