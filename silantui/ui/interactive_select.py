"""Interactive selection components with modern animations.

Provides keyboard-navigable selection menus with loading animations
matching the style of ModernLogger.
"""

import sys
import tty
import termios
from typing import List, Dict, Any, Optional, Callable
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.box import ROUNDED


class InteractiveSelect:
    """Interactive selection menu with keyboard navigation and animations.

    Features:
    - Arrow key navigation (↑/↓)
    - Enter to select
    - Visual highlight of current selection
    - Loading animation on selection
    - Modern gradient styling
    """

    # Gradient colors matching ModernLogger
    GRADIENT_START = "#41B883"
    GRADIENT_END = "#6574CD"

    def __init__(
        self,
        choices: List[Dict[str, Any]],
        title: str = "Select an option",
        columns: List[str] = None,
        value_key: str = "value",
        console: Optional[Console] = None,
        on_select: Optional[Callable] = None,
    ):
        """Initialize interactive select.

        Args:
            choices: List of choice dictionaries
            title: Menu title
            columns: Columns to display (None = all keys)
            value_key: Key to return as selected value
            console: Rich console instance
            on_select: Optional callback on selection
        """
        self.choices = choices
        self.title = title
        self.columns = columns or (list(choices[0].keys()) if choices else [])
        self.value_key = value_key
        self.console = console or Console()
        self.on_select = on_select

        self.current_index = 0
        self.selected_value = None

    def _create_gradient_text(self, text: str) -> Text:
        """Create gradient text effect."""
        import re

        def hex_to_rgb(hex_code: str):
            hex_code = hex_code.strip().lstrip('#')
            return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

        sr, sg, sb = hex_to_rgb(self.GRADIENT_START)
        er, eg, eb = hex_to_rgb(self.GRADIENT_END)
        n = max(1, len(text))

        out = Text()
        for i, ch in enumerate(text):
            t = i / (n - 1) if n > 1 else 0.0
            r = int(sr + (er - sr) * t)
            g = int(sg + (eg - sg) * t)
            b = int(sb + (eb - sb) * t)
            out.append(ch, style=f"#{r:02X}{g:02X}{b:02X}")
        return out

    def _render_menu(self) -> Panel:
        """Render the selection menu."""
        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=None,
            padding=(0, 1),
            expand=False
        )

        # Add columns
        table.add_column("", style="dim", width=2)  # Indicator column
        for col in self.columns:
            table.add_column(col.title(), style="white")

        # Add rows
        for idx, choice in enumerate(self.choices):
            indicator = "▶" if idx == self.current_index else " "
            indicator_style = "bold green" if idx == self.current_index else "dim"

            row_values = [Text(indicator, style=indicator_style)]

            for col in self.columns:
                value = str(choice.get(col, ""))
                if idx == self.current_index:
                    row_values.append(Text(value, style="bold cyan"))
                else:
                    row_values.append(Text(value, style="white"))

            table.add_row(*row_values)

        # Create panel with gradient title
        gradient_title = self._create_gradient_text(f" {self.title} ")

        panel = Panel(
            table,
            title=gradient_title,
            subtitle="[dim]↑/↓: Navigate | Enter: Select | q: Quit[/dim]",
            border_style=self.GRADIENT_START,
            box=ROUNDED,
            padding=(1, 2)
        )

        return panel

    def _get_key(self):
        """Get a single keypress from user."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)

            # Handle arrow keys (escape sequences)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A':
                        return 'UP'
                    elif ch3 == 'B':
                        return 'DOWN'

            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _show_loading(self, message: str = "Loading"):
        """Show loading animation."""
        with Progress(
            SpinnerColumn(spinner_name="dots", style=self.GRADIENT_START),
            TextColumn(f"[bold {self.GRADIENT_START}]{message}...[/bold {self.GRADIENT_START}]"),
            console=self.console,
            transient=True
        ) as progress:
            progress.add_task("loading", total=None)
            import time
            time.sleep(0.5)  # Simulated loading time

    def prompt(self) -> Any:
        """Display menu and get user selection.

        Returns:
            Selected value based on value_key
        """
        import os

        while True:
            # Clear screen and render menu
            os.system('clear' if os.name == 'posix' else 'cls')
            self.console.print(self._render_menu())

            # Get user input
            key = self._get_key()

            if key == 'UP':
                self.current_index = max(0, self.current_index - 1)

            elif key == 'DOWN':
                self.current_index = min(len(self.choices) - 1, self.current_index + 1)

            elif key == '\r' or key == '\n':  # Enter
                # Clear screen
                os.system('clear' if os.name == 'posix' else 'cls')

                # Show loading animation
                self._show_loading("Processing selection")

                # Get selected value
                selected_choice = self.choices[self.current_index]
                self.selected_value = selected_choice.get(self.value_key)

                # Call callback if provided
                if self.on_select:
                    self.on_select(self.selected_value, selected_choice)

                # Show confirmation
                self.console.print()
                self.console.print(
                    f"[bold green]✓[/bold green] Selected: "
                    f"[bold cyan]{self.selected_value}[/bold cyan]"
                )
                self.console.print()

                return self.selected_value

            elif key == 'q' or key == 'Q':  # Quit
                os.system('clear' if os.name == 'posix' else 'cls')
                self.console.print("\n[yellow]Selection cancelled.[/yellow]\n")
                return None


class QuickSelect:
    """Quick selection helper for simple use cases."""

    @staticmethod
    def from_list(
        items: List[str],
        title: str = "Select an option",
        console: Optional[Console] = None
    ) -> Optional[str]:
        """Quick select from a list of strings.

        Args:
            items: List of string options
            title: Menu title
            console: Console instance

        Returns:
            Selected string or None
        """
        choices = [{"option": item, "value": item} for item in items]
        selector = InteractiveSelect(
            choices=choices,
            title=title,
            columns=["option"],
            value_key="value",
            console=console
        )
        return selector.prompt()

    @staticmethod
    def from_dict(
        items: Dict[str, str],
        title: str = "Select an option",
        console: Optional[Console] = None
    ) -> Optional[str]:
        """Quick select from a dictionary.

        Args:
            items: Dict of {label: value}
            title: Menu title
            console: Console instance

        Returns:
            Selected value or None
        """
        choices = [
            {"label": label, "value": value}
            for label, value in items.items()
        ]
        selector = InteractiveSelect(
            choices=choices,
            title=title,
            columns=["label"],
            value_key="value",
            console=console
        )
        return selector.prompt()


# Example usage
if __name__ == "__main__":
    console = Console()

    # Example 1: Table select with multiple columns
    models = [
        {"name": "gpt-4-turbo-preview", "provider": "OpenAI", "cost": "$$"},
        {"name": "gpt-4", "provider": "OpenAI", "cost": "$$$"},
        {"name": "claude-3-opus", "provider": "Anthropic", "cost": "$$$"},
        {"name": "claude-3-sonnet", "provider": "Anthropic", "cost": "$$"},
    ]

    selector = InteractiveSelect(
        choices=models,
        title="Select AI Model",
        columns=["name", "provider", "cost"],
        value_key="name",
        console=console
    )

    selected = selector.prompt()
    print(f"You selected: {selected}")

    # Example 2: Quick select from list
    # providers = ["OpenAI", "Anthropic", "Custom"]
    # selected = QuickSelect.from_list(providers, "Select Provider", console)
    # print(f"Provider: {selected}")
