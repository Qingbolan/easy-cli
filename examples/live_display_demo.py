#!/usr/bin/env python3
"""
Live Display and Markdown Demo - Demonstrates fixed input box and Markdown rendering
"""

from silantui import ModernLogger, ChatDisplay, LiveChatDisplay
from rich.markdown import Markdown
import time


def demo_chat_display():
    """Demo basic chat display"""
    logger = ModernLogger(name="chat-demo", level="info")

    logger.banner(
        project_name="Chat Display",
        title="Chat Display Demo",
        description="Fixed input box + Markdown rendering",
        font="slant"
    )

    # Create chat display
    display = ChatDisplay(console=logger.console)

    logger.section("Example 1: Basic message display")

    # Add user message
    display.add_user_message("Hello! Please introduce Python.")

    # Simulate AI streaming response
    display.start_assistant_message()

    ai_response = """Python is a high-level programming language.

## Key Features

1. **Simple and Readable** - Clear syntax
2. **Powerful** - Rich libraries
3. **Cross-platform** - Runs everywhere

### Code Example

```python
def hello():
    print("Hello, World!")
```

Perfect for beginners!"""

    # Simulate streaming output
    for char in ai_response:
        display.append_streaming(char)
        time.sleep(0.01)

    display.finish_assistant_message()

    # Display results
    display.show()

    logger.print()
    logger.success("Basic display demo complete!")
    logger.print()


def demo_live_display():
    """Demo live chat display"""
    logger = ModernLogger(name="live-demo", level="info")

    logger.banner(
        project_name="Live Display",
        title="Live Chat Display Demo",
        description="True fixed layout + real-time updates",
        font="slant"
    )

    logger.info("Starting live display...")
    logger.console.print("[dim]This demo shows the fixed bottom input box effect[/dim]\n")
    time.sleep(2)

    logger.console.clear()

    # Create live display
    display = LiveChatDisplay()
    display.start()

    try:
        # Simulate conversation 1
        time.sleep(1)
        display.add_user_message("What is Markdown?")
        time.sleep(0.5)

        display.start_assistant_message()

        response1 = """Markdown is a lightweight markup language.

## Basic Syntax

- **Bold**: `**text**`
- *Italic*: `*text*`
- `Code`: `` `code` ``

### Advantages

1. Easy to learn
2. Plain text format
3. Widely supported

Great for documentation!"""

        for char in response1:
            display.append_streaming(char)
            time.sleep(0.01)

        display.finish_assistant_message()
        time.sleep(2)

        # Simulate conversation 2
        display.add_user_message("Give me a Python code example")
        time.sleep(0.5)

        display.start_assistant_message()

        response2 = """Of course! Here's a simple Python example:

```python
# Define a function
def greet(name):
    return f"Hello, {name}!"

# Use the function
message = greet("World")
print(message)
```

**Output**: `Hello, World!`

This example demonstrates:
- Function definition
- String formatting
- Function calling"""

        for char in response2:
            display.append_streaming(char)
            time.sleep(0.01)

        display.finish_assistant_message()
        time.sleep(3)

        # Show success message
        display.show_success("Demo complete!")
        time.sleep(2)

    finally:
        display.stop()

    logger.console.print()
    logger.success("Live display demo complete!")
    logger.print()


def demo_markdown_rendering():
    """Demo Markdown rendering"""
    logger = ModernLogger(name="markdown-demo", level="info")

    logger.banner(
        project_name="Markdown",
        title="Markdown Rendering Demo",
        description="Shows complete Markdown support",
        font="slant"
    )

    logger.section("Markdown Rendering Example")

    markdown_text = """
# Welcome to SilanTui

## Features

SilanTui is a modern CLI framework with the following features:

### 1. Beautiful Terminal UI

- 🎨 Rich-powered interface
- 🌈 Gradient themes
- 📊 Progress bars and tables

### 2. AI Integration

Supports LLM API, providing:

1. **Streaming responses** - Real-time display
2. **Markdown rendering** - Formatted output
3. **Session management** - Auto-save

### 3. Code Examples

```python
from silantui import AIClient, ModernLogger

logger = ModernLogger(name="demo")
client = AIClient(api_key="your-key", logger=logger)

response = client.chat("Hello!")
print(response)
```

### 4. Quick Start

Installation is simple:

```bash
pip install silantui
silantui
```

---

## Custom Commands

Register commands using decorators:

```python
@registry.command("greet", description="Greet someone")
def greet_cmd(app, args):
    app.logger.info(f"Hello {args}!")
```

**Very simple!**

### More Information

Visit the [documentation](https://github.com/yourusername/silantui) to learn more.

> **Tip**: SilanTui makes CLI development simple and fun!
"""

    # Render Markdown
    md = Markdown(markdown_text)
    logger.console.print(md)

    logger.print()
    logger.success("Markdown rendering complete!")
    logger.print()

    logger.console.print("[bold cyan]Notes:[/bold cyan]")
    logger.console.print("  • Supports headers, lists, code blocks")
    logger.console.print("  • Supports bold, italic, links")
    logger.console.print("  • Supports quotes and separators")
    logger.console.print("  • Code blocks auto syntax highlighting")
    logger.print()


def main():
    """Main demo program"""
    logger = ModernLogger(name="main", level="info")

    logger.banner(
        project_name="Demos",
        title="SilanTui Display Features Demo",
        description="Fixed input box + Markdown rendering",
        font="slant"
    )

    logger.console.print("\n[bold cyan]Demo Menu:[/bold cyan]\n")
    logger.console.print("1. Basic Chat Display")
    logger.console.print("2. Live Chat Display (Fixed Layout)")
    logger.console.print("3. Markdown Rendering")
    logger.console.print("4. Run All Demos")
    logger.console.print()

    from rich.prompt import Prompt

    choice = Prompt.ask(
        "[yellow]Please select[/yellow]",
        choices=["1", "2", "3", "4"],
        default="4"
    )

    logger.console.clear()

    if choice == "1":
        demo_chat_display()
    elif choice == "2":
        demo_live_display()
    elif choice == "3":
        demo_markdown_rendering()
    elif choice == "4":
        demo_markdown_rendering()
        input("\nPress Enter to continue to next demo...")
        logger.console.clear()

        demo_chat_display()
        input("\nPress Enter to continue to next demo...")
        logger.console.clear()

        demo_live_display()

    logger.console.print()
    logger.highlight("All demos complete!")
    logger.console.print()
    logger.console.print("[bold green]✨ SilanTui New Features:[/bold green]")
    logger.console.print("  1. ✅ Fixed bottom input box")
    logger.console.print("  2. ✅ Complete Markdown rendering")
    logger.console.print("  3. ✅ Real-time streaming display")
    logger.console.print("  4. ✅ Beautiful message bubbles")
    logger.console.print()
    logger.success("Now you can enjoy a better chat experience!")


if __name__ == "__main__":
    main()
