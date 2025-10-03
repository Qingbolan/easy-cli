"""API Configuration Wizard for Chat Demo.

Interactive wizard using SilanTui components to configure LLM API settings.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from silantui.ui import ConfigForm, UIBuilder, InteractiveSelect
from silantui.core import get_config
from typing import Dict, Any


def select_provider(console) -> str:
    """Select provider using InteractiveSelect."""
    providers = [
        {"name": "OpenAI", "key": "openai", "desc": "GPT-4, GPT-3.5"},
        {"name": "Anthropic", "key": "anthropic", "desc": "Claude 3 Opus, Sonnet, Haiku"},
        {"name": "Custom API", "key": "custom", "desc": "OpenAI-compatible API"},
    ]

    selector = InteractiveSelect(
        choices=providers,
        title="Select LLM Provider",
        columns=["name", "desc"],
        value_key="key",
        console=console
    )

    return selector.prompt()


def create_openai_form(console) -> ConfigForm:
    """Create OpenAI configuration form."""
    form = (
        ConfigForm(
            title="OpenAI API Configuration",
            description="Configure OpenAI API credentials and model",
            auto_load=True,
            auto_save=True,
            console=console
        )
        .add_text(
            "api.openai.api_key",
            "API Key",
            password=True,
            placeholder="sk-..."
        )
        .add_text(
            "api.openai.base_url",
            "Base URL (optional)",
            default="https://api.openai.com/v1"
        )
    )

    return form


def select_openai_model(console) -> str:
    """Select OpenAI model using InteractiveSelect."""
    models = [
        {"name": "gpt-4-turbo-preview", "speed": "Fast", "cost": "$$", "context": "128K"},
        {"name": "gpt-4", "speed": "Medium", "cost": "$$$", "context": "8K"},
        {"name": "gpt-3.5-turbo", "speed": "Very Fast", "cost": "$", "context": "16K"},
    ]

    selector = InteractiveSelect(
        choices=models,
        title="Select OpenAI Model",
        columns=["name", "speed", "cost", "context"],
        value_key="name",
        console=console
    )

    return selector.prompt()


def create_anthropic_form(console) -> ConfigForm:
    """Create Anthropic configuration form."""
    form = (
        ConfigForm(
            title="Anthropic API Configuration",
            description="Configure Anthropic Claude API credentials and model",
            auto_load=True,
            auto_save=True,
            console=console
        )
        .add_text(
            "api.anthropic.api_key",
            "API Key",
            password=True,
            placeholder="sk-ant-..."
        )
        .add_text(
            "api.anthropic.base_url",
            "Base URL (optional)",
            default="https://api.anthropic.com"
        )
    )

    return form


def select_anthropic_model(console) -> str:
    """Select Anthropic model using InteractiveSelect."""
    models = [
        {"name": "claude-3-opus-20240229", "tier": "Most Capable", "context": "200K"},
        {"name": "claude-3-sonnet-20240229", "tier": "Balanced", "context": "200K"},
        {"name": "claude-3-haiku-20240307", "tier": "Fastest", "context": "200K"},
    ]

    selector = InteractiveSelect(
        choices=models,
        title="Select Claude Model",
        columns=["name", "tier", "context"],
        value_key="name",
        console=console
    )

    return selector.prompt()


def create_custom_form(console) -> ConfigForm:
    """Create custom API configuration form."""
    form = (
        ConfigForm(
            title="Custom API Configuration",
            description="Configure custom OpenAI-compatible API (Ollama, LM Studio, etc.)",
            auto_load=True,
            auto_save=True,
            console=console
        )
        .add_text(
            "api.custom.base_url",
            "Base URL",
            placeholder="http://localhost:11434/v1"
        )
        .add_text(
            "api.custom.api_key",
            "API Key (optional, use 'none' for local)",
            password=True,
            default="not-required"
        )
        .add_text(
            "api.custom.default_model",
            "Model Name",
            placeholder="llama2, mistral, etc."
        )
    )

    return form


def run_configuration_wizard() -> Dict[str, Any]:
    """Run the complete configuration wizard.

    Returns:
        Configuration dictionary
    """
    ui = UIBuilder()
    config = get_config()

    # Welcome message
    ui.console.clear()
    welcome_panel = (
        ui.panel(
            "🤖 Setup Wizard",
            "[bold cyan]LLM API Configuration Wizard[/bold cyan]\n\n"
            "Welcome! This wizard will help you configure your AI chat application.\n\n"
            "Steps:\n"
            "  1. Select your AI provider\n"
            "  2. Enter API credentials\n"
            "  3. Choose a model\n\n"
            "[dim]All settings are saved automatically to ~/.silantui/config.json[/dim]"
        )
        .border("cyan")
        .build()
    )
    ui.console.print(welcome_panel)
    ui.console.print()

    # Step 1: Select provider
    provider = select_provider(ui.console)

    if not provider:
        ui.console.print("[yellow]Selection cancelled.[/yellow]")
        return {}

    ui.console.print()

    # Step 2: Configure provider
    if provider == "openai":
        form = create_openai_form(ui.console)
        config.set("models.provider", "openai")

        # Prompt for credentials
        values = form.prompt_all()

        # Select model with InteractiveSelect
        ui.console.print()
        model = select_openai_model(ui.console)
        if model:
            config.set("models.selected", model)

    elif provider == "anthropic":
        form = create_anthropic_form(ui.console)
        config.set("models.provider", "anthropic")

        # Prompt for credentials
        values = form.prompt_all()

        # Select model with InteractiveSelect
        ui.console.print()
        model = select_anthropic_model(ui.console)
        if model:
            config.set("models.selected", model)

    else:
        form = create_custom_form(ui.console)
        config.set("models.provider", "custom")
        # For custom, model name is in different location
        values = form.prompt_all()
        model = values.get("api.custom.default_model")
        if model:
            config.set("models.selected", model)

    # Show completion message
    ui.console.print()
    completion_panel = (
        ui.panel(
            "Success",
            f"[bold green]✓ Configuration Complete![/bold green]\n\n"
            f"Provider: [cyan]{provider.title()}[/cyan]\n"
            f"Model: [cyan]{config.get('models.selected')}[/cyan]\n\n"
            f"[dim]Settings saved to: {config.config_path}[/dim]"
        )
        .border("green")
        .build()
    )
    ui.console.print(completion_panel)
    ui.console.print()

    return values


def check_existing_config() -> bool:
    """Check if valid configuration exists.

    Returns:
        True if configuration exists and is valid
    """
    config = get_config()

    provider = config.get("models.provider")
    if not provider:
        return False

    api_key = config.get(f"api.{provider}.api_key")
    model = config.get("models.selected")

    return bool(api_key and model)


def show_current_config():
    """Show current configuration using SilanTui components."""
    ui = UIBuilder()
    config = get_config()

    provider = config.get("models.provider", "None")
    model = config.get("models.selected", "None")
    api_key = config.get(f"api.{provider}.api_key", "")

    # Mask API key
    if api_key and len(api_key) > 10:
        masked_key = f"{api_key[:4]}...{api_key[-4:]}"
    else:
        masked_key = api_key or "Not set"

    # Create info table
    from rich.table import Table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="cyan bold", justify="right")
    table.add_column(style="white")

    table.add_row("Provider:", provider.title() if provider else "None")
    table.add_row("Model:", model)
    table.add_row("API Key:", masked_key)

    panel = ui.panel("Current Configuration", table).border("magenta").build()

    ui.console.print(panel)


if __name__ == "__main__":
    ui = UIBuilder()

    # Check for existing config
    if check_existing_config():
        ui.console.print("[yellow]Existing configuration found:[/yellow]\n")
        show_current_config()
        ui.console.print()

        from rich.prompt import Confirm
        if not Confirm.ask("Reconfigure?", default=False):
            ui.console.print("[green]Using existing configuration.[/green]")
            sys.exit(0)

        ui.console.print()

    # Run wizard
    config = run_configuration_wizard()

    ui.console.print("[bold cyan]✓ Ready to chat![/bold cyan]")
    ui.console.print("\nRun: [bold]python demo/chat_app.py[/bold]\n")
