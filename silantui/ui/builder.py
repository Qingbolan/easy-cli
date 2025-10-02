"""
UI Components Builder - Convenient UI Component Building System
"""

from typing import Optional, List, Dict, Any, Callable
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.box import Box, ROUNDED, HEAVY, DOUBLE, MINIMAL
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from dataclasses import dataclass


@dataclass
class UITheme:
    """UI Theme Configuration"""
    primary: str = "cyan"
    secondary: str = "magenta"
    success: str = "green"
    warning: str = "yellow"
    error: str = "red"
    info: str = "blue"
    dim: str = "dim"


class UIBuilder:
    """
    UI Builder - Convenient Interface Component Creation

    Example:
        >>> ui = UIBuilder()
        >>> panel = ui.panel("Title", "Content").border("cyan").build()
        >>> table = ui.table("Data").add_column("Name").add_row("Alice").build()
    """
    
    def __init__(self, console: Optional[Console] = None, theme: Optional[UITheme] = None):
        self.console = console or Console()
        self.theme = theme or UITheme()
    
    # ==================== Panel Builder ====================
    
    def panel(self, title: str = "", content: Any = "") -> 'PanelBuilder':
        """Create Panel builder"""
        return PanelBuilder(self.console, title, content, self.theme)

    # ==================== Table Builder ====================

    def table(self, title: str = "") -> 'TableBuilder':
        """Create Table builder"""
        return TableBuilder(self.console, title, self.theme)

    # ==================== Layout Builder ====================

    def layout(self, name: str = "root") -> 'LayoutBuilder':
        """Create Layout builder"""
        return LayoutBuilder(self.console, name, self.theme)

    # ==================== Menu Builder ====================

    def menu(self, title: str = "Menu") -> 'MenuBuilder':
        """Create Menu builder"""
        return MenuBuilder(self.console, title, self.theme)

    # ==================== Form Builder ====================

    def form(self, title: str = "Form") -> 'FormBuilder':
        """Create Form builder"""
        return FormBuilder(self.console, title, self.theme)

    # ==================== Quick Components ====================

    def success(self, message: str):
        """Quickly display success message"""
        text = Text()
        text.append("✓ ", style=f"bold {self.theme.success}")
        text.append(message, style=self.theme.success)
        self.console.print(text)

    def error(self, message: str):
        """Quickly display error message"""
        text = Text()
        text.append("✗ ", style=f"bold {self.theme.error}")
        text.append(message, style=self.theme.error)
        self.console.print(text)

    def warning(self, message: str):
        """Quickly display warning message"""
        text = Text()
        text.append("⚠ ", style=f"bold {self.theme.warning}")
        text.append(message, style=self.theme.warning)
        self.console.print(text)

    def info(self, message: str):
        """Quickly display info message"""
        text = Text()
        text.append("ℹ ", style=f"bold {self.theme.info}")
        text.append(message, style=self.theme.info)
        self.console.print(text)

    def confirm(self, message: str, default: bool = False) -> bool:
        """Quick confirmation dialog"""
        return Confirm.ask(f"[{self.theme.warning}]{message}[/{self.theme.warning}]", default=default)


class PanelBuilder:
    """Panel Builder"""

    def __init__(self, console: Console, title: str, content: Any, theme: UITheme):
        self.console = console
        self._title = title
        self._content = content
        self._theme = theme
        self._border_style = theme.primary
        self._box = ROUNDED
        self._padding = (1, 2)
        self._expand = False
        self._subtitle = None

    def border(self, style: str) -> 'PanelBuilder':
        """Set border style"""
        self._border_style = style
        return self

    def box_style(self, box: Box) -> 'PanelBuilder':
        """Set box type"""
        self._box = box
        return self

    def padding(self, padding: tuple) -> 'PanelBuilder':
        """Set padding"""
        self._padding = padding
        return self

    def expand(self, expand: bool = True) -> 'PanelBuilder':
        """Set whether to expand"""
        self._expand = expand
        return self

    def subtitle(self, subtitle: str) -> 'PanelBuilder':
        """Set subtitle"""
        self._subtitle = subtitle
        return self

    def build(self) -> Panel:
        """Build Panel"""
        return Panel(
            self._content,
            title=self._title,
            subtitle=self._subtitle,
            border_style=self._border_style,
            box=self._box,
            padding=self._padding,
            expand=self._expand
        )

    def show(self):
        """Build and display"""
        self.console.print(self.build())


