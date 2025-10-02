#!/usr/bin/env python3
"""
Pure UI Framework Example - Data Dashboard
Demonstrates SilanTui as a pure UI framework, no AI required
"""

from silantui import (
    ModernLogger,
    UIBuilder,
    QuickUI,
    CommandRegistry,
    CommandBuilder,
)
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
import time
import random
from datetime import datetime


class DataDashboard:
    """Data Dashboard Example - Demonstrates UI building capabilities"""

    def __init__(self):
        self.logger = ModernLogger(name="dashboard", level="info")
        self.ui = UIBuilder(console=self.logger.console)
        self.quick_ui = QuickUI(console=self.logger.console)
        self.registry = CommandRegistry()
        self.running = True

        # Mock data
        self.data = {
            "users": 1234,
            "sessions": 567,
            "revenue": 89012,
            "requests": 0,
        }

        self.register_commands()

    def register_commands(self):
        """Register commands"""

        @self.registry.command("stats", description="Show statistics", aliases=["st"])
        def cmd_stats(app, args):
            app.show_stats()

        @self.registry.command("chart", description="Show charts", aliases=["c"])
        def cmd_chart(app, args):
            app.show_chart()

        @self.registry.command("live", description="Live monitoring", aliases=["l"])
        def cmd_live(app, args):
            app.show_live_monitor()

        @self.registry.command("settings", description="Settings", aliases=["set"])
        def cmd_settings(app, args):
            app.show_settings()

        @self.registry.command("exit", description="Exit", aliases=["q"])
        def cmd_exit(app, args):
            app.running = False
            self.logger.console.print("\n[green]👋 Goodbye![/green]\n")
    
    def show_welcome(self):
        """Display welcome screen"""
        self.logger.banner(
            project_name="Dashboard",
            title="Data Dashboard",
            description="Demonstrates SilanTui UI framework's powerful features",
            font="slant"
        )

        # Use UI builder to create welcome panel
        welcome_panel = self.ui.panel(
            "Welcome to Data Dashboard",
            "This is a pure UI example, no AI features required.\n"
            "Demonstrates SilanTui as a general-purpose UI framework.\n\n"
            "[cyan]Enter commands to start:[/cyan]\n"
            "  • /stats - View statistics\n"
            "  • /chart - View charts\n"
            "  • /live  - Live monitoring\n"
            "  • /settings - Settings\n"
            "  • /exit  - Exit"
        ).border("cyan").build()

        self.logger.console.print()
        self.logger.console.print(welcome_panel)
        self.logger.console.print()
    
    def show_stats(self):
        """Display statistics"""
        self.logger.console.print()

        # Use Table builder
        table = self.ui.table("📊 Live Statistics")
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="yellow", justify="right", width=15)
        table.add_column("Status", style="green", width=15)
        table.add_column("Trend", style="magenta", width=10)

        table.add_row(
            "Active Users",
            f"{self.data['users']:,}",
            "✓ Normal",
            "↗ +12%"
        )
        table.add_row(
            "Sessions",
            f"{self.data['sessions']:,}",
            "✓ Normal",
            "↗ +8%"
        )
        table.add_row(
            "Revenue ($)",
            f"${self.data['revenue']:,}",
            "✓ Normal",
            "↗ +23%"
        )
        table.add_row(
            "API Requests",
            f"{self.data['requests']:,}",
            "⚠ Peak",
            "↗ +156%"
        )

        table.show()
        self.logger.console.print()
    
    def show_chart(self):
        """Display chart (simulated with characters)"""
        self.logger.console.print()

        # Generate random data
        data = [random.randint(10, 100) for _ in range(24)]
        max_val = max(data)

        # Create panel
        chart_content = "[bold cyan]User Activity (24 hours)[/bold cyan]\n\n"

        # Simple character chart
        for hour, value in enumerate(data):
            bar_length = int((value / max_val) * 40)
            bar = "█" * bar_length
            chart_content += f"{hour:02d}:00 │{bar} {value}\n"

        panel = self.ui.panel("📈 Data Chart", chart_content).border("green").build()
        self.logger.console.print(panel)
        self.logger.console.print()
    
    def show_live_monitor(self):
        """Live monitoring"""
        self.logger.console.print("\n[cyan]Starting live monitoring...[/cyan]\n")
        time.sleep(1)

        # Create layout
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3),
        )

        # Use Live updates
        with Live(layout, refresh_per_second=2, console=self.logger.console) as live:
            for i in range(20):  # Monitor for 10 seconds
                # Update data
                self.data['requests'] += random.randint(10, 50)

                # Update header
                layout["header"].update(
                    Panel(
                        f"[bold cyan]Live Monitoring[/bold cyan] - {datetime.now().strftime('%H:%M:%S')}",
                        style="cyan"
                    )
                )

                # Update body - create table
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Metric", style="cyan")
                table.add_column("Current Value", style="yellow")
                table.add_column("Change", style="green")

                table.add_row(
                    "Total Users",
                    f"{self.data['users']:,}",
                    f"+{random.randint(0, 5)}"
                )
                table.add_row(
                    "Active Sessions",
                    f"{self.data['sessions']:,}",
                    f"+{random.randint(0, 3)}"
                )
                table.add_row(
                    "API Requests",
                    f"{self.data['requests']:,}",
                    f"+{random.randint(10, 50)}"
                )

                layout["body"].update(table)

                # Update footer
                status = "🟢 System Normal" if i % 3 != 0 else "🟡 High Load"
                layout["footer"].update(
                    Panel(f"{status} | Press Ctrl+C to stop", style="green")
                )

                time.sleep(0.5)

        self.logger.console.print("\n[green]✓ Monitoring ended[/green]\n")
    
    def show_settings(self):
        """Display settings interface"""
        self.logger.console.print()

        # Use Form builder
        results = self.ui.form("⚙️  System Settings") \
            .add_field("refresh_rate", "Refresh Rate (seconds)", field_type="int", default=5) \
            .add_field("max_users", "Max Users", field_type="int", default=10000) \
            .add_field("enable_alerts", "Enable Alerts", field_type="confirm", default=True) \
            .add_field("theme", "Theme", field_type="choice",
                      choices=["light", "dark", "auto"], default="dark") \
            .show()

        self.logger.console.print()
        self.ui.success("Settings saved!")
        self.logger.console.print()

        # Display saved settings
        table = self.ui.table("Current Settings")
        table.add_column("Option", style="cyan")
        table.add_column("Value", style="green")

        for key, value in results.items():
            table.add_row(key, str(value))

        table.show()
        self.logger.console.print()
    
    def run(self):
        """Run dashboard"""
        self.logger.console.clear()
        self.show_welcome()

        while self.running:
            try:
                # Show menu
                choice = self.ui.menu("📋 Main Menu") \
                    .add_item("1", "Statistics", description="View system statistics") \
                    .add_item("2", "Data Charts", description="Visualize data") \
                    .add_item("3", "Live Monitoring", description="Monitor system status") \
                    .add_separator() \
                    .add_item("4", "Settings", description="System settings") \
                    .add_item("5", "Exit", description="Exit program") \
                    .show()

                if choice == "1":
                    self.show_stats()
                elif choice == "2":
                    self.show_chart()
                elif choice == "3":
                    self.show_live_monitor()
                elif choice == "4":
                    self.show_settings()
                elif choice == "5":
                    self.running = False
                    self.logger.console.print("\n[green]👋 Goodbye![/green]\n")

            except KeyboardInterrupt:
                self.logger.console.print("\n\n[yellow]Use menu option 5 to exit[/yellow]\n")
                time.sleep(1)
                continue


def main():
    """Main function"""
    dashboard = DataDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
