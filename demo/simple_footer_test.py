#!/usr/bin/env python3
"""Simple footer layout test - Shows the footer for 10 seconds"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from silantui.ui.chat_display import LiveChatDisplay


def main():
    """Display the chat interface with footer for inspection"""
    console = Console()

    # Clear screen and show info
    console.clear()
    console.print("[bold cyan]Testing Footer Layout[/bold cyan]")
    console.print("The chat interface will appear for 10 seconds...")
    console.print("Check the footer at the bottom:")
    console.print("  Line 1: Status (left-aligned)")
    console.print("  Line 2: Horizontal separator")
    console.print("  Line 3: Input prompt")
    console.print("  Line 4: Horizontal separator")
    console.print("  Line 5: Mode (left) | Tips (right)")
    console.print()
    time.sleep(3)

    # Initialize chat display
    chat_display = LiveChatDisplay(
        console=console,
        role="Assistant",
        mode="interactive"
    )

    # Start live display
    chat_display.start()

    # Add a test message to show in chat area
    time.sleep(1)
    chat_display.add_user_message("Hello! This is a test message.")
    time.sleep(1)

    # Start and finish a response
    chat_display.start_assistant_message()
    chat_display.append_streaming("This is a test response to demonstrate the layout. ")
    time.sleep(0.5)
    chat_display.append_streaming("The footer should show status, input area, and mode information.")
    time.sleep(0.5)
    chat_display.finish_assistant_message()

    # Wait to inspect
    time.sleep(10)

    # Stop and show completion
    chat_display.stop()
    console.print("\n[green]✓ Footer test complete![/green]")
    console.print("\nDid you see:")
    console.print("  1. [dim]Ready[/dim] status at top (left-aligned)?")
    console.print("  2. Horizontal line separators?")
    console.print("  4. [cyan]interactive[/cyan] mode on left?")
    console.print("  5. [dim]Type / for commands[/dim] tip on right?")
    console.print()


if __name__ == "__main__":
    main()
