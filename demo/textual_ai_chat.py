#!/usr/bin/env python3
"""
Textual AI Chat - Complete AI-powered chat application

This demo shows a production-ready chat interface with:
- Real AI integration (OpenAI/Anthropic/Custom)
- Configuration management
- Streaming responses
- Error handling
- Command system
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from silantui.ui.textual_chat import ChatApp
from silantui.core import get_config
from rich.text import Text
import time


class AIChatApp(ChatApp):
    """
    Production-ready AI chat application using Textual

    Supports multiple AI providers through configuration
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load configuration
        self.config = get_config()
        self.provider = self.config.get("models.provider")
        self.model = self.config.get("models.selected")
        self.api_key = self.config.get(f"api.{self.provider}.api_key")
        self.base_url = self.config.get(f"api.{self.provider}.base_url")

        # Initialize client
        self._init_client()

    def _init_client(self):
        """Initialize AI client based on provider"""
        try:
            if self.provider in ["openai", "custom"]:
                import openai
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                self.conversation = []
            elif self.provider == "anthropic":
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.conversation = []
            else:
                self.client = None
                chat_history = self.query_one("#chat-history")
                error = Text(f"Unknown provider: {self.provider}", style="red")
                chat_history.write(error)
        except Exception as e:
            self.client = None
            chat_history = self.query_one("#chat-history")
            error = Text(f"Failed to initialize client: {str(e)}", style="red")
            chat_history.write(error)

    def on_mount(self):
        """Show welcome with provider info"""
        super().on_mount()

        if self.client:
            chat_history = self.query_one("#chat-history")
            welcome = Text.from_markup(
                f"\n[bold green]Connected to {self.provider.title()}[/bold green]\n"
                f"Model: [cyan]{self.model}[/cyan]\n"
                f"Base URL: [dim]{self.base_url or 'Default'}[/dim]\n"
            )
            chat_history.write(welcome)

    def simulate_response(self, user_message: str):
        """Generate AI response with streaming"""
        if not self.client:
            self.add_assistant_message("Error: AI client not initialized. Please check your configuration.")
            return

        # Add to conversation history
        self.conversation.append({"role": "user", "content": user_message})

        # Start streaming
        self.start_streaming()

        try:
            if self.provider in ["openai", "custom"]:
                self._handle_openai_response()
            elif self.provider == "anthropic":
                self._handle_anthropic_response()
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.finish_streaming(error_msg)
            # Remove failed message from history
            if self.conversation and self.conversation[-1]["role"] == "user":
                self.conversation.pop()

    def _handle_openai_response(self):
        """Handle OpenAI/compatible API streaming response"""
        import openai

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation,
            stream=True
        )

        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                self.append_streaming(content)

        # Add to conversation history
        self.conversation.append({"role": "assistant", "content": full_response})

        # Finish streaming
        self.finish_streaming(full_response)

    def _handle_anthropic_response(self):
        """Handle Anthropic API streaming response"""
        import anthropic

        # Anthropic uses different message format
        messages = [{"role": "user", "content": self.conversation[-1]["content"]}]

        full_response = ""
        with self.client.messages.stream(
            model=self.model,
            max_tokens=4096,
            messages=messages
        ) as stream:
            for text in stream.text_stream:
                full_response += text
                self.append_streaming(text)

        # Add to conversation history
        self.conversation.append({"role": "assistant", "content": full_response})

        # Finish streaming
        self.finish_streaming(full_response)

    def handle_command(self, command: str):
        """Extended command handling"""
        cmd = command.lower().strip()

        if cmd == "/config":
            self._show_config()
        elif cmd == "/model":
            self._show_model_info()
        elif cmd == "/clear-context":
            self._clear_context()
        else:
            super().handle_command(command)

    def _show_config(self):
        """Show current configuration"""
        chat_history = self.query_one("#chat-history")
        config_text = Text.from_markup(
            "[bold cyan]Current Configuration:[/bold cyan]\n"
            f"  Provider: [green]{self.provider}[/green]\n"
            f"  Model: [yellow]{self.model}[/yellow]\n"
            f"  Base URL: [dim]{self.base_url or 'Default'}[/dim]\n"
            f"  Messages in context: [cyan]{len(self.conversation)}[/cyan]\n"
        )
        chat_history.write(config_text)

    def _show_model_info(self):
        """Show model information"""
        chat_history = self.query_one("#chat-history")
        info_text = Text.from_markup(
            f"[bold cyan]Model Information:[/bold cyan]\n"
            f"  Name: [yellow]{self.model}[/yellow]\n"
            f"  Provider: [green]{self.provider}[/green]\n"
        )
        chat_history.write(info_text)

    def _clear_context(self):
        """Clear conversation context but keep UI history"""
        self.conversation.clear()
        chat_history = self.query_one("#chat-history")
        chat_history.write(Text("Conversation context cleared.", style="yellow"))

    def show_help(self):
        """Extended help message"""
        chat_history = self.query_one("#chat-history")
        help_text = Text.from_markup(
            "[bold cyan]Available Commands:[/bold cyan]\n"
            "  [yellow]/help[/yellow] - Show this help\n"
            "  [yellow]/new[/yellow] - Clear chat history\n"
            "  [yellow]/config[/yellow] - Show configuration\n"
            "  [yellow]/model[/yellow] - Show model info\n"
            "  [yellow]/clear-context[/yellow] - Clear conversation context\n"
            "  [yellow]Ctrl+N[/yellow] - New chat\n"
            "  [yellow]Ctrl+C[/yellow] - Quit\n"
        )
        chat_history.write(help_text)


def main():
    """Main entry point"""
    # Check if configured
    config = get_config()
    provider = config.get("models.provider")

    if not provider:
        print("Error: No configuration found!")
        print("Please run the configuration wizard first:")
        print("  python demo/config_wizard.py")
        sys.exit(1)

    api_key = config.get(f"api.{provider}.api_key")
    model = config.get("models.selected")

    if not api_key or not model:
        print("Error: Incomplete configuration!")
        print("Please run the configuration wizard:")
        print("  python demo/config_wizard.py")
        sys.exit(1)

    # Run the app
    app = AIChatApp(role=f"{provider.title()} {model}")
    app.run()


if __name__ == "__main__":
    main()
