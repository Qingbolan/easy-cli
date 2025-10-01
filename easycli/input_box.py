from typing import Optional, Callable

from rich.console import Group
from rich.text import Text
from rich.table import Table
from rich.rule import Rule


class InputBox:
    """Polymorphic footer input component.

    Renders a minimalist footer (status, rule, input, rule, tips) and
    provides multiple input strategies:
      - 'footer': cooked input on the footer line (IME friendly)
      - 'inline': cbreak char-by-char update via callback (less IME friendly)
      - 'prompt': regular prompt below UI
    """

    def __init__(
        self,
        *,
        left_label: str = "",
        tips: str = "Type / for commands",
        placeholder: str = "Type your message...",
        footer_offset: int = 2,
    ) -> None:
        self.left_label = left_label
        self.tips = tips
        self.placeholder = placeholder
        self.footer_offset = max(1, footer_offset)

    # ---------------- Rendering ----------------
    def render(self, status: str, user_input: str = "", input_active: bool = False):
        # Status line
        if status == "ready":
            status_renderable = Text("Ready", style="dim", no_wrap=True, overflow="crop")
        elif status == "typing":
            status_renderable = Text("Typing...", style="green", no_wrap=True, overflow="crop")
        else:
            try:
                status_renderable = Text.from_markup(status)
                status_renderable.no_wrap = True
                status_renderable.overflow = "crop"
            except Exception:
                status_renderable = Text(status, style="dim", no_wrap=True, overflow="crop")

        # Input line
        if input_active:
            # Allow wrapping while active to support multi-line input block
            line = f"> {user_input}" if user_input else "> "
            prompt = Text(line, style="yellow")
        else:
            if user_input:
                prompt = Text(f"> {user_input}", style="yellow", no_wrap=True, overflow="crop")
            else:
                prompt = Text(f"> {self.placeholder}", style="dim", no_wrap=True, overflow="crop")

        # Bottom row: left label + tips
        mode_tips = Table.grid(padding=0, expand=True)
        mode_tips.add_column(justify="left")
        mode_tips.add_column(justify="right")
        left = Text(self.left_label, style="cyan", no_wrap=True, overflow="crop")
        right = Text(self.tips, style="dim", no_wrap=True, overflow="crop")
        mode_tips.add_row(left, right)

        return Group(
            status_renderable,
            Rule(style="dim"),
            prompt,
            Rule(style="dim"),
            mode_tips,
        )

    # ---------------- Input strategies ----------------
    def read(
        self,
        mode: str,
        pause_cm,
        *,
        on_change: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Read input in one of the supported modes.

        Args:
            mode: 'footer' | 'inline' | 'prompt'
            pause_cm: a context manager returned by caller to pause the UI
            on_change: callback used by 'inline' mode to report changes
        """
        if mode == "prompt":
            # Standard prompt below the UI
            try:
                from rich.prompt import Prompt
                return Prompt.ask("").strip()
            except Exception:
                return input("").strip()

        if mode == "footer":
            # IME-friendly cooked input on the footer line
            import sys
            with pause_cm():
                # Move to input row and to after "> "
                sys.stdout.write(f"\x1b[{self.footer_offset}A\r\x1b[2C")
                sys.stdout.flush()
                try:
                    line = input("")
                except EOFError:
                    line = ""
                # Move back to bottom of footer
                sys.stdout.write(f"\x1b[{self.footer_offset}B\r")
                sys.stdout.flush()
            return (line or "").strip()

        # inline mode (cbreak)
        try:
            import sys
            import termios
            import tty
            import select

            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                buf = ""
                if on_change:
                    on_change(buf)
                while True:
                    r, _, _ = select.select([sys.stdin], [], [], 0.1)
                    if not r:
                        continue
                    ch = sys.stdin.read(1)
                    if ch in ("\r", "\n"):
                        break
                    if ch in ("\x08", "\x7f"):
                        buf = buf[:-1]
                    elif ch == "\x03":
                        raise KeyboardInterrupt
                    elif ch == "\x1b":
                        _ = select.select([sys.stdin], [], [], 0.01)[0]
                        if _:
                            sys.stdin.read(2)
                    elif ch >= " ":
                        buf += ch
                    if on_change:
                        on_change(buf)
                if on_change:
                    on_change(buf)
                return buf.strip()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except Exception:
            # Fallback to prompt
            try:
                from rich.prompt import Prompt
                return Prompt.ask("").strip()
            except Exception:
                return input("").strip()