class TableBuilder:
    """Table Builder"""
    
    def __init__(self, console: Console, title: str, theme: UITheme):
        self.console = console
        self._theme = theme
        self._table = Table(
            title=title,
            show_header=True,
            header_style="bold cyan",
            box=ROUNDED
        )
    
    def add_column(
        self,
        name: str,
        style: Optional[str] = None,
        width: Optional[int] = None,
        justify: str = "left"
    ) -> 'TableBuilder':
        """Add column"""
        self._table.add_column(
            name,
            style=style or "white",
            width=width,
            justify=justify
        )
        return self

    def add_row(self, *values: str) -> 'TableBuilder':
        """Add row"""
        self._table.add_row(*values)
        return self

    def add_rows(self, rows: List[tuple]) -> 'TableBuilder':
        """Batch add rows"""
        for row in rows:
            self._table.add_row(*row)
        return self

    def style(self, **kwargs) -> 'TableBuilder':
        """Set table style"""
        for key, value in kwargs.items():
            setattr(self._table, key, value)
        return self

    def build(self) -> Table:
        """Build Table"""
        return self._table

    def show(self):
        """Build and display"""
        self.console.print(self._table)


class LayoutBuilder:
    """Layout 构建器"""
    
    def __init__(self, console: Console, name: str, theme: UITheme):
        self.console = console
        self._theme = theme
        self._layout = Layout(name=name)
        self._sections: Dict[str, Any] = {}
    
    def split_column(self, *sections) -> 'LayoutBuilder':
        """垂直分割"""
        self._layout.split_column(*[
            Layout(name=name) if isinstance(name, str) else name
            for name in sections
        ])
        return self
    
    def split_row(self, *sections) -> 'LayoutBuilder':
        """水平分割"""
        self._layout.split_row(*[
            Layout(name=name) if isinstance(name, str) else name
            for name in sections
        ])
        return self
    
    def update(self, section: str, content: Any) -> 'LayoutBuilder':
        """更新区块内容"""
        self._layout[section].update(content)
        return self
    
    def size(self, section: str, size: int) -> 'LayoutBuilder':
        """设置区块大小"""
        self._layout[section].size = size
        return self
    
    def build(self) -> Layout:
        """构建 Layout"""
        return self._layout
    
    def show(self):
        """构建并显示"""
        self.console.print(self._layout)


class MenuBuilder:
    """Menu 构建器 - 创建交互式菜单"""
    
    def __init__(self, console: Console, title: str, theme: UITheme):
        self.console = console
        self._title = title
        self._theme = theme
        self._items: List[Dict[str, Any]] = []
    
    def add_item(
        self,
        key: str,
        label: str,
        handler: Optional[Callable] = None,
        description: str = ""
    ) -> 'MenuBuilder':
        """添加菜单项"""
        self._items.append({
            "key": key,
            "label": label,
            "handler": handler,
            "description": description
        })
        return self
    
    def add_separator(self) -> 'MenuBuilder':
        """添加分隔符"""
        self._items.append({"type": "separator"})
        return self
    
    def show(self) -> Optional[str]:
        """显示菜单并获取选择"""
        self.console.print(f"\n[bold {self._theme.primary}]{self._title}[/bold {self._theme.primary}]\n")
        
        choices = []
        for item in self._items:
            if item.get("type") == "separator":
                self.console.print("[dim]" + "─" * 50 + "[/dim]")
            else:
                key = item["key"]
                label = item["label"]
                desc = item["description"]
                choices.append(key)
                
                text = Text()
                text.append(f"{key}. ", style=f"bold {self._theme.warning}")
                text.append(label, style="white")
                if desc:
                    text.append(f" - {desc}", style=self._theme.dim)
                self.console.print(text)
        
        if not choices:
            return None
        
        choice = Prompt.ask(
            f"\n[{self._theme.primary}]请选择[/{self._theme.primary}]",
            choices=choices
        )
        
        # 执行处理函数
        for item in self._items:
            if item.get("key") == choice and item.get("handler"):
                item["handler"]()
        
        return choice


