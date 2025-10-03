"""Generic configuration input components for building interactive config UIs.

This module provides reusable components for creating rich terminal-based
configuration interfaces with automatic saving and loading capabilities.
"""

from typing import Optional, List, Callable, Dict, Any, Union
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm

try:
    from ..core.config import ConfigManager, get_config
except ImportError:
    ConfigManager = None
    get_config = None


class InputField:
    """Base class for configuration input fields."""

    def __init__(
        self,
        key: str,
        label: str,
        default: Any = None,
        validator: Optional[Callable[[Any], bool]] = None,
        required: bool = False,
    ):
        """Initialize input field.

        Args:
            key: Configuration key path (dot notation)
            label: Display label for the field
            default: Default value
            validator: Optional validation function
            required: Whether the field is required
        """
        self.key = key
        self.label = label
        self.default = default
        self.validator = validator
        self.required = required
        self.value: Any = None


class TextInput(InputField):
    """Text input field."""

    def __init__(
        self,
        key: str,
        label: str,
        default: str = "",
        password: bool = False,
        placeholder: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(key, label, default, **kwargs)
        self.password = password
        self.placeholder = placeholder

    def prompt(self, console: Console, current_value: Optional[str] = None) -> str:
        """Prompt for text input."""
        prompt_text = self.label
        if self.placeholder:
            prompt_text += f" ({self.placeholder})"

        value = Prompt.ask(
            f"[cyan]{prompt_text}[/cyan]",
            default=current_value or self.default,
            password=self.password,
        )

        if self.validator and not self.validator(value):
            console.print("[red]Invalid input. Please try again.[/red]")
            return self.prompt(console, current_value)

        self.value = value
        return value


class SelectInput(InputField):
    """Select input field with multiple choices."""

    def __init__(
        self,
        key: str,
        label: str,
        choices: List[str],
        default: Optional[str] = None,
        show_index: bool = True,
        **kwargs,
    ):
        super().__init__(key, label, default, **kwargs)
        self.choices = choices
        self.show_index = show_index

    def prompt(self, console: Console, current_value: Optional[str] = None) -> str:
        """Prompt for selection."""
        console.print(f"\n[bold cyan]{self.label}:[/bold cyan]")

        # Create choices table
        table = Table(show_header=False, box=None, padding=(0, 2))
        if self.show_index:
            table.add_column("No.", style="dim", width=4)
        table.add_column("Choice", style="cyan")

        for idx, choice in enumerate(self.choices, 1):
            if self.show_index:
                table.add_row(str(idx), choice)
            else:
                table.add_row(choice)

        console.print(table)

        # Get selection
        while True:
            if self.show_index:
                choice = Prompt.ask(
                    "\n[cyan]Select number[/cyan]",
                    default="1" if self.choices else "",
                )
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(self.choices):
                        self.value = self.choices[idx]
                        console.print(f"[green]✓[/green] Selected: [bold]{self.value}[/bold]")
                        return self.value
                    else:
                        console.print("[red]Invalid selection. Please try again.[/red]")
                except ValueError:
                    console.print("[red]Please enter a valid number.[/red]")
            else:
                choice = Prompt.ask("\n[cyan]Enter choice[/cyan]", default=current_value or self.default)
                if choice in self.choices:
                    self.value = choice
                    return choice
                else:
                    console.print("[red]Invalid choice. Please try again.[/red]")


class TableSelectInput(SelectInput):
    """Enhanced select input with table display and custom columns."""

    def __init__(
        self,
        key: str,
        label: str,
        choices: List[Dict[str, str]],
        columns: List[str],
        value_key: str = "value",
        default: Optional[str] = None,
        **kwargs,
    ):
        """Initialize table select input.

        Args:
            key: Configuration key
            label: Display label
            choices: List of dicts with choice data
            columns: Column names to display
            value_key: Key in choice dict to use as value
            default: Default value
        """
        choice_values = [choice[value_key] for choice in choices]
        super().__init__(key, label, choice_values, default, **kwargs)
        self.choice_data = choices
        self.columns = columns
        self.value_key = value_key

    def prompt(self, console: Console, current_value: Optional[str] = None) -> str:
        """Prompt with table display."""
        console.print(f"\n[bold cyan]{self.label}:[/bold cyan]")

        # Create table
        table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 2))
        table.add_column("No.", style="dim", width=4)
        for col in self.columns:
            table.add_column(col, style="cyan")

        # Add rows
        for idx, choice in enumerate(self.choice_data, 1):
            row = [str(idx)] + [str(choice.get(col, "")) for col in self.columns]
            table.add_row(*row)

        console.print(table)

        # Get selection
        while True:
            choice = Prompt.ask(
                "\n[cyan]Select number[/cyan]",
                default="1" if self.choices else "",
            )
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.choices):
                    self.value = self.choices[idx]
                    console.print(f"[green]✓[/green] Selected: [bold]{self.value}[/bold]")
                    return self.value
                else:
                    console.print("[red]Invalid selection. Please try again.[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number.[/red]")


