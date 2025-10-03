# ConfigForm - Generic Configuration Component Guide

`ConfigForm` is a flexible, reusable component for building interactive configuration interfaces in the terminal using Rich.

## Overview

The component provides:

- **Generic Input Fields**: Text, Select, and Table Select inputs
- **Auto-load/Auto-save**: Automatic configuration persistence
- **Chainable API**: Fluent interface for building forms
- **Validation**: Built-in field validation
- **Rich Display**: Beautiful terminal rendering with panels and tables

## Components

### 1. InputField (Base Class)

Base class for all input fields.

```python
from silantui.ui import InputField

field = InputField(
    key="config.key",           # Dot-notation config path
    label="Display Label",      # User-facing label
    default="default_value",    # Default value
    validator=lambda x: True,   # Optional validator function
    required=False              # Is field required?
)
```

### 2. TextInput

Text input field with optional password masking.

```python
from silantui.ui import TextInput

field = TextInput(
    key="api.key",
    label="API Key",
    default="",
    password=True,              # Mask input
    placeholder="sk-...",       # Placeholder text
)
```

### 3. SelectInput

Selection from a list of choices.

```python
from silantui.ui import SelectInput

field = SelectInput(
    key="theme",
    label="Theme",
    choices=["dark", "light", "auto"],
    default="dark",
    show_index=True             # Show numbered list
)
```

### 4. TableSelectInput

Selection with multi-column table display.

```python
from silantui.ui import TableSelectInput

models = [
    {"name": "gpt-4", "provider": "OpenAI", "cost": "$$$"},
    {"name": "gpt-3.5-turbo", "provider": "OpenAI", "cost": "$"},
]

field = TableSelectInput(
    key="model",
    label="Select Model",
    choices=models,
    columns=["name", "provider", "cost"],  # Columns to display
    value_key="name",                      # Which field to use as value
)
```

### 5. ConfigForm

Main form component that combines multiple fields.

```python
from silantui.ui import ConfigForm

form = ConfigForm(
    title="Configuration",
    description="Optional description",
    console=console,            # Rich Console instance
    config_manager=None,        # Optional ConfigManager
    auto_load=True,            # Load existing values
    auto_save=True,            # Save on changes
)
```

## Usage Examples

### Basic Form

```python
from silantui.ui import ConfigForm
from rich.console import Console

console = Console()

form = (
    ConfigForm(title="User Settings", console=console)
    .add_text("user.name", "Name")
    .add_text("user.email", "Email")
    .add_text("user.token", "API Token", password=True)
)

# Prompt for all fields
values = form.prompt_all()
print(values)  # {"user.name": "...", "user.email": "...", "user.token": "..."}
```

### Select Input

```python
form = (
    ConfigForm(title="Preferences", console=console)
    .add_select(
        "ui.theme",
        "Theme",
        choices=["dark", "light", "auto"],
        default="dark"
    )
    .add_select(
        "ui.language",
        "Language",
        choices=["en", "zh", "ja"],
        default="en"
    )
)

values = form.prompt_all()
```

### Table Select

```python
databases = [
    {"name": "PostgreSQL", "type": "SQL", "port": "5432"},
    {"name": "MongoDB", "type": "NoSQL", "port": "27017"},
    {"name": "Redis", "type": "Cache", "port": "6379"},
]

form = (
    ConfigForm(title="Database", console=console)
    .add_table_select(
        "database.type",
        "Database",
        choices=databases,
        columns=["name", "type", "port"],
        value_key="name"
    )
    .add_text("database.host", "Host", default="localhost")
    .add_text("database.password", "Password", password=True)
)

values = form.prompt_all()
```

### With Auto-save

```python
from silantui.core import get_config

config = get_config()

form = (
    ConfigForm(
        title="Settings",
        console=console,
        auto_load=True,   # Load from config
        auto_save=True    # Save on each input
    )
    .add_text("app.name", "App Name")
    .add_text("app.version", "Version")
)

# Each input is automatically saved to ~/.silantui/config.json
values = form.prompt_all()
```

### Custom Validation

```python
def validate_email(email: str) -> bool:
    return "@" in email and "." in email

form = ConfigForm(title="User", console=console)

email_field = TextInput(
    key="user.email",
    label="Email",
    validator=validate_email,
    required=True
)

form.add_field(email_field)
```

### Individual Field Prompts

```python
form = (
    ConfigForm(title="Config", console=console)
    .add_text("field1", "Field 1")
    .add_text("field2", "Field 2")
    .add_text("field3", "Field 3")
)

# Prompt for specific field only
value = form.prompt_field("field1")

# Or prompt for all
all_values = form.prompt_all()
```

### Display Configuration Panel

```python
form = (
    ConfigForm(title="Current Config", console=console, auto_load=True)
    .add_text("api.key", "API Key", password=True)
    .add_text("api.url", "Base URL")
)

# Render as panel (passwords are masked)
panel = form.render_panel()
console.print(panel)
```

## Real-World Examples

### API Configuration

