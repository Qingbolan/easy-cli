"""Simple Chat Application Demo using SilanTui.

A functional chat application using configured LLM API.
Supports OpenAI, Anthropic, and OpenAI-compatible APIs.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from silantui.ui import UIBuilder
from silantui.core import get_config
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.live import Live
from rich.table import Table
from typing import List, Dict
import openai
import anthropic


class ChatApp:
    """Simple chat application using SilanTui components."""

    def __init__(self):
        self.ui = UIBuilder()
        self.config = get_config()
        self.messages: List[Dict[str, str]] = []

        # Load configuration
        self.provider = self.config.get("models.provider")
        self.model = self.config.get("models.selected")
        self.api_key = self.config.get(f"api.{self.provider}.api_key")
        self.base_url = self.config.get(f"api.{self.provider}.base_url")

        # Initialize client
        self._init_client()

    def _init_client(self):
        """Initialize API client."""
        if self.provider in ["openai", "custom"]:
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        elif self.provider == "anthropic":
            self.client = anthropic.Anthropic(
                api_key=self.api_key
            )
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def show_welcome(self):
        """Show welcome screen using SilanTui."""
        self.ui.console.clear()

        # Create info table
        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_column(style="cyan bold", justify="right")
        info_table.add_column(style="white")

        info_table.add_row("Provider:", self.provider.title())
        info_table.add_row("Model:", self.model)
        info_table.add_row("Base URL:", self.base_url or "Default")

        panel = (
            self.ui.panel("🤖 AI Chat Application", info_table)
            .subtitle("Type 'quit' or 'exit' to end")
            .border("cyan")
            .build()
        )

        self.ui.console.print(panel)
        self.ui.console.print()

        # Show commands
        commands_table = (
            self.ui.table()
            .add_column("Command")
            .add_column("Description")
            .add_row("/clear", "Clear chat history")
            .add_row("/config", "Show current configuration")
            .add_row("/help", "Show this help")
            .add_row("quit/exit", "Exit application")
            .build()
        )

        commands_panel = (
            self.ui.panel("Available Commands", commands_table)
            .border("dim")
            .build()
        )

        self.ui.console.print(commands_panel)
        self.ui.console.print()

    def chat_openai(self, user_message: str) -> str:
        """Chat using OpenAI API."""
        self.messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                stream=True
            )

            full_response = ""
            with Live(console=self.ui.console, refresh_per_second=10) as live:
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        panel = (
                            self.ui.panel("Assistant", Markdown(full_response))
                            .border("green")
                            .build()
                        )
                        live.update(panel)

            self.messages.append({"role": "assistant", "content": full_response})
            return full_response

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            error_panel = (
                self.ui.panel("Error", error_msg)
                .border("red")
                .build()
            )
            self.ui.console.print(error_panel)
            return error_msg

    def chat_anthropic(self, user_message: str) -> str:
        """Chat using Anthropic API."""
        messages = [{"role": "user", "content": user_message}]

        try:
            full_response = ""
            with Live(console=self.ui.console, refresh_per_second=10) as live:
                with self.client.messages.stream(
                    model=self.model,
                    max_tokens=4096,
                    messages=messages
                ) as stream:
                    for text in stream.text_stream:
                        full_response += text
                        panel = (
                            self.ui.panel("Assistant", Markdown(full_response))
                            .border("green")
                            .build()
                        )
                        live.update(panel)

            self.messages.append({"role": "user", "content": user_message})
            self.messages.append({"role": "assistant", "content": full_response})

            return full_response

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            error_panel = (
                self.ui.panel("Error", error_msg)
                .border("red")
                .build()
            )
            self.ui.console.print(error_panel)
            return error_msg

    def send_message(self, user_message: str) -> str:
        """Send message to AI."""
        if self.provider in ["openai", "custom"]:
            return self.chat_openai(user_message)
        elif self.provider == "anthropic":
            return self.chat_anthropic(user_message)
        else:
            return f"Error: Unknown provider {self.provider}"

    def handle_command(self, command: str) -> bool:
        """Handle special commands.

        Returns:
            True to continue chat, False to exit
        """
        command = command.lower().strip()

        if command in ["quit", "exit", "q"]:
            return False

        elif command == "/clear":
            self.messages.clear()
            self.ui.console.clear()
            self.show_welcome()
            self.ui.console.print("[green]✓ Chat history cleared.[/green]\n")

        elif command == "/config":
            self._show_config()

        elif command == "/help":
            self._show_help()

        else:
            self.ui.console.print(f"[yellow]Unknown command: {command}[/yellow]")
            self.ui.console.print("Type [cyan]/help[/cyan] for available commands.\n")

        return True

    def _show_config(self):
        """Show current configuration."""
        config_table = Table(show_header=False, box=None, padding=(0, 2))
        config_table.add_column(style="cyan bold", justify="right")
        config_table.add_column(style="white")

        config_table.add_row("Provider:", self.provider.title())
        config_table.add_row("Model:", self.model)
        config_table.add_row("Base URL:", self.base_url or "Default")
        config_table.add_row("Messages:", str(len(self.messages)))

        panel = (
            self.ui.panel("Current Configuration", config_table)
            .border("magenta")
            .build()
        )

        self.ui.console.print(panel)
        self.ui.console.print()

    def _show_help(self):
        """Show help message."""
        table = (
            self.ui.table()
            .add_column("Command")
            .add_column("Description")
            .add_row("/clear", "Clear chat history")
            .add_row("/config", "Show current configuration")
            .add_row("/help", "Show this help")
            .add_row("quit/exit", "Exit application")
            .build()
        )

        panel = (
            self.ui.panel("Available Commands", table)
            .border("cyan")
            .build()
        )

        self.ui.console.print(panel)
        self.ui.console.print()

    def run(self):
        """Run the chat application."""
        self.show_welcome()

        try:
            while True:
                # Get user input
                try:
                    user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
                except (KeyboardInterrupt, EOFError):
                    break

                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.startswith("/") or user_input.lower() in ["quit", "exit", "q"]:
                    if not self.handle_command(user_input):
                        break
                    continue

                # Send message to AI
                self.ui.console.print()
                response = self.send_message(user_input)

                # Add spacing
                self.ui.console.print()

        except KeyboardInterrupt:
            pass

        self.ui.console.print("\n[cyan]Goodbye! 👋[/cyan]\n")


def main():
    """Main entry point."""
    ui = UIBuilder()
    config = get_config()

    # Check if configured
    provider = config.get("models.provider")

    if not provider:
        panel = (
            ui.panel(
                "Error",
                "[red]No configuration found![/red]\n\n"
                "Please run the configuration wizard first:\n"
                "[bold]python demo/config_wizard.py[/bold]"
            )
            .border("red")
            .build()
        )
        ui.console.print(panel)
        sys.exit(1)

    # Get API key and model
    api_key = config.get(f"api.{provider}.api_key")
    model = config.get("models.selected")

    if not api_key or not model:
        panel = (
            ui.panel(
                "Error",
                "[red]Incomplete configuration![/red]\n\n"
                "Please run the configuration wizard:\n"
                "[bold]python demo/config_wizard.py[/bold]"
            )
            .border("red")
            .build()
        )
        ui.console.print(panel)
        sys.exit(1)

    # Run chat app
    app = ChatApp()
    app.run()


if __name__ == "__main__":
    main()
