# SilanTui Customization Guide

## 🎯 Overview

SilanTui v0.2.0 introduces powerful command systems and UI builders, making it incredibly convenient to:

1. **Add Custom Commands** - 3 methods, super simple
2. **Build Beautiful UIs** - Method chaining, WYSIWYG
3. **Create Interactive Components** - Menus, forms, layouts, etc.

## 📚 Table of Contents

- [Custom Commands](#custom-commands)
- [UI Component Building](#ui-component-building)
- [Complete Examples](#complete-examples)
- [Best Practices](#best-practices)

---

## 🎮 Custom Commands

### Method 1: Decorator Registration (Recommended)

The simplest and most direct approach:

```python
from silantui import CommandRegistry

registry = CommandRegistry()

@registry.command(
    "greet",                           # Command name
    description="Greet someone",       # Description
    usage="/greet <name>",             # Usage instructions
    aliases=["hi", "hello"],           # Aliases
    category="Social",                 # Category
    requires_args=True                 # Whether arguments are required
)
def greet_command(app, args: str):
    app.logger.info(f"Hello, {args}!")

# Usage
registry.execute("greet", app, "John")
```

### Method 2: CommandBuilder (Flexible)

Suitable for scenarios requiring dynamic command construction:

```python
from silantui import CommandBuilder

def my_handler(app, args: str):
    app.logger.success(f"Processing args: {args}")

cmd = CommandBuilder("mycommand") \
    .description("My custom command") \
    .usage("/mycommand <args>") \
    .aliases(["mc", "my"]) \
    .category("Custom") \
    .requires_args(True) \
    .handler(my_handler) \
    .build()

registry.register(cmd)
```

### Method 3: Quick Registration (Minimal)

One line of code:

```python
from silantui import quick_command

quick_command(
    registry,
    "time",
    lambda app, args: app.logger.info(f"Time: {args}"),
    description="Display time",
    aliases=["t"]
)
```

### Using Custom Commands in Your Application

```python
from silantui import ChatApplication

class MyApp(ChatApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add custom commands
        self.register_custom_commands()

    def register_custom_commands(self):
        @self.command_registry.command("joke", description="Tell a joke")
        def tell_joke(app, args):
            app.logger.info("Why do programmers prefer dark mode? Because light attracts bugs!")

        @self.command_registry.command("count", description="Count numbers", requires_args=True)
        def count_command(app, args):
            try:
                n = int(args)
                for i in range(1, n + 1):
                    app.logger.console.print(f"{i}...")
            except ValueError:
                app.ui.show_error("Please enter a number")
```

---

## 🎨 UI Component Building

### UIBuilder - Core Builder

```python
from silantui import UIBuilder

ui = UIBuilder()
```

### 1. Panel

```python
# Basic usage
panel = ui.panel("Title", "Content").build()

# Method chaining
panel = ui.panel("Title", "Content") \
    .border("cyan") \
    .padding((2, 4)) \
    .subtitle("Subtitle") \
    .expand(True) \
    .build()

# Direct display
ui.panel("Title", "Content").border("green").show()
```

### 2. Table

```python
# Create table
table = ui.table("User List") \
    .add_column("ID", style="cyan", width=10) \
    .add_column("Name", style="green") \
    .add_column("Status", style="yellow") \
    .add_row("1", "Alice", "Online") \
    .add_row("2", "Bob", "Offline") \
    .build()

# Or display directly
ui.table("Data") \
    .add_column("Column1") \
    .add_column("Column2") \
    .add_row("Value1", "Value2") \
    .show()
```

### 3. Menu

```python
# Create interactive menu
def on_item1():
    print("Option 1 selected")

choice = ui.menu("Main Menu") \
    .add_item("1", "Option 1", handler=on_item1, description="This is option 1") \
    .add_item("2", "Option 2", description="This is option 2") \
    .add_separator() \
    .add_item("3", "Exit") \
    .show()

print(f"User selected: {choice}")
```

### 4. Form

```python
# Create form
results = ui.form("User Registration") \
    .add_field("username", "Username", required=True) \
    .add_field("age", "Age", field_type="int", default=18) \
    .add_field("email", "Email", required=True) \
    .add_field("subscribe", "Subscribe to notifications", field_type="confirm", default=True) \
    .add_field("theme", "Theme", field_type="choice",
              choices=["light", "dark", "auto"]) \
    .show()

print(f"Submitted data: {results}")
```

### 5. Layout

```python
# Create complex layout
layout = ui.layout("root") \
    .split_column("header", "main", "footer") \
    .size("header", 3) \
    .size("footer", 3) \
    .update("header", ui.panel("Title", "Welcome").build()) \
    .update("main", "Main content area") \
    .update("footer", "Footer info") \
    .build()

# Display
ui.layout("root") \
    .split_row("left", "center", "right") \
    .update("left", "Left") \
    .update("center", "Center") \
    .update("right", "Right") \
    .show()
```

### QuickUI - Quick Components

```python
from silantui import QuickUI

quick = QuickUI()

# Messages
ui.success("Operation successful!")
ui.error("An error occurred!")
ui.warning("Warning message!")
ui.info("Info message!")

# Confirmation dialog
if quick.yes_no("Are you sure you want to continue?"):
    print("User confirmed")

# List selection
items = ["Option 1", "Option 2", "Option 3"]
choice = quick.select_from_list("Please select", items)

# Quick table
quick.data_table(
    "Data",
    ["Column1", "Column2", "Column3"],
    [
        ["Value1", "Value2", "Value3"],
        ["Value4", "Value5", "Value6"]
    ]
)

# Info box
quick.info_box("Info", "This is a message", style="info")

# Three-column layout
quick.three_column_layout(
    left_content="Left content",
    center_content="Center content",
    right_content="Right content"
)
```

### Custom Theme

```python
from silantui import UIBuilder, UITheme

# Create custom theme
theme = UITheme(
    primary="magenta",
    secondary="cyan",
    success="bright_green",
    warning="bright_yellow",
    error="bright_red",
    info="bright_blue"
)

# Use theme
ui = UIBuilder(theme=theme)
ui.panel("Title", "Content").border(theme.primary).show()
```

---

## 📝 Complete Examples

### Example 1: Create a Todo Manager

```python
from silantui import CommandRegistry, UIBuilder, ChatSession

class TodoApp:
    def __init__(self):
        self.registry = CommandRegistry()
        self.ui = UIBuilder()
        self.todos = []
        self.register_commands()

    def register_commands(self):
        @self.registry.command("add", description="Add todo", requires_args=True)
        def add_todo(app, args):
            app.todos.append({"task": args, "done": False})
            app.ui.success(f"Added: {args}")

        @self.registry.command("list", description="Show list", aliases=["ls"])
        def list_todos(app, args):
            if not app.todos:
                app.ui.info("List is empty")
                return

            table = app.ui.table("📝 Todo List")
            table.add_column("#", width=5)
            table.add_column("Task", style="cyan")
            table.add_column("Status", width=10)

            for i, todo in enumerate(app.todos, 1):
                status = "✓ Done" if todo["done"] else "○ Pending"
                table.add_row(str(i), todo["task"], status)

            table.show()

        @self.registry.command("done", description="Mark as done", requires_args=True)
        def mark_done(app, args):
            try:
                index = int(args) - 1
                if 0 <= index < len(app.todos):
                    app.todos[index]["done"] = True
                    app.ui.success("Marked as done")
                else:
                    app.ui.error("Invalid number")
            except ValueError:
                app.ui.error("Please enter a number")

    def run(self):
        print("Todo Manager - Type /help to see commands")
        while True:
            cmd = input("\n> ").strip()
            if cmd.startswith("/"):
                parts = cmd.split(maxsplit=1)
                command = parts[0][1:]
                args = parts[1] if len(parts) > 1 else ""

                if command == "exit":
                    break

                try:
                    self.registry.execute(command, self, args)
                except Exception as e:
                    self.ui.error(str(e))

# Run
app = TodoApp()
app.run()
```

### Example 2: Create a Configuration Wizard

```python
from silantui import UIBuilder, QuickUI

def config_wizard():
    ui = UIBuilder()
    quick = QuickUI()

    # Show welcome
    ui.panel(
        "Welcome to Configuration Wizard",
        "We will help you complete initial configuration"
    ).border("cyan").show()

    # Collect configuration
    config = ui.form("Basic Configuration") \
        .add_field("name", "Application Name", required=True) \
        .add_field("port", "Port", field_type="int", default=8080) \
        .add_field("debug", "Debug Mode", field_type="confirm", default=False) \
        .add_field("theme", "Theme", field_type="choice",
                  choices=["light", "dark", "auto"], default="dark") \
        .show()

    # Confirm configuration
    table = ui.table("Configuration Summary")
    table.add_column("Item", style="cyan")
    table.add_column("Value", style="green")

    for key, value in config.items():
        table.add_row(key, str(value))

    table.show()

    # Confirm save
    if quick.yes_no("Confirm saving configuration?"):
        quick.info_box("Success", "Configuration saved!", style="success")
        return config
    else:
        quick.warning("Configuration not saved")
        return None

# Run wizard
config_wizard()
```

---

## 💡 Best Practices

### 1. Command Organization

```python
# Group by functionality
@registry.command("user.add", category="User Management")
def add_user(app, args): pass

@registry.command("user.delete", category="User Management")
def delete_user(app, args): pass

@registry.command("data.export", category="Data")
def export_data(app, args): pass
```

### 2. Error Handling

```python
@registry.command("divide", requires_args=True)
def divide_command(app, args):
    try:
        a, b = map(int, args.split())
        result = a / b
        app.ui.success(f"Result: {result}")
    except ValueError:
        app.ui.error("Please enter two numbers")
    except ZeroDivisionError:
        app.ui.error("Divisor cannot be zero")
    except Exception as e:
        app.ui.error(f"An error occurred: {e}")
```

### 3. UI Component Reuse

```python
def create_status_panel(title, status, message):
    color = "green" if status == "success" else "red"
    icon = "✓" if status == "success" else "✗"

    return ui.panel(
        f"{icon} {title}",
        message
    ).border(color).build()

# Usage
success_panel = create_status_panel("Operation Successful", "success", "File saved")
error_panel = create_status_panel("Operation Failed", "error", "Network error")
```

### 4. Method Chaining

```python
# Good practice - method chaining
ui.table("Data") \
    .add_column("A") \
    .add_column("B") \
    .add_row("1", "2") \
    .show()

# Also acceptable - step by step
table = ui.table("Data")
table.add_column("A")
table.add_column("B")
table.add_row("1", "2")
table.show()
```

### 5. Theme Consistency

```python
# Define application theme
APP_THEME = UITheme(
    primary="cyan",
    secondary="magenta",
    success="green",
    warning="yellow",
    error="red"
)

# Use globally
ui = UIBuilder(theme=APP_THEME)
```

---

## 🎯 Quick Reference

### Command System

| Method | Purpose | Example |
|------|------|------|
| `@registry.command()` | Decorator registration | `@registry.command("cmd")` |
| `CommandBuilder` | Builder pattern | `CommandBuilder("cmd").build()` |
| `quick_command()` | Quick registration | `quick_command(registry, "cmd", handler)` |
| `registry.execute()` | Execute command | `registry.execute("cmd", app, args)` |

### UI Components

| Component | Method | Example |
|------|------|------|
| Panel | `ui.panel()` | `ui.panel("Title", "Content").show()` |
| Table | `ui.table()` | `ui.table("Title").add_column().show()` |
| Menu | `ui.menu()` | `ui.menu("Menu").add_item().show()` |
| Form | `ui.form()` | `ui.form("Form").add_field().show()` |
| Layout | `ui.layout()` | `ui.layout().split_column().show()` |

### Quick Methods

| Method | Purpose |
|------|------|
| `ui.success()` | Success message |
| `ui.error()` | Error message |
| `ui.warning()` | Warning message |
| `ui.info()` | Info message |
| `ui.confirm()` | Confirmation dialog |

---

## 🚀 Getting Started

```bash
# Run complete example
python examples/custom_commands_ui.py

# In your project
from silantui import CommandRegistry, UIBuilder

registry = CommandRegistry()
ui = UIBuilder()

# Start creating your commands and UI!
```

---

**Now you can easily extend SilanTui!** 🎉

Check out `examples/custom_commands_ui.py` for more inspiration.
