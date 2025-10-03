#!/usr/bin/env python3
"""
AI Chat Application - Optional AI chat functionality
This is just an example application of SilanTui, not a core feature
"""

from silantui import (
    ModernLogger,
    UIBuilder,
    CommandRegistry,
    LiveChatDisplay,
    ChatSession,
    SessionManager,
)
from silantui.integrations.universal_client import (
    AIClient,
    get_preset_config,
)
from pathlib import Path
from rich.prompt import Prompt
import time


class AIChatApp:
    """AI Chat Application - Demonstrates how to build AI apps with SilanTui"""

    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = "gpt-3.5-turbo",
        use_live_display: bool = True,
    ):
        self.logger = ModernLogger(name="ai-chat", level="info")
        self.ui = UIBuilder(console=self.logger.console)
        self.registry = CommandRegistry()

        # AI client
        self.ai_client = AIClient(
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

        # Session management
        self.session_manager = SessionManager(
            base_dir=Path.home() / ".silantui" / "ai_sessions"
        )
        self.current_session = ChatSession()

        # UI
        self.use_live_display = use_live_display
        if use_live_display:
            self.chat_display = LiveChatDisplay(console=self.logger.console)

        self.system_prompt = None
        self.running = True

        self.register_commands()

    def register_commands(self):
        """Register commands"""

        @self.registry.command("new", description="New session", aliases=["n"])
        def cmd_new(app, args):
            app.current_session = ChatSession()
            if app.use_live_display:
                app.chat_display.clear_messages()
                app.chat_display.show_success("Created new session")
            else:
                app.ui.success("Created new session")

        @self.registry.command("clear", description="Clear session", aliases=["cls"])
        def cmd_clear(app, args):
            if app.ui.confirm("Clear current session?"):
                app.current_session = ChatSession()
                if app.use_live_display:
                    app.chat_display.clear_messages()
                    app.chat_display.show_success("Session cleared")
                else:
                    app.logger.console.clear()
                    app.ui.success("Session cleared")

        @self.registry.command("save", description="Save session", aliases=["s"])
        def cmd_save(app, args):
            path = app.session_manager.save(app.current_session)
            if app.use_live_display:
                app.chat_display.show_success(f"Saved: {path.name}")
            else:
                app.ui.success(f"Saved: {path}")

        @self.registry.command("model", description="Switch model", aliases=["m"])
        def cmd_model(app, args):
            if not args:
                app.ui.info("Current model", app.ai_client.model)
            else:
                app.ai_client.model = args
                app.ui.success(f"Switched to: {args}")

        @self.registry.command("system", description="Set system prompt", aliases=["sys"])
        def cmd_system(app, args):
            if not args:
                if app.system_prompt:
                    app.ui.info("System prompt", app.system_prompt)
                else:
                    app.ui.info("System prompt", "Not set")
            else:
                app.system_prompt = args
                app.ui.success("System prompt updated")
    
    def show_welcome(self):
        """Display welcome screen"""
        self.logger.banner(
            project_name="AI Chat",
            title="AI Chat Assistant",
            description="AI chat application built with SilanTui",
            font="slant"
        )

        self.logger.console.print(f"\n[cyan]Current Configuration:[/cyan]")
        self.logger.console.print(f"  Model: [yellow]{self.ai_client.model}[/yellow]")
        if self.ai_client.client.base_url:
            self.logger.console.print(f"  API: [yellow]{self.ai_client.client.base_url}[/yellow]")
        self.logger.console.print()

        self.logger.console.print("[dim]Enter a message to start chatting, or use commands:[/dim]")
        self.logger.console.print("  /new     - New session")
        self.logger.console.print("  /clear   - Clear session")
        self.logger.console.print("  /model   - Switch model")
        self.logger.console.print("  /system  - Set system prompt")
        self.logger.console.print()
    
    def run_with_live_display(self):
        """Run with live display"""
        self.chat_display.start()

        try:
            while self.running:
                try:
                    # Stop display to get input
                    self.chat_display.stop()
                    user_input = Prompt.ask("\n[bold yellow]>You[/bold yellow]").strip()
                    self.chat_display.start()

                    if not user_input:
                        continue

                    # Handle commands
                    if user_input.startswith('/'):
                        if user_input.lower() in ['/exit', '/quit', '/q']:
                            self.running = False
                            break

                        self.chat_display.stop()
                        parts = user_input.split(maxsplit=1)
                        cmd = parts[0].lstrip('/').lower()
                        args = parts[1] if len(parts) > 1 else ""

                        if self.registry.exists(cmd):
                            self.registry.execute(cmd, self, args)
                        else:
                            self.ui.error(f"Unknown command: {cmd}")

                        input("\nPress Enter to continue...")
                        self.chat_display.start()
                        continue

                    # Add user message
                    self.chat_display.add_user_message(user_input)
                    self.current_session.add_message("user", user_input)

                    # Get AI response
                    self.chat_display.start_assistant_message()

                    full_response = ""
                    for chunk in self.ai_client.chat_stream(
                        message=user_input,
                        system=self.system_prompt,
                        conversation_history=self.current_session.get_messages()[:-1]
                    ):
                        full_response += chunk
                        self.chat_display.append_streaming(chunk)
                        time.sleep(0.01)

                    self.chat_display.finish_assistant_message()
                    self.current_session.add_message("assistant", full_response)

                    # Auto-save
                    self.session_manager.save(self.current_session)

                except KeyboardInterrupt:
                    self.chat_display.stop()
                    self.logger.console.print("\n\n[yellow]Use /exit to quit[/yellow]\n")
                    time.sleep(1)
                    self.chat_display.start()

                except Exception as e:
                    self.chat_display.show_error(str(e))
                    self.logger.error(f"Error: {e}")
                    time.sleep(2)

        finally:
            self.chat_display.stop()

    def run_traditional(self):
        """Run in traditional mode"""
        self.logger.console.print()

        while self.running:
            try:
                user_input = Prompt.ask("\n[bold yellow]> You[/bold yellow]").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['/exit', '/quit', '/q']:
                    break

                # Handle commands
                if user_input.startswith('/'):
                    parts = user_input.split(maxsplit=1)
                    cmd = parts[0].lstrip('/').lower()
                    args = parts[1] if len(parts) > 1 else ""

                    if self.registry.exists(cmd):
                        self.registry.execute(cmd, self, args)
                    else:
                        self.ui.error(f"Unknown command: {cmd}")
                    continue

                # Add user message
                self.current_session.add_message("user", user_input)

                # Display AI response
                self.logger.console.print("\n[bold green]🤖 Assistant:[/bold green]\n")

                full_response = ""
                for chunk in self.ai_client.chat_stream(
                    message=user_input,
                    system=self.system_prompt,
                    conversation_history=self.current_session.get_messages()[:-1]
                ):
                    full_response += chunk
                    self.logger.console.print(chunk, end="")

                self.logger.console.print("\n")

                # Render Markdown
                from rich.markdown import Markdown
                try:
                    md = Markdown(full_response)
                    self.logger.console.print(md)
                except:
                    pass

                self.current_session.add_message("assistant", full_response)
                self.session_manager.save(self.current_session)

            except KeyboardInterrupt:
                self.logger.console.print("\n\n[yellow]Use /exit to quit[/yellow]\n")
            except Exception as e:
                self.ui.error(f"Error: {e}")

    def run(self):
        """Run application"""
        self.logger.console.clear()
        self.show_welcome()

        time.sleep(1)
        self.logger.console.clear()

        if self.use_live_display:
            self.run_with_live_display()
        else:
            self.run_traditional()

        self.logger.console.print("\n[green]👋 Goodbye![/green]\n")


def main():
    """Main function"""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="AI Chat - SilanTui Example Application")
    parser.add_argument("--api-key", help="API Key")
    parser.add_argument("--base-url", help="API Base URL")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="Model name")
    parser.add_argument("--preset", choices=["openai", "ollama", "lm-studio", "azure"],
                       help="Use preset configuration")
    parser.add_argument("--traditional", action="store_true", help="Use traditional mode")

    args = parser.parse_args()

    # Get configuration
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    base_url = args.base_url
    model = args.model

    # Use preset
    if args.preset:
        config = get_preset_config(args.preset)
        base_url = base_url or config.get("base_url")
        if not api_key and args.preset in ["ollama", "lm-studio"]:
            api_key = config.get("api_key", "dummy")

    if not api_key:
        print("Error: API Key required")
        print("\nUsage:")
        print("  export OPENAI_API_KEY=your-key")
        print("  python ai_chat_app.py")
        print("\nOr use local model:")
        print("  python ai_chat_app.py --preset ollama --model llama2")
        return

    app = AIChatApp(
        api_key=api_key,
        base_url=base_url,
        model=model,
        use_live_display=not args.traditional,
    )
    app.run()


if __name__ == "__main__":
    main()
