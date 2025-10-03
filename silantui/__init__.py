"""
SilanTui
=======

A modern Terminal UI Framework for Python - powered by Rich and Textual.

Author: Silan Hu (https://silan.tech)
License: MIT

Build beautiful command-line applications with:
- Rich UI components (Tables, Panels, Menus, Forms)
- Textual-based interactive chat interfaces
- Flexible command system
- Real-time displays with automatic scrolling
- Internationalization (i18n)
- Optional AI integration

Core Example:
    >>> from silantui import UIBuilder, ModernLogger
    >>>
    >>> logger = ModernLogger(name="app")
    >>> ui = UIBuilder()
    >>>
    >>> ui.table("Data").add_column("Name").add_row("Alice").show()

Textual Chat Example:
    >>> from silantui import ChatApp, run_chat_app
    >>>
    >>> # Quick start
    >>> run_chat_app(role="Assistant")
    >>>
    >>> # Or customize
    >>> class MyChatApp(ChatApp):
    >>>     def simulate_response(self, user_message: str):
    >>>         # Your AI logic here
    >>>         self.add_assistant_message(f"Response to: {user_message}")
    >>>
    >>> app = MyChatApp(role="My Bot")
    >>> app.run()

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
from .ui.textual_chat import ChatApp, ChatHistory, ChatInput, run_chat_app
from .ui.chat_ui import ChatUI, ChatUIApp
from .integrations.AIClient import AIClient, PRESET_CONFIGS, get_preset_config

__version__ = "0.4.0"
__author__ = "Silan Hu"
__author_email__ = "contact@silan.tech"
__url__ = "https://silan.tech"
__license__ = "MIT"

__all__ = [
    # Core
    "ModernLogger",
    "ChatSession",
    "SessionManager",
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
    # UI Builders (Textual-based)
    "UIBuilder",
    "UITheme",
    "QuickUI",
    "PanelBuilder",
    "TableBuilder",
    "LayoutBuilder",
    "MenuBuilder",
    "FormBuilder",
    # Textual Chat (Main Interface)
    "ChatApp",
    "ChatHistory",
    "ChatInput",
    "run_chat_app",
    "ChatUI",
    "ChatUIApp",
]
