"""Main Demo Entry Point.

Complete demo flow using SilanTui components:
1. Check for existing configuration
2. Run configuration wizard if needed
3. Launch chat application
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from silantui.ui import UIBuilder
from silantui.core import get_config
from rich.prompt import Confirm


def check_configuration() -> tuple[bool, dict]:
    """Check if valid configuration exists.

    Returns:
        Tuple of (is_configured, config_dict)
    """
    config = get_config()

    provider = config.get("models.provider")
    if not provider:
        return False, {}

    api_key = config.get(f"api.{provider}.api_key")
    model = config.get("models.selected")
    base_url = config.get(f"api.{provider}.base_url")

    if not api_key or not model:
        return False, {}

    return True, {
        "provider": provider,
        "api_key": api_key,
        "model": model,
        "base_url": base_url
    }


def show_welcome(ui: UIBuilder):
    """Show welcome screen using SilanTui."""
    ui.console.clear()

    welcome_panel = (
        ui.panel(
            "🚀 Welcome to SilanTui Demo",
            "[bold cyan]AI Chat Application Demo[/bold cyan]\n\n"
            "This demo showcases SilanTui's configuration and chat capabilities.\n\n"
            "[bold]Features:[/bold]\n"
            "  • [yellow]Interactive configuration wizard[/yellow]\n"
            "  • [yellow]Auto-save configuration[/yellow]\n"
            "  • [yellow]Multi-provider support[/yellow] (OpenAI, Anthropic, Custom)\n"
            "  • [yellow]Real-time streaming chat[/yellow]\n\n"
            "[dim]All settings are saved to ~/.silantui/config.json[/dim]"
        )
        .border("cyan")
        .build()
    )

    ui.console.print(welcome_panel)
    ui.console.print()


def show_current_config(ui: UIBuilder, config: dict):
    """Show current configuration."""
    from rich.table import Table

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="cyan bold", justify="right")
    table.add_column(style="white")

    # Mask API key
    api_key = config["api_key"]
    if len(api_key) > 10 and api_key != "not-required":
        masked_key = f"{api_key[:4]}...{api_key[-4:]}"
    else:
        masked_key = api_key

    table.add_row("Provider:", config["provider"].title())
    table.add_row("API Key:", masked_key)
    table.add_row("Model:", config["model"])
    table.add_row("Base URL:", config["base_url"] or "Default")

    panel = (
        ui.panel("Current Configuration", table)
        .border("magenta")
        .build()
    )

    ui.console.print(panel)
    ui.console.print()


def run_config_wizard():
    """Run configuration wizard."""
    from config_wizard import run_configuration_wizard
    return run_configuration_wizard()


def run_chat_app():
    """Run chat application."""
    from chat_app import ChatApp

    app = ChatApp()
    app.run()


def main():
    """Main entry point."""
    ui = UIBuilder()

    # Show welcome
    show_welcome(ui)

    # Check for existing configuration
    is_configured, config = check_configuration()

    if is_configured:
        ui.console.print("[green]✓ Existing configuration found![/green]\n")
        show_current_config(ui, config)

        # Ask if user wants to start chat or reconfigure
        if Confirm.ask("[cyan]Start chat with this configuration?[/cyan]", default=True):
            ui.console.print()
            run_chat_app()
            return
        else:
            ui.console.print()

    # Run configuration wizard
    ui.console.print("[yellow]→ Starting configuration wizard...[/yellow]\n")
    config = run_config_wizard()

    # Ask to start chat
    if Confirm.ask("\n[cyan]Start chat now?[/cyan]", default=True):
        ui.console.print()
        run_chat_app()
    else:
        ui.console.print()
        panel = (
            ui.panel(
                "All Set!",
                "[green]✓ Configuration saved![/green]\n\n"
                "You can start chatting anytime by running:\n"
                "[bold]python demo/main.py[/bold]\n"
                "or\n"
                "[bold]python demo/chat_app.py[/bold]"
            )
            .border("green")
            .build()
        )
        ui.console.print(panel)
        ui.console.print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        ui = UIBuilder()
        ui.console.print("\n\n[yellow]Interrupted by user.[/yellow]")
        ui.console.print("[cyan]Goodbye! 👋[/cyan]\n")
        sys.exit(0)
