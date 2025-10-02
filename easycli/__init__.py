"""
EasyCli
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
    >>> from easycli import UIBuilder, ModernLogger
    >>> 
    >>> logger = ModernLogger(name="app")
    >>> ui = UIBuilder()
    >>> 
    >>> ui.table("Data").add_column("Name").add_row("Alice").show()
    
Commands Example:
    >>> from easycli import CommandRegistry
    >>> 
    >>> registry = CommandRegistry()
    >>> 
    >>> @registry.command("greet", description="Say hello")
    >>> def greet_cmd(app, args):
    >>>     print(f"Hello {args}!")

i18n Example:
    >>> from easycli.i18n import set_language, t
    >>> 
    >>> set_language('zh')  # Chinese
    >>> print(t('welcome'))  # 欢迎

AI Example (Optional):
    >>> from easycli.ai_client import UniversalAIClient
    >>> 
    >>> client = UniversalAIClient(api_key="key", model="gpt-4")
    >>> response = client.chat("Hello!")
"""

from .logger import ModernLogger
from .session import ChatSession, SessionManager
from .ui import ChatUI
from .command_manager import CommandManager
from .command_system import (
    CommandRegistry,
    CommandInfo,
    CommandBuilder,
    quick_command,
    register_builtin_commands
)
from .ui_builder import (
    UIBuilder,
    UITheme,
    QuickUI,
    PanelBuilder,
    TableBuilder,
    LayoutBuilder,
    MenuBuilder,
    FormBuilder
)
from .chat_display import LiveChatDisplay

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
