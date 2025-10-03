# Textual Chat Interface

## Overview

SilanTui now includes a modern, Textual-based chat interface that provides a superior user experience compared to the traditional Rich-based implementation.

## Why Textual?

**Textual** is a modern TUI framework built by the same team that created Rich. It provides:

- **True Interactivity**: Native event-driven architecture
- **Automatic Scrolling**: Built-in mouse wheel and keyboard navigation
- **No Flickering**: Efficient rendering without manual refresh cycles
- **Better Performance**: Optimized for complex UIs
- **CSS Styling**: Theme and style your components
- **Responsive Layout**: Automatically adapts to terminal size

## Quick Start

### Simple Usage

```python
from silantui import run_chat_app

# Launch a chat interface in one line
run_chat_app(role="Assistant")
```

### Custom Chat Application

```python
from silantui import ChatApp

class MyChatApp(ChatApp):
    def simulate_response(self, user_message: str):
        """Override this method to add your AI logic"""
        # Example: Echo response
        response = f"You said: {user_message}"
        self.add_assistant_message(response)

        # Or with streaming:
        # self.start_streaming()
        # for chunk in generate_chunks(user_message):
        #     self.append_streaming(chunk)
        # self.finish_streaming(full_response)

# Run your app
app = MyChatApp(role="My Bot")
app.run()
```

## Features

### User Messages
- **Styling**: Light grey background (`grey93`) with `>` prefix
- **Format**: `> Your message here`

### Assistant Messages
- **Metadata Header**: Shows role, timestamp, and duration
- **Format**: `* 「Role/Time/Duration」`
- **Content**: Full Markdown rendering

### Keyboard Shortcuts
- **Enter**: Submit message
- **Ctrl+C**: Quit application
- **Ctrl+N**: Start new chat (clear history)
- **Escape**: Focus input field
- **Arrow Keys**: Navigate chat history
- **Page Up/Down**: Scroll by page
- **Home/End**: Jump to top/bottom

### Mouse Support
- **Scroll Wheel**: Scroll through chat history
- **Click**: Focus input field

## Architecture

### Components

#### `ChatApp`
Main application class that manages the entire TUI.

**Key Methods**:
- `add_user_message(content)`: Add user message to history
- `add_assistant_message(content, duration)`: Add assistant message
- `start_streaming()`: Begin streaming response
- `append_streaming(chunk)`: Append streaming chunk
- `finish_streaming(content)`: Complete streaming response

#### `ChatHistory`
Scrollable message history widget based on `RichLog`.

**Features**:
- Auto-scroll to bottom on new messages
- Mouse wheel scrolling
- Keyboard navigation
- Markdown rendering

#### `ChatInput`
Interactive input widget for message composition.

**Features**:
- Submit on Enter
- Placeholder text
- Command detection
- Yellow border with horizontal lines

## Comparison: Rich vs Textual

| Feature | Rich (`LiveChatDisplay`) | Textual (`ChatApp`) |
|---------|-------------------------|---------------------|
| **Scrolling** | Manual implementation | Native support |
| **Input** | Stop/start cycles | True interactive |
| **Performance** | Manual refresh | Event-driven |
| **Mouse** | Limited | Full support |
| **Keyboard Nav** | Custom implementation | Built-in |
| **Layout** | Manual management | Responsive |
| **Styling** | Limited | CSS-based |
| **Complexity** | High | Low |

## Advanced Usage

### Streaming Responses

```python
from silantui import ChatApp
import time

class StreamingChatApp(ChatApp):
    def simulate_response(self, user_message: str):
        # Start streaming indicator
        self.start_streaming()

        # Generate response word by word
        response = "This is a streaming response..."
        words = response.split()

        for word in words:
            self.append_streaming(word + " ")
            time.sleep(0.05)  # Simulate network delay

        # Finish and render final markdown
        self.finish_streaming(response)

app = StreamingChatApp(role="Streaming Bot")
app.run()
```

### Custom Commands

