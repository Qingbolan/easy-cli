# SilanTui

**A Modern Terminal UI Framework for Python**

Build beautiful, interactive command-line applications with ease. SilanTui provides powerful UI components, command management, and extensibility - no AI required (but AI integration is optional and easy).

> **Author**: [Silan Hu](https://silan.tech)  
> **License**: MIT

## 🌍 Internationalization (i18n)

SilanTui supports multiple languages out of the box:

```python
from silantui.i18n import set_language, t

# Set language
set_language('zh')  # Chinese
set_language('en')  # English (default)
set_language('es')  # Spanish
set_language('fr')  # French
set_language('ja')  # Japanese

# Use translations
print(t('welcome'))      # Outputs in current language
print(t('success'))      # Translated success message
print(t('command.help')) # Translated command help
```

See [examples/i18n_demo.py](examples/i18n_demo.py) for a complete example.

## 🎯 What is SilanTui?

SilanTui is a **UI-first CLI framework** that makes it simple to create professional terminal applications. Think of it as a toolkit for building TUIs (Text User Interfaces) with:

- Beautiful, Rich-based components
- Intuitive command systems
- Flexible layouts and displays
- Easy customization

**AI integration is just one of many possible use cases.**

## ✨ Core Features

### 🎨 UI Components
- **ModernLogger** - Advanced logging with colors, progress bars, and formatting
- **UIBuilder** - Fluent API for Panels, Tables, Menus, Forms, and Layouts
- **ChatDisplay** - Fixed-bottom input with scrollable content
- **LiveDisplay** - Real-time updating layouts without flicker

### 🎮 Command System
- **3 Ways to Register** - Decorators, Builders, or Quick functions
- **Command Categories** - Organize commands by function
- **Aliases Support** - Create shortcuts for any command
- **Help Generation** - Automatic help text and documentation

### 🔧 Extensibility
- **Custom Themes** - Define your own color schemes
- **Plugin Architecture** - Easy to extend and customize
- **Session Management** - Save/load application state
- **Configuration** - Flexible config system

### 🤖 Optional AI Integration
- **Universal AI Client** - Works with OpenAI, Anthropic, Ollama, or any compatible API
- **Custom BaseURL** - Point to any API endpoint
- **Streaming Support** - Real-time response display
- **Markdown Rendering** - Beautiful AI response formatting

## 📦 Installation

```bash
pip install silantui
```

Or from source:

```bash
git clone https://github.com/yourusername/silantui.git
cd silantui
pip install -e .
```

## 🚀 Quick Start

### Example 1: Simple Dashboard

```python
from silantui import ModernLogger, UIBuilder

logger = ModernLogger(name="dashboard")
ui = UIBuilder(console=logger.console)

# Create a beautiful table
ui.table("User Data") \
    .add_column("Name", style="cyan") \
    .add_column("Status", style="green") \
    .add_row("Alice", "Active") \
    .add_row("Bob", "Inactive") \
    .show()

# Create an info panel
ui.panel("Welcome", "This is your dashboard!") \
    .border("cyan") \
    .show()
```

### Example 2: Interactive Menu

```python
from silantui import UIBuilder

ui = UIBuilder()

choice = ui.menu("Main Menu") \
    .add_item("1", "Start", description="Start the application") \
    .add_item("2", "Settings", description="Configure options") \
    .add_separator() \
    .add_item("3", "Exit") \
    .show()

print(f"You selected: {choice}")
```

### Example 3: Custom Commands

```python
from silantui import CommandRegistry, ModernLogger

registry = CommandRegistry()
logger = ModernLogger(name="app")

@registry.command("greet", description="Say hello", aliases=["hi"])
def greet_command(app, args):
    logger.success(f"Hello, {args}!")

@registry.command("stats", description="Show statistics")
def stats_command(app, args):
    logger.info("Statistics: ...")

# Execute commands
registry.execute("greet", None, "World")
registry.show_help(logger.console)
```

### Example 4: AI Chat (Optional)

```python
from silantui import LiveChatDisplay
from silantui.integrations.universal_client import UniversalAIClient

# Works with OpenAI, Ollama, or any compatible API
client = UniversalAIClient(
    api_key="your-key",
    base_url="http://localhost:11434/v1",  # Optional: use local Ollama
    model="llama2"
)

display = LiveChatDisplay()
display.start()

# Add messages
display.add_user_message("Hello!")

# Stream AI response
display.start_assistant_message()
for chunk in client.chat_stream("Hello!"):
    display.append_streaming(chunk)
display.finish_assistant_message()

display.stop()
```

## 📚 Complete Examples

SilanTui includes full-featured example applications:

### 1. Dashboard App
```bash
python examples/dashboard_app.py
```
Real-time data dashboard with live monitoring, charts, and statistics.

### 2. Task Manager
```bash
python examples/task_manager.py
```
Complete task management application with persistence, filtering, and statistics.

### 3. AI Chat (Optional)
```bash
# With OpenAI
export OPENAI_API_KEY=your-key
python examples/ai_chat_app.py

# With Ollama (local)
python examples/ai_chat_app.py --preset ollama --model llama2

# With custom API
python examples/ai_chat_app.py --base-url http://your-api.com/v1 --model your-model
```

## 🎬 Showcase

### Interactive Chat Interface

SilanTui provides a beautiful, modern chat interface with real-time streaming, alternate screen mode, and smooth animations:

![Chat Demo 1](https://github.com/Qingbolan/easy-cli/blob/main/assets/chat-demo-1.png)
*Clean, minimalist chat interface with streaming responses*

![Chat Demo 2](https://github.com/Qingbolan/easy-cli/blob/main/assets/chat-demo-2.png)
*Real-time message streaming with metadata display*

![Chat Demo 3](https://github.com/Qingbolan/easy-cli/blob/main/assets/chat-demo-3.png)
*Full conversation flow with markdown rendering*

Features demonstrated:
- 🎨 Alternate screen mode for isolated UI experience
- ⚡ Real-time streaming with frame merging
- 📝 Markdown rendering for formatted responses
- 🎯 Bottom-aligned chat with scrollable history
- 💬 Fixed input area with IME support
- ⏱️ Response timing and metadata display

## 🎨 UI Components Guide

### Tables

```python
from silantui import UIBuilder

ui = UIBuilder()

table = ui.table("User List")
table.add_column("ID", style="cyan", width=5)
table.add_column("Name", style="green")
table.add_column("Email", style="yellow")

table.add_row("1", "Alice", "alice@example.com")
table.add_row("2", "Bob", "bob@example.com")

table.show()
```

### Panels

```python
panel = ui.panel("Title", "Content here") \
    .border("cyan") \
    .padding((2, 4)) \
    .expand(True) \
    .build()
```

### Forms

```python
results = ui.form("User Settings") \
    .add_field("name", "Name", required=True) \
    .add_field("age", "Age", field_type="int") \
    .add_field("theme", "Theme", field_type="choice",
              choices=["light", "dark"]) \
    .show()
```

### Layouts

```python
layout = ui.layout("root") \
    .split_column("header", "main", "footer") \
    .update("header", "Header Content") \
    .update("main", "Main Content") \
    .update("footer", "Footer Content") \
    .show()
```

### Live Display

```python
from silantui import LiveChatDisplay

display = LiveChatDisplay()
display.start()

display.add_user_message("Hello!")
display.start_assistant_message()
display.append_streaming("Response...")
display.finish_assistant_message()

display.stop()
```

## 🎯 Command System

### Method 1: Decorator (Recommended)

```python
from silantui import CommandRegistry

registry = CommandRegistry()

@registry.command(
    "deploy",
    description="Deploy application",
    aliases=["d"],
    category="Operations",
    requires_args=True
)
def deploy_command(app, args):
    print(f"Deploying to {args}...")
```

### Method 2: Builder Pattern

```python
from silantui import CommandBuilder

cmd = CommandBuilder("backup") \
    .description("Backup data") \
    .aliases(["bk"]) \
    .category("Operations") \
    .handler(lambda app, args: print("Backing up...")) \
    .build()

registry.register(cmd)
```

### Method 3: Quick Register

```python
from silantui import quick_command

quick_command(
    registry,
    "status",
    lambda app, args: print("Status: OK"),
    description="Show status",
    aliases=["st"]
)
```

## 🤖 AI Integration (Optional)

SilanTui supports multiple AI providers through a universal client:

### OpenAI

```python
from silantui.integrations.universal_client import UniversalAIClient

client = UniversalAIClient(
    api_key="sk-...",
    model="gpt-4"
)
```

### Ollama (Local)

```python
client = UniversalAIClient(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
    model="llama2"
)
```

### Azure OpenAI

```python
client = AIClient(
    api_key="your-key",
    base_url="https://YOUR_RESOURCE.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT",
    model="gpt-4"
)
```

### Any Custom API

```python
client = AIClient(
    api_key="your-key",
    base_url="https://your-api.com/v1",
    model="your-model"
)
```

## 🎨 Custom Themes

```python
from silantui import UITheme, UIBuilder

theme = UITheme(
    primary="magenta",
    secondary="cyan",
    success="bright_green",
    warning="bright_yellow",
    error="bright_red"
)

ui = UIBuilder(theme=theme)
```

## 📖 Documentation

- **[CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md)** - Complete customization guide
- **[UI_ENHANCEMENT_NOTES.md](UI_ENHANCEMENT_NOTES.md)** - UI features documentation
- **[examples/](examples/)** - Full application examples

## 🎯 Use Cases

SilanTui is perfect for:

- **System Administration Tools** - Server management, monitoring dashboards
- **Development Tools** - Build tools, deployment scripts, code generators
- **Data Processing** - ETL pipelines, data analysis tools
- **Interactive Applications** - Games, tutorials, wizards
- **AI Applications** - Chatbots, code assistants, content generators (optional)

## 🏗️ Architecture

```
SilanTui Framework
├── Core UI Components
│   ├── ModernLogger      # Logging & output
│   ├── UIBuilder         # Component builder
│   ├── ChatDisplay       # Chat interface
│   └── LiveDisplay       # Real-time updates
│
├── Command System
│   ├── CommandRegistry   # Command management
│   ├── CommandBuilder    # Fluent command API
│   └── CommandManager    # Alias management
│
├── Optional Features
│   ├── AI Client         # Universal AI integration
│   ├── SessionManager    # State persistence
│   └── ThemeSystem       # Color customization
│
└── Examples
    ├── Dashboard         # Data visualization
    ├── Task Manager      # CRUD application
    └── AI Chat           # Optional AI app
```

## 🤝 Contributing

Contributions are welcome! SilanTui is designed to be a general-purpose UI framework.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE)

Copyright (c) 2024 [Silan Hu](https://silan.tech)

## Author

**Silan Hu**

- Website: [silan.tech](https://silan.tech)
- GitHub: [@Qingbolan](https://github.com/Qingbolan)

## 🙏 Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) by Will McGugan
- Inspired by modern TUI frameworks
- ASCII art by [pyfiglet](https://github.com/pwaller/pyfiglet)

## 🗺️ Roadmap

- [x] Core UI components (Tables, Panels, Menus, Forms)
- [x] Command system with multiple registration methods
- [x] Live display with fixed layouts
- [x] Internationalization (i18n) support
- [x] Optional AI integration with multiple providers
- [ ] More UI components (charts, graphs, trees)
- [ ] Plugin system
- [ ] Advanced configuration management
- [ ] Testing utilities and examples
- [ ] Documentation site
- [ ] More example applications
- [ ] Performance optimizations

---

**Build beautiful CLI applications with ease!** 🚀

```bash
pip install silantui
```

Made with ❤️ by [Silan Hu](https://silan.tech)
