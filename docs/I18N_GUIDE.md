# Internationalization (i18n) Guide

SilanTui provides built-in support for internationalization, making it easy to build multilingual CLI applications.

## Quick Start

```python
from silantui.i18n import set_language, t

# Set language (default is 'en')
set_language('zh')  # Chinese
set_language('es')  # Spanish
set_language('fr')  # French
set_language('ja')  # Japanese

# Use translations
print(t('welcome'))       # Outputs in current language
print(t('success'))       # Translated message
print(t('error'))         # Translated error
```

## Supported Languages

Out of the box, SilanTui supports:

- **English (en)** - Default
- **Chinese (zh)** - 中文
- **Spanish (es)** - Español
- **French (fr)** - Français
- **Japanese (ja)** - 日本語

## Basic Usage

### 1. Simple Translation

```python
from silantui.i18n import t, set_language

# Set language
set_language('zh')

# Get translations
welcome_msg = t('welcome')        # "欢迎"
exit_msg = t('exit')              # "退出"
success_msg = t('success')        # "成功"
```

### 2. Format Arguments

```python
from silantui.i18n import t

# Translation with placeholders
msg = t('command.not_found', 'deploy')
# English: "Command not found: deploy"
# Chinese: "命令未找到: deploy"
```

### 3. Using with UIBuilder

```python
from silantui import UIBuilder
from silantui.i18n import t, set_language

ui = UIBuilder()
set_language('zh')

# All UI text uses translations
ui.panel(t('welcome'), "Content").show()
ui.success(t('success'))
ui.error(t('error'))
```

## Advanced Usage

### Custom Translations

#### Method 1: Add to Existing Translator

```python
from silantui.i18n import get_translator

translator = get_translator()

# Add single translation
translator.add_translation('en', 'app.title', 'My App')
translator.add_translation('zh', 'app.title', '我的应用')

# Add multiple translations
translator.add_translations('en', {
    'app.description': 'A great CLI app',
    'app.version': 'Version {0}',
})
```

#### Method 2: Load from JSON File

```python
from silantui.i18n import get_translator
from pathlib import Path

translator = get_translator()
translator.load_from_file(Path('translations.json'))
```

**translations.json format:**
```json
{
  "en": {
    "app.title": "My Application",
    "app.greeting": "Hello, {0}!"
  },
  "zh": {
    "app.title": "我的应用",
    "app.greeting": "你好，{0}！"
  }
}
```

### Create Custom Translator

```python
from silantui.i18n import Translator

# Create with custom translations
translator = Translator(
    language='zh',
    custom_translations={
        'custom_lang': {
            'key1': 'value1',
            'key2': 'value2',
        }
    }
)

# Use custom translator
translator.set_language('custom_lang')
print(translator.get('key1'))  # "value1"
```

## Built-in Translation Keys

### Common UI
- `welcome` - Welcome message
- `exit` - Exit
- `cancel` - Cancel
- `confirm` - Confirm
- `yes` - Yes
- `no` - No
- `ok` - OK
- `error` - Error
- `warning` - Warning
- `info` - Info
- `success` - Success

### Menu
- `menu.title` - Menu title
- `menu.select` - Selection prompt
- `menu.back` - Back button

### Commands
- `command.unknown` - Unknown command
- `command.help` - Help text
- `command.exit` - Exit command
- `command.clear` - Clear command
- `command.not_found` - Command not found (with format)

### Chat
- `chat.user` - User label
- `chat.assistant` - Assistant label
- `chat.typing` - Typing indicator
- `chat.new_session` - New session message
- `chat.session_cleared` - Session cleared
- `chat.session_saved` - Session saved

### Form
- `form.required` - Required field
- `form.invalid` - Invalid input
- `form.submit` - Submit button

### Table
- `table.empty` - No data message
- `table.total` - Total count

### Progress
- `progress.complete` - Complete message
- `progress.processing` - Processing message

### File
- `file.not_found` - File not found
- `file.saved` - File saved
- `file.loaded` - File loaded

## Complete Example

