# SilanTui - Quick Start Guide

## 🚀 Installation (3 steps)

```bash
# 1. Extract
tar -xzf silantui.tar.gz
cd silantui

# 2. Install
pip install -e .

# 3. Run
export LLM_API_KEY="your-api-key"
silantui
```

## 🎯 First Chat

Once installed, just type:

```bash
silantui
```

Then start chatting! Type `/help` to see all commands.

## 🔧 Create Custom Commands

### Quick Method

```bash
# Create shortcuts
silantui --add-alias chat "silantui"
silantui --add-alias ai "silantui --model claude-sonnet-4-20250514"
silantui --add-alias code "silantui --system 'You are a coding assistant'"

# Now use them
chat        # Quick chat
ai          # With specific model
code        # Coding assistant
```

### Interactive Setup

```bash
silantui --setup-aliases
```

This will guide you through:
1. Adding/removing aliases
2. Installing to shell config (.bashrc/.zshrc)
3. Creating executable scripts

## 📝 Common Aliases

```bash
# Quick shortcuts
silantui --add-alias chat "silantui"
silantui --add-alias ai "silantui"

# Model selection
silantui --add-alias sonnet "silantui --model claude-sonnet-4-20250514"
silantui --add-alias opus "silantui --model claude-opus-4-20250514"

# Specialized assistants
silantui --add-alias code "silantui --system 'You are a coding assistant'"
silantui --add-alias write "silantui --system 'You are a creative writer'"
silantui --add-alias teach "silantui --system 'You are a teacher'"
```

## 💬 In-Chat Commands

Once in a chat session:

```
/help            - Show all commands
/new             - Start new conversation
/list            - See saved conversations
/export          - Save as Markdown
/model opus      - Switch to Opus model
/system <text>   - Set system prompt
/exit            - Quit
```

## 🐍 Python API

```python
from silantui import AIClient, ModernLogger

# Simple usage
logger = ModernLogger(name="demo")
client = AIClient(api_key="your-key", logger=logger)

# Stream response with beautiful UI
response = client.chat_stream_with_logger(
    "Tell me a joke",
    stream_title="Comedy Time"
)

# Command aliases
from silantui import CommandManager
cm = CommandManager()
cm.add_alias("mychat", "silantui")
```

## 🎨 Three Ways to Use Aliases

### 1. Shell Config (Best for daily use)

```bash
silantui --setup-aliases
# Choose option 3: "Install to shell config"
source ~/.bashrc  # or ~/.zshrc

# Now use anywhere
chat
ai
code
```

### 2. Executable Scripts (Cross-shell)

```bash
silantui --setup-aliases
# Choose option 4: "Create executable aliases"

# Works in any shell
chat
ai
```

### 3. Command Line (Quick)

```bash
silantui --add-alias myname "silantui --model opus"
myname  # If in PATH
```

## 📦 What You Get

- ✅ Beautiful terminal UI with Rich
- ✅ Streaming AI responses
- ✅ Automatic session saving
- ✅ Markdown rendering
- ✅ Custom command aliases
- ✅ Progress bars & indicators
- ✅ Export conversations
- ✅ Python API access

## 🔑 Get API Key

Refer to the project homepage for provider setup details: https://github.com/Qingbolan/silan-tui

## 🐛 Troubleshooting

### Command not found

```bash
# Make sure you installed
pip install -e .

# Check installation
which silantui

# Reinstall if needed
pip uninstall silantui
pip install -e .
```

### Alias not working

```bash
# For shell aliases, reload config
source ~/.bashrc  # or ~/.zshrc

# For executable aliases, check PATH
echo $PATH | grep ".local/bin"

# Add to PATH if missing
export PATH="$HOME/.local/bin:$PATH"
```

### API Key Error

```bash
# Set environment variable
export LLM_API_KEY="your-key"

# Or pass as argument
silantui --api-key "your-key"
```

## 📚 Next Steps

1. **Run examples**: `python examples/basic_chat.py`
2. **Read full docs**: Check `README.md`
3. **Customize**: Create your own aliases
4. **Build apps**: Use the Python API

## 💡 Pro Tips

1. **Create role-specific commands**:
   ```bash
   silantui --add-alias debug "silantui --log-level debug"
   silantui --add-alias teacher "silantui --system 'Explain like I am 5'"
   ```

2. **Use shorter names**:
   ```bash
   silantui --add-alias c "silantui"
   silantui --add-alias a "silantui --model opus"
   ```

3. **Combine options**:
   ```bash
   silantui --add-alias dev "silantui --model opus --log-level debug"
   ```

## 🎉 You're Ready!

Start chatting:
```bash
silantui
```

Or with your custom command:
```bash
chat
```

Enjoy SilanTui! 🚀
