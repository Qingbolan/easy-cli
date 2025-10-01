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
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.messages: List[dict] = []
        self.current_streaming = ""
        self.layout = None
        self.live = None
        self._setup_layout()
    
    def _setup_layout(self):
        """Setup three-section layout"""
        self.layout = Layout()
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="chat", ratio=1),
            Layout(name="footer", size=5),
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
    
    def _update_footer(self, status: str = "ready"):
        """Update footer status bar"""
        if status == "ready":
            content = (
                "💬 [bold yellow]Ready[/bold yellow] - Type message to start conversation\n"
                "[dim]Tip: Type /help for commands | /exit to quit[/dim]"
            )
            style = "yellow"
        elif status == "typing":
            content = (
                "⌨️  [bold green]LLM is typing...[/bold green]\n"
                "[dim]Please wait for response...[/dim]"
            )
            style = "green"
        else:
            content = status
            style = "white"
        
        footer = Panel(content, style=style, box=ROUNDED)
        self.layout["footer"].update(footer)
    
    def _update_chat(self):
        """Update chat area"""
        if not self.messages and not self.current_streaming:
            # Welcome message
            welcome = Panel(
                Padding(
                    Text.from_markup(
                        "[bold cyan]👋 Welcome to EasyCli![/bold cyan]\n\n"
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

        rendered = []

        # Historical messages
        for msg in self.messages[-10:]:  # Show only last 10
            panel = self._render_message(msg["role"], msg["content"])
            rendered.append(panel)
            rendered.append("")  # Empty line
        
        # Current streaming message
        if self.current_streaming:
            panel = self._render_message("assistant", self.current_streaming, streaming=True)
            rendered.append(panel)

        self.layout["chat"].update(Group(*rendered))

    def _render_message(self, role: str, content: str, streaming: bool = False) -> Panel:
        """Render message bubble"""
        if role == "user":
            # User message
            return Panel(
                Text(content, style="white"),
                title="[bold blue]👤 You[/bold blue]",
                border_style="blue",
                box=ROUNDED
            )
        else:
            # AI message
            if streaming:
                # Streaming: plain text
                message = Text(content + "▌", style="white")  # Add cursor
                title = "[bold green]🤖 LLM[/bold green] [blink]●[/blink]"
            else:
                # Complete: Markdown
                try:
                    message = Markdown(content)
                except Exception:
                    message = Text(content, style="white")
                title = "[bold green]🤖 LLM[/bold green]"
            
            return Panel(
                message,
                title=title,
                border_style="green",
                box=ROUNDED
            )
    
    def start(self):
        """Start real-time display"""
        self.live = Live(
            self.layout,
            console=self.console,
            refresh_per_second=10,
            screen=False
        )
        self.live.start()
    
    def stop(self):
        """Stop real-time display"""
        if self.live:
            self.live.stop()
    
    def add_user_message(self, content: str):
        """Add user message"""
        self.messages.append({"role": "user", "content": content})
        self._update_chat()
        self.live.refresh()
    
    def start_assistant_message(self):
        """Start AI response"""
        self.current_streaming = ""
        self._update_footer("typing")
        self._update_chat()
        self.live.refresh()
    
    def append_streaming(self, chunk: str):
        """Append streaming content"""
        self.current_streaming += chunk
        self._update_chat()
        # live.refresh() will be called automatically

    def finish_assistant_message(self):
        """Finish AI response"""
        if self.current_streaming:
            self.messages.append({"role": "assistant", "content": self.current_streaming})
            self.current_streaming = ""
        self._update_footer("ready")
        self._update_chat()
        self.live.refresh()
    
    def clear_messages(self):
        """Clear messages"""
        self.messages = []
        self.current_streaming = ""
        self._update_chat()
        self.live.refresh()
    
    def show_error(self, message: str):
        """Display error"""
        self._update_footer(f"❌ [bold red]{message}[/bold red]")
        self.live.refresh()
    
    def show_success(self, message: str):
        """Display success"""
        self._update_footer(f"✅ [bold green]{message}[/bold green]")
        self.live.refresh()


# Export
__all__ = ['ChatDisplay', 'LiveChatDisplay']
