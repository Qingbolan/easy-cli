"""
Internationalization (i18n) Module for SilanTui
Supports multiple languages with English as default
"""

from typing import Dict, Optional
from pathlib import Path
import json


class Translator:
    """
    Simple translation system for SilanTui
    
    Usage:
        >>> t = Translator()
        >>> t.set_language('zh')
        >>> print(t.get('welcome'))
        欢迎
    """
    
    # Default translations (English)
    DEFAULT_TRANSLATIONS = {
        'en': {
            # Common UI
            'welcome': 'Welcome',
            'exit': 'Exit',
            'cancel': 'Cancel',
            'confirm': 'Confirm',
            'yes': 'Yes',
            'no': 'No',
            'ok': 'OK',
            'error': 'Error',
            'warning': 'Warning',
            'info': 'Info',
            'success': 'Success',
            
            # Menu
            'menu.title': 'Menu',
            'menu.select': 'Please select',
            'menu.back': 'Back',
            
            # Commands
            'command.unknown': 'Unknown command',
            'command.help': 'Show help',
            'command.exit': 'Exit application',
            'command.clear': 'Clear screen',
            'command.not_found': 'Command not found: {0}',
            
            # Chat
            'chat.user': 'You',
            'chat.assistant': 'Assistant',
            'chat.typing': 'Typing...',
            'chat.new_session': 'New session created',
            'chat.session_cleared': 'Session cleared',
            'chat.session_saved': 'Session saved',
            
            # Form
            'form.required': 'Required',
            'form.invalid': 'Invalid input',
            'form.submit': 'Submit',
            
            # Table
            'table.empty': 'No data',
            'table.total': 'Total',
            
            # Progress
            'progress.complete': 'Complete',
            'progress.processing': 'Processing...',
            
            # File
            'file.not_found': 'File not found',
            'file.saved': 'File saved',
            'file.loaded': 'File loaded',
            
            # Logger
            'logger.level.debug': 'DEBUG',
            'logger.level.info': 'INFO',
            'logger.level.warning': 'WARNING',
            'logger.level.error': 'ERROR',
            'logger.level.critical': 'CRITICAL',
        },
        
        'zh': {
            # Common UI
            'welcome': '欢迎',
            'exit': '退出',
            'cancel': '取消',
            'confirm': '确认',
            'yes': '是',
            'no': '否',
            'ok': '好的',
            'error': '错误',
            'warning': '警告',
            'info': '信息',
            'success': '成功',
            
            # Menu
            'menu.title': '菜单',
            'menu.select': '请选择',
            'menu.back': '返回',
            
            # Commands
            'command.unknown': '未知命令',
            'command.help': '显示帮助',
            'command.exit': '退出应用',
            'command.clear': '清空屏幕',
            'command.not_found': '命令未找到: {0}',
            
            # Chat
            'chat.user': '你',
            'chat.assistant': '助手',
            'chat.typing': '正在输入...',
            'chat.new_session': '已创建新会话',
            'chat.session_cleared': '会话已清空',
            'chat.session_saved': '会话已保存',
            
            # Form
            'form.required': '必填',
            'form.invalid': '输入无效',
            'form.submit': '提交',
            
            # Table
            'table.empty': '无数据',
            'table.total': '总计',
            
            # Progress
            'progress.complete': '完成',
            'progress.processing': '处理中...',
            
            # File
            'file.not_found': '文件未找到',
            'file.saved': '文件已保存',
            'file.loaded': '文件已加载',
            
            # Logger
            'logger.level.debug': '调试',
            'logger.level.info': '信息',
            'logger.level.warning': '警告',
            'logger.level.error': '错误',
            'logger.level.critical': '严重',
        },
        
        'es': {
            # Common UI
            'welcome': 'Bienvenido',
            'exit': 'Salir',
            'cancel': 'Cancelar',
            'confirm': 'Confirmar',
            'yes': 'Sí',
            'no': 'No',
            'ok': 'OK',
            'error': 'Error',
            'warning': 'Advertencia',
            'info': 'Información',
            'success': 'Éxito',
            
            # Menu
            'menu.title': 'Menú',
            'menu.select': 'Por favor seleccione',
            'menu.back': 'Volver',
            
            # Commands
            'command.unknown': 'Comando desconocido',
            'command.help': 'Mostrar ayuda',
            'command.exit': 'Salir de la aplicación',
            'command.clear': 'Limpiar pantalla',
            'command.not_found': 'Comando no encontrado: {0}',
            
            # Chat
            'chat.user': 'Tú',
            'chat.assistant': 'Asistente',
            'chat.typing': 'Escribiendo...',
            'chat.new_session': 'Nueva sesión creada',
            'chat.session_cleared': 'Sesión borrada',
            'chat.session_saved': 'Sesión guardada',
        },
        
        'fr': {
            # Common UI
            'welcome': 'Bienvenue',
            'exit': 'Quitter',
            'cancel': 'Annuler',
            'confirm': 'Confirmer',
            'yes': 'Oui',
            'no': 'Non',
            'ok': 'OK',
            'error': 'Erreur',
            'warning': 'Avertissement',
            'info': 'Information',
            'success': 'Succès',
            
            # Menu
            'menu.title': 'Menu',
            'menu.select': 'Veuillez sélectionner',
            'menu.back': 'Retour',
            
            # Commands
            'command.unknown': 'Commande inconnue',
            'command.help': 'Afficher l\'aide',
            'command.exit': 'Quitter l\'application',
            'command.clear': 'Effacer l\'écran',
            'command.not_found': 'Commande introuvable: {0}',
            
            # Chat
            'chat.user': 'Vous',
            'chat.assistant': 'Assistant',
            'chat.typing': 'Écriture...',
            'chat.new_session': 'Nouvelle session créée',
            'chat.session_cleared': 'Session effacée',
            'chat.session_saved': 'Session sauvegardée',
        },
        
        'ja': {
            # Common UI
            'welcome': 'ようこそ',
            'exit': '終了',
            'cancel': 'キャンセル',
            'confirm': '確認',
            'yes': 'はい',
            'no': 'いいえ',
            'ok': 'OK',
            'error': 'エラー',
            'warning': '警告',
            'info': '情報',
            'success': '成功',
            
            # Menu
            'menu.title': 'メニュー',
            'menu.select': '選択してください',
            'menu.back': '戻る',
            
            # Commands
            'command.unknown': '不明なコマンド',
            'command.help': 'ヘルプを表示',
            'command.exit': 'アプリケーションを終了',
            'command.clear': '画面をクリア',
            'command.not_found': 'コマンドが見つかりません: {0}',
            
            # Chat
            'chat.user': 'あなた',
            'chat.assistant': 'アシスタント',
            'chat.typing': '入力中...',
            'chat.new_session': '新しいセッションが作成されました',
            'chat.session_cleared': 'セッションがクリアされました',
            'chat.session_saved': 'セッションが保存されました',
        },
    }
    
    def __init__(self, language: str = 'en', custom_translations: Optional[Dict] = None):
        """
        Initialize translator
        
        Args:
            language: Language code (en, zh, es, fr, ja, etc.)
            custom_translations: Custom translation dictionary
        """
        self.current_language = language
        self.translations = self.DEFAULT_TRANSLATIONS.copy()
        
        if custom_translations:
            self.translations.update(custom_translations)
    
    def set_language(self, language: str):
        """Set current language"""
        if language not in self.translations:
            available = ', '.join(self.translations.keys())
            raise ValueError(f"Language '{language}' not supported. Available: {available}")
        self.current_language = language
    
    def get_language(self) -> str:
        """Get current language"""
        return self.current_language
    
    def get(self, key: str, *args, **kwargs) -> str:
        """
        Get translated text
        
        Args:
            key: Translation key
            *args: Format arguments
            **kwargs: Format keyword arguments
            
        Returns:
            Translated text
            
        Example:
            >>> t.get('command.not_found', 'test')
            'Command not found: test'
        """
        # Get translation for current language, fallback to English
        lang_dict = self.translations.get(self.current_language, {})
        text = lang_dict.get(key)
        
        if text is None:
            # Fallback to English
            text = self.translations.get('en', {}).get(key, key)
        
        # Format text with arguments
        if args or kwargs:
            try:
                text = text.format(*args, **kwargs)
            except (KeyError, IndexError):
                pass
        
        return text
    
    def add_translation(self, language: str, key: str, value: str):
        """
        Add or update a translation
        
        Args:
            language: Language code
            key: Translation key
            value: Translation value
        """
        if language not in self.translations:
            self.translations[language] = {}
        self.translations[language][key] = value
    
    def add_translations(self, language: str, translations: Dict[str, str]):
        """
        Add multiple translations for a language
        
        Args:
            language: Language code
            translations: Dictionary of translations
        """
        if language not in self.translations:
            self.translations[language] = {}
        self.translations[language].update(translations)
    
    def load_from_file(self, file_path: Path):
        """
        Load translations from JSON file
        
        Args:
            file_path: Path to JSON file
            
        File format:
            {
                "en": {"key": "value"},
                "zh": {"key": "值"}
            }
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for lang, trans in data.items():
                self.add_translations(lang, trans)
    
    def save_to_file(self, file_path: Path):
        """
        Save translations to JSON file
        
        Args:
            file_path: Path to JSON file
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.translations, f, ensure_ascii=False, indent=2)
    
    def get_available_languages(self) -> list:
        """Get list of available languages"""
        return list(self.translations.keys())
    
    def __call__(self, key: str, *args, **kwargs) -> str:
        """Shorthand for get()"""
        return self.get(key, *args, **kwargs)


# Global translator instance
_global_translator = Translator()


def get_translator() -> Translator:
    """Get global translator instance"""
    return _global_translator


def set_language(language: str):
    """Set global language"""
    _global_translator.set_language(language)


def get_language() -> str:
    """Get current global language"""
    return _global_translator.get_language()


def t(key: str, *args, **kwargs) -> str:
    """
    Shorthand for translation
    
    Example:
        >>> from silantui.i18n import t, set_language
        >>> set_language('zh')
        >>> print(t('welcome'))
        欢迎
    """
    return _global_translator.get(key, *args, **kwargs)


__all__ = [
    'Translator',
    'get_translator',
    'set_language',
    'get_language',
    't',
]
