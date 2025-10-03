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

    # Initialize chat display with role and mode
    chat_display = LiveChatDisplay(
        console=console,
        role="Assistant",
        mode="streaming"
    )

    # Start live display - this will use alt-screen
    chat_display.start()

    # Add welcome message as a system message in chat
    time.sleep(0.5)

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

            # Show progress in footer without stopping Live
            chat_display.notify(f"Demo message {i}/{len(demo_conversations)}: {conv['user'][:40]}...", "yellow")
            time.sleep(1)

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

        # Show completion message in footer
        time.sleep(1)
        chat_display.show_success("Demo completed! Press Ctrl+C to exit")

        # Keep Live running, wait for exit
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        chat_display.stop()
        console.print("\n\n[yellow]Demo interrupted. Goodbye![/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
