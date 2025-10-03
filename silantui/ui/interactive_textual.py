"""
Textual-based interactive components

Modern replacements for:
- interactive_select.py
- config_input.py
"""

from typing import Optional, List, Dict, Callable, Any, Tuple
from dataclasses import dataclass

from textual.app import ComposeResult
from textual.widgets import (
    Static, Label, Button, Input, Select,
    OptionList
)
from textual.containers import Container, Vertical, Horizontal
from textual.screen import ModalScreen
from textual.binding import Binding


# ==================== Interactive Select ====================

class SelectOption:
    """Represents a selectable option"""

    def __init__(self, value: str, label: str, description: str = ""):
        self.value = value
        self.label = label
        self.description = description

    def __str__(self):
        if self.description:
            return f"{self.label} - {self.description}"
        return self.label


class InteractiveSelectScreen(ModalScreen[Optional[str]]):
    """Modal screen for interactive selection"""

    DEFAULT_CSS = """
    InteractiveSelectScreen {
        align: center middle;
    }

    #select-dialog {
        width: 60;
        height: auto;
        max-height: 30;
        border: thick $primary;
        background: $surface;
        padding: 1;
    }

    #select-title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    #select-list {
        width: 100%;
        height: auto;
        max-height: 20;
        border: solid $primary;
        margin: 1 0;
    }

    #select-buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "select", "Select"),
    ]

    def __init__(
        self,
        title: str,
        options: List[SelectOption],
        allow_none: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.select_title = title
        self.options = options
        self.allow_none = allow_none
        self.selected_value: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Build the selection dialog"""
        with Container(id="select-dialog"):
            yield Static(self.select_title, id="select-title")

            # Create option list
            option_list = OptionList(id="select-list")
            for opt in self.options:
                display = opt.label
                if opt.description:
                    display += f"\n  [dim]{opt.description}[/dim]"
                option_list.add_option((display, opt.value))

            yield option_list

            # Buttons
            with Horizontal(id="select-buttons"):
                yield Button("Select", variant="primary", id="btn-select")
                if self.allow_none:
                    yield Button("Cancel", variant="default", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press"""
        if event.button.id == "btn-select":
            self.action_select()
        elif event.button.id == "btn-cancel":
            self.action_cancel()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection (double-click or Enter)"""
        self.selected_value = event.option.id
        self.dismiss(self.selected_value)

    def action_select(self) -> None:
        """Select current option"""
        option_list = self.query_one("#select-list", OptionList)
        if option_list.highlighted is not None:
            self.selected_value = self.options[option_list.highlighted].value
            self.dismiss(self.selected_value)

    def action_cancel(self) -> None:
        """Cancel selection"""
        self.dismiss(None)


class InteractiveSelect:
    """
    Interactive selection widget - Textual version

    Replacement for rich-based interactive_select.py
    """

    @staticmethod
    async def select(
        title: str,
        options: List[Tuple[str, str]] | List[Tuple[str, str, str]],
        allow_none: bool = False
    ) -> Optional[str]:
        """
        Show interactive selection and return selected value

        Args:
            title: Selection title
            options: List of (value, label) or (value, label, description) tuples
            allow_none: Allow canceling without selection

        Returns:
            Selected value or None
        """
        # Convert options to SelectOption objects
        select_options = []
        for opt in options:
            if len(opt) == 2:
                value, label = opt
                desc = ""
            else:
                value, label, desc = opt

            select_options.append(SelectOption(value, label, desc))

        # Create and run selection screen
        # Note: This requires an active Textual app
        # In practice, would be called from within a Textual app
        screen = InteractiveSelectScreen(title, select_options, allow_none)

        # Return placeholder for now - real implementation would:
        # return await app.push_screen_wait(screen)
        return None


# ==================== Config Input ====================

@dataclass
class ConfigField:
    """Configuration field definition"""
    name: str
    label: str
    type: str = "text"
    default: Any = ""
    placeholder: str = ""
    required: bool = False
    options: List[Tuple[str, str]] = None
    validator: Optional[Callable] = None
    description: str = ""


class ConfigInputScreen(ModalScreen[Dict[str, Any]]):
    """Modal screen for configuration input"""

    DEFAULT_CSS = """
    ConfigInputScreen {
        align: center middle;
    }

    #config-dialog {
        width: 70;
        height: auto;
        max-height: 40;
        border: thick $primary;
        background: $surface;
        padding: 2;
    }

    #config-title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    #config-form {
        width: 100%;
        height: auto;
        max-height: 30;
        overflow-y: auto;
    }

    .field-container {
        width: 100%;
        margin: 1 0;
    }

    .field-label {
        width: 100%;
        margin-bottom: 1;
    }

    .field-input {
        width: 100%;
    }

    .field-description {
        width: 100%;
        color: $text-muted;
        margin-top: 1;
    }

    #config-buttons {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "submit", "Submit"),
    ]

    def __init__(self, title: str, fields: List[ConfigField], **kwargs):
        super().__init__(**kwargs)
        self.config_title = title
        self.fields = fields
        self.values: Dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        """Build the configuration form"""
        with Container(id="config-dialog"):
            yield Static(self.config_title, id="config-title")

            with Vertical(id="config-form"):
                for field in self.fields:
                    with Vertical(classes="field-container"):
                        # Label
                        label_text = field.label
                        if field.required:
                            label_text += " *"
                        yield Label(label_text, classes="field-label")

                        # Input widget
                        if field.type == "text":
                            yield Input(
                                value=str(field.default),
                                placeholder=field.placeholder,
                                id=f"field-{field.name}",
                                classes="field-input"
                            )
                        elif field.type == "password":
                            yield Input(
                                value=str(field.default),
                                password=True,
                                id=f"field-{field.name}",
                                classes="field-input"
                            )
                        elif field.type == "select":
                            if field.options:
                                yield Select(
                                    options=[(label, value) for value, label in field.options],
                                    value=field.default,
                                    id=f"field-{field.name}",
                                    classes="field-input"
                                )

                        # Description
                        if field.description:
                            yield Static(
                                f"[dim]{field.description}[/dim]",
                                classes="field-description"
                            )

            # Buttons
            with Horizontal(id="config-buttons"):
                yield Button("Submit", variant="primary", id="btn-submit")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press"""
        if event.button.id == "btn-submit":
            self.action_submit()
        elif event.button.id == "btn-cancel":
            self.action_cancel()

    def action_submit(self) -> None:
        """Collect and validate form values"""
        values = {}

        for field in self.fields:
            widget = self.query_one(f"#field-{field.name}")

            if isinstance(widget, Input):
                value = widget.value
            elif isinstance(widget, Select):
                value = widget.value
            else:
                value = None

            # Validate required fields
            if field.required and not value:
                # Show error
                self.notify(f"{field.label} is required", severity="error")
                return

            # Custom validation
            if field.validator and value:
                try:
                    if not field.validator(value):
                        self.notify(f"Invalid value for {field.label}", severity="error")
                        return
                except Exception as e:
                    self.notify(f"Validation error: {str(e)}", severity="error")
                    return

            values[field.name] = value

        self.dismiss(values)

    def action_cancel(self) -> None:
        """Cancel form"""
        self.dismiss({})


class ConfigInput:
    """
    Configuration input wizard - Textual version

    Replacement for rich-based config_input.py
    """

    @staticmethod
    async def get_config(
        title: str,
        fields: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Show configuration form and return values

        Args:
            title: Form title
            fields: List of field definitions (dict with name, label, type, etc.)

        Returns:
            Dictionary of field values
        """
        # Convert dict fields to ConfigField objects
        config_fields = []
        for field_dict in fields:
            config_fields.append(ConfigField(
                name=field_dict.get("name", ""),
                label=field_dict.get("label", ""),
                type=field_dict.get("type", "text"),
                default=field_dict.get("default", ""),
                placeholder=field_dict.get("placeholder", ""),
                required=field_dict.get("required", False),
                options=field_dict.get("options"),
                validator=field_dict.get("validator"),
                description=field_dict.get("description", "")
            ))

        # Create and show screen
        screen = ConfigInputScreen(title, config_fields)

        # Return placeholder - real implementation would:
        # return await app.push_screen_wait(screen)
        return {}


__all__ = [
    "InteractiveSelect",
    "SelectOption",
    "ConfigInput",
    "ConfigField",
    "InteractiveSelectScreen",
    "ConfigInputScreen",
]
