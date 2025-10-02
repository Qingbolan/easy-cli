#!/usr/bin/env python3
"""
Custom UI components demonstration.
"""

import time
from silantui import ModernLogger

def main():
    logger = ModernLogger(name="ui-demo", level="info")
    
    # Banner
    logger.banner(
        project_name="UI Demo",
        title="Custom UI Components",
        description="Showcasing ModernLogger's UI capabilities",
        font="slant"
    )
    
    # Sections
    logger.section("Log Levels")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.print()
    
    # Highlights
    logger.section("Highlights and Success")
    logger.highlight("This is a highlighted message with gradient")
    logger.success("Operation completed successfully!")
    logger.print()
    
    # Progress bar
    logger.section("Progress Bar")
    with logger.progress_bar(total=50, description="Processing items") as (progress, task):
        for i in range(50):
            time.sleep(0.05)
            progress.advance(task)
    logger.success("Processing complete!")
    logger.print()
    
    # Tables
    logger.section("Data Tables")
    table = logger.table(title="Sample Data")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Name", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Score", justify="right", style="yellow")
    
    table.add_row("1", "Alice", "Active", "95")
    table.add_row("2", "Bob", "Active", "87")
    table.add_row("3", "Charlie", "Inactive", "92")
    
    logger.console.print(table)
    logger.print()
    
    # Info panels
    logger.section("Information Panels")
    logger.info_panel(
        "System Status",
        "All systems operational\nCPU: 45%\nMemory: 2.1 GB\nDisk: 120 GB free"
    )
    logger.print()
    
    # Error box
    logger.section("Error Display")
    logger.error_box(
        "Connection failed!\n\n"
        "Could not connect to database server.\n"
        "Please check your network connection and try again."
    )
    logger.print()
    
    # Streaming demo
    logger.section("Live Streaming Display")
    sample_text = """# Welcome to Streaming

This is a demonstration of the **live streaming** display feature.

## Features

- Real-time updates
- Markdown rendering
- Code syntax highlighting

```python
def hello_world():
    print("Hello, World!")
```

The text updates smoothly as new content arrives!
"""
    
    with logger.stream(title="Live Content") as stream:
        words = sample_text.split()
        accumulated = ""
        for i, word in enumerate(words):
            accumulated += word + " "
            elapsed = (i + 1) * 0.1
            stream.update_text(accumulated, elapsed_s=elapsed)
            time.sleep(0.05)
    
    logger.print()
    
    # Gradient text
    logger.section("Gradient Text")
    logger.gradient_text("This text has a beautiful gradient effect!")
    logger.print()
    
    # Stage announcements
    logger.stage("Pipeline Started")
    time.sleep(1)
    logger.info("Step 1: Initializing...")
    time.sleep(1)
    logger.info("Step 2: Processing...")
    time.sleep(1)
    logger.info("Step 3: Finalizing...")
    time.sleep(1)
    logger.stage("Pipeline Completed")
    
    logger.print()
    logger.success("UI demonstration completed!")


if __name__ == "__main__":
    main()