class FormBuilder:
    """Form 构建器 - 创建表单"""
    
    def __init__(self, console: Console, title: str, theme: UITheme):
        self.console = console
        self._title = title
        self._theme = theme
        self._fields: List[Dict[str, Any]] = []
    
    def add_field(
        self,
        name: str,
        label: str,
        field_type: str = "text",
        default: Any = None,
        required: bool = False,
        choices: Optional[List[str]] = None
    ) -> 'FormBuilder':
        """
        添加表单字段
        
        field_type: text, int, confirm, choice
        """
        self._fields.append({
            "name": name,
            "label": label,
            "type": field_type,
            "default": default,
            "required": required,
            "choices": choices
        })
        return self
    
    def show(self) -> Dict[str, Any]:
        """显示表单并获取输入"""
        self.console.print(f"\n[bold {self._theme.primary}]{self._title}[/bold {self._theme.primary}]\n")
        
        results = {}
        
        for field in self._fields:
            name = field["name"]
            label = field["label"]
            field_type = field["type"]
            default = field["default"]
            required = field["required"]
            choices = field["choices"]
            
            prompt_text = f"[{self._theme.info}]{label}[/{self._theme.info}]"
            
            if field_type == "text":
                value = Prompt.ask(prompt_text, default=default or "")
            elif field_type == "int":
                value = IntPrompt.ask(prompt_text, default=default or 0)
            elif field_type == "confirm":
                value = Confirm.ask(prompt_text, default=default or False)
            elif field_type == "choice":
                value = Prompt.ask(prompt_text, choices=choices, default=default)
            else:
                value = Prompt.ask(prompt_text, default=default or "")
            
            if required and not value:
                self.console.print(f"[{self._theme.error}]此字段必填！[/{self._theme.error}]")
                return self.show()  # 重新显示表单
            
            results[name] = value
        
        return results


# ==================== 预制组件 ====================

class QuickUI:
    """
    快速 UI 组件 - 提供常用的即用型 UI 组件
    
    Example:
        >>> quick = QuickUI()
        >>> quick.loading("Processing...", task_function)
        >>> choice = quick.yes_no("Continue?")
    """
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.builder = UIBuilder(self.console)
    
    def yes_no(self, question: str, default: bool = True) -> bool:
        """是/否选择"""
        return self.builder.confirm(question, default)
    
    def select_from_list(
        self,
        title: str,
        items: List[str],
        descriptions: Optional[List[str]] = None
    ) -> Optional[str]:
        """从列表中选择"""
        menu = self.builder.menu(title)
        for i, item in enumerate(items):
            desc = descriptions[i] if descriptions and i < len(descriptions) else ""
            menu.add_item(str(i + 1), item, description=desc)
        
        choice = menu.show()
        if choice:
            return items[int(choice) - 1]
        return None
    
    def progress_task(
        self,
        description: str,
        task: Callable,
        total: int = 100
    ):
        """带进度条的任务执行"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(),
            TextColumn("{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            task_id = progress.add_task(description, total=total)
            result = task(progress, task_id)
            return result
    
    def data_table(
        self,
        title: str,
        headers: List[str],
        rows: List[List[str]],
        styles: Optional[List[str]] = None
    ):
        """快速创建数据表格"""
        table = self.builder.table(title)
        
        for i, header in enumerate(headers):
            style = styles[i] if styles and i < len(styles) else None
            table.add_column(header, style=style)
        
        table.add_rows([tuple(row) for row in rows])
        table.show()
    
    def info_box(self, title: str, content: str, style: str = "info"):
        """信息框"""
        theme_map = {
            "info": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red"
        }
        border_style = theme_map.get(style, "blue")
        
        self.builder.panel(title, content).border(border_style).show()
    
    def three_column_layout(
        self,
        left_content: Any,
        center_content: Any,
        right_content: Any,
        left_size: int = 20,
        right_size: int = 20
    ):
        """三栏布局"""
        layout = self.builder.layout()
        layout.split_row("left", "center", "right")
        layout.size("left", left_size)
        layout.size("right", right_size)
        layout.update("left", left_content)
        layout.update("center", center_content)
        layout.update("right", right_content)
        layout.show()


# ==================== 导出 ====================

__all__ = [
    'UIBuilder',
    'UITheme',
    'PanelBuilder',
    'TableBuilder',
    'LayoutBuilder',
    'MenuBuilder',
    'FormBuilder',
    'QuickUI'
]
