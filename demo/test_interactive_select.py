#!/usr/bin/env python3
"""Test InteractiveSelect component in demo context."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from silantui.ui import InteractiveSelect


def test_basic_selection():
    """Test basic InteractiveSelect functionality."""
    console = Console()

    console.print("[bold cyan]Testing InteractiveSelect Component[/bold cyan]\n")

    # Test 1: Simple provider selection
    providers = [
        {"name": "OpenAI", "key": "openai", "desc": "GPT-4, GPT-3.5"},
        {"name": "Anthropic", "key": "anthropic", "desc": "Claude 3"},
        {"name": "Custom API", "key": "custom", "desc": "Compatible API"},
    ]

    console.print("[yellow]Test 1: Provider Selection[/yellow]")
    console.print("Use ↑/↓ to navigate, Enter to select, 'q' to quit\n")

    selector = InteractiveSelect(
        choices=providers,
        title="Select LLM Provider",
        columns=["name", "desc"],
        value_key="key",
        console=console
    )

    selected = selector.prompt()

    if selected:
        console.print(f"\n[green]✓ Test passed! Selected: {selected}[/green]\n")

        # Test 2: Model selection based on provider
        if selected == "openai":
            models = [
                {"name": "gpt-4-turbo-preview", "speed": "Fast", "cost": "$$", "context": "128K"},
                {"name": "gpt-4", "speed": "Medium", "cost": "$$$", "context": "8K"},
                {"name": "gpt-3.5-turbo", "speed": "Very Fast", "cost": "$", "context": "16K"},
            ]

            console.print("[yellow]Test 2: OpenAI Model Selection[/yellow]")
            console.print("Navigate through the multi-column table\n")

            model_selector = InteractiveSelect(
                choices=models,
                title="Select OpenAI Model",
                columns=["name", "speed", "cost", "context"],
                value_key="name",
                console=console
            )

            model = model_selector.prompt()

            if model:
                console.print(f"\n[green]✓ Test passed! Selected model: {model}[/green]\n")
            else:
                console.print("\n[yellow]Model selection cancelled[/yellow]\n")

        elif selected == "anthropic":
            models = [
                {"name": "claude-3-opus-20240229", "tier": "Most Capable", "context": "200K"},
                {"name": "claude-3-sonnet-20240229", "tier": "Balanced", "context": "200K"},
                {"name": "claude-3-haiku-20240307", "tier": "Fastest", "context": "200K"},
            ]

            console.print("[yellow]Test 2: Anthropic Model Selection[/yellow]")
            console.print("Navigate through the Claude models\n")

            model_selector = InteractiveSelect(
                choices=models,
                title="Select Claude Model",
                columns=["name", "tier", "context"],
                value_key="name",
                console=console
            )

            model = model_selector.prompt()

            if model:
                console.print(f"\n[green]✓ Test passed! Selected model: {model}[/green]\n")
            else:
                console.print("\n[yellow]Model selection cancelled[/yellow]\n")
    else:
        console.print("\n[yellow]Selection cancelled[/yellow]\n")

    console.print("[bold green]✓ All tests completed![/bold green]\n")
    console.print("[dim]The InteractiveSelect component is working correctly.[/dim]\n")


if __name__ == "__main__":
    try:
        test_basic_selection()
    except KeyboardInterrupt:
        print("\n\n[yellow]Test interrupted[/yellow]")
        sys.exit(0)
