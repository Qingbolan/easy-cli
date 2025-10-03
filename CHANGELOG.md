# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2025-01-03

### 🚀 Major Features

#### Textual Chat Interface
- **NEW**: Complete rewrite of chat interface using Textual framework
- **ChatApp**: Modern TUI application with full interactivity
- **ChatHistory**: Native scrolling with mouse and keyboard support
- **ChatInput**: True interactive input without stop/start cycles
- **Better UX**: Event-driven architecture, no flickering
- **Streaming**: Real-time AI response streaming built-in
- **Theming**: CSS-based styling system

### ✨ Enhancements

#### UI Improvements
- User messages now display with light grey background (`grey93`)
- Assistant messages with metadata header (role/time/duration)
- Double horizontal lines (`─`) for input field separation
- Automatic scrolling to bottom on new messages
- Better markdown rendering for AI responses

#### Architecture
- Migrated from manual Rich Live management to Textual's event system
- Removed complex scroll offset tracking (now handled by Textual)
- Simplified input handling (no more pause/resume cycles)
- Better separation of concerns

### 📝 Documentation
- Added `docs/TEXTUAL_CHAT.md` - Complete Textual chat guide
- Updated main README with Textual examples
- Added migration guide from Rich to Textual
- Included OpenAI/Anthropic integration examples

### 🎯 New Demos
- `demo/textual_chat_demo.py` - Interactive demo with simulated responses
- `demo/textual_ai_chat.py` - Production-ready AI chat application
- Both demos showcase streaming and command handling

### 🔧 API Changes

#### New Exports
```python
from silantui import (
    ChatApp,          # Main Textual chat application
    ChatHistory,      # Scrollable history widget
    ChatInput,        # Interactive input widget
    run_chat_app,     # Quick start function
)
```

#### Recommended Usage
```python
# Old (Rich-based - still supported)
from silantui import LiveChatDisplay
display = LiveChatDisplay()
display.start()
# ... manual input loop ...

# New (Textual-based - RECOMMENDED)
from silantui import ChatApp
class MyChatApp(ChatApp):
    def simulate_response(self, user_message: str):
        self.add_assistant_message(f"Response: {user_message}")

app = MyChatApp(role="Bot")
app.run()
```

### 🐛 Bug Fixes
- Fixed header stacking issue in Rich-based LiveChatDisplay
- Fixed frame append/scroll issues with Live display
- Removed unnecessary pause/resume logic
- Fixed input field losing focus

### ⚡ Performance
- Better rendering performance with Textual's optimized engine
- Reduced CPU usage during idle
- Faster scrolling with native Textual widgets
- Eliminated unnecessary full redraws

### 🎨 Styling
- Consistent color scheme across components
- Better contrast for user messages
- Cleaner input field borders
- Improved spacing between messages

### 📦 Dependencies
- Added `textual` as core dependency
- Maintained compatibility with existing Rich-based components
- No breaking changes to existing APIs

### 🔄 Migration Path
Both Rich and Textual implementations are available:
- **Legacy apps**: Continue using `LiveChatDisplay`
- **New apps**: Use `ChatApp` for better UX
- **Gradual migration**: Both can coexist in same project

## [0.3.0] - Previous Release

### Features
- Rich-based chat display
- Command system
- UI builders
- i18n support
- AI client integration

---

## Migration Guide: 0.3.x → 0.4.0

### No Breaking Changes
All existing code continues to work. The new Textual interface is additive.

### Recommended Updates

**Before (Rich-based)**:
```python
from silantui import LiveChatDisplay
from rich.console import Console

console = Console()
chat = LiveChatDisplay(console=console)
chat.start()

while True:
    msg = chat.read_input()
    if msg == "/exit":
        break
    chat.add_user_message(msg)
    # ... AI logic ...

chat.stop()
```

**After (Textual-based)**:
```python
from silantui import ChatApp

class MyChatApp(ChatApp):
    def simulate_response(self, user_message: str):
        # Your AI logic here
        self.add_assistant_message(f"Response: {user_message}")

app = MyChatApp(role="Assistant")
app.run()
```

### Benefits of Migration
1. **Better UX**: No input blocking, smoother interactions
2. **Less Code**: Event-driven, no manual loops
3. **Native Features**: Scrolling, mouse support, keyboard shortcuts
4. **Easier Testing**: Textual has built-in testing tools
5. **Future-Proof**: Active development, more features coming

### Quick Migration Checklist
- [ ] Install textual: `pip install textual`
- [ ] Create subclass of `ChatApp`
- [ ] Move response logic to `simulate_response()`
- [ ] Replace main loop with `app.run()`
- [ ] Test scrolling and keyboard shortcuts
- [ ] Update documentation/examples

## Support

For questions, issues, or contributions:
- GitHub: https://github.com/yourusername/silan-tui
- Email: contact@silan.tech
- Website: https://silan.tech
