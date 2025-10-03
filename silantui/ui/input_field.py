"""
Interactive Input Field Component - Integrated input within Live display

This component provides a truly integrated input field that works within
Rich Live layouts without requiring pause/stop cycles.
"""

import sys
import tty
import termios
from typing import Optional, Callable
from dataclasses import dataclass

from rich.console import Console, RenderableType, Group as RichGroup
from rich.text import Text
from rich.panel import Panel
from rich.box import ROUNDED
from rich.rule import Rule


@dataclass
class InputState:
    """State of the input field"""
    buffer: str = ""
    cursor_pos: int = 0
    prompt: str = "> "
    placeholder: str = "Type your message..."
    max_length: int = 1000


class InputField:
    """
    Interactive input field that works within Rich Live layouts

    Features:
    - Real-time character input without blocking Live
    - Cursor positioning and editing
    - Backspace, delete, arrow keys
    - IME support for CJK input
    - Visual feedback within layout
    """

    def __init__(
        self,
        console: Optional[Console] = None,
        prompt: str = "> ",
        placeholder: str = "Type your message...",
        on_submit: Optional[Callable[[str], None]] = None,
        on_change: Optional[Callable[[str], None]] = None,
    ):
        self.console = console or Console()
        self.state = InputState(prompt=prompt, placeholder=placeholder)
        self.on_submit = on_submit
        self.on_change = on_change
        self._active = False

    def render(self, status: str = "ready") -> RenderableType:
        """Render the input field for display in a layout"""
        # Build the display text
        if self.state.buffer:
            # Show current input with cursor
            display = Text()
            display.append(self.state.prompt, style="bold yellow")

            # Text before cursor
            if self.state.cursor_pos > 0:
                display.append(self.state.buffer[:self.state.cursor_pos])

            # Cursor
            if self.state.cursor_pos < len(self.state.buffer):
                display.append(self.state.buffer[self.state.cursor_pos], style="reverse")
                display.append(self.state.buffer[self.state.cursor_pos + 1:])
            else:
                display.append("▌", style="bold cyan")
        else:
            # Show placeholder
            display = Text()
            display.append(self.state.prompt, style="bold yellow")
            display.append(self.state.placeholder, style="dim")

        # Add status indicator
        if status != "ready":
            display.append(f"  [{status}]", style="dim cyan")

        # Use full-width lines instead of Panel
        return RichGroup(
            Rule(style="yellow", characters="─"),
            display,
            Rule(style="yellow", characters="─"),
        )

    def clear(self):
        """Clear the input buffer"""
        self.state.buffer = ""
        self.state.cursor_pos = 0

    def insert(self, char: str):
        """Insert a character at cursor position"""
        if len(self.state.buffer) >= self.state.max_length:
            return

        self.state.buffer = (
            self.state.buffer[:self.state.cursor_pos] +
            char +
            self.state.buffer[self.state.cursor_pos:]
        )
        self.state.cursor_pos += len(char)

        if self.on_change:
            self.on_change(self.state.buffer)

    def backspace(self):
        """Delete character before cursor"""
        if self.state.cursor_pos > 0:
            self.state.buffer = (
                self.state.buffer[:self.state.cursor_pos - 1] +
                self.state.buffer[self.state.cursor_pos:]
            )
            self.state.cursor_pos -= 1

            if self.on_change:
                self.on_change(self.state.buffer)

    def delete(self):
        """Delete character at cursor"""
        if self.state.cursor_pos < len(self.state.buffer):
            self.state.buffer = (
                self.state.buffer[:self.state.cursor_pos] +
                self.state.buffer[self.state.cursor_pos + 1:]
            )

            if self.on_change:
                self.on_change(self.state.buffer)

    def move_cursor_left(self):
        """Move cursor left"""
        if self.state.cursor_pos > 0:
            self.state.cursor_pos -= 1

    def move_cursor_right(self):
        """Move cursor right"""
        if self.state.cursor_pos < len(self.state.buffer):
            self.state.cursor_pos += 1

    def move_cursor_home(self):
        """Move cursor to start"""
        self.state.cursor_pos = 0

    def move_cursor_end(self):
        """Move cursor to end"""
        self.state.cursor_pos = len(self.state.buffer)

    def get_value(self) -> str:
        """Get current input value"""
        return self.state.buffer

    def read_char(self) -> Optional[str]:
        """
        Read a single character from stdin (Unix only)
        Returns None on timeout or error
        """
        if not sys.stdin.isatty():
            return None

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            char = sys.stdin.read(1)
            return char
        except:
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def process_key(self, key: str) -> bool:
        """
        Process a key press
        Returns True if Enter was pressed (submit)
        """
        if key == '\r' or key == '\n':  # Enter
            return True
        elif key == '\x7f' or key == '\b':  # Backspace
            self.backspace()
        elif key == '\x1b':  # Escape sequence (arrow keys, etc)
            # Try to read the rest of the sequence
            next1 = self.read_char()
            if next1 == '[':
                next2 = self.read_char()
                if next2 == 'D':  # Left arrow
                    self.move_cursor_left()
                elif next2 == 'C':  # Right arrow
                    self.move_cursor_right()
                elif next2 == 'H':  # Home
                    self.move_cursor_home()
                elif next2 == 'F':  # End
                    self.move_cursor_end()
                elif next2 == '3':  # Delete
                    tilde = self.read_char()
                    if tilde == '~':
                        self.delete()
        elif key == '\x01':  # Ctrl+A
            self.move_cursor_home()
        elif key == '\x05':  # Ctrl+E
            self.move_cursor_end()
        elif key == '\x03':  # Ctrl+C
            raise KeyboardInterrupt
        elif key == '\x04':  # Ctrl+D (EOF)
            raise EOFError
        elif ord(key) >= 32:  # Printable characters
            self.insert(key)

        return False


__all__ = ["InputField", "InputState"]