```python
from silantui import ChatApp
from rich.text import Text

class CommandChatApp(ChatApp):
    def handle_command(self, command: str):
        """Override to add custom commands"""
        cmd = command.lower().strip()

        if cmd == "/stats":
            chat_history = self.query_one("#chat-history")
            stats = Text(f"Total messages: {self.message_count}", style="cyan")
            chat_history.write(stats)
        elif cmd == "/time":
            import time
            chat_history = self.query_one("#chat-history")
            current_time = Text(time.strftime("%Y-%m-%d %H:%M:%S"), style="green")
            chat_history.write(current_time)
        else:
            # Fall back to default command handling
            super().handle_command(command)

app = CommandChatApp(role="Command Bot")
app.run()
```

### Custom Styling

```python
from silantui import ChatApp

class ThemedChatApp(ChatApp):
    CSS = """
    ChatApp {
        background: #1a1a1a;
    }

    Header {
        background: #2d5016;
        color: #ffffff;
    }

    ChatHistory {
        border: solid #4a9d2a;
        background: #0d0d0d;
    }

    ChatInput {
        border: solid #4a9d2a;
        background: #1a1a1a;
    }
    """

app = ThemedChatApp(role="Themed Bot")
app.run()
```

## Integration with AI APIs

### OpenAI Example

```python
from silantui import ChatApp
import openai

class OpenAIChatApp(ChatApp):
    def __init__(self, api_key: str, model: str = "gpt-4", **kwargs):
        super().__init__(**kwargs)
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.conversation = []

    def simulate_response(self, user_message: str):
        # Add to conversation history
        self.conversation.append({"role": "user", "content": user_message})

        # Start streaming
        self.start_streaming()

        try:
            # Call OpenAI API with streaming
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation,
                stream=True
            )

            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    self.append_streaming(content)

            # Add to conversation history
            self.conversation.append({"role": "assistant", "content": full_response})

            # Finish streaming
            self.finish_streaming(full_response)

        except Exception as e:
            self.finish_streaming(f"Error: {str(e)}")

# Run
app = OpenAIChatApp(
    api_key="your-api-key",
    model="gpt-4",
    role="GPT-4"
)
app.run()
```

## Migration Guide

### From LiveChatDisplay to ChatApp

**Old (Rich-based)**:
```python
from silantui import LiveChatDisplay
from rich.console import Console

console = Console()
chat = LiveChatDisplay(console=console, role="Bot")
chat.start()

# Main loop
while True:
    user_input = chat.read_input()
    if user_input == "/exit":
        break

    chat.add_user_message(user_input)
    chat.start_assistant_message()
    # ... streaming ...
    chat.finish_assistant_message()

chat.stop()
```

**New (Textual-based)**:
```python
from silantui import ChatApp

class MyChatApp(ChatApp):
    def simulate_response(self, user_message: str):
        # Your response logic here
        self.add_assistant_message(f"Response: {user_message}")

app = MyChatApp(role="Bot")
app.run()
```

## Troubleshooting

### Issue: Application doesn't start

**Solution**: Ensure Textual is installed:
```bash
pip install textual
```

### Issue: Scrolling not working

**Solution**: Make sure your terminal supports mouse events. Try:
- Modern terminals: iTerm2, Windows Terminal, Alacritty
- Enable mouse support in your terminal settings

### Issue: Colors look wrong

**Solution**: Ensure your terminal supports 256 colors or true color:
```bash
echo $TERM  # Should show something like 'xterm-256color'
```

## Best Practices

1. **Use Textual for new projects**: It's the recommended approach
2. **Override `simulate_response()`**: This is where your AI logic goes
3. **Use streaming for long responses**: Better UX
4. **Handle errors gracefully**: Wrap API calls in try/except
5. **Keep conversation history**: For context-aware responses

## Examples

Check out these demo files:
- `demo/textual_chat_demo.py` - Basic interactive demo
- `demo/chat_app.py` - Full-featured chat with AI integration

## License

MIT License - See LICENSE file for details
