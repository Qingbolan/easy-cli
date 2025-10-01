# EasyCli Chat Display Demos

This directory contains demonstration scripts showcasing the new minimalist chat interface design.

## Features Demonstrated

### 🎨 Visual Design
- **Minimalist Input Box**: Fixed at bottom with horizontal line separators
- **User Messages**: White background with `>` prefix (no borders)
- **AI Messages**: Animated `*` indicator with metadata in `「」` brackets
- **Status Display**: Real-time status shown above input (left-aligned)
- **Mode Display**: Current mode shown below input at left, tips at right

### ⚡ Animations
- **Pulsing Star**: The `*` indicator pulses during streaming (`*` → `✦` → `✧`)
- **Typing Indicator**: Visual feedback when AI is responding
- **Streaming Cursor**: Live cursor `▌` showing real-time text generation

### 📊 Information Display
- **Metadata Format**: `「Role/Time/Duration」`
  - Role: Optional, shows only if configured (e.g., "Assistant")
  - Time: Current time in HH:MM:SS format
  - Duration: Response generation time in seconds
- **Example**: `* 「Assistant/14:23:45/2.3s」`

## Demo Scripts

### 1. `chat_display_demo.py` - Automated Demo
**Purpose**: Shows all features automatically with pre-scripted conversations

**Features**:
- Automated conversation flow
- Multiple demo messages
- Shows all UI features in action
- No interaction required

**Usage**:
```bash
cd /Users/silan/Documents/github/Easy-Cli
python demo/chat_display_demo.py
```

**What You'll See**:
1. Welcome screen explaining features
2. Three pre-scripted conversations
3. Demonstrates streaming, timing, and all visual elements
4. Summary of features at the end

---

### 2. `interactive_chat_demo.py` - Interactive Demo
**Purpose**: Try the interface yourself with simulated AI responses

**Features**:
- Type your own messages
- Simulated AI responses
- Command support (/exit, /new, /help)
- Real interaction experience

**Usage**:
```bash
cd /Users/silan/Documents/github/Easy-Cli
python demo/interactive_chat_demo.py
```

**Available Commands**:
- `/exit` - Quit the demo
- `/new` - Clear chat history
- `/help` - Show help message

**What You'll See**:
1. Interactive input prompt
2. Your messages displayed with white background
3. AI responses with animated indicators
4. Real-time status updates
5. Duration tracking for each response

## Technical Details

### Display Layout
```
┌─────────────────────────────────────────────────────────┐
│                  Header (EasyCli title)                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  > User message with white background                   │
│                                                         │
│  * 「Assistant/14:23:45/2.3s」                          │
│  AI response content with Markdown support...           │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Ready                                                  │ ← Status (left-aligned)
│  ──────────────────────────────────────────────────────│ ← Separator
│  > Type your message...                                 │ ← Input prompt
│  ──────────────────────────────────────────────────────│ ← Separator
│  interactive                    Type / for commands     │ ← Mode (left) + Tips (right)
└─────────────────────────────────────────────────────────┘
```

### Animation Cycle
The `*` indicator cycles through three states during streaming:
1. Frame 1: `*` (standard asterisk)
2. Frame 2: `✦` (medium star)
3. Frame 3: `✧` (small star)

Cycle speed: ~3 frames per second

### Color Scheme
- **User messages**: Black text on white background
- **AI indicator**: Bold green `*`
- **Metadata**: Dim gray text
- **Status**: Changes based on state (dim/green)
- **Mode**: Cyan dim text
- **Borders**: Dim horizontal lines

## Requirements

All demos use the EasyCli library components:
- `easycli.chat_display.LiveChatDisplay`
- `rich` library for terminal UI

Make sure you have the parent directory in your Python path or run from the project root.

## Customization

### Setting Custom Role
```python
chat_display = LiveChatDisplay(
    console=console,
    role="Assistant",  # Your custom role name
    mode="chat"
)
```

### Setting Custom Mode
```python
chat_display = LiveChatDisplay(
    console=console,
    role="Helper",
    mode="streaming"  # Your custom mode (e.g., "debug", "api", etc.)
)
```

### Without Role (Only Time/Duration)
```python
chat_display = LiveChatDisplay(console=console)
# Display: * 「14:23:45/2.3s」
```

### With Role (Role/Time/Duration)
```python
chat_display = LiveChatDisplay(console=console, role="Assistant")
# Display: * 「Assistant/14:23:45/2.3s」
```

## Tips

1. **Terminal Size**: Works best with terminal width ≥ 80 characters
2. **Color Support**: Requires a terminal that supports ANSI colors
3. **Performance**: Streaming updates at ~10 FPS for smooth animation
4. **Markdown**: AI responses support full Markdown formatting

## Troubleshooting

**Issue**: Animation looks choppy
- **Solution**: Update your terminal emulator or increase refresh rate

**Issue**: Colors not displaying
- **Solution**: Ensure your terminal supports ANSI/24-bit colors

**Issue**: Layout looks broken
- **Solution**: Resize terminal to at least 80 columns width

## Next Steps

After exploring the demos, you can:
1. Integrate the `LiveChatDisplay` into your own applications
2. Customize colors and styles to match your theme
3. Connect to real AI APIs for actual conversations
4. Extend with additional features and commands

## License

Part of the EasyCli project. See parent directory for license information.