class ConfigForm:
    """Generic configuration form with multiple input fields."""

    def __init__(
        self,
        title: str = "Configuration",
        description: Optional[str] = None,
        console: Optional[Console] = None,
        config_manager: Optional["ConfigManager"] = None,
        auto_load: bool = True,
        auto_save: bool = True,
    ):
        """Initialize configuration form.

        Args:
            title: Form title
            description: Form description
            console: Rich console instance
            config_manager: ConfigManager instance
            auto_load: Automatically load values from config
            auto_save: Automatically save on updates
        """
        self.title = title
        self.description = description
        self.console = console or Console()
        self.auto_load = auto_load
        self.auto_save = auto_save

        # Config manager
        if config_manager is not None:
            self.config = config_manager
        elif get_config is not None:
            self.config = get_config()
        else:
            self.config = None

        self.fields: List[InputField] = []
        self.values: Dict[str, Any] = {}

    def add_field(self, field: InputField) -> "ConfigForm":
        """Add a field to the form.

        Args:
            field: InputField instance

        Returns:
            Self for chaining
        """
        self.fields.append(field)

        # Auto-load value from config if available
        if self.auto_load and self.config:
            value = self.config.get(field.key)
            if value is not None:
                field.value = value
                self.values[field.key] = value

        return self

    def add_text(
        self,
        key: str,
        label: str,
        default: str = "",
        password: bool = False,
        **kwargs,
    ) -> "ConfigForm":
        """Add a text input field.

        Args:
            key: Config key path
            label: Display label
            default: Default value
            password: Password mode
            **kwargs: Additional TextInput arguments

        Returns:
            Self for chaining
        """
        field = TextInput(key, label, default, password, **kwargs)
        return self.add_field(field)

    def add_select(
        self,
        key: str,
        label: str,
        choices: List[str],
        default: Optional[str] = None,
        **kwargs,
    ) -> "ConfigForm":
        """Add a select input field.

        Args:
            key: Config key path
            label: Display label
            choices: List of choices
            default: Default value
            **kwargs: Additional SelectInput arguments

        Returns:
            Self for chaining
        """
        field = SelectInput(key, label, choices, default, **kwargs)
        return self.add_field(field)

    def add_table_select(
        self,
        key: str,
        label: str,
        choices: List[Dict[str, str]],
        columns: List[str],
        value_key: str = "value",
        **kwargs,
    ) -> "ConfigForm":
        """Add a table select input field.

        Args:
            key: Config key path
            label: Display label
            choices: List of choice dicts
            columns: Column names
            value_key: Key to use as value
            **kwargs: Additional arguments

        Returns:
            Self for chaining
        """
        field = TableSelectInput(key, label, choices, columns, value_key, **kwargs)
        return self.add_field(field)

    def render_panel(self) -> Panel:
        """Render configuration as a panel."""
        table = Table.grid(padding=(0, 2), expand=False)
        table.add_column(style="cyan bold", justify="right")
        table.add_column(style="white")

        for field in self.fields:
            value = self.values.get(field.key, field.value)
            if value is not None:
                # Mask password fields
                if isinstance(field, TextInput) and field.password and value:
                    if len(value) >= 8:
                        display = Text(f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}", style="dim")
                    else:
                        display = Text("***", style="dim")
                else:
                    display = Text(str(value), style="green")
            else:
                display = Text("Not Set", style="red")

            table.add_row(f"{field.label}:", display)

        return Panel(
            table,
            title=f"[bold magenta]{self.title}[/bold magenta]",
            border_style="magenta",
            padding=(1, 2),
        )

    def prompt_all(self) -> Dict[str, Any]:
        """Prompt for all fields.

        Returns:
            Dictionary of all field values
        """
        if self.description:
            self.console.print(Panel(
                f"[bold cyan]{self.title}[/bold cyan]\n{self.description}",
                border_style="cyan",
            ))

        for field in self.fields:
            current = self.values.get(field.key, field.value)
            value = field.prompt(self.console, current)
            self.values[field.key] = value

            # Auto-save if enabled
            if self.auto_save and self.config:
                self.config.set(field.key, value)

        # Display final config
        self.console.print("\n")
        self.console.print(self.render_panel())

        return self.values

    def prompt_field(self, key: str) -> Any:
        """Prompt for a specific field.

        Args:
            key: Field key

        Returns:
            Field value
        """
        field = next((f for f in self.fields if f.key == key), None)
        if not field:
            raise ValueError(f"Field '{key}' not found")

        current = self.values.get(field.key, field.value)
        value = field.prompt(self.console, current)
        self.values[field.key] = value

        # Auto-save if enabled
        if self.auto_save and self.config:
            self.config.set(field.key, value)

        return value

    def get_values(self) -> Dict[str, Any]:
        """Get all current values.

        Returns:
            Dictionary of all values
        """
        return self.values.copy()

    def set_value(self, key: str, value: Any) -> None:
        """Set a field value.

        Args:
            key: Field key
            value: Value to set
        """
        self.values[key] = value

        # Update field
        for field in self.fields:
            if field.key == key:
                field.value = value
                break

        # Auto-save if enabled
        if self.auto_save and self.config:
            self.config.set(key, value)

    def reload(self) -> None:
        """Reload all values from config."""
        if not self.config:
            return

        for field in self.fields:
            value = self.config.get(field.key)
            if value is not None:
                field.value = value
                self.values[field.key] = value
