#!/usr/bin/env python3
"""
Custom Commands and UI Example - Demonstrates how to easily add custom commands and UI components
"""

from silantui import ModernLogger, ChatSession
from silantui.core.command_system import CommandRegistry, CommandBuilder, quick_command
from silantui.ui.builder import UIBuilder, QuickUI, UITheme


def main():
    logger = ModernLogger(name="custom-demo", level="info")
    ui_builder = UIBuilder(console=logger.console)
    quick_ui = QuickUI(console=logger.console)
    registry = CommandRegistry()
    
    logger.banner(
        project_name="Custom",
        title="Custom Commands and UI Demo",
        description="Shows how to quickly add commands and build UI",
        font="slant"
    )
    
    # ==================== Example 1: Register commands using decorators ====================
    logger.section("Example 1: Register commands with decorators")

    @registry.command(
        "greet",
        description="Greeting command",
        usage="/greet <name>",
        aliases=["hi", "hello"],
        category="Social",
        requires_args=True
    )
    def greet_command(app, args: str):
        logger.success(f"Hello, {args}! 👋")

        # Use UI builder to create welcome panel
        panel = ui_builder.panel(
            "Welcome Message",
            f"Nice to meet you, {args}!\n\nThis is a custom command example."
        ).border("green").build()
        logger.console.print(panel)

    logger.info("Registered command: /greet")
    logger.console.print("[dim]Aliases: /hi, /hello[/dim]\n")

    # Simulate execution
    class MockApp:
        pass

    app = MockApp()
    greet_command(app, "Alice")
    logger.print()
    
    # ==================== Example 2: Using CommandBuilder ====================
    logger.section("Example 2: Using CommandBuilder")

    def show_stats(app, args: str):
        # Use TableBuilder to display statistics
        table = ui_builder.table("📊 System Statistics")
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="yellow", justify="right")
        table.add_column("Status", style="green")

        table.add_row("User Count", "1,234", "✓ Normal")
        table.add_row("Active Sessions", "567", "✓ Normal")
        table.add_row("Total Messages", "45,678", "✓ Normal")

        table.show()

    cmd = CommandBuilder("stats") \
        .description("Show system statistics") \
        .aliases(["st", "statistics"]) \
        .category("System") \
        .handler(show_stats) \
        .build()

    registry.register(cmd)
    logger.info("Registered command: /stats")
    show_stats(app, "")
    logger.print()
    
    # ==================== Example 3: Quick command registration ====================
    logger.section("Example 3: Quick command registration")

    quick_command(
        registry,
        "time",
        lambda app, args: logger.info(f"Current time: {args or 'Unknown'}"),
        description="Display current time",
        aliases=["t"],
        category="Utility"
    )

    logger.info("Registered command: /time")
    logger.print()
    
    # ==================== Example 4: Interactive menu ====================
    logger.section("Example 4: Interactive menu")

    def menu_demo():
        choice = ui_builder.menu("📋 Main Menu") \
            .add_item("1", "Start New Session", description="Create a new chat session") \
            .add_item("2", "View History", description="Browse session history") \
            .add_separator() \
            .add_item("3", "Settings", description="Modify configuration") \
            .add_item("4", "Exit", description="Exit program") \
            .show()

        logger.success(f"You selected: {choice}")

    logger.info("Menu demo:")
    # menu_demo()  # Uncomment to show interactive menu
    logger.console.print("[dim](Interactive menu disabled to avoid blocking demo)[/dim]\n")
    
    # ==================== Example 5: Form building ====================
    logger.section("Example 5: Form building")

    def form_demo():
        results = ui_builder.form("⚙️ User Configuration") \
            .add_field("username", "Username", default="admin") \
            .add_field("age", "Age", field_type="int", default=25) \
            .add_field("email", "Email", required=True) \
            .add_field("notifications", "Receive Notifications", field_type="confirm", default=True) \
            .add_field("theme", "Theme", field_type="choice",
                      choices=["light", "dark", "auto"], default="dark") \
            .show()

        logger.success("Form submitted successfully!")
        for key, value in results.items():
            logger.console.print(f"  • {key}: [cyan]{value}[/cyan]")

    logger.info("Form demo:")
    logger.console.print("[dim](Form disabled to avoid blocking demo)[/dim]\n")
    
    # ==================== Example 6: Quick UI components ====================
    logger.section("Example 6: Quick UI components")

    # Success/Error/Warning messages
    ui_builder.success("Operation completed successfully!")
    ui_builder.error("An error occurred")
    ui_builder.warning("This is a warning")
    ui_builder.info("This is information")
    logger.print()

    # Info box
    quick_ui.info_box(
        "Note",
        "This is an info box example\nSupports multiple lines",
        style="info"
    )
    logger.print()

    # Data table
    quick_ui.data_table(
        "User List",
        ["ID", "Name", "Role"],
        [
            ["1", "Alice", "Admin"],
            ["2", "Bob", "User"],
            ["3", "Charlie", "Guest"]
        ],
        styles=["cyan", "green", "yellow"]
    )
    logger.print()
    
    # ==================== Example 7: Custom theme ====================
    logger.section("Example 7: Custom theme")

    custom_theme = UITheme(
        primary="magenta",
        secondary="cyan",
        success="bright_green",
        warning="bright_yellow",
        error="bright_red"
    )

    custom_ui = UIBuilder(console=logger.console, theme=custom_theme)

    panel = custom_ui.panel(
        "Custom Theme",
        "This panel uses custom theme colors"
    ).border(custom_theme.primary).show()

    logger.print()
    
    # ==================== Example 8: Layout management ====================
    logger.section("Example 8: Layout management")

    # Three-column layout
    from rich.panel import Panel as RichPanel

    left = RichPanel("Left Content\n\nMenu Item 1\nMenu Item 2\nMenu Item 3", border_style="cyan")
    center = RichPanel("Center Content\n\nThis is the main content area\nCan display conversations or other information", border_style="green")
    right = RichPanel("Right Content\n\nStatus Info\nSystem Alerts", border_style="yellow")

    quick_ui.three_column_layout(left, center, right, left_size=20, right_size=20)
    logger.print()
    
    # ==================== Example 9: Command categorization display ====================
    logger.section("Example 9: All registered commands")

    registry.show_help(logger.console)
    
    # ==================== Example 10: Useful tips ====================
    logger.section("Example 10: Useful tips")

    tips = [
        "Use @registry.command() decorator to quickly register commands",
        "Use CommandBuilder to build complex commands",
        "Use UIBuilder to create beautiful UI components",
        "Use QuickUI to quickly create common components",
        "Commands support aliases for quick access",
        "Customize theme colors",
        "Support interactive menus and forms",
        "All components use method chaining for cleaner code"
    ]

    table = ui_builder.table("💡 Usage Tips")
    table.add_column("#", style="cyan", width=5)
    table.add_column("Tip", style="white")

    for i, tip in enumerate(tips, 1):
        table.add_row(str(i), tip)

    table.show()
    logger.print()
    
    # ==================== Summary ====================
    logger.highlight("Example demonstrations complete!")

    logger.console.print("\n[bold cyan]Key Features:[/bold cyan]")
    logger.console.print("  1. [green]Easy command registration[/green] - Decorators, builders, quick functions")
    logger.console.print("  2. [green]Powerful UI building[/green] - Panel, Table, Menu, Form, Layout")
    logger.console.print("  3. [green]Method chaining[/green] - Fluent API design")
    logger.console.print("  4. [green]Ready to use[/green] - Pre-built components and quick methods")
    logger.console.print("  5. [green]Highly customizable[/green] - Themes, styles, behaviors")

    logger.print()
    logger.success("You can now easily create your own commands and UI interfaces!")


if __name__ == "__main__":
    main()
