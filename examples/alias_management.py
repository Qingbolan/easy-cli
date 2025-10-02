#!/usr/bin/env python3
"""
Command Management Example - Demonstrates how to manage custom commands
"""

from silantui import CommandManager, ModernLogger

def main():
    logger = ModernLogger(name="command-demo", level="info")
    cm = CommandManager()
    
    logger.banner(
        project_name="Commands",
        title="Custom Command Management",
        description="Create your own CLI commands",
        font="slant"
    )
    
    # Example 1: Adding custom commands
    logger.section("Adding Custom Commands")
    
    logger.info("Adding custom commands...")
    cm.add_command("chat", description="Quick chat")
    cm.add_command(
        "sonnet",
        model="claude-sonnet-4-20250514",
        description="LLM Sonnet model"
    )
    cm.add_command(
        "opus",
        model="claude-opus-4-20250514",
        description="LLM Opus model"
    )
    cm.add_command(
        "code",
        system="You are an expert coding assistant",
        description="Coding assistant"
    )
    cm.add_command(
        "writer",
        system="You are a creative writing assistant",
        model="claude-opus-4-20250514",
        description="Creative writing assistant"
    )
    
    logger.success("Commands added!")
    logger.print()
    
    # Example 2: List all commands
    logger.section("Current Commands")
    
    commands = cm.list_commands()
    table = logger.table(title="Configured Commands")
    table.add_column("Command", style="yellow", width=15)
    table.add_column("Model", style="green", width=25)
    table.add_column("System", style="cyan", width=30)
    table.add_column("Description", style="white")
    
    for name, config in commands.items():
        model = config.get("model", "Default")
        system = config.get("system", "-")
        if len(system) > 28:
            system = system[:25] + "..."
        desc = config.get("description", "-")
        table.add_row(name, model, system, desc)
    
    logger.console.print(table)
    logger.print()
    
    # Example 3: Create executable files
    logger.section("Creating Executable Commands")
    
    logger.info("Creating executable commands in ~/.local/bin/")
    try:
        created = cm.create_executables()
        logger.success(f"Created {len(created)} executable commands:")
        for path in created:
            logger.console.print(f"  • {path.name} → {path}")
        logger.print()
        
        logger.info("Make sure ~/.local/bin is in your PATH:")
        logger.console.print('[yellow]export PATH="$HOME/.local/bin:$PATH"[/yellow]')
        logger.print()
    except Exception as e:
        logger.error(f"Failed to create executables: {e}")
    
    # Example 4: Usage instructions
    logger.section("Usage Examples")
    
    usage_examples = [
        ("chat", "Start a quick chat"),
        ("sonnet", "Use LLM Sonnet model"),
        ("opus", "Use LLM Opus model"),
        ("code", "Start coding assistant"),
        ("writer", "Start writing assistant"),
    ]
    
    table = logger.table(title="How to Use Your Commands")
    table.add_column("Command", style="cyan", width=15)
    table.add_column("Description", style="white")
    
    for cmd, desc in usage_examples:
        table.add_row(cmd, desc)
    
    logger.console.print(table)
    logger.print()
    
    # Configuration instructions
    logger.highlight("Command Configuration")
    logger.console.print("\n[bold cyan]Each command can have:[/bold cyan]")
    logger.console.print("  • [yellow]model[/yellow]: LLM model to use")
    logger.console.print("  • [cyan]system[/cyan]: System prompt for the assistant")
    logger.console.print("  • [green]log_level[/green]: Logging verbosity")
    logger.console.print("  • [white]description[/white]: Command description")
    logger.print()
    
    logger.highlight("Interactive Setup")
    logger.console.print("\nUse the interactive setup for easier configuration:")
    logger.console.print("[yellow]silantui --setup-commands[/yellow]")
    logger.print()
    
    logger.success("Command management demo completed!")


if __name__ == "__main__":
    main()
