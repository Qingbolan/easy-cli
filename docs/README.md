# SilanTui Documentation

Complete documentation for SilanTui - A modern, elegant CLI framework for building AI chat applications.

## Getting Started

- **[Quick Start Guide](../QUICKSTART.md)** - Get up and running in minutes
- **[Main README](../README.md)** - Project overview and features

## Configuration System

### Core Documentation

1. **[Generic Config Components](./GENERIC_CONFIG_COMPONENTS.md)** - **Start Here**
   - Overview of the generic configuration architecture
   - Why generic components matter
   - Core components: ConfigForm, TextInput, SelectInput, TableSelectInput
   - Usage patterns and examples
   - Best practices

2. **[ConfigForm API Guide](./CONFIG_FORM_GUIDE.md)** - **API Reference**
   - Detailed API documentation
   - All input field types
   - ConfigForm methods and options
   - Real-world examples
   - Custom field creation

### Practical Examples

3. **[Examples Directory](../examples/README.md)** - **Hands-on Learning**
   - API configuration setup
   - Simple form examples
   - Advanced patterns
   - Working code you can run

## Customization

- **[Customization Guide](./CUSTOMIZATION_GUIDE.md)** - Customize UI components and themes
- **[I18N Guide](./I18N_GUIDE.md)** - Internationalization and localization

## Quick Links

### Configuration Quick Start

```python
from silantui.ui import ConfigForm
from rich.console import Console

console = Console()

# Build a form
form = (
    ConfigForm(title="My Config", console=console)
    .add_text("api.key", "API Key", password=True)
    .add_select("theme", "Theme", ["dark", "light"])
)

# Get values (auto-saved)
config = form.prompt_all()
```

### ConfigManager Quick Start

```python
from silantui.core import get_config

config = get_config()

# Set values (auto-saved to ~/.silantui/config.json)
config.set("api.key", "sk-...")
config.set("model", "gpt-4")

# Get values
api_key = config.get("api.key")
```

## Documentation Structure

```
docs/
├── README.md                          # This file
├── GENERIC_CONFIG_COMPONENTS.md       # Architecture overview
├── CONFIG_FORM_GUIDE.md              # Complete API reference
├── CUSTOMIZATION_GUIDE.md            # UI customization
└── I18N_GUIDE.md                     # Internationalization

examples/
├── README.md                         # Examples overview
├── api_config_setup.py              # Multi-provider setup
├── simple_config_form.py            # Basic examples
├── advanced_config_patterns.py      # Advanced patterns
└── test_components.py               # Test suite
```

## Key Concepts

### Generic Components

SilanTui uses **generic, reusable components** rather than hardcoded solutions:

- ✅ **Flexible** - Build any type of configuration form
- ✅ **Reusable** - Use across different projects
- ✅ **Extensible** - Create custom field types
- ✅ **Clean** - Core library stays generic

### Auto-save & Auto-load

Configuration is automatically persisted:

- **Auto-load** - Loads existing config from `~/.silantui/config.json`
- **Auto-save** - Saves changes in real-time
- **No manual file handling** - It just works

### Chainable API

Build forms fluently:

```python
form = (
    ConfigForm(title="Config")
    .add_text("field1", "Label 1")
    .add_select("field2", "Label 2", choices)
    .add_table_select("field3", "Label 3", data, columns)
)
```

## Common Tasks

### Create a Simple Form

See: [Simple Forms Example](../examples/simple_config_form.py)

```python
form = ConfigForm(title="Settings", console=console)
form.add_text("name", "Name")
form.add_text("email", "Email")
values = form.prompt_all()
```

### Create API Configuration

See: [API Config Example](../examples/api_config_setup.py)

```python
models = [
    {"name": "gpt-4", "provider": "OpenAI"},
    {"name": "claude-3", "provider": "Anthropic"},
]

form = (
    ConfigForm(title="API Config", console=console)
    .add_text("api.key", "API Key", password=True)
    .add_table_select("model", "Model", models, ["name", "provider"])
)
```

### Save and Load Configuration

See: [ConfigForm Guide - Auto-save Section](./CONFIG_FORM_GUIDE.md#integration-with-configmanager)

```python
form = ConfigForm(
    title="Settings",
    auto_load=True,   # Load from config
    auto_save=True    # Save automatically
)
```

### Create Custom Field Types

See: [ConfigForm Guide - Custom Fields](./CONFIG_FORM_GUIDE.md#custom-field-types)

```python
class NumberInput(InputField):
    def prompt(self, console, current_value=None):
        # Custom implementation
        pass
```

## Examples You Can Run

```bash
# Multi-provider API configuration
python examples/api_config_setup.py

# Seven simple examples
python examples/simple_config_form.py

# Advanced patterns
python examples/advanced_config_patterns.py

# Test all components
python examples/test_components.py
```

## Documentation Reading Order

### For Beginners

1. [Quick Start Guide](../QUICKSTART.md)
2. [Examples README](../examples/README.md)
3. Run `python examples/simple_config_form.py`
4. [Generic Components Overview](./GENERIC_CONFIG_COMPONENTS.md)

### For API Users

1. [Generic Components Overview](./GENERIC_CONFIG_COMPONENTS.md)
2. [ConfigForm API Guide](./CONFIG_FORM_GUIDE.md)
3. [Advanced Patterns Example](../examples/advanced_config_patterns.py)

### For Contributors

1. [Generic Components Architecture](./GENERIC_CONFIG_COMPONENTS.md)
2. [All Examples](../examples/)
3. [Customization Guide](./CUSTOMIZATION_GUIDE.md)

## FAQs

**Q: Where is configuration saved?**
```
~/.silantui/config.json
```

**Q: How do I reset configuration?**
```python
from silantui.core import get_config
get_config().reset_to_defaults()
```

**Q: Can I use a custom config location?**
```python
from pathlib import Path
from silantui.core import ConfigManager
config = ConfigManager(config_dir=Path("/custom/path"))
```

**Q: How do I create custom fields?**
See: [CONFIG_FORM_GUIDE.md - Custom Field Types](./CONFIG_FORM_GUIDE.md#custom-field-types)

**Q: Are there working examples?**
Yes! See: [examples/](../examples/)

## Support

- **Examples**: See [examples/README.md](../examples/README.md)
- **API Reference**: See [CONFIG_FORM_GUIDE.md](./CONFIG_FORM_GUIDE.md)
- **Issues**: [GitHub Issues](https://github.com/Qingbolan/silantui/issues)

## Contributing

Documentation improvements are welcome! See individual guides for details.

---

**Latest Update**: Configuration system refactored to use generic, reusable components (v0.1.1)
