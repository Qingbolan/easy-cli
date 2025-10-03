"""Configuration management system for SilanTui.

Provides automatic loading, saving, and validation of user configurations
including API keys, base URLs, model selections, and other settings.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


class ConfigManager:
    """Manages application configuration with auto-load and auto-save capabilities.

    Features:
    - Automatic loading from user config directory
    - Real-time saving on updates
    - Schema validation
    - Default values
    - Backward compatibility
    """

    DEFAULT_CONFIG = {
        "api": {
            "openai": {
                "api_key": "",
                "base_url": "https://api.openai.com/v1",
                "default_model": "gpt-4-turbo-preview",
            },
            "anthropic": {
                "api_key": "",
                "base_url": "https://api.anthropic.com",
                "default_model": "claude-3-opus-20240229",
            },
            "custom": {
                "api_key": "",
                "base_url": "",
                "default_model": "",
            },
        },
        "ui": {
            "theme": "default",
            "show_timestamps": True,
            "auto_save_chat": True,
        },
        "models": {
            "available": [
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-3.5-turbo",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ],
            "selected": "gpt-4-turbo-preview",
            "provider": "openai",
        },
        "chat": {
            "max_history": 100,
            "stream_response": True,
            "auto_title": True,
        },
        "metadata": {
            "version": "0.1.1",
            "created_at": None,
            "updated_at": None,
        },
    }

    def __init__(
        self,
        config_dir: Optional[Path] = None,
        config_name: str = "config.json",
        auto_save: bool = True,
    ):
        """Initialize the configuration manager.

        Args:
            config_dir: Custom config directory path. Defaults to ~/.silantui
            config_name: Configuration file name
            auto_save: Enable automatic saving on changes
        """
        self.auto_save = auto_save
        self.config_name = config_name

        # Set config directory (default: ~/.silantui)
        if config_dir is None:
            self.config_dir = Path.home() / ".silantui"
        else:
            self.config_dir = Path(config_dir)

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config_path = self.config_dir / self.config_name

        # Load or create configuration
        self.config: Dict[str, Any] = self._load_or_create()

    def _load_or_create(self) -> Dict[str, Any]:
        """Load existing config or create default one."""
        if self.config_path.exists():
            try:
                return self._load()
            except Exception as e:
                print(f"Warning: Failed to load config ({e}). Using defaults.")
                return self._create_default()
        else:
            return self._create_default()

    def _load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        with open(self.config_path, "r", encoding="utf-8") as f:
            loaded_config = json.load(f)

        # Merge with defaults to ensure all keys exist
        return self._merge_with_defaults(loaded_config)

    def _create_default(self) -> Dict[str, Any]:
        """Create and save default configuration."""
        config = self.DEFAULT_CONFIG.copy()
        config["metadata"]["created_at"] = datetime.now().isoformat()
        config["metadata"]["updated_at"] = datetime.now().isoformat()

        self._save(config)
        return config

    def _merge_with_defaults(self, loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults to handle missing keys."""
        def deep_merge(default: dict, loaded: dict) -> dict:
            result = default.copy()
            for key, value in loaded.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        return deep_merge(self.DEFAULT_CONFIG, loaded)

    def _save(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Save configuration to file."""
        if config is None:
            config = self.config

        # Update timestamp
        config["metadata"]["updated_at"] = datetime.now().isoformat()

        # Write to file
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def save(self) -> None:
        """Manually save current configuration."""
        self._save()

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation.

        Args:
            key_path: Dot-separated path (e.g., "api.openai.api_key")
            default: Default value if key not found

        Returns:
            Configuration value or default

        Examples:
            >>> config.get("api.openai.api_key")
            "sk-..."
            >>> config.get("models.selected")
            "gpt-4"
        """
        keys = key_path.split(".")
        value = self.config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any) -> None:
        """Set a configuration value using dot notation.

        Args:
            key_path: Dot-separated path (e.g., "api.openai.api_key")
            value: Value to set

        Examples:
            >>> config.set("api.openai.api_key", "sk-...")
            >>> config.set("models.selected", "gpt-4")
        """
        keys = key_path.split(".")
        target = self.config

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]

        # Set the value
        target[keys[-1]] = value

        # Auto-save if enabled
        if self.auto_save:
            self._save()

    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values.

        Args:
            updates: Dictionary of key paths and values

        Examples:
            >>> config.update({
            ...     "api.openai.api_key": "sk-...",
            ...     "models.selected": "gpt-4"
            ... })
        """
        for key_path, value in updates.items():
            keys = key_path.split(".")
            target = self.config

            for key in keys[:-1]:
                if key not in target:
                    target[key] = {}
                target = target[key]

            target[keys[-1]] = value

        # Auto-save once after all updates
        if self.auto_save:
            self._save()

    def get_api_config(self, provider: str = "openai") -> Dict[str, str]:
        """Get API configuration for a specific provider.

        Args:
            provider: API provider name (openai, anthropic, custom)

        Returns:
            Dictionary with api_key, base_url, and default_model
        """
        return self.get(f"api.{provider}", {})

    def set_api_config(
        self,
        provider: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
    ) -> None:
        """Set API configuration for a specific provider.

        Args:
            provider: API provider name
            api_key: API key
            base_url: Base URL for API
            default_model: Default model to use
        """
        updates = {}

        if api_key is not None:
            updates[f"api.{provider}.api_key"] = api_key
        if base_url is not None:
            updates[f"api.{provider}.base_url"] = base_url
        if default_model is not None:
            updates[f"api.{provider}.default_model"] = default_model

        self.update(updates)

    def add_model(self, model: str) -> None:
        """Add a model to available models list."""
        models = self.get("models.available", [])
        if model not in models:
            models.append(model)
            self.set("models.available", models)

    def set_selected_model(self, model: str, provider: Optional[str] = None) -> None:
        """Set the currently selected model.

        Args:
            model: Model name
            provider: Provider name (auto-detected if None)
        """
        updates = {"models.selected": model}

        if provider:
            updates["models.provider"] = provider
        else:
            # Auto-detect provider
            model_lower = model.lower()
            if "gpt" in model_lower or "openai" in model_lower:
                updates["models.provider"] = "openai"
            elif "claude" in model_lower:
                updates["models.provider"] = "anthropic"
            else:
                updates["models.provider"] = "custom"

        self.update(updates)

    def get_current_model_config(self) -> Dict[str, str]:
        """Get configuration for the currently selected model.

        Returns:
            Dictionary with model, provider, api_key, and base_url
        """
        model = self.get("models.selected")
        provider = self.get("models.provider")
        api_config = self.get_api_config(provider)

        return {
            "model": model,
            "provider": provider,
            "api_key": api_config.get("api_key", ""),
            "base_url": api_config.get("base_url", ""),
        }

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.config = self._create_default()

    def export_config(self, path: Path) -> None:
        """Export configuration to a file.

        Args:
            path: Export file path
        """
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def import_config(self, path: Path) -> None:
        """Import configuration from a file.

        Args:
            path: Import file path
        """
        with open(path, "r", encoding="utf-8") as f:
            imported = json.load(f)

        self.config = self._merge_with_defaults(imported)

        if self.auto_save:
            self._save()

    def __repr__(self) -> str:
        return f"ConfigManager(config_path={self.config_path})"


# Global config instance
_global_config: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get the global configuration instance.

    Returns:
        Global ConfigManager instance
    """
    global _global_config
    if _global_config is None:
        _global_config = ConfigManager()
    return _global_config


def set_config(config: ConfigManager) -> None:
    """Set the global configuration instance.

    Args:
        config: ConfigManager instance to use globally
    """
    global _global_config
    _global_config = config