```python
from silantui import UIBuilder, ModernLogger, CommandRegistry
from silantui.i18n import set_language, t, get_translator
from rich.prompt import Prompt


class MultilingualApp:
    def __init__(self):
        self.ui = UIBuilder()
        self.logger = ModernLogger(name="app")
        self.registry = CommandRegistry()
        
        # Load custom translations
        translator = get_translator()
        translator.load_from_file('translations.json')
        
        # Set default language
        set_language('en')
        
        self.setup_commands()
    
    def setup_commands(self):
        @self.registry.command("lang", description="Change language")
        def change_lang(app, args):
            if args in ['en', 'zh', 'es', 'fr', 'ja']:
                set_language(args)
                app.ui.success(f"Language: {args}")
            else:
                app.ui.error("Invalid language code")
    
    def show_welcome(self):
        panel = self.ui.panel(
            t('welcome'),
            t('app.description')
        ).border("cyan").build()
        
        self.logger.console.print(panel)
    
    def show_menu(self):
        choice = self.ui.menu(t('menu.main')) \
            .add_item("1", t('menu.settings')) \
            .add_item("2", t('exit')) \
            .show()
        
        return choice
    
    def run(self):
        self.show_welcome()
        
        while True:
            choice = self.show_menu()
            
            if choice == "2":
                self.logger.console.print(f"\n{t('exit')}...\n")
                break


if __name__ == "__main__":
    app = MultilingualApp()
    app.run()
```

## Language Detection

### From Environment

```python
import os
from silantui.i18n import set_language

# Detect from system
system_lang = os.getenv('LANG', 'en_US').split('_')[0]
set_language(system_lang if system_lang in ['en', 'zh', 'es', 'fr', 'ja'] else 'en')
```

### User Selection

```python
from silantui import UIBuilder
from silantui.i18n import set_language

ui = UIBuilder()

lang = ui.menu("Select Language / 选择语言") \
    .add_item("en", "English") \
    .add_item("zh", "中文") \
    .add_item("es", "Español") \
    .add_item("fr", "Français") \
    .add_item("ja", "日本語") \
    .show()

set_language(lang)
```

## Best Practices

### 1. Use Translation Keys Consistently

```python
# Good: Use translation keys
ui.success(t('success'))
ui.error(t('error'))

# Avoid: Hard-coded text
ui.success("Success!")  # Not translatable
```

### 2. Organize Keys Hierarchically

```python
# Use dot notation for organization
t('app.title')
t('app.description')
t('menu.main')
t('menu.settings')
t('settings.language')
```

### 3. Load Translations Early

```python
def main():
    # Load translations at startup
    translator = get_translator()
    translator.load_from_file('translations.json')
    
    # Set language
    set_language('zh')
    
    # Run app
    app = MyApp()
    app.run()
```

### 4. Provide Fallbacks

```python
# SilanTui automatically falls back to English
# if a key is missing in the current language
set_language('zh')
print(t('some.missing.key'))  # Falls back to English if not in Chinese
```

## Testing Translations

```python
from silantui.i18n import Translator

def test_translations():
    translator = Translator()
    
    # Test all languages
    for lang in ['en', 'zh', 'es', 'fr', 'ja']:
        translator.set_language(lang)
        
        assert translator.get('welcome') != 'welcome'
        assert translator.get('success') != 'success'
        
        print(f"{lang}: {translator.get('welcome')}")

test_translations()
```

## Adding New Languages

```python
from silantui.i18n import get_translator

translator = get_translator()

# Add German translations
translator.add_translations('de', {
    'welcome': 'Willkommen',
    'exit': 'Beenden',
    'success': 'Erfolg',
    'error': 'Fehler',
    # ... more translations
})

# Save to file for reuse
translator.save_to_file('translations.json')
```

## Summary

SilanTui's i18n system provides:

✅ **Built-in Support** - 5 languages out of the box  
✅ **Easy Integration** - Simple `t()` function  
✅ **Custom Translations** - Add your own languages  
✅ **File Loading** - Load from JSON  
✅ **Format Support** - String formatting with placeholders  
✅ **Fallback System** - Automatic fallback to English  
✅ **Framework Integration** - Works with all UI components  

**Start building multilingual CLI applications today!**

```python
from silantui.i18n import set_language, t

set_language('zh')
print(t('welcome'))  # 欢迎
```
