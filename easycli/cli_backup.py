#!/usr/bin/env python3
"""
Main CLI application entry point.
"""

import sys
import os
from typing import Optional
from pathlib import Path

from rich.prompt import Prompt

from .logger import ModernLogger
from .client import AIClient
from .session import ChatSession, SessionManager
from .ui import ChatUI


class ChatApplication:
    """Main chat application."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        log_level: str = "info",
    ):
        self.logger = ModernLogger(
            name="ai-cli",
            level=log_level,
            log_file=str(Path.home() / ".ai_cli" / "app.log")
        )
        
        self.client = AIClient(
            api_key=api_key,
            model=model,
            logger=self.logger
        )
        
        self.session_manager = SessionManager()
        self.current_session = ChatSession()
        self.ui = ChatUI(logger=self.logger)
        
        self.system_prompt: Optional[str] = None
        self.running = True
    
    def run(self) -> None:
        """Main application loop."""
        try:
            # Show welcome
            self.logger.console.clear()
            self.ui.show_welcome("AI CLI")
            
            self.logger.info("Application started")
            self.logger.info(f"Model: {self.client.model}")
            self.logger.print()
            
            # Main loop
            while self.running:
                try:
                    # Show current state
                    self.ui.show_conversation(self.current_session)
                    
                    # Get user input
                    user_input = Prompt.ask(
                        "\n[bold yellow]💬 You[/bold yellow]"
                    ).strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle commands
                    if user_input.startswith('/'):
                        self.handle_command(user_input)
                        continue
                    
                    # Add user message
                    self.current_session.add_message("user", user_input)
                    
                    # Get AI response with streaming
                    self.logger.console.clear()
                    self.logger.console.print(
                        self.ui.show_header(
                            self.current_session.session_id,
                            len(self.current_session.messages),
                            self.client.model
                        )
                    )
                    self.logger.print()
                    
                    response = self.client.chat_stream_with_logger(
                        message=user_input,
                        system=self.system_prompt,
                        conversation_history=self.current_session.get_messages()[:-1],
                        stream_title="LLM Response"
                    )
                    
                    # Add assistant response
                    self.current_session.add_message("assistant", response)
                    
                    # Auto-save
                    self.session_manager.save(self.current_session)
                    
                    self.logger.print()
                    
                except KeyboardInterrupt:
                    self.logger.console.print(
                        "\n\n[yellow]⚠️  Use /exit to quit[/yellow]\n"
                    )
                    continue
                    
                except Exception as e:
                    self.logger.error(f"Error: {e}")
                    self.ui.show_error(str(e))
                    continue
        
        finally:
            self.cleanup()
    
    def handle_command(self, command: str) -> None:
        """Handle slash commands."""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd in ['/exit', '/quit']:
            if self.ui.confirm("Are you sure you want to exit?"):
                self.logger.console.print("\n[bold green]👋 Goodbye![/bold green]\n")
                self.running = False
        
        elif cmd == '/help':
            self.ui.show_help()
        
        elif cmd == '/clear':
            if self.ui.confirm("Clear current conversation?"):
                self.current_session = ChatSession()
                self.logger.console.clear()
                self.ui.show_success("Conversation cleared")
        
        elif cmd == '/new':
            self.current_session = ChatSession()
            self.logger.console.clear()
            self.ui.show_success(f"New session created: {self.current_session.session_id}")
        
        elif cmd == '/save':
            path = self.session_manager.save(self.current_session)
            self.ui.show_success(f"Session saved: {path}")
        
        elif cmd == '/list':
            sessions = self.session_manager.list_sessions(limit=20)
            self.ui.show_sessions(sessions)
        
        elif cmd == '/load':
            if not args:
                self.ui.show_error("Usage: /load <session_id>")
                return
            
            session = self.session_manager.load(args)
            if session:
                self.current_session = session
                self.logger.console.clear()
                self.ui.show_success(f"Loaded session: {args}")
            else:
                self.ui.show_error(f"Session not found: {args}")
        
        elif cmd == '/export':
            path = self.session_manager.export_markdown(self.current_session.session_id)
            if path:
                self.logger.file_saved(str(path), "Markdown export")
            else:
                self.ui.show_error("Export failed")
        
        elif cmd == '/model':
            if not args:
                self.ui.show_info("Current Model", self.client.model)
                return
            
            self.client.model = args
            self.ui.show_success(f"Model changed to: {args}")
        
        elif cmd == '/system':
            if not args:
                if self.system_prompt:
                    self.ui.show_info("Current System Prompt", self.system_prompt)
                else:
                    self.ui.show_info("System Prompt", "Not set")
                return
            
            self.system_prompt = args
            self.ui.show_success("System prompt updated")
        
        else:
            self.ui.show_error(f"Unknown command: {cmd}")
            self.logger.console.print("[dim]Type /help for available commands[/dim]\n")
    
    def cleanup(self) -> None:
        """Cleanup before exit."""
        # Auto-save current session
        if self.current_session.messages:
            self.session_manager.save(self.current_session)
        
        self.logger.info("Application stopped")


def main() -> None:
    """Entry point for the CLI application."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI CLI - Modern terminal interface for AI conversations"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Anthropic API key (or set LLM_API_KEY env var)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="claude-sonnet-4-20250514",
        help="LLM model to use"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Get API key from args or environment
    api_key = args.api_key or os.getenv("LLM_API_KEY")
    if not api_key:
        print("Error: API key required. Set LLM_API_KEY or use --api-key")
        sys.exit(1)
    
    try:
        app = ChatApplication(
            api_key=api_key,
            model=args.model,
            log_level=args.log_level
        )
        app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