```python
def create_api_config_form(console):
    models = [
        {"name": "gpt-4", "speed": "Fast", "cost": "$$"},
        {"name": "gpt-3.5-turbo", "speed": "Very Fast", "cost": "$"},
    ]

    return (
        ConfigForm(
            title="API Configuration",
            description="Configure API credentials",
            console=console,
            auto_load=True,
            auto_save=True
        )
        .add_text("api.key", "API Key", password=True, required=True)
        .add_text("api.url", "Base URL", default="https://api.openai.com/v1")
        .add_table_select(
            "api.model",
            "Model",
            choices=models,
            columns=["name", "speed", "cost"],
            value_key="name"
        )
    )

# Usage
form = create_api_config_form(console)
config = form.prompt_all()
```

### Multi-step Configuration

```python
def setup_application(console):
    # Step 1: General settings
    general = (
        ConfigForm(title="General Settings", console=console, auto_save=True)
        .add_text("app.name", "Name")
        .add_text("app.version", "Version")
    ).prompt_all()

    # Step 2: API settings
    api = (
        ConfigForm(title="API Settings", console=console, auto_save=True)
        .add_text("api.key", "Key", password=True)
        .add_text("api.url", "URL")
    ).prompt_all()

    # Step 3: UI preferences
    ui = (
        ConfigForm(title="UI Preferences", console=console, auto_save=True)
        .add_select("ui.theme", "Theme", ["dark", "light"])
    ).prompt_all()

    return {**general, **api, **ui}
```

### Conditional Fields

```python
form = (
    ConfigForm(title="Config", console=console)
    .add_select("type", "Type", ["simple", "advanced"])
)

config_type = form.prompt_field("type")

if config_type == "advanced":
    form.add_text("advanced.option1", "Option 1")
    form.add_text("advanced.option2", "Option 2")

values = form.prompt_all()
```

## API Reference

### ConfigForm Methods

#### Constructor

```python
ConfigForm(
    title: str = "Configuration",
    description: Optional[str] = None,
    console: Optional[Console] = None,
    config_manager: Optional[ConfigManager] = None,
    auto_load: bool = True,
    auto_save: bool = True,
)
```

#### Adding Fields

```python
# Add any field
.add_field(field: InputField) -> ConfigForm

# Add text input
.add_text(
    key: str,
    label: str,
    default: str = "",
    password: bool = False,
    **kwargs
) -> ConfigForm

# Add select input
.add_select(
    key: str,
    label: str,
    choices: List[str],
    default: Optional[str] = None,
    **kwargs
) -> ConfigForm

# Add table select
.add_table_select(
    key: str,
    label: str,
    choices: List[Dict[str, str]],
    columns: List[str],
    value_key: str = "value",
    **kwargs
) -> ConfigForm
```

#### Prompting

```python
# Prompt for all fields
.prompt_all() -> Dict[str, Any]

# Prompt for specific field
.prompt_field(key: str) -> Any
```

#### Display

```python
# Render as panel
.render_panel() -> Panel
```

#### Data Access

```python
# Get all values
.get_values() -> Dict[str, Any]

# Set value
.set_value(key: str, value: Any) -> None

# Reload from config
.reload() -> None
```

## Integration with ConfigManager

ConfigForm integrates seamlessly with ConfigManager:

```python
from silantui.core import get_config
from silantui.ui import ConfigForm

# ConfigForm automatically uses global config
form = ConfigForm(
    title="Settings",
    auto_load=True,   # Loads from ~/.silantui/config.json
    auto_save=True    # Saves to ~/.silantui/config.json
)

# All values are persisted automatically
form.add_text("api.key", "API Key")
values = form.prompt_all()

# Values are now in config
config = get_config()
api_key = config.get("api.key")
```

## Examples Location

Complete working examples are in `/examples/`:

1. **`api_config_setup.py`** - Multi-provider API configuration
2. **`simple_config_form.py`** - Basic form examples
3. **`advanced_config_patterns.py`** - Advanced patterns and use cases

Run examples:

```bash
python examples/api_config_setup.py
python examples/simple_config_form.py
python examples/advanced_config_patterns.py
```

## Best Practices

1. **Use Chainable API**: Build forms fluently with method chaining
2. **Enable Auto-save**: Use `auto_save=True` for persistence
3. **Validate Input**: Add validators to fields for data quality
4. **Mask Passwords**: Use `password=True` for sensitive data
5. **Provide Defaults**: Set sensible default values
6. **Group Related Fields**: Create separate forms for logical sections
7. **Show Existing Config**: Display current config before prompting

## Custom Field Types

Create custom input fields by extending `InputField`:

```python
from silantui.ui import InputField

class NumberInput(InputField):
    def prompt(self, console, current_value=None):
        from rich.prompt import IntPrompt
        value = IntPrompt.ask(
            f"[cyan]{self.label}[/cyan]",
            default=current_value or self.default
        )
        self.value = value
        return value

# Use custom field
form = ConfigForm(title="Config", console=console)
form.add_field(NumberInput("port", "Port", default=8080))
```

## Styling

Customize colors and styles:

```python
# Modify field display in render_panel by subclassing ConfigForm
class CustomConfigForm(ConfigForm):
    def render_panel(self):
        # Custom rendering logic
        pass
```

## Error Handling

```python
try:
    form = ConfigForm(title="Config", console=console)
    values = form.prompt_all()
except ValueError as e:
    console.print(f"[red]Configuration error: {e}[/red]")
```
