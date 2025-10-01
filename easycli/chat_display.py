"""
Enhanced Chat UI - Improved chat interface with fixed input box and Markdown rendering
"""

from typing import Optional, List
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
from contextlib import contextmanager


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
    
    def render_chat_history(self) -> Layout:
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
        self.layout = None
        self.live = None
        self.role = role  # Optional role name
        self.mode = mode  # Display mode
        self.status = "ready"  # Current status
        self._alt_screen = False  # remember alt-screen preference
        self.input_reserved_lines = max(1, int(input_reserved_lines))
        self._default_reserved_lines = self.input_reserved_lines
        self.clear_on_refresh = False  # when True, clear scrollback each refresh
        # Footer input component (polymorphic)
        self.input_box = InputBox(
            left_label=left_label or self.mode,
            tips=tips or "Type / for commands",
            footer_offset=footer_offset,
        )
        self._setup_layout()
    
    def _setup_layout(self):
        """Setup three-section layout"""
        self.layout = Layout()
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="chat", ratio=1),
            Layout(name="footer", size=5),  # 5 lines: status, separator, input, separator, mode+tips
        )

        self._update_header()
        self._update_footer()
        self._update_chat()
    
    def _update_header(self):
        """Update header bar"""
        header = Panel(
            "[bold cyan]EasyCli - Intelligent Chat Assistant[/bold cyan]",
            style="cyan on black",
            box=ROUNDED
        )
        self.layout["header"].update(header)
    
    def _update_footer(self, status: str = "ready", user_input: str = "", input_mode: bool = False):
        """Update footer using the InputBox component.

        Keep footer height stable to avoid layout jitter; composer remains
        single-line (cropped) for reliability with IME.
        """
        self.status = status
        # Keep stable height of 5 lines for the footer
        self.layout["footer"].size = 3
        renderable = self.input_box.render(status)
        self.layout["footer"].update(renderable)

    @contextmanager
    def pause(self):
        """Context manager to temporarily stop Live and restore it safely."""
        was_running = bool(self.live)
        try:
            if was_running:
                self.stop()
            yield
        finally:
            if was_running:
                self.start(use_alt_screen=self._alt_screen)
                # Restore footer to non-input mode after external IO
                self._update_footer(self.status or "ready", user_input="", input_mode=False)
                self.live.refresh()
    
    def _update_chat(self):
        """Update chat area"""
        if not self.messages and not self.current_streaming:
            # Welcome message
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

        # Render message history
        from rich.console import Group
        from rich.align import Align
        import time

        rendered = []

        # Compute available chat area height
        term_h = self.console.size.height
        header_h = self.layout["header"].size or 0
        footer_h = self.layout["footer"].size or 0
        chat_h = max(3, term_h - header_h - footer_h)

        # Build visible region from bottom up using real rendered heights
        visible: List = []
        used = 0
        width = self.console.size.width
        opts = self.console.options.update(width=width)

        # Include current streaming (treated as newest)
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

        # Walk history from newest to oldest, fill remaining space
        for msg in reversed(self.messages):
            duration = msg.get("duration")
            r = self._render_message(msg["role"], msg["content"], duration=duration)
            lines = self.console.render_lines(r, opts)
            h = max(1, len(lines))
            if used + h > chat_h:
                break
            visible.insert(0, r)
            used += h

        # Bottom-align content within the chat area (let Layout control height)
        self.layout["chat"].update(Align(Group(*visible), vertical="bottom"))

    def _render_message(self, role: str, content: str, streaming: bool = False, duration: Optional[float] = None):
        """Render message in minimalist style (no emoji, minimal chrome)"""
        if role == "user":
            # Simple user message with > prefix
            user_content = Text(f"> {content}", style="black on white")
            return user_content
        else:
            # Assistant message: metadata header + body (Markdown when possible)
            from datetime import datetime
            from rich.console import Group

            timestamp = datetime.now().strftime("%H:%M:%S")
            metadata_parts = []
            if self.role:
                metadata_parts.append(self.role)
            metadata_parts.append(timestamp)
            if duration is not None:
                metadata_parts.append(f"{duration:.1f}s")
            metadata = "/".join(metadata_parts)

            if streaming:
                import time
                cycle = int(time.time() * 3) % 3
                star = "*" if cycle == 0 else ("✦" if cycle == 1 else "✧")
                header = Text()
                header.append(f"{star} ", style="bold green blink")
                header.append(f"「{metadata}」", style="dim")
                header.append(" ●", style="blink green")
                message = Text(content + "▌", style="white")
                return Group(header, message)
            else:
                header = Text()
                header.append("* ", style="bold green")
                header.append(f"「{metadata}」", style="dim")
                try:
                    body = Markdown(content)
                except Exception:
                    body = Text(content, style="white")
                return Group(header, body)
    
    def start(self, use_alt_screen: bool = False):
        """Start real-time display.

        Args:
            use_alt_screen: when True, use terminal alternate screen for
                            a focused full-screen UI. Defaults to False
                            for better compatibility with prompts/demos.
        """
        self._alt_screen = use_alt_screen
        if use_alt_screen:
            self.console.clear()
        self.live = Live(
            self.layout,
            console=self.console,
            refresh_per_second=10,
            screen=use_alt_screen,
        )
        self.live.start()
        if self.clear_on_refresh:
            # Clear terminal scrollback so only current UI is visible
            try:
                self.console.print("\x1b[3J", end="")
            except Exception:
                pass
    
    def stop(self):
        """Stop real-time display"""
        if self.live:
            self.live.stop()

    def clear_scrollback(self):
        """Clear terminal scrollback buffer (xterm CSI 3 J)."""
        try:
            out = getattr(self.console, "file", None)
            if out:
                out.write("\x1b[3J")
                out.flush()
        except Exception:
            pass

    def _clear_all(self):
        """Clear screen and scrollback, then home cursor."""
        try:
            out = getattr(self.console, "file", None)
            if out:
                out.write("\x1b[H\x1b[2J\x1b[3J")
                out.flush()
        except Exception:
            pass

    def refresh(self):
        """Refresh Live, optionally clearing scrollback first."""
        if self.clear_on_refresh:
            self._clear_all()
        if self.live:
            self.live.refresh()
    
    def add_user_message(self, content: str):
        """Add user message"""
        self.messages.append({"role": "user", "content": content})
        self._update_chat()
        self.refresh()
    
    def start_assistant_message(self):
        """Start AI response"""
        import time
        self.current_streaming = ""
        self.current_streaming_start_time = time.time()
        self._update_footer("typing")
        self._update_chat()
        self.refresh()

    def append_streaming(self, chunk: str):
        """Append streaming content"""
        self.current_streaming += chunk
        self._update_chat()
        # live.refresh() will be called automatically

    def finish_assistant_message(self):
        """Finish AI response"""
        import time
        if self.current_streaming:
            # Calculate duration
            duration = None
            if self.current_streaming_start_time:
                duration = time.time() - self.current_streaming_start_time

            self.messages.append({
                "role": "assistant",
                "content": self.current_streaming,
                "duration": duration
            })
            self.current_streaming = ""
            self.current_streaming_start_time = None
        self._update_footer("ready")
        self._update_chat()
        self.refresh()
    
    def clear_messages(self):
        """Clear messages"""
        self.messages = []
        self.current_streaming = ""
        self._update_chat()
        self.refresh()
    
    def show_error(self, message: str):
        """Display error"""
        self._update_footer(f"❌ [bold red]{message}[/bold red]")
        self.refresh()
    
    def show_success(self, message: str):
        """Display success"""
        self._update_footer(f"✅ [bold green]{message}[/bold green]")
        self.refresh()

    def notify(self, message: str, style: str = "cyan"):
        """Transient info message in footer status."""
        try:
            self._update_footer(f"[bold {style}]{message}[/bold {style}]")
            self.live.refresh()
        except Exception:
            pass

    def read_input(self, mode: str = "multiline") -> str:
        """Read user input with IME support.

        - mode="multiline": Multi-line input with Shift+Enter (best IME support, recommended)
        - mode="prompt":    Standard prompt below the UI (simple fallback)
        """
        with self.pause():
            return input("> ").strip()
              


# Export
__all__ = ['ChatDisplay', 'LiveChatDisplay']
