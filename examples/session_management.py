#!/usr/bin/env python3
"""
Session management example.
"""

from silantui import ChatSession, SessionManager, ChatUI, ModernLogger

def main():
    logger = ModernLogger(name="session-demo", level="info")
    ui = ChatUI(logger=logger)
    manager = SessionManager()
    
    logger.banner(
        project_name="Sessions",
        title="Session Management Demo",
        description="Save, load, and export conversations",
        font="slant"
    )
    
    # Create a sample session
    logger.section("Creating Sample Session")
    
    session = ChatSession()
    
    # Add some messages
    session.add_message("user", "Hello! Can you help me with Python?")
    session.add_message(
        "assistant",
        "Of course! I'd be happy to help you with Python. What would you like to know?"
    )
    session.add_message("user", "How do I read a file in Python?")
    session.add_message(
        "assistant",
        """Here's how to read a file in Python:

```python
# Method 1: Using with statement (recommended)
with open('file.txt', 'r') as f:
    content = f.read()

# Method 2: Read line by line
with open('file.txt', 'r') as f:
    for line in f:
        print(line.strip())

# Method 3: Read all lines into a list
with open('file.txt', 'r') as f:
    lines = f.readlines()
```

The `with` statement is recommended because it automatically closes the file.
"""
    )
    
    logger.success(f"Created session: {session.session_id}")
    logger.info(f"Messages: {len(session.messages)}")
    logger.print()
    
    # Display the conversation
    logger.section("Conversation Display")
    ui.show_conversation(session)
    
    # Save session
    logger.section("Saving Session")
    path = manager.save(session)
    logger.file_saved(str(path), "Session data")
    
    # Export to Markdown
    logger.section("Exporting to Markdown")
    md_path = manager.export_markdown(session.session_id)
    if md_path:
        logger.file_saved(str(md_path), "Markdown export")
    
    # List all sessions
    logger.section("All Saved Sessions")
    sessions = manager.list_sessions(limit=10)
    ui.show_sessions(sessions)
    
    # Load the session back
    logger.section("Loading Session")
    loaded_session = manager.load(session.session_id)
    if loaded_session:
        logger.success(f"Loaded session: {loaded_session.session_id}")
        logger.info(f"Messages: {len(loaded_session.messages)}")
    
    logger.print()
    logger.success("Session management demo completed!")


if __name__ == "__main__":
    main()
