#!/usr/bin/env python3
"""
Internationalization (i18n) Example
Shows how to use SilanTui with different languages
"""

from silantui import UIBuilder, ModernLogger, CommandRegistry
from silantui.i18n import set_language, get_language, t
from rich.prompt import Prompt


class MultilingualApp:
    """Example application with i18n support"""
    
    def __init__(self):
        self.logger = ModernLogger(name="i18n-demo")
        self.ui = UIBuilder(console=self.logger.console)
        self.registry = CommandRegistry()
        
        # Default to English
        set_language('en')
        
        self.register_commands()
    
    def register_commands(self):
        """Register commands with translations"""
        
        @self.registry.command("lang", description="Change language")
        def cmd_lang(app, args):
            app.change_language(args)
        
        @self.registry.command("menu", description="Show menu")
        def cmd_menu(app, args):
            app.show_menu()
        
        @self.registry.command("table", description="Show table")
        def cmd_table(app, args):
            app.show_table()
    
    def show_welcome(self):
        """Show welcome message"""
        self.logger.console.print(f"\n[bold cyan]{t('welcome')} to SilanTui![/bold cyan]")
        self.logger.console.print(f"[dim]Current language: {get_language()}[/dim]\n")
        
        # Show available commands
        panel = self.ui.panel(
            "Commands",
            f"/lang <code>  - Change language (en, zh, es, fr, ja)\n"
            f"/menu         - Show menu\n"
            f"/table        - Show table\n"
            f"/exit         - {t('command.exit')}"
        ).border("cyan").build()
        
        self.logger.console.print(panel)
        self.logger.console.print()
    
    def change_language(self, lang_code: str):
        """Change application language"""
        if not lang_code:
            self.logger.console.print(f"\nCurrent language: [yellow]{get_language()}[/yellow]")
            self.logger.console.print("Available: en, zh, es, fr, ja\n")
            return
        
        try:
            set_language(lang_code)
            self.ui.success(f"Language changed to: {lang_code}")
            self.show_welcome()
        except ValueError as e:
            self.ui.error(str(e))
    
    def show_menu(self):
        """Show multilingual menu"""
        self.logger.console.print()
        
        choice = self.ui.menu(t('menu.title')) \
            .add_item("1", "Option 1", description=f"{t('info')}: This is option 1") \
            .add_item("2", "Option 2", description=f"{t('info')}: This is option 2") \
            .add_separator() \
            .add_item("3", t('menu.back')) \
            .show()
        
        if choice == "1":
            self.ui.success(f"{t('success')}: Option 1 selected")
        elif choice == "2":
            self.ui.success(f"{t('success')}: Option 2 selected")
        elif choice == "3":
            self.logger.console.print(f"[dim]{t('menu.back')}...[/dim]")
        
        self.logger.console.print()
    
    def show_table(self):
        """Show multilingual table"""
        self.logger.console.print()
        
        table = self.ui.table("User Data")
        table.add_column("ID", style="cyan", width=5)
        table.add_column("Name", style="green")
        table.add_column("Status", style="yellow")
        
        table.add_row("1", "Alice", t('success'))
        table.add_row("2", "Bob", t('warning'))
        table.add_row("3", "Charlie", t('error'))
        
        table.show()
        self.logger.console.print()
    
    def run(self):
        """Run the application"""
        self.logger.console.clear()
        self.show_welcome()
        
        running = True
        
        while running:
            try:
                user_input = Prompt.ask(
                    f"\n[bold yellow]> [/bold yellow]"
                ).strip()
                
                if not user_input:
                    continue
                
                # Handle exit
                if user_input.lower() in ['/exit', '/quit', '/q']:
                    self.logger.console.print(f"\n[green]{t('exit')}...[/green]\n")
                    break
                
                # Handle commands
                if user_input.startswith('/'):
                    parts = user_input.split(maxsplit=1)
                    cmd = parts[0].lstrip('/').lower()
                    args = parts[1] if len(parts) > 1 else ""
                    
                    if self.registry.exists(cmd):
                        self.registry.execute(cmd, self, args)
                    else:
                        self.ui.error(t('command.not_found', cmd))
                else:
                    self.logger.console.print(
                        f"[dim]{t('info')}: Type /help for commands[/dim]"
                    )
            
            except KeyboardInterrupt:
                self.logger.console.print(f"\n\n[yellow]Use /exit to quit[/yellow]\n")
                continue


def demo_all_languages():
    """Demo all supported languages"""
    from silantui import ModernLogger
    from silantui.i18n import Translator
    
    logger = ModernLogger(name="lang-demo")
    translator = Translator()
    
    logger.banner(
        project_name="i18n Demo",
        title="Multilingual Support",
        description="SilanTui supports multiple languages",
        font="slant"
    )
    
    # Show translations in all languages
    logger.section("Supported Languages")
    
    for lang in translator.get_available_languages():
        translator.set_language(lang)
        
        logger.console.print(f"\n[bold cyan]{lang.upper()}[/bold cyan]")
        logger.console.print(f"  {translator.get('welcome')}")
        logger.console.print(f"  {translator.get('success')}")
        logger.console.print(f"  {translator.get('error')}")
        logger.console.print(f"  {translator.get('command.help')}")
    
    logger.console.print()


def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        # Show all languages
        demo_all_languages()
    else:
        # Run interactive app
        app = MultilingualApp()
        app.run()


if __name__ == "__main__":
    main()
