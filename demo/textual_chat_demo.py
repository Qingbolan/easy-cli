#!/usr/bin/env python3
"""
Textual Chat Demo - Modern interactive chat interface

This demo showcases the Textual-based chat UI with:
- Automatic scrolling
- True interactive input
- Mouse and keyboard navigation
- Better performance and user experience
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from silantui.ui.textual_chat import ChatApp


class DemoChatApp(ChatApp):
    """
    Demo chat application with simulated responses
    """

    def simulate_response(self, user_message: str):
        """Simulate an AI response with streaming"""
        # Detect greeting
        if any(word in user_message.lower() for word in ["hello", "hi", "hey"]):
            response = (
                "Hello! Welcome to the Textual-based chat demo. 👋\n\n"
                "I'm here to demonstrate the new interface built with Textual. "
                "Try asking me questions or giving me tasks!\n\n"
                "**Features:**\n"
                "- Automatic scrolling with mouse wheel\n"
                "- True interactive input (no stop/start)\n"
                "- Native keyboard navigation\n"
                "- Clean, modern design\n"
            )
        elif "?" in user_message:
            response = (
                f"Great question about '{user_message[:50]}...'!\n\n"
                "Here are some key points:\n\n"
                "1. **First**: Understanding the fundamentals\n"
                "2. **Second**: Considering practical implications\n"
                "3. **Third**: Looking at real-world examples\n\n"
                "Would you like me to elaborate on any of these?"
            )
        else:
            response = (
                f"You said: *{user_message[:80]}*\n\n"
                "This is a simulated response to demonstrate the chat interface. "
                "In a real implementation, this would be connected to an actual AI model.\n\n"
                "Notice how smooth the scrolling is, and you can use arrow keys or mouse wheel!"
            )

        # Simulate streaming with word-by-word output
        self.start_streaming()

        words = response.split()
        streamed_content = ""

        for i, word in enumerate(words):
            streamed_content += word + (" " if i < len(words) - 1 else "")
            self.append_streaming(word + " ")
            time.sleep(0.05)  # Simulate network delay

        self.finish_streaming(response)


def main():
    """Run the Textual chat demo"""
    app = DemoChatApp(role="Demo Bot")
    app.run()


if __name__ == "__main__":
    main()
