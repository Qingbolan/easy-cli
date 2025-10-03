"""Advanced configuration patterns and use cases.

This example shows advanced patterns for using ConfigForm in real applications.
"""

from silantui.ui.config_input import ConfigForm, TextInput, SelectInput, TableSelectInput
from silantui.core import get_config, ConfigManager
from rich.console import Console
from rich.prompt import Confirm
from typing import Dict, Any


class MultiProviderAPIConfig:
    """Multi-provider API configuration manager."""

    def __init__(self, console: Console):
        self.console = console
        self.config = get_config()

    def get_provider_form(self, provider: str) -> ConfigForm:
        """Get configuration form for specific provider."""
        forms = {
            "openai": self._create_openai_form,
            "anthropic": self._create_anthropic_form,
            "azure": self._create_azure_form,
            "local": self._create_local_form,
        }

        form_creator = forms.get(provider)
        if not form_creator:
            raise ValueError(f"Unknown provider: {provider}")

        return form_creator()

    def _create_openai_form(self) -> ConfigForm:
        """Create OpenAI configuration form."""
        models = [
            {"model": "gpt-4-turbo-preview", "speed": "Fast", "cost": "$$"},
            {"model": "gpt-4", "speed": "Medium", "cost": "$$$"},
            {"model": "gpt-3.5-turbo", "speed": "Very Fast", "cost": "$"},
        ]

        return (
            ConfigForm(
                title="OpenAI Configuration",
                description="Configure OpenAI API access",
                console=self.console,
                auto_load=True,
                auto_save=True,
            )
            .add_text("api.openai.api_key", "API Key", password=True)
            .add_text("api.openai.organization", "Organization ID (optional)")
            .add_text("api.openai.base_url", "Base URL", default="https://api.openai.com/v1")
            .add_table_select(
                "api.openai.default_model",
                "Default Model",
                choices=models,
                columns=["model", "speed", "cost"],
                value_key="model",
            )
        )

    def _create_anthropic_form(self) -> ConfigForm:
        """Create Anthropic configuration form."""
        models = [
            {"model": "claude-3-opus-20240229", "tier": "Premium", "context": "200K"},
            {"model": "claude-3-sonnet-20240229", "tier": "Standard", "context": "200K"},
            {"model": "claude-3-haiku-20240307", "tier": "Fast", "context": "200K"},
        ]

        return (
            ConfigForm(
                title="Anthropic Configuration",
                description="Configure Anthropic Claude API access",
                console=self.console,
                auto_load=True,
                auto_save=True,
            )
            .add_text("api.anthropic.api_key", "API Key", password=True)
            .add_text("api.anthropic.base_url", "Base URL", default="https://api.anthropic.com")
            .add_table_select(
                "api.anthropic.default_model",
                "Default Model",
                choices=models,
                columns=["model", "tier", "context"],
                value_key="model",
            )
        )

    def _create_azure_form(self) -> ConfigForm:
        """Create Azure OpenAI configuration form."""
        return (
            ConfigForm(
                title="Azure OpenAI Configuration",
                description="Configure Azure OpenAI Service",
                console=self.console,
                auto_load=True,
                auto_save=True,
            )
            .add_text("api.azure.api_key", "API Key", password=True)
            .add_text("api.azure.endpoint", "Endpoint", placeholder="https://your-resource.openai.azure.com")
            .add_text("api.azure.deployment_name", "Deployment Name")
            .add_text("api.azure.api_version", "API Version", default="2024-02-15-preview")
        )

    def _create_local_form(self) -> ConfigForm:
        """Create local model configuration form."""
        return (
            ConfigForm(
                title="Local Model Configuration",
                description="Configure local LLM endpoint (Ollama, LM Studio, etc.)",
                console=self.console,
                auto_load=True,
                auto_save=True,
            )
            .add_text("api.local.base_url", "Base URL", default="http://localhost:11434")
            .add_text("api.local.model", "Model Name", placeholder="llama2, mistral, etc.")
            .add_select(
                "api.local.backend",
                "Backend",
                choices=["ollama", "lm-studio", "text-generation-webui", "vllm"],
                default="ollama"
            )
        )

    def setup(self):
        """Interactive setup for API configuration."""
        self.console.print("\n[bold cyan]Multi-Provider API Configuration[/bold cyan]\n")

        # Select provider
        providers = {
            "1": ("OpenAI", "openai"),
            "2": ("Anthropic Claude", "anthropic"),
            "3": ("Azure OpenAI", "azure"),
            "4": ("Local Model", "local"),
        }

        self.console.print("[bold]Select Provider:[/bold]")
        for key, (name, _) in providers.items():
            self.console.print(f"{key}. {name}")

        from rich.prompt import Prompt
        choice = Prompt.ask("\nEnter choice", choices=list(providers.keys()), default="1")

        provider_name, provider_key = providers[choice]

        # Get and run form
        form = self.get_provider_form(provider_key)

        # Check for existing config
        has_existing = any(self.config.get(field.key) for field in form.fields)

        if has_existing:
            self.console.print(f"\n[yellow]Existing {provider_name} configuration:[/yellow]")
            self.console.print(form.render_panel())

            if not Confirm.ask("\nUpdate configuration?", default=True):
                return

        # Prompt for config
        values = form.prompt_all()

        # Save provider selection
        self.config.set("models.provider", provider_key)

        self.console.print(f"\n[bold green]✓ {provider_name} configuration saved![/bold green]")


