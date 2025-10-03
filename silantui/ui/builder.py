"""
Textual-based UI Builder - Modern replacement for Rich-based builder

Provides fluent API for building TUI components with Textual
"""

from typing import Optional, List, Dict, Callable, Any
from dataclasses import dataclass, field

from textual.app import App, ComposeResult
from textual.widgets import (
    Static, Label, Button, DataTable, Input,
    Select, SelectionList, OptionList, Tree, ListView, ListItem
)
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.screen import Screen
from textual.binding import Binding
from rich.text import Text
from rich.markdown import Markdown
from rich.panel import Panel as RichPanel
from rich.table import Table as RichTable


# ==================== Textual Widgets ====================

class PanelWidget(Static):
    """A panel widget with title and content"""

    DEFAULT_CSS = """
    PanelWidget {
        border: solid;
        padding: 1;
        margin: 1;
    }
    """

    def __init__(self, title: str, content: Any, border_style: str = "cyan", **kwargs):
        super().__init__(**kwargs)
        self.panel_title = title
        self.panel_content = content
        self.border_style = border_style

    def compose(self) -> ComposeResult:
        """Render panel content"""
        if self.panel_title:
            yield Label(f"[bold]{self.panel_title}[/bold]")

        if isinstance(self.panel_content, str):
            yield Static(Text(self.panel_content))
        else:
            yield Static(self.panel_content)


