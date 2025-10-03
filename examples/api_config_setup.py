"""API Configuration Setup Example.

This example demonstrates how to create an API configuration form
using the generic ConfigForm component.
"""

from silantui.ui.config_input import ConfigForm, TextInput, TableSelectInput
from silantui.core import get_config
from rich.console import Console


def create_openai_config_form(console: Console) -> ConfigForm:
    """Create OpenAI API configuration form."""
    models = [
        {"name": "gpt-4-turbo-preview", "provider": "OpenAI", "type": "Chat"},
        {"name": "gpt-4", "provider": "OpenAI", "type": "Chat"},
        {"name": "gpt-3.5-turbo", "provider": "OpenAI", "type": "Chat"},
    ]

    form = (
        ConfigForm(
            title="OpenAI API Configuration",
            description="Configure your OpenAI API credentials and model selection",
            console=console,
            auto_load=True,
            auto_save=True,
        )
        .add_text(
            key="api.openai.api_key",
            label="API Key",
            password=True,
            placeholder="sk-...",
            required=True,
        )
        .add_text(
            key="api.openai.base_url",
            label="Base URL",
            default="https://api.openai.com/v1",
        )
        .add_table_select(
            key="models.selected",
            label="Select Model",
            choices=models,
            columns=["name", "provider", "type"],
            value_key="name",
        )
    )

    return form


def create_anthropic_config_form(console: Console) -> ConfigForm:
    """Create Anthropic API configuration form."""
    models = [
        {"name": "claude-3-opus-20240229", "provider": "Anthropic", "context": "200K"},
        {"name": "claude-3-sonnet-20240229", "provider": "Anthropic", "context": "200K"},
        {"name": "claude-3-haiku-20240307", "provider": "Anthropic", "context": "200K"},
    ]

    form = (
        ConfigForm(
            title="Anthropic API Configuration",
            description="Configure your Anthropic API credentials and model selection",
            console=console,
            auto_load=True,
            auto_save=True,
        )
        .add_text(
            key="api.anthropic.api_key",
            label="API Key",
            password=True,
            placeholder="sk-ant-...",
            required=True,
        )
        .add_text(
            key="api.anthropic.base_url",
            label="Base URL",
            default="https://api.anthropic.com",
        )
        .add_table_select(
            key="models.selected",
            label="Select Model",
            choices=models,
            columns=["name", "provider", "context"],
            value_key="name",
        )
    )

    return form


def create_custom_api_config_form(console: Console) -> ConfigForm:
    """Create custom API configuration form."""
    form = (
        ConfigForm(
            title="Custom API Configuration",
            description="Configure your custom API endpoint",
            console=console,
            auto_load=True,
            auto_save=True,
        )
        .add_text(
            key="api.custom.api_key",
            label="API Key",
            password=True,
            required=True,
        )
        .add_text(
            key="api.custom.base_url",
            label="Base URL",
            placeholder="https://your-api.com/v1",
            required=True,
        )
        .add_text(
            key="api.custom.default_model",
            label="Model Name",
            placeholder="custom-model-v1",
        )
    )

    return form


def main():
    """Main function demonstrating API configuration setup."""
    console = Console()

    console.print("\n[bold cyan]API Configuration Setup[/bold cyan]\n")

    # Ask which provider to configure
    console.print("[bold]Select API Provider:[/bold]")
    console.print("1. OpenAI")
    console.print("2. Anthropic")
    console.print("3. Custom API")

    from rich.prompt import Prompt
    choice = Prompt.ask("\nEnter choice", choices=["1", "2", "3"], default="1")

    # Create appropriate form
    if choice == "1":
        form = create_openai_config_form(console)
    elif choice == "2":
        form = create_anthropic_config_form(console)
    else:
        form = create_custom_api_config_form(console)

    # Show current config if exists
    config = get_config()
    has_config = any(
        config.get(field.key) for field in form.fields
    )

    if has_config:
        console.print("\n[yellow]Existing configuration found:[/yellow]")
        console.print(form.render_panel())

        from rich.prompt import Confirm
        if not Confirm.ask("\nUpdate configuration?", default=True):
            console.print("[dim]Configuration unchanged.[/dim]")
            return

    # Prompt for all fields
    values = form.prompt_all()

    console.print("\n[bold green]✓ Configuration saved successfully![/bold green]")
    console.print(f"[dim]Saved to: {config.config_path}[/dim]")


if __name__ == "__main__":
    main()