class DatabaseConfig:
    """Database configuration example."""

    def __init__(self, console: Console):
        self.console = console

    def setup(self):
        """Setup database configuration."""
        self.console.print("\n[bold cyan]Database Configuration[/bold cyan]\n")

        # Database type selection
        db_types = [
            {"type": "PostgreSQL", "category": "SQL", "default_port": "5432"},
            {"type": "MySQL", "category": "SQL", "default_port": "3306"},
            {"type": "MongoDB", "category": "NoSQL", "default_port": "27017"},
            {"type": "Redis", "category": "Cache", "default_port": "6379"},
        ]

        form = (
            ConfigForm(
                title="Database Setup",
                description="Configure database connection",
                console=self.console,
                auto_load=True,
                auto_save=True,
            )
            .add_table_select(
                "database.type",
                "Database Type",
                choices=db_types,
                columns=["type", "category", "default_port"],
                value_key="type",
            )
            .add_text("database.host", "Host", default="localhost")
            .add_text("database.port", "Port", default="5432")
            .add_text("database.database", "Database Name")
            .add_text("database.username", "Username")
            .add_text("database.password", "Password", password=True)
            .add_select(
                "database.ssl",
                "SSL Mode",
                choices=["disable", "require", "verify-ca", "verify-full"],
                default="disable"
            )
        )

        values = form.prompt_all()

        # Generate connection string
        db_type = values.get("database.type", "").lower()
        if "postgres" in db_type:
            conn_str = self._postgres_connection_string(values)
        elif "mysql" in db_type:
            conn_str = self._mysql_connection_string(values)
        elif "mongo" in db_type:
            conn_str = self._mongo_connection_string(values)
        else:
            conn_str = None

        if conn_str:
            self.console.print(f"\n[dim]Connection string: {conn_str}[/dim]")

    def _postgres_connection_string(self, values: Dict[str, Any]) -> str:
        """Generate PostgreSQL connection string."""
        return (
            f"postgresql://{values.get('database.username')}:"
            f"{values.get('database.password')}@"
            f"{values.get('database.host')}:{values.get('database.port')}/"
            f"{values.get('database.database')}"
        )

    def _mysql_connection_string(self, values: Dict[str, Any]) -> str:
        """Generate MySQL connection string."""
        return (
            f"mysql://{values.get('database.username')}:"
            f"{values.get('database.password')}@"
            f"{values.get('database.host')}:{values.get('database.port')}/"
            f"{values.get('database.database')}"
        )

    def _mongo_connection_string(self, values: Dict[str, Any]) -> str:
        """Generate MongoDB connection string."""
        return (
            f"mongodb://{values.get('database.username')}:"
            f"{values.get('database.password')}@"
            f"{values.get('database.host')}:{values.get('database.port')}/"
            f"{values.get('database.database')}"
        )


class ApplicationConfig:
    """Complete application configuration."""

    def __init__(self, console: Console):
        self.console = console

    def setup(self):
        """Setup complete application configuration."""
        self.console.print("\n[bold cyan]Application Configuration Wizard[/bold cyan]\n")

        sections = [
            ("General", self._setup_general),
            ("API Provider", self._setup_api),
            ("UI Preferences", self._setup_ui),
            ("Advanced", self._setup_advanced),
        ]

        for section_name, setup_func in sections:
            self.console.print(f"\n[bold magenta]→ {section_name}[/bold magenta]")
            setup_func()

        self.console.print("\n[bold green]✓ Configuration complete![/bold green]")

    def _setup_general(self):
        """Setup general configuration."""
        form = (
            ConfigForm(
                title="General Settings",
                console=self.console,
                auto_load=True,
                auto_save=True,
            )
            .add_text("app.name", "Application Name", default="SilanTui App")
            .add_text("app.version", "Version", default="1.0.0")
            .add_select(
                "app.environment",
                "Environment",
                choices=["development", "staging", "production"],
                default="development"
            )
        )
        form.prompt_all()

    def _setup_api(self):
        """Setup API configuration."""
        api_config = MultiProviderAPIConfig(self.console)
        api_config.setup()

    def _setup_ui(self):
        """Setup UI preferences."""
        form = (
            ConfigForm(
                title="UI Preferences",
                console=self.console,
                auto_load=True,
                auto_save=True,
            )
            .add_select("ui.theme", "Theme", choices=["dark", "light", "auto"], default="dark")
            .add_select("ui.language", "Language", choices=["en", "zh", "ja", "es"], default="en")
            .add_select("chat.max_history", "Chat History", choices=["50", "100", "200", "unlimited"], default="100")
        )
        form.prompt_all()

    def _setup_advanced(self):
        """Setup advanced options."""
        if not Confirm.ask("\nConfigure advanced options?", default=False):
            return

        form = (
            ConfigForm(
                title="Advanced Settings",
                console=self.console,
                auto_load=True,
                auto_save=True,
            )
            .add_text("advanced.timeout", "Request Timeout (seconds)", default="30")
            .add_text("advanced.max_retries", "Max Retries", default="3")
            .add_select("advanced.log_level", "Log Level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
        )
        form.prompt_all()


if __name__ == "__main__":
    console = Console()

    examples = {
        "1": ("Multi-Provider API Config", lambda: MultiProviderAPIConfig(console).setup()),
        "2": ("Database Config", lambda: DatabaseConfig(console).setup()),
        "3": ("Complete Application Setup", lambda: ApplicationConfig(console).setup()),
    }

    console.print("\n[bold cyan]Advanced Configuration Examples[/bold cyan]\n")
    for key, (name, _) in examples.items():
        console.print(f"{key}. {name}")

    from rich.prompt import Prompt
    choice = Prompt.ask("\nSelect example", choices=list(examples.keys()), default="1")

    _, example_func = examples[choice]
    example_func()
