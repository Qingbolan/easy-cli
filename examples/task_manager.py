#!/usr/bin/env python3
"""
Task Manager
Demonstrates SilanTui as a pure UI application framework
"""

from silantui import ModernLogger, UIBuilder, CommandRegistry
from datetime import datetime
import json
from pathlib import Path


class Task:
    """Task data class"""

    def __init__(self, id: int, title: str, status: str = "todo", priority: str = "medium"):
        self.id = id
        self.title = title
        self.status = status  # todo, doing, done
        self.priority = priority  # low, medium, high
        self.created = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "priority": self.priority,
            "created": self.created,
        }
    
    @classmethod
    def from_dict(cls, data):
        task = cls(data["id"], data["title"], data["status"], data["priority"])
        task.created = data["created"]
        return task


class TaskManager:
    """Task Manager application"""

    def __init__(self):
        self.logger = ModernLogger(name="tasks", level="info")
        self.ui = UIBuilder(console=self.logger.console)
        self.registry = CommandRegistry()

        self.tasks = []
        self.next_id = 1
        self.data_file = Path.home() / ".silantui" / "tasks.json"
        self.running = True

        self.load_tasks()
        self.register_commands()

    def register_commands(self):
        """Register commands"""

        @self.registry.command("add", description="Add task", aliases=["a"])
        def cmd_add(app, args):
            if not args:
                app.ui.error("Please provide task title")
                return
            app.add_task(args)

        @self.registry.command("list", description="List tasks", aliases=["ls"])
        def cmd_list(app, args):
            filter_status = args.lower() if args else None
            app.list_tasks(filter_status)

        @self.registry.command("done", description="Complete task", aliases=["d"])
        def cmd_done(app, args):
            if not args:
                app.ui.error("Please provide task ID")
                return
            try:
                app.mark_done(int(args))
            except ValueError:
                app.ui.error("Invalid ID")

        @self.registry.command("delete", description="Delete task", aliases=["del"])
        def cmd_delete(app, args):
            if not args:
                app.ui.error("Please provide task ID")
                return
            try:
                app.delete_task(int(args))
            except ValueError:
                app.ui.error("Invalid ID")

        @self.registry.command("stats", description="Statistics", aliases=["st"])
        def cmd_stats(app, args):
            app.show_stats()
    
    def load_tasks(self):
        """Load tasks"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(t) for t in data["tasks"]]
                    self.next_id = data.get("next_id", 1)
            except Exception as e:
                self.logger.warning(f"Failed to load tasks: {e}")

    def save_tasks(self):
        """Save tasks"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "tasks": [t.to_dict() for t in self.tasks],
                    "next_id": self.next_id,
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save tasks: {e}")

    def add_task(self, title: str):
        """Add task"""
        task = Task(self.next_id, title)
        self.tasks.append(task)
        self.next_id += 1
        self.save_tasks()

        self.ui.success(f"Added task #{task.id}: {title}")

    def list_tasks(self, filter_status: str = None):
        """List tasks"""
        self.logger.console.print()

        # Filter tasks
        if filter_status:
            filtered = [t for t in self.tasks if t.status == filter_status]
            title = f"📝 Task List ({filter_status})"
        else:
            filtered = self.tasks
            title = "📝 Task List (All)"

        if not filtered:
            self.ui.info("No tasks")
            return

        # Create table
        table = self.ui.table(title)
        table.add_column("ID", style="cyan", width=5)
        table.add_column("Title", style="white", width=40)
        table.add_column("Status", style="yellow", width=10)
        table.add_column("Priority", style="magenta", width=10)
        table.add_column("Created", style="dim", width=20)

        for task in filtered:
            # Status icons
            status_icons = {
                "todo": "○ Todo",
                "doing": "◐ In Progress",
                "done": "● Done",
            }
            status = status_icons.get(task.status, task.status)

            # Priority colors
            priority_colors = {
                "low": "[dim]Low[/dim]",
                "medium": "[yellow]Medium[/yellow]",
                "high": "[red]High[/red]",
            }
            priority = priority_colors.get(task.priority, task.priority)

            # Format time
            created = datetime.fromisoformat(task.created).strftime("%Y-%m-%d %H:%M")

            table.add_row(
                str(task.id),
                task.title,
                status,
                priority,
                created
            )

        table.show()
        self.logger.console.print()

    def mark_done(self, task_id: int):
        """Mark task as done"""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            self.ui.error(f"Task #{task_id} does not exist")
            return

        task.status = "done"
        self.save_tasks()
        self.ui.success(f"Task #{task_id} completed!")

    def delete_task(self, task_id: int):
        """Delete task"""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            self.ui.error(f"Task #{task_id} does not exist")
            return

        if self.ui.confirm(f"Are you sure you want to delete task #{task_id}?"):
            self.tasks.remove(task)
            self.save_tasks()
            self.ui.success(f"Task #{task_id} deleted")

    def show_stats(self):
        """Display statistics"""
        self.logger.console.print()

        total = len(self.tasks)
        todo = len([t for t in self.tasks if t.status == "todo"])
        doing = len([t for t in self.tasks if t.status == "doing"])
        done = len([t for t in self.tasks if t.status == "done"])

        # Create statistics panel
        stats_content = f"""
[bold cyan]Task Statistics[/bold cyan]

Total Tasks: [yellow]{total}[/yellow]
Todo: [red]{todo}[/red]
In Progress: [yellow]{doing}[/yellow]
Completed: [green]{done}[/green]

Completion Rate: [{"green" if total > 0 and done / total > 0.7 else "yellow"}]{done / total * 100 if total > 0 else 0:.1f}%[/]
"""

        panel = self.ui.panel("📊 Statistics", stats_content).border("cyan").build()
        self.logger.console.print(panel)
        self.logger.console.print()
    
    def show_welcome(self):
        """Display welcome screen"""
        self.logger.banner(
            project_name="TaskManager",
            title="Task Manager",
            description="Simple and efficient task management tool",
            font="slant"
        )

        self.logger.console.print("\n[bold cyan]Quick Start:[/bold cyan]")
        self.logger.console.print("  /add <title>    - Add task")
        self.logger.console.print("  /list          - List all tasks")
        self.logger.console.print("  /done <ID>     - Complete task")
        self.logger.console.print("  /delete <ID>   - Delete task")
        self.logger.console.print("  /stats         - View statistics")
        self.logger.console.print()

    def run(self):
        """Run application"""
        self.logger.console.clear()
        self.show_welcome()

        # Display current tasks
        if self.tasks:
            self.list_tasks()

        while self.running:
            try:
                # Show menu
                choice = self.ui.menu("📋 Main Menu") \
                    .add_item("1", "Add Task") \
                    .add_item("2", "View Tasks") \
                    .add_item("3", "Complete Task") \
                    .add_item("4", "Delete Task") \
                    .add_separator() \
                    .add_item("5", "Statistics") \
                    .add_item("6", "Exit") \
                    .show()

                if choice == "1":
                    from rich.prompt import Prompt
                    title = Prompt.ask("[yellow]Task Title[/yellow]")
                    if title:
                        self.add_task(title)

                elif choice == "2":
                    filter_choice = self.ui.menu("Filter") \
                        .add_item("1", "All") \
                        .add_item("2", "Todo") \
                        .add_item("3", "In Progress") \
                        .add_item("4", "Done") \
                        .show()

                    filter_map = {
                        "2": "todo",
                        "3": "doing",
                        "4": "done",
                    }
                    self.list_tasks(filter_map.get(filter_choice))

                elif choice == "3":
                    self.list_tasks()
                    from rich.prompt import IntPrompt
                    task_id = IntPrompt.ask("[yellow]Task ID[/yellow]")
                    self.mark_done(task_id)

                elif choice == "4":
                    self.list_tasks()
                    from rich.prompt import IntPrompt
                    task_id = IntPrompt.ask("[yellow]Task ID[/yellow]")
                    self.delete_task(task_id)

                elif choice == "5":
                    self.show_stats()

                elif choice == "6":
                    self.running = False
                    self.logger.console.print("\n[green]👋 Goodbye![/green]\n")

            except KeyboardInterrupt:
                self.logger.console.print("\n\n[yellow]Use menu option 6 to exit[/yellow]\n")
                continue
            except Exception as e:
                self.ui.error(f"Error: {e}")


def main():
    """Main function"""
    app = TaskManager()
    app.run()


if __name__ == "__main__":
    main()
