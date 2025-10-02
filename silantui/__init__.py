"""
SilanTui
=======

A modern Terminal UI Framework for Python.

Author: Silan Hu (https://silan.tech)
License: MIT

Build beautiful command-line applications with:
- Rich UI components (Tables, Panels, Menus, Forms)
- Flexible command system
- Real-time displays
- Internationalization (i18n)
- Optional AI integration

Core Example:
    >>> from silantui import UIBuilder, ModernLogger
    >>> 
    >>> logger = ModernLogger(name="app")
    >>> ui = UIBuilder()
    >>> 
    >>> ui.table("Data").add_column("Name").add_row("Alice").show()
    
Commands Example:
    >>> from silantui import CommandRegistry
    >>> 
    >>> registry = CommandRegistry()
    >>> 
    >>> @registry.command("greet", description="Say hello")
    >>> def greet_cmd(app, args):
    >>>     print(f"Hello {args}!")

i18n Example:
    >>> from silantui.i18n import set_language, t
    >>> 
    >>> set_language('zh')  # Chinese
    >>> print(t('welcome'))  # 欢迎

AI Example (Optional):
    >>> from silantui.integrations.universal_client import UniversalAIClient
    >>> 
    >>> client = UniversalAIClient(api_key="key", model="gpt-4")
    >>> response = client.chat("Hello!")
"""

from .logging.modern import ModernLogger
from .core.session import ChatSession, SessionManager
from .ui.chat_ui import ChatUI
from .core.command_manager import CommandManager
from .core.command_system import (
    CommandRegistry,
    CommandInfo,
    CommandBuilder,
    quick_command,
    register_builtin_commands
)
from .ui.builder import (
    UIBuilder,
    UITheme,
    QuickUI,
    PanelBuilder,
    TableBuilder,
    LayoutBuilder,
    MenuBuilder,
    FormBuilder
)
from .ui.chat_display import ChatDisplay, LiveChatDisplay
from .integrations.AIClient import AIClient, PRESET_CONFIGS, get_preset_config

__version__ = "0.3.0"
__author__ = "Silan Hu"
__author_email__ = "contact@silan.tech"
__url__ = "https://silan.tech"
__license__ = "MIT"

__all__ = [
    # Core
    "ModernLogger",
    "ChatSession",
    "SessionManager",
    "ChatUI",
    "AIClient",
    "PRESET_CONFIGS",
    "get_preset_config",
    # Command System
    "CommandManager",
    "CommandRegistry",
    "CommandInfo",
    "CommandBuilder",
    "quick_command",
    "register_builtin_commands",
    # UI Builders
    "UIBuilder",
    "UITheme",
    "QuickUI",
    "PanelBuilder",
    "TableBuilder",
    "LayoutBuilder",
    "MenuBuilder",
    "FormBuilder",
    # Chat Display
    "ChatDisplay",
    "LiveChatDisplay",
]
