#!/usr/bin/env python3
"""
Interactive Chat Demo - Try the chat interface yourself

This is an interactive demo where you can type messages and see
simulated AI responses with the modern Textual interface.
"""

import os
import sys
import time
import random
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from silantui.ui.textual_chat import ChatApp
from silantui.core.command_system import CommandRegistry


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


class DemoChatApp(ChatApp):
    """Demo chat app with simulated responses"""

    async def simulate_response(self, user_message: str):
        """Generate and stream simulated response"""
        import asyncio

        response = generate_demo_response(user_message)

        # Start streaming
        self.start_streaming()

        # Stream word by word asynchronously
        words = response.split()
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            self.append_streaming(chunk)
            await asyncio.sleep(0.04)  # Non-blocking delay

        # Finish streaming (不带参数，内容已经通过 append_streaming 累积了)
        self.finish_streaming()


def main():
    """Main interactive demo"""
    # Run the Textual app
    app = DemoChatApp(role="Demo Bot")
    app.run()


if __name__ == "__main__":
    main()
