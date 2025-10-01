"""
EasyCli - Universal CLI UI Framework
Universal command-line interface framework focused on beautiful and easy-to-use UI components
"""

from typing import Optional, List, Dict, Any, Callable
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.box import ROUNDED
import time


class CLIApplication:
    """
    Universal CLI Application Base Class

    Provides:
    - Fixed layout management
    - Input/output separation
    - Component-based UI
    - Command system

    Example:
        >>> class MyApp(CLIApplication):
        >>>     def setup(self):
        >>>         self.add_command("hello", self.hello_cmd)
        >>>
        >>>     def hello_cmd(self, args):
        >>>         self.show_message("Hello, World!")
    """
    
    def __init__(
        self,
        title: str = "CLI Application",
        use_layout: bool = True,
        console: Optional[Console] = None
    ):
        self.console = console or Console()
        self.title = title
        self.use_layout = use_layout
        
        # Layout components
        self.layout = None
        self.live = None

        # Application state
        self.running = False
        self.content_buffer: List[Any] = []
        self.status_message = "Ready"

        # Command system
        self.commands: Dict[str, Callable] = {}
        
        if use_layout:
            self._setup_layout()
    
    def _setup_layout(self):
        """Setup three-section layout"""
        self.layout = Layout()
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="content", ratio=1),
            Layout(name="footer", size=3),
        )
        
        self._update_header()
        self._update_footer()
        self._update_content()
    
    def _update_header(self):
        """Update header bar"""
        header = Panel(
            f"[bold cyan]{self.title}[/bold cyan]",
            style="cyan",
            box=ROUNDED
        )
        self.layout["header"].update(header)
    
    def _update_footer(self):
        """Update footer status bar"""
        footer = Panel(
            f"[yellow]{self.status_message}[/yellow]",
            style="yellow",
            box=ROUNDED
        )
        self.layout["footer"].update(footer)
    
    def _update_content(self):
        """Update content area"""
        from rich.console import Group

        if not self.content_buffer:
            content = Panel(
                "[dim]No content to display[/dim]",
                style="dim"
            )
        else:
            # Display recent content
            recent = self.content_buffer[-20:]  # Last 20 items
            content = Group(*recent)
        
        self.layout["content"].update(content)
    
    def add_content(self, content: Any):
        """Add content to display area"""
        self.content_buffer.append(content)
        if self.use_layout and self.live:
            self._update_content()
    
    def show_message(self, message: str, style: str = "white"):
        """Display message"""
        text = Text(message, style=style)
        panel = Panel(text, border_style=style, box=ROUNDED)
        self.add_content(panel)
    
    def show_info(self, message: str):
        """Display information"""
        self.show_message(f"ℹ️  {message}", "blue")
    
    def show_success(self, message: str):
        """Display success"""
        self.show_message(f"✅ {message}", "green")
    
    def show_error(self, message: str):
        """Display error"""
        self.show_message(f"❌ {message}", "red")
    
    def show_warning(self, message: str):
        """Display warning"""
        self.show_message(f"⚠️  {message}", "yellow")
    
    def set_status(self, message: str):
        """Set status bar message"""
        self.status_message = message
        if self.use_layout and self.live:
            self._update_footer()
    
    def clear_content(self):
        """Clear content"""
        self.content_buffer = []
        if self.use_layout and self.live:
            self._update_content()
    
    def add_command(self, name: str, handler: Callable):
        """Register command"""
        self.commands[name] = handler
    
    def execute_command(self, command_line: str):
        """Execute command"""
        parts = command_line.strip().split(maxsplit=1)
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd in self.commands:
            try:
                self.commands[cmd](args)
            except Exception as e:
                self.show_error(f"Command error: {e}")
        else:
            self.show_error(f"Unknown command: {cmd}")
    
    def start(self):
        """Start application"""
        if self.use_layout:
            self.live = Live(
                self.layout,
                console=self.console,
                refresh_per_second=10,
                screen=False
            )
            self.live.start()
        
        self.running = True
        self.setup()
    
    def stop(self):
        """Stop application"""
        self.running = False
        if self.live:
            self.live.stop()
    
    def setup(self):
        """
        Override in subclass: initialization setup

        Here you can:
        - Register commands
        - Initialize data
        - Configure application
        """
        pass
    
    def run(self):
        """
        Run application main loop

        Subclass can override this method to implement custom logic
        """
        from rich.prompt import Prompt
        
        try:
            self.start()

            while self.running:
                # Stop Live to get input
                if self.live:
                    self.live.stop()

                # Get user input
                user_input = Prompt.ask(
                    "\n[bold yellow]›[/bold yellow]"
                ).strip()

                # Restart Live
                if self.live:
                    self.live.start()

                if not user_input:
                    continue

                # Process input
                self.handle_input(user_input)
        
        except KeyboardInterrupt:
            self.show_warning("Interrupted by user")
        finally:
            self.cleanup()
    
    def handle_input(self, user_input: str):
        """
        Handle user input

        Subclass can override this method
        """
        if user_input.startswith('/'):
            # Command
            self.execute_command(user_input[1:])
        else:
            # Regular input
            self.process_input(user_input)
    
    def process_input(self, user_input: str):
        """
        Process regular input

        Subclass overrides this method to implement specific logic
        """
        self.show_message(f"You said: {user_input}")
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop()


# Export
__all__ = ['CLIApplication']
