"""Example demonstrating the configuration system with auto-load and auto-save.

This example shows how to:
1. Automatically load existing configuration
2. Update configuration with real-time saving
3. Use ConfigInput for interactive configuration
4. Switch between different providers
"""

from silantui.core import ConfigManager, get_config
from silantui.ui import ConfigInput
from rich.console import Console


def example_1_basic_config_manager():
    """Example 1: Basic ConfigManager usage"""
    print("\n=== Example 1: Basic ConfigManager ===\n")

    # Create config manager (auto-loads from ~/.silantui/config.json)
    config = ConfigManager()

    # Get values using dot notation
    api_key = config.get("api.openai.api_key")
    selected_model = config.get("models.selected")

    print(f"Current API Key: {api_key[:10] if api_key else 'Not set'}...")
    print(f"Selected Model: {selected_model}")

    # Set values (automatically saved)
    config.set("api.openai.api_key", "sk-example-key-12345")
    config.set("models.selected", "gpt-4")

    print("\n✓ Configuration updated and saved automatically")


def example_2_batch_update():
    """Example 2: Batch update configuration"""
    print("\n=== Example 2: Batch Update ===\n")

    config = get_config()

    # Update multiple values at once
    config.update({
        "api.openai.api_key": "sk-new-key-67890",
        "api.openai.base_url": "https://api.openai.com/v1",
        "models.selected": "gpt-4-turbo-preview",
    })

    print("✓ Multiple values updated in one operation")
    print(f"  Model: {config.get('models.selected')}")
    print(f"  Base URL: {config.get('api.openai.base_url')}")


def example_3_interactive_config():
    """Example 3: Interactive configuration with ConfigInput"""
    print("\n=== Example 3: Interactive Configuration ===\n")

    console = Console()

    # Create ConfigInput (auto-loads existing config)
    config_input = ConfigInput(
        console=console,
        provider="openai",
        auto_load=True  # Load existing configuration
    )

    # Display current configuration
    console.print(config_input.render_config_panel())

    # Prompt for updates (uncomment to test interactively)
    # config_input.prompt_api_key()
    # config_input.prompt_base_url()
    # config_input.prompt_model_selection()

    print("\n✓ Current configuration loaded and displayed")


def example_4_provider_switching():
    """Example 4: Switch between providers"""
    print("\n=== Example 4: Provider Switching ===\n")

    config = get_config()
    console = Console()

    # Configure OpenAI
    config.set_api_config(
        provider="openai",
        api_key="sk-openai-key",
        base_url="https://api.openai.com/v1",
        default_model="gpt-4"
    )

    # Configure Anthropic
    config.set_api_config(
        provider="anthropic",
        api_key="sk-ant-key",
        base_url="https://api.anthropic.com",
        default_model="claude-3-opus-20240229"
    )

    # Create ConfigInput for OpenAI
    openai_config = ConfigInput(console=console, provider="openai", auto_load=True)
    console.print("\n[bold]OpenAI Configuration:[/bold]")
    console.print(openai_config.render_config_panel())

    # Switch to Anthropic
    openai_config.switch_provider("anthropic")
    console.print("\n[bold]Anthropic Configuration:[/bold]")
    console.print(openai_config.render_config_panel())

    print("\n✓ Provider switching complete")


def example_5_current_model_config():
    """Example 5: Get complete configuration for current model"""
    print("\n=== Example 5: Current Model Configuration ===\n")

    config = get_config()

    # Set the current model
    config.set_selected_model("claude-3-opus-20240229", provider="anthropic")

    # Get complete config for current model
    current = config.get_current_model_config()

    print("Current Model Configuration:")
    print(f"  Model: {current['model']}")
    print(f"  Provider: {current['provider']}")
    print(f"  API Key: {current['api_key'][:10] if current['api_key'] else 'Not set'}...")
    print(f"  Base URL: {current['base_url']}")


def example_6_add_custom_models():
    """Example 6: Add custom models"""
    print("\n=== Example 6: Add Custom Models ===\n")

    config = get_config()
    console = Console()

    # Add custom models
    custom_models = [
        "llama-2-70b",
        "mistral-7b",
        "custom-model-v1"
    ]

    for model in custom_models:
        config.add_model(model)

    print(f"✓ Added {len(custom_models)} custom models")
    print(f"  Total models available: {len(config.get('models.available', []))}")


def example_7_export_import():
    """Example 7: Export and import configuration"""
    print("\n=== Example 7: Export/Import Configuration ===\n")

    from pathlib import Path

    config = get_config()

    # Export configuration
    export_path = Path("/tmp/silantui_config_backup.json")
    config.export_config(export_path)
    print(f"✓ Configuration exported to {export_path}")

    # Import configuration
    # config.import_config(export_path)
    # print(f"✓ Configuration imported from {export_path}")


if __name__ == "__main__":
    console = Console()

    console.print("\n[bold cyan]SilanTui Configuration System Examples[/bold cyan]\n")
    console.print("This demonstrates auto-load and auto-save capabilities\n")

    try:
        example_1_basic_config_manager()
        example_2_batch_update()
        example_3_interactive_config()
        example_4_provider_switching()
        example_5_current_model_config()
        example_6_add_custom_models()
        example_7_export_import()

        console.print("\n[bold green]✓ All examples completed successfully![/bold green]")
        console.print(f"\nConfiguration saved to: {get_config().config_path}")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        import traceback
        traceback.print_exc()
