#!/usr/bin/env python3
"""Test SimpleChatDisplay - no Live component version."""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from silantui.ui import SimpleChatDisplay


def simulate_streaming(text: str, delay: float = 0.05):
    """Simulate streaming response"""
    words = text.split()
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        time.sleep(delay)


def main():
    """Test SimpleChatDisplay"""
    console = Console()

    # Create chat display
    chat = SimpleChatDisplay(
        console=console,
        role="Assistant",
        mode="chat"
    )

    # Start display
    chat.start()

    # Simulate conversation
    time.sleep(2)

    # User message
    chat.add_user_message("Hello! Can you help me?")
    time.sleep(1)

    # Assistant streaming response
    chat.start_assistant_message()
    response = "Of course! I'm here to help. What would you like to know?"

    for chunk in simulate_streaming(response):
        chat.append_streaming(chunk)

    chat.finish_assistant_message()
    time.sleep(2)

    # Another exchange
    chat.add_user_message("Tell me about Python.")
    time.sleep(1)

    chat.start_assistant_message()
    response2 = "Python is a high-level programming language known for:\n\n- Easy to learn syntax\n- Large ecosystem of libraries\n- Great for web development, data science, and automation"

    for chunk in simulate_streaming(response2):
        chat.append_streaming(chunk)

    chat.finish_assistant_message()
    time.sleep(2)

    console.print("\n[green]✓ Test completed! SimpleChatDisplay works correctly.[/green]\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[yellow]Test interrupted[/yellow]")
        sys.exit(0)
