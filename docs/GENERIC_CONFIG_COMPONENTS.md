# Generic Configuration Components

SilanTui provides generic, reusable configuration input components that can be used to build any type of configuration interface.

## Philosophy

The configuration system is designed to be **generic and flexible**, not hardcoded for specific use cases. This allows you to:

- Build custom configuration forms for any purpose
- Reuse components across different projects
- Extend and customize behavior
- Keep the core library clean and maintainable

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Generic Components                       │
│  (silantui/ui/config_input.py)                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  • InputField          - Base input field class             │
│  • TextInput           - Text input with password support   │
│  • SelectInput         - Select from choices                │
│  • TableSelectInput    - Select with table display          │
│  • ConfigForm          - Form builder and manager           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    Used by (not part of core)
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Specific Implementations                   │
│  (examples/)                                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  • api_config_setup.py          - API configurations        │
│  • simple_config_form.py         - Basic examples           │
│  • advanced_config_patterns.py   - Complex patterns         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. ConfigForm - The Form Builder

Main component for building configuration forms:

```python
from silantui.ui import ConfigForm

form = (
    ConfigForm(title="My Config", console=console)
    .add_text("key1", "Label 1")
    .add_select("key2", "Label 2", ["option1", "option2"])
    .add_table_select("key3", "Label 3", choices, columns)
)

values = form.prompt_all()
```

**Features:**
- Chainable API for building forms
- Auto-load from ConfigManager
- Auto-save on changes
- Field validation
- Beautiful rendering

### 2. Input Field Types

#### TextInput
```python
from silantui.ui import TextInput

field = TextInput(
    key="api.key",
    label="API Key",
    password=True,      # Mask input
    placeholder="sk-..."
)
```

#### SelectInput
```python
from silantui.ui import SelectInput

field = SelectInput(
    key="theme",
    label="Theme",
    choices=["dark", "light", "auto"],
    default="dark"
)
```

#### TableSelectInput
```python
from silantui.ui import TableSelectInput

field = TableSelectInput(
    key="model",
    label="Model",
    choices=[
        {"name": "gpt-4", "provider": "OpenAI"},
        {"name": "claude-3", "provider": "Anthropic"}
    ],
    columns=["name", "provider"],
    value_key="name"
)
```

## Usage Patterns

### Pattern 1: Simple Configuration

```python
form = (
    ConfigForm(title="Settings", console=console)
    .add_text("name", "Name")
    .add_text("email", "Email")
)

values = form.prompt_all()
```

### Pattern 2: With Persistence

```python
from silantui.core import get_config

form = ConfigForm(
    title="Settings",
    console=console,
    auto_load=True,   # Load from ~/.silantui/config.json
    auto_save=True    # Save automatically
)

form.add_text("api.key", "API Key", password=True)
values = form.prompt_all()  # Auto-saved!
```

### Pattern 3: Factory Pattern

```python
def create_api_form(provider: str, console) -> ConfigForm:
    """Factory function for creating API config forms."""

    if provider == "openai":
        return (
            ConfigForm(title="OpenAI Config", console=console)
            .add_text("api.openai.key", "API Key", password=True)
            .add_text("api.openai.url", "URL")
        )
    elif provider == "anthropic":
        return (
            ConfigForm(title="Anthropic Config", console=console)
            .add_text("api.anthropic.key", "API Key", password=True)
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")

# Usage
form = create_api_form("openai", console)
config = form.prompt_all()
```

### Pattern 4: Custom Validation

```python
def validate_url(url: str) -> bool:
    return url.startswith(("http://", "https://"))

form = ConfigForm(title="Config", console=console)

url_field = TextInput(
    key="api.url",
    label="API URL",
    validator=validate_url
)

form.add_field(url_field)
```

### Pattern 5: Conditional Fields

```python
form = ConfigForm(title="Config", console=console)
form.add_select("type", "Type", ["basic", "advanced"])

config_type = form.prompt_field("type")

if config_type == "advanced":
    form.add_text("advanced.option1", "Option 1")
    form.add_text("advanced.option2", "Option 2")

values = form.prompt_all()
```

## Integration with ConfigManager

ConfigForm automatically integrates with ConfigManager:

```python
from silantui.core import get_config
from silantui.ui import ConfigForm

# ConfigForm uses global config by default
form = ConfigForm(
    title="Settings",
    auto_load=True,   # Loads from config
    auto_save=True    # Saves to config
)

form.add_text("setting1", "Setting 1")
values = form.prompt_all()

# Values are now persisted
config = get_config()
assert config.get("setting1") == values["setting1"]
```

## Real-World Examples

All examples are in `/examples/` directory:

