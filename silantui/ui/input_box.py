from typing import Optional, Callable

from rich.console import Group, Console
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
        footer_offset: int = 2,
    ) -> None:
        self.left_label = left_label
        self.tips = tips
        self.footer_offset = max(1, footer_offset)

    # ---------------- Rendering ----------------
    def render(self, status: str):
        # Status line (left-aligned)
        if status == "ready":
            status_text = Text("Ready", style="dim")
        elif status == "typing":
            status_text = Text("Typing...", style="green")
        else:
            try:
                status_text = Text.from_markup(status)
            except Exception:
                status_text = Text(status, style="dim")

        # Bottom row: mode on left, tips on right
        info_line = Table.grid(padding=0, expand=True)
        info_line.add_column(justify="left")
        info_line.add_column(justify="right")
        info_line.add_row(
            status_text,
            Text(self.tips, style="dim")
        )

        return Group(
            Rule(style="yellow", characters="─"),  # Top separator line (full width)
            info_line,
            Rule(style="yellow", characters="─"),  # Bottom separator line (full width)
        )