class TableWidget(DataTable):
    """Enhanced DataTable widget"""

    DEFAULT_CSS = """
    TableWidget {
        border: solid;
        height: auto;
    }
    """

    def __init__(self, title: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.table_title = title


class MenuWidget(OptionList):
    """Menu selection widget"""

    DEFAULT_CSS = """
    MenuWidget {
        border: solid cyan;
        height: auto;
        max-height: 20;
    }
    """

    def __init__(self, title: str, **kwargs):
        super().__init__(**kwargs)
        self.menu_title = title


# ==================== Builder Classes ====================

@dataclass
class UITheme:
    """Theme configuration for Textual UI"""
    primary: str = "cyan"
    secondary: str = "magenta"
    success: str = "green"
    warning: str = "yellow"
    error: str = "red"
    info: str = "blue"
    background: str = "$background"
    surface: str = "$surface"


class PanelBuilder:
    """Fluent builder for panel widgets"""

    def __init__(self, title: str, content: Any):
        self.title = title
        self.content = content
        self._border_style = "cyan"
        self._padding = 1
        self._classes = []

    def border(self, style: str):
        """Set border style"""
        self._border_style = style
        return self

    def padding(self, padding: int):
        """Set padding"""
        self._padding = padding
        return self

    def style(self, css_class: str):
        """Add CSS class"""
        self._classes.append(css_class)
        return self

    def build(self) -> PanelWidget:
        """Build the panel widget"""
        widget = PanelWidget(
            self.title,
            self.content,
            border_style=self._border_style,
            classes=" ".join(self._classes)
        )
        return widget


class TableBuilder:
    """Fluent builder for table widgets"""

    def __init__(self, title: Optional[str] = None):
        self.title = title
        self._columns: List[tuple[str, Dict]] = []
        self._rows: List[List[str]] = []
        self._show_header = True
        self._border_style = "cyan"

    def add_column(self, name: str, **kwargs) -> 'TableBuilder':
        """Add a column"""
        self._columns.append((name, kwargs))
        return self

    def add_row(self, *cells) -> 'TableBuilder':
        """Add a row"""
        self._rows.append(list(cells))
        return self

    def header(self, show: bool = True) -> 'TableBuilder':
        """Show/hide header"""
        self._show_header = show
        return self

    def border(self, style: str) -> 'TableBuilder':
        """Set border style"""
        self._border_style = style
        return self

    def build(self) -> TableWidget:
        """Build the table widget"""
        table = TableWidget(title=self.title)

        # Add columns
        for col_name, col_opts in self._columns:
            table.add_column(col_name, **col_opts)

        # Add rows
        for row in self._rows:
            table.add_row(*row)

        return table

    def show(self, app: Optional[App] = None):
        """Show the table (for compatibility)"""
        # For now, just build and return
        # In a real app, would mount to current screen
        return self.build()


class MenuBuilder:
    """Fluent builder for menu widgets"""

    def __init__(self, title: str):
        self.title = title
        self._items: List[tuple[str, str, str]] = []

    def add_item(self, key: str, label: str, description: str = "") -> 'MenuBuilder':
        """Add menu item"""
        self._items.append((key, label, description))
        return self

    def add_separator(self) -> 'MenuBuilder':
        """Add separator (visual only)"""
        self._items.append(("---", "---", ""))
        return self

    def build(self) -> MenuWidget:
        """Build the menu widget"""
        menu = MenuWidget(title=self.title)

        for key, label, desc in self._items:
            if key == "---":
                continue  # Skip separators in Textual OptionList

            display = f"{key}. {label}"
            if desc:
                display += f" - {desc}"
            menu.add_option((display, key))

        return menu

    def show(self) -> Optional[str]:
        """Show menu and return selection (simplified for now)"""
        # In real implementation, would run an app and return selection
        return None


class FormBuilder:
    """Fluent builder for form inputs"""

    def __init__(self, title: str):
        self.title = title
        self._fields: List[Dict] = []

    def add_text(self, name: str, label: str, placeholder: str = "", required: bool = False):
        """Add text input field"""
        self._fields.append({
            "type": "text",
            "name": name,
            "label": label,
            "placeholder": placeholder,
            "required": required
        })
        return self

    def add_password(self, name: str, label: str, required: bool = False):
        """Add password input field"""
        self._fields.append({
            "type": "password",
            "name": name,
            "label": label,
            "required": required
        })
        return self

    def add_select(self, name: str, label: str, options: List[tuple[str, str]]):
        """Add select/dropdown field"""
        self._fields.append({
            "type": "select",
            "name": name,
            "label": label,
            "options": options
        })
        return self

    def build(self) -> Container:
        """Build form container with all fields"""
        container = Vertical(classes="form-container")

        for field in self._fields:
            # Add label
            label_text = field["label"]
            if field.get("required"):
                label_text += " *"

            # Add appropriate input widget
            if field["type"] == "text":
                widget = Input(
                    placeholder=field.get("placeholder", ""),
                    id=field["name"]
                )
            elif field["type"] == "password":
                widget = Input(
                    password=True,
                    id=field["name"]
                )
            elif field["type"] == "select":
                widget = Select(
                    options=[(label, val) for val, label in field["options"]],
                    id=field["name"]
                )

            # In real implementation, would mount label and widget

        return container


class LayoutBuilder:
    """Builder for complex layouts"""

    def __init__(self):
        self._sections: List[Dict] = []

    def add_row(self, *widgets, ratio: int = 1):
        """Add a horizontal row"""
        self._sections.append({
            "type": "row",
            "widgets": widgets,
            "ratio": ratio
        })
        return self

    def add_column(self, *widgets, ratio: int = 1):
        """Add a vertical column"""
        self._sections.append({
            "type": "column",
            "widgets": widgets,
            "ratio": ratio
        })
        return self

    def build(self) -> Container:
        """Build the layout"""
        container = Vertical()

        for section in self._sections:
            if section["type"] == "row":
                row = Horizontal()
                # In real implementation, would mount widgets
            elif section["type"] == "column":
                col = Vertical()
                # In real implementation, would mount widgets

        return container


class UIBuilder:
    """
    Main UI Builder - Textual version

    Provides fluent API for creating TUI components
    """

    def __init__(self, theme: Optional[UITheme] = None):
        self.theme = theme or UITheme()
        self.app: Optional[App] = None

    def panel(self, title: str, content: Any = "") -> PanelBuilder:
        """Create a panel builder"""
        return PanelBuilder(title, content)

    def table(self, title: Optional[str] = None) -> TableBuilder:
        """Create a table builder"""
        return TableBuilder(title)

    def menu(self, title: str) -> MenuBuilder:
        """Create a menu builder"""
        return MenuBuilder(title)

    def form(self, title: str) -> FormBuilder:
        """Create a form builder"""
        return FormBuilder(title)

    def layout(self) -> LayoutBuilder:
        """Create a layout builder"""
        return LayoutBuilder()


# ==================== Quick UI Functions ====================

class QuickUI:
    """Quick utility functions for common UI tasks"""

    @staticmethod
    def confirm(question: str, default: bool = False) -> bool:
        """Show confirmation dialog"""
        # Simplified - in real implementation would use Textual modal
        from rich.prompt import Confirm
        return Confirm.ask(question, default=default)

    @staticmethod
    def prompt(question: str, default: str = "") -> str:
        """Prompt for text input"""
        # Simplified - in real implementation would use Textual modal
        from rich.prompt import Prompt
        return Prompt.ask(question, default=default)

    @staticmethod
    def select(question: str, choices: List[str]) -> str:
        """Select from list"""
        # Simplified - in real implementation would use Textual selection
        from rich.prompt import Prompt
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice}")
        idx = int(Prompt.ask(question)) - 1
        return choices[idx] if 0 <= idx < len(choices) else choices[0]


__all__ = [
    "UIBuilder",
    "UITheme",
    "QuickUI",
    "PanelBuilder",
    "TableBuilder",
    "MenuBuilder",
    "FormBuilder",
    "LayoutBuilder",
    # Widgets
    "PanelWidget",
    "TableWidget",
    "MenuWidget",
]