### 1. API Configuration (`api_config_setup.py`)

Multi-provider API configuration with:
- OpenAI configuration
- Anthropic configuration
- Custom API configuration
- Table-based model selection

```bash
python examples/api_config_setup.py
```

### 2. Simple Forms (`simple_config_form.py`)

Seven different examples:
1. Basic text form
2. Select input
3. Table select
4. Auto-save configuration
5. Custom fields with validation
6. Individual field prompts
7. Reload values

```bash
python examples/simple_config_form.py
```

### 3. Advanced Patterns (`advanced_config_patterns.py`)

Real-world patterns:
- Multi-provider API config manager
- Database configuration with connection strings
- Complete application setup wizard
- Factory pattern implementations

```bash
python examples/advanced_config_patterns.py
```

## Extending Components

### Create Custom Input Type

```python
from silantui.ui import InputField
from rich.prompt import IntPrompt

class NumberInput(InputField):
    def prompt(self, console, current_value=None):
        value = IntPrompt.ask(
            f"[cyan]{self.label}[/cyan]",
            default=current_value or self.default
        )
        self.value = value
        return value

# Use it
form = ConfigForm(title="Config", console=console)
form.add_field(NumberInput("port", "Port", default=8080))
```

### Create Custom Form

```python
class APIConfigForm(ConfigForm):
    """Custom API configuration form."""

    def __init__(self, provider: str, console):
        super().__init__(
            title=f"{provider.title()} API Configuration",
            console=console,
            auto_load=True,
            auto_save=True
        )

        self.add_text(f"api.{provider}.key", "API Key", password=True)
        self.add_text(f"api.{provider}.url", "Base URL")

    def validate(self) -> bool:
        """Custom validation logic."""
        values = self.get_values()
        return all(values.values())

# Usage
form = APIConfigForm("openai", console)
if form.prompt_all() and form.validate():
    print("Configuration valid!")
```

## Why Generic?

### ❌ Hardcoded (Bad)

```python
class OpenAIConfig:
    """Hardcoded for OpenAI only."""

    def setup(self):
        self.api_key = prompt("API Key")
        self.model = select(["gpt-4", "gpt-3.5"])
        # Cannot reuse for other providers
```

### ✅ Generic (Good)

```python
def create_provider_config(provider: str, models: List[str]):
    """Generic form builder."""

    return (
        ConfigForm(title=f"{provider} Config")
        .add_text(f"api.{provider}.key", "API Key", password=True)
        .add_select(f"api.{provider}.model", "Model", models)
    )

# Reusable for any provider
openai_form = create_provider_config("openai", ["gpt-4", "gpt-3.5"])
anthropic_form = create_provider_config("anthropic", ["claude-3"])
custom_form = create_provider_config("custom", ["llama-2"])
```

## Best Practices

1. **Keep Components Generic**
   - Don't hardcode specific values in components
   - Use parameters and configuration

2. **Use Factory Functions**
   - Create forms using factory functions
   - Keep configuration logic in examples

3. **Separate Concerns**
   - Core components in `/silantui/ui/`
   - Specific implementations in `/examples/`

4. **Validate Input**
   - Add validators to fields
   - Validate at form level

5. **Provide Defaults**
   - Set sensible defaults
   - Make fields optional when possible

6. **Chain Methods**
   - Use chainable API
   - Build forms fluently

7. **Auto-save When Appropriate**
   - Enable auto-save for persistent config
   - Disable for temporary forms

## API Reference

See [CONFIG_FORM_GUIDE.md](./CONFIG_FORM_GUIDE.md) for complete API reference.

## Testing

Test the components:

```bash
python -c "
from silantui.ui import ConfigForm
from rich.console import Console

form = ConfigForm(title='Test', console=Console())
form.add_text('key', 'Label', default='value')
form.set_value('key', 'new_value')
print(form.get_values())
"
```

## Migration Guide

If you have existing hardcoded config forms:

**Before:**
```python
class MyConfig:
    def setup(self):
        self.api_key = input("API Key: ")
        self.model = input("Model: ")
```

**After:**
```python
def create_config_form(console):
    return (
        ConfigForm(title="My Config", console=console)
        .add_text("api_key", "API Key", password=True)
        .add_text("model", "Model")
    )

form = create_config_form(console)
values = form.prompt_all()
```

## Summary

- **Generic components** in `/silantui/ui/config_input.py`
- **Specific examples** in `/examples/`
- **Flexible and reusable** design
- **Easy to extend** with custom fields
- **Auto-save integration** with ConfigManager
- **Beautiful terminal UI** with Rich

For complete guide, see [CONFIG_FORM_GUIDE.md](./CONFIG_FORM_GUIDE.md)
