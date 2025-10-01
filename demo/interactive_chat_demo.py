#!/usr/bin/env python3
"""
Interactive Chat Demo - Try the chat interface yourself

This is an interactive demo where you can type messages and see
simulated AI responses with the new minimalist interface.
"""

import os
import sys
import time
import random
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.prompt import Prompt
from easycli.chat_display import LiveChatDisplay
from easycli.command_system import CommandRegistry


# Sample responses for demo
SAMPLE_RESPONSES = [
    "That's an interesting question! Let me think about that for a moment...",
    "I understand what you're asking. Here's my perspective on this topic.",
    "Great point! This relates to several important concepts in computer science.",
    "Let me break this down for you in a clear and structured way.",
    "Excellent question! This is actually a fascinating area to explore.",
    "I appreciate you asking that. Here's a comprehensive answer:",
]


def generate_demo_response(user_message: str) -> str:
    """Generate a demo response based on user message"""
    intro = random.choice(SAMPLE_RESPONSES)

    # Generate contextual content
    if "?" in user_message:
        response_type = "answer"
        content = (
            f"{intro}\n\n"
            f"Regarding your question about '{user_message[:50]}...', "
            f"there are several key points to consider:\n\n"
            f"1. **First aspect**: This involves understanding the fundamental concepts\n"
            f"2. **Second aspect**: We need to consider the practical implications\n"
            f"3. **Third aspect**: Looking at real-world applications and examples\n\n"
            f"Would you like me to elaborate on any of these points?"
        )
    elif any(word in user_message.lower() for word in ["hello", "hi", "hey"]):
        content = (
            "Hello! Welcome to the interactive chat demo. 👋\n\n"
            "I'm here to demonstrate the new minimalist chat interface. "
            "Try asking me questions or giving me tasks to see how the interface responds!\n\n"
            "**Features you'll notice:**\n"
            "- Animated * indicator while I'm typing\n"
            "- Your messages with white background\n"
            "- Response time tracking\n"
            "- Clean, minimal design"
        )
    else:
        content = (
            f"{intro}\n\n"
            f"You mentioned: *{user_message[:80]}*\n\n"
            f"This is a simulated response to demonstrate the chat interface. "
            f"In a real implementation, this would be connected to an actual AI model. "
            f"Notice how the response streams in word by word with the animated * indicator!"
        )

    return content


def simulate_streaming(text: str, delay: float = 0.04):
    """Simulate streaming response"""
    words = text.split()
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        time.sleep(delay)


def main():
    """Main interactive demo"""
    console = Console()

    # Welcome screen
    console.clear()
    console.print("[bold cyan]" + "=" * 60 + "[/bold cyan]")
    console.print("[bold cyan]         Interactive Chat Demo - Try It Yourself!         [/bold cyan]")
    console.print("[bold cyan]" + "=" * 60 + "[/bold cyan]")
    console.print()
    console.print("[bold]Instructions:[/bold]")
    console.print("  • Type messages and press Enter to chat")
    console.print("  • Type [yellow]/exit[/yellow] to quit")
    console.print("  • Type [yellow]/new[/yellow] to clear chat history")
    console.print("  • Type [yellow]/help[/yellow] to see commands")
    console.print()
    console.print("[dim]Note: Responses are simulated for demo purposes[/dim]")
    console.print()
    console.print("[green]Press Enter to start chatting...[/green]")
    input()

    # Initialize chat display
    chat_display = LiveChatDisplay(
        console=console,
        role="Demo Bot",
        mode="interactive"
    )

    # Create simple command registry for demo
    demo_commands = CommandRegistry()

    # Register demo commands
    @demo_commands.command("exit", description="Exit the demo", category="Demo")
    def exit_cmd(app, args): pass

    @demo_commands.command("new", description="Clear chat history", category="Demo")
    def new_cmd(app, args): pass

    @demo_commands.command("help", description="Show help", category="Demo")
    def help_cmd(app, args): pass

    # Start live display (no alternate screen to keep input stable)
    chat_display.start(use_alt_screen=False)

    running = True

    try:
        while running:
            # Read user input inside the footer area (or fallback prompt)
            input_mode = os.getenv("EASYCLI_INPUT_MODE", "footer")  # footer | inline | prompt
            user_input = chat_display.read_input(mode=input_mode)

            if not user_input:
                chat_display.start()
                continue

            # Show command list if user just types /
            if user_input == "/":
                # Temporarily pause live to show command list below the UI
                with chat_display.pause():
                    demo_commands.show_command_list(console)
                    input("\n[dim]Press Enter to continue...[/dim]")
                continue

            # Handle commands
            if user_input.lower() == "/exit" or user_input.lower() == "/bye":
                # Stop display to show terminal history
                break

            if user_input.lower() == "/new":
                chat_display.clear_messages()
                time.sleep(0.5)
                continue

            if user_input.lower() == "/help":
                with chat_display.pause():
                    demo_commands.show_command_list(console)
                    input("\n[dim]Press Enter to continue...[/dim]")
                continue

            # Add user message
            chat_display.add_user_message(user_input)
            time.sleep(0.3)

            # Generate and stream response
            chat_display.start_assistant_message()

            response = generate_demo_response(user_input)
            for chunk in simulate_streaming(response):
                chat_display.append_streaming(chunk)

            chat_display.finish_assistant_message()
            time.sleep(0.5)

    except KeyboardInterrupt:
        pass

    finally:
        # Stop and show goodbye message (terminal history will be visible)
        chat_display.stop()
        console.print("\n[green]👋 Goodbye! Thanks for trying the demo.[/green]")
        console.print("[dim]Terminal history is now visible above.[/dim]\n")


if __name__ == "__main__":
    main()
