#!/usr/bin/env python3
"""
Chat Display Demo - Showcasing the minimalist chat interface

This demo showcases:
- Minimalist input box with horizontal lines
- User messages with white background (> prefix)
- AI messages with animated * indicator
- Status display (top-right of input box)
- Mode display (bottom-right of input box)
- Real-time streaming with duration tracking
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.prompt import Prompt
from silantui.ui.chat_display import LiveChatDisplay


def simulate_streaming_response(text: str, delay: float = 0.03):
    """Simulate streaming response word by word"""
    words = text.split()
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        time.sleep(delay)


def main():
    """Main demo function"""
    console = Console()

    # Clear screen and show welcome
    console.clear()
    console.print("[bold cyan]═══════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]   Chat Display Demo - Minimalist Interface   [/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════[/bold cyan]")
    console.print()
    console.print("This demo showcases the new minimalist chat interface:")
    console.print("  • [green]Animated * indicator[/green] during streaming")
    console.print("  • [white on black]White background user messages[/white on black] with > prefix")
    console.print("  • [dim]Status display[/dim] above input (left-aligned)")
    console.print("  • [cyan]Mode and tips display[/cyan] below input")
    console.print("  • [yellow]Duration tracking[/yellow] for responses")
    console.print("  • [magenta]5-line footer layout[/magenta] with horizontal separators")
    console.print()
    console.print("[dim]Press Enter to start the demo...[/dim]")
    input()

    # Initialize chat display with role and mode
    chat_display = LiveChatDisplay(
        console=console,
        role="Assistant",
        mode="streaming"
    )

    # Start live display
    chat_display.start()

    # Demo conversations
    demo_conversations = [
        {
            "user": "Hello! What can you help me with?",
            "assistant": "Hello! I'm an AI assistant. I can help you with various tasks like answering questions, writing code, creative writing, problem-solving, and much more. What would you like to explore today?"
        },
        {
            "user": "Can you explain what quantum computing is?",
            "assistant": "Quantum computing is a revolutionary computing paradigm that leverages quantum mechanical phenomena like superposition and entanglement. Unlike classical computers that use bits (0 or 1), quantum computers use qubits which can exist in multiple states simultaneously. This enables them to solve certain complex problems exponentially faster than traditional computers."
        },
        {
            "user": "That's fascinating! What are some practical applications?",
            "assistant": "Quantum computers have exciting applications including:\n\n• **Cryptography**: Breaking current encryption and creating quantum-safe algorithms\n• **Drug Discovery**: Simulating molecular interactions for new medicines\n• **Optimization**: Solving complex logistics and scheduling problems\n• **AI/ML**: Accelerating machine learning algorithms\n• **Financial Modeling**: Risk analysis and portfolio optimization\n\nWhile still in early stages, these applications could transform multiple industries!"
        }
    ]

    try:
        for i, conv in enumerate(demo_conversations, 1):
            # Simulate user typing
            time.sleep(1.5)

            # Stop live display to get input
            chat_display.stop()
            console.print(f"\n[dim]Demo message {i}/{len(demo_conversations)}[/dim]")
            console.print(f"[bold yellow]Simulating user input:[/bold yellow] {conv['user']}")
            time.sleep(1)
            chat_display.start()

            # Add user message
            chat_display.add_user_message(conv['user'])
            time.sleep(0.5)

            # Start AI response
            chat_display.start_assistant_message()

            # Stream response
            for chunk in simulate_streaming_response(conv['assistant']):
                chat_display.append_streaming(chunk)
                time.sleep(0.05)

            # Finish response
            chat_display.finish_assistant_message()
            time.sleep(1)

        # Show completion message
        time.sleep(1)
        chat_display.stop()

        console.print("\n[bold green]✓ Demo completed![/bold green]")
        console.print("\n[bold cyan]Key Features Demonstrated:[/bold cyan]")
        console.print("  1. [green]Pulsing * animation[/green] during streaming (* → ✦ → ✧)")
        console.print("  2. [white on black]User messages[/white on black] with > prefix and white background")
        console.print("  3. [yellow]Metadata display[/yellow] - Role/Time/Duration in 「」 brackets")
        console.print("  4. [dim]Status indicator[/dim] above input (left-aligned)")
        console.print("  5. [cyan]Mode display[/cyan] below input (left: mode, right: tips)")
        console.print("  6. [magenta]Markdown rendering[/magenta] for formatted AI responses")
        console.print("  7. [yellow]Footer layout[/yellow] - 5 lines with horizontal separators")
        console.print("\n[dim]Press Ctrl+C to exit[/dim]")

        input()

    except KeyboardInterrupt:
        chat_display.stop()
        console.print("\n\n[yellow]Demo interrupted. Goodbye![/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
