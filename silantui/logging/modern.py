from __future__ import annotations

from pathlib import Path
import logging
import re
import time
from functools import lru_cache
from logging.handlers import RotatingFileHandler
from typing import Any, Optional, Tuple, Set, Dict, List

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install as install_rich_traceback
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.box import ROUNDED
from rich.theme import Theme
from rich.live import Live
from rich.align import Align
from pyfiglet import Figlet


class ModernLogger:
    """
    A modern, colorful logger built on top of Rich.

    Highlights
    ----------
    • Clean, emoji-tagged log levels
    • Gradient titles / headers (Vue-style palette)
    • File logging with rotation
    • Ready-to-use progress bars and live XML highlighting stream
    • Handy helpers: sections, banners, tables, saved-file links

    Example
    -------
    >>> log = ModernLogger(level="debug", show_path=False)
    >>> log.section("Boot")
    >>> log.info("Service starting...")
    >>> with log.progress_bar(total=3, description="Warmup") as (p, task):
    ...     for _ in range(3):
    ...         p.advance(task); time.sleep(0.1)
    >>> with log.stream(title="Model Output") as s:
    ...     s.update_text("<answer>Hello</answer>", elapsed_s=0.12)
    """

    LEVEL_ICONS = {
        "DEBUG": "🐛",
        "INFO": "ℹ️",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "💀",
    }

    # Gradient palette (Vue-ish green → purple)
    GRADIENT_START = "#41B883"
    GRADIENT_END = "#6574CD"

    def __init__(
        self,
        name: str = "app",
        level: str = "info",
        log_file: Optional[str] = None,
        show_path: bool = False,
        rich_tracebacks: bool = True,
        max_bytes: int = 5 * 1024 * 1024,
        backup_count: int = 3,
    ):
        # Rich tracebacks (opt-in locals)
        install_rich_traceback(show_locals=rich_tracebacks)

        levels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        log_level = levels.get(level.lower(), logging.INFO)

        theme = Theme(
            {
                # log styles
                "info": "bold cyan",
                "warning": "bold yellow",
                "error": "bold red",
                "critical": "bold white on red",
                "success": "#4CAF50",
                "logging.time": "dim white",
                "logging.level.debug": "grey70",
                "logging.level.info": "bold cyan",
                "logging.level.warning": "bold yellow",
                "logging.level.error": "bold red",
                "logging.level.critical": "bold white on red",
                # palette
                "vue_primary": "#42B883",
                "vue_secondary": "#35495E",
                "vue_info": "bright_blue",
                "vue_success": "green",
                "vue_warning": "yellow",
                "default": "white",
                "vue_inside": "cyan",
            }
        )

        self.console = Console(theme=theme, highlight=True)

        rich_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_level=True,
            show_path=show_path,
            markup=True,
            rich_tracebacks=rich_tracebacks,
            log_time_format="%H:%M:%S",
        )

        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.logger.handlers.clear()
        self.logger.addHandler(rich_handler)

        if log_file:
            self._setup_file_handler(
                log_file=log_file, max_bytes=max_bytes, backup_count=backup_count
            )

    # -------------------- Core setup --------------------

    def _setup_file_handler(
        self, log_file: str, max_bytes: int, backup_count: int
    ) -> None:
        """
        Attach a rotating file handler. Creates parent directories if needed.
        """
        log_path = Path(log_file).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)

        fh = RotatingFileHandler(
            log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        fh.setLevel(self.logger.level)
        fh.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        self.logger.addHandler(fh)

    # -------------------- Utilities --------------------

    @staticmethod
    def _hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
        hex_code = hex_code.strip()
        if not re.fullmatch(r"#?[0-9A-Fa-f]{6}", hex_code):
            raise ValueError(f"Invalid hex color: {hex_code}")
        hex_code = hex_code if hex_code.startswith("#") else f"#{hex_code}"
        return (int(hex_code[1:3], 16), int(hex_code[3:5], 16), int(hex_code[5:7], 16))

    def _create_gradient_text(self, text: str) -> Text:
        sr, sg, sb = self._hex_to_rgb(self.GRADIENT_START)
        er, eg, eb = self._hex_to_rgb(self.GRADIENT_END)
        n = max(1, len(text))

        out = Text()
        for i, ch in enumerate(text):
            t = i / (n - 1) if n > 1 else 0.0
            r = int(sr + (er - sr) * t)
            g = int(sg + (eg - sg) * t)
            b = int(sb + (eb - sb) * t)
            out.append(ch, style=f"#{r:02X}{g:02X}{b:02X}")
        return out

    # -------------------- Log level helpers --------------------

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.logger.debug(f"{self.LEVEL_ICONS['DEBUG']} {message}", *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.logger.info(f"{self.LEVEL_ICONS['INFO']} {message}", *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.logger.warning(f"{self.LEVEL_ICONS['WARNING']} {message}", *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.logger.error(f"{self.LEVEL_ICONS['ERROR']} {message}", *args, **kwargs)

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.logger.critical(f"{self.LEVEL_ICONS['CRITICAL']} {message}", *args, **kwargs)

    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.logger.exception(f"{self.LEVEL_ICONS['ERROR']} {message}", *args, **kwargs)

    # -------------------- Rich printing helpers --------------------

    def print(self, *args: Any, **kwargs: Any) -> None:
        self.console.print(*args, **kwargs)

    # Progress (persistent until closed)
    def progress(self, total: int = 100, description: str = "Processing") -> Tuple[Progress, int]:
        progress = Progress(
            SpinnerColumn(spinner_name="dots", style="vue_secondary"),
            TextColumn("[bold vue_primary]{task.description}"),
            BarColumn(complete_style=self.GRADIENT_START, finished_style=self.GRADIENT_END),
            TaskProgressColumn("[bold vue_secondary]{task.percentage:>3.0f}%"),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            expand=True,
        )
        task_id = progress.add_task(description, total=total)
        return progress, int(task_id)

    # Progress (auto-disappears on exit)
    def tmp_progress(self, total: int = 100, description: str = "Processing") -> Tuple[Progress, int]:
        progress = Progress(
            SpinnerColumn(spinner_name="dots", style="vue_secondary"),
            TextColumn("[bold vue_primary]{task.description}"),
            BarColumn(complete_style=self.GRADIENT_START, finished_style=self.GRADIENT_END),
            TaskProgressColumn("[bold vue_secondary]{task.percentage:>3.0f}%"),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            expand=True,
            transient=True,
        )
        task_id = progress.add_task(description, total=total)
        return progress, int(task_id)

    # Convenience context manager: closes automatically
    def progress_bar(
        self, total: int, description: str = "Processing", transient: bool = False
    ):
        """
        Context manager that yields (Progress, task_id) and auto-closes.
        """
        progress_factory = self.tmp_progress if transient else self.progress
        progress, task_id = progress_factory(total=total, description=description)

        class _Mgr:
            def __enter__(_self):
                progress.start()
                return progress, task_id

            def __exit__(_self, exc_type, exc, tb):
                progress.stop()
                progress.__exit__(exc_type, exc, tb)

        return _Mgr()

    def stage(self, message: str) -> None:
        self.console.print()
        panel = Panel(
            self._create_gradient_text(f" {message} "),
            box=ROUNDED,
            border_style="vue_primary",
            expand=False,
            padding=(0, 2),
        )
        self.console.print(panel, justify="left")
        self.console.print()

    def highlight(self, message: str) -> None:
        txt = Text(" ★ ", style=f"bold {self.GRADIENT_START}")
        txt.append(self._create_gradient_text(message))
        self.console.print(txt)

    def success(self, message: str) -> None:
        txt = Text()
        txt.append(" ✓ ", style="bold green")
        txt.append(message, style="green")
        self.console.print(txt)

    def error_box(self, message: str) -> None:
        panel = Panel(
            message,
            title="ERROR",
            title_align="left",
            border_style="bold red",
            box=ROUNDED,
            padding=(1, 2),
        )
        self.console.print(panel)

    def section(self, message: str) -> None:
        self.console.print()
        header = self._create_gradient_text(f" {message} ")
        self.console.rule(header, style="vue_secondary", align="center")
        self.console.print()

    def info_panel(self, title: str, message: str) -> None:
        panel = Panel(
            message,
            title=title,
            title_align="left",
            border_style="vue_primary",
            box=ROUNDED,
            padding=(1, 2),
        )
        self.console.print(panel)

    def gradient_text(self, message: str) -> None:
        self.console.print(self._create_gradient_text(message))

    def table(self, title: Optional[str] = None) -> Table:
        return Table(
            title=title,
            box=ROUNDED,
            title_style="bold vue_primary",
            border_style="vue_primary",
            header_style="bold",
        )

    def file_saved(self, file_path: str, file_name: Optional[str] = None) -> None:
        path = Path(file_path).expanduser().resolve()
        uri = path.as_uri() if path.exists() else str(path)
        label = f"({file_name}) " if file_name else ""
        self.console.print(f"💾 {label}File saved: [link={uri}][bold blue]{path}[/bold blue][/link]")

    def banner(self, project_name: str, title: str, description: str, font: str = "slant") -> None:
        fig = Figlet(font=font)
        art = fig.renderText(project_name)
        for line in art.splitlines():
            self.console.print(self._create_gradient_text(line))
        panel = Panel(
            description,
            title=f"[bold vue_primary]{title}",
            border_style="vue_primary",
            box=ROUNDED,
            padding=(1, 2),
        )
        self.console.print(panel)

    # -------------------- Live streaming display --------------------

    def stream(
        self,
        title: str = "Streaming",
        width: Optional[int] = None,
        min_interval_s: float = 0.25,
        annotated_tags: Optional[Tuple[str, ...]] = ("product",),
        annotated_inside_tags: Optional[Tuple[str, ...]] = None,
        xml_gray_style: str = "grey62",
        vue_styles: Optional[dict] = None,
    ):
        """
        Create a live stream view that highlights XML-like tags.
        - `annotated_tags` are highlighted with palette colors.
        - If text appears *inside* any tag listed in `annotated_inside_tags`,
          it will use `vue_styles['inside']`.
        - Other tags are rendered in gray; other text uses `vue_styles['text']`.
        """
        return _LiveStream(
            console=self.console,
            title=title,
            width=width,
            grad_start=self.GRADIENT_START,
            grad_end=self.GRADIENT_END,
            min_interval_s=min_interval_s,
            annotated_tags=set(annotated_tags or ()),
            annotated_inside_tags=set(annotated_inside_tags or annotated_tags or ()),
            xml_gray_style=xml_gray_style,
            vue_styles=vue_styles
            or {
                "tag": "vue_primary",
                "attr": "vue_info",
                "value": "vue_success",
                "text": "default",
                "inside": "vue_inside",
                "bracket": "vue_warning",
                "punct": "vue_warning",
                "timer": "dim",
            },
        )


# ================================================================
# Internal: Live stream implementation
# ================================================================

class _LiveStream:
    """
    Internal helper for ModernLogger.stream() with fast XML-style highlighting.
    """

    TAG_RE = re.compile(
        r"(?P<bracket><)(?P<leadslash>/)?"
        r"(?P<tag>[A-Za-z_][\w:.\-]*)"
        r"(?P<attrs>(?:\s+[\w:.\-]+\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+))*)"
        r"\s*(?P<selfclose>/?)\s*(?P<end>>)"
    )
    ATTR_RE = re.compile(
        r"(?P<name>[\w:.\-]+)\s*=\s*(?P<val>\"[^\"]*\"|'[^']*'|[^\s>]+)"
    )

    def __init__(
        self,
        console: Console,
        title: str,
        width: Optional[int],
        grad_start: str,
        grad_end: str,
        min_interval_s: float,
        annotated_tags: Set[str],
        annotated_inside_tags: Set[str],
        xml_gray_style: str,
        vue_styles: Dict[str, str],
    ):
        self.console = console
        self.title = title
        self.width = width
        self.grad_start = grad_start
        self.grad_end = grad_end

        self._live: Optional[Live] = None
        self._text: str = ""
        self._elapsed: float = 0.0

        self._last_len: int = 0
        self._last_render_at: float = 0.0
        self._min_interval_s: float = max(0.05, float(min_interval_s))

        self.annotated_tags = annotated_tags
        self.annotated_inside_tags = annotated_inside_tags
        self.xml_gray_style = xml_gray_style
        self.vue_styles = vue_styles

        # Tracks which annotated tag(s) we're currently inside
        self._stack: List[str] = []

    # ---- context management ----

    def __enter__(self):
        renderable = self._build_panel()
        self._live = Live(renderable, console=self.console, refresh_per_second=24, transient=False)
        self._live.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._live is not None:
            self._live.__exit__(exc_type, exc, tb)
            self._live = None

    # ---- public API ----

    def update_text(self, full_text: str, elapsed_s: float) -> None:
        """
        Update displayed text and (optionally) an external elapsed timer.
        Rendering is rate-limited by `min_interval_s` for performance.
        """
        self._text = full_text or ""
        self._elapsed = max(float(elapsed_s), 0.0)

        now = time.time()
        length_changed = len(self._text) != self._last_len
        interval_ok = (now - self._last_render_at) >= self._min_interval_s

        if self._live is not None and (length_changed or interval_ok):
            self._live.update(self._build_panel())
            self._last_len = len(self._text)
            self._last_render_at = now

    # ---- rendering ----

    def _build_panel(self) -> Panel:
        body = self._syntax_highlight(self._text)
        body.no_wrap = False
        body.overflow = "fold"
        subtitle = Text(f"Elapsed: {self._elapsed:.2f}s", style=self.vue_styles.get("timer", "dim"))
        return Panel(
            Align.left(body),
            title=self._gradient_title(self.title, self.grad_start, self.grad_end),
            subtitle=subtitle,
            border_style="vue_primary",
            box=ROUNDED,
            padding=(1, 2),
            width=self.width,
        )

    @staticmethod
    @lru_cache(maxsize=128)
    def _gradient_title(text: str, start_hex: str, end_hex: str) -> Text:
        def _hex_to_rgb(h: str) -> Tuple[int, int, int]:
            h = h.strip()
            if not re.fullmatch(r"#?[0-9A-Fa-f]{6}", h):
                raise ValueError(f"Invalid hex color: {h}")
            if not h.startswith("#"):
                h = "#" + h
            return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))

        sr, sg, sb = _hex_to_rgb(start_hex)
        er, eg, eb = _hex_to_rgb(end_hex)

        out = Text()
        n = max(1, len(text))
        for i, ch in enumerate(text):
            t = i / (n - 1) if n > 1 else 0.0
            r = int(sr + (er - sr) * t)
            g = int(sg + (eg - sg) * t)
            b = int(sb + (eb - sb) * t)
            out.append(ch, style=f"#{r:02X}{g:02X}{b:02X}")
        return out

    def _syntax_highlight(self, raw: str) -> Text:
        """
        Rules:
        • Tags in `annotated_tags`: colorized with palette (tag/attr/value/brackets).
        • Text inside any tag from `annotated_inside_tags`: `vue_styles['inside']`.
        • Other tags: gray.
        • Other text: `vue_styles['text']`.
        """
        result = Text()
        pos = 0
        self._stack.clear()

        for m in self.TAG_RE.finditer(raw):
            # Plain text before the tag
            if m.start() > pos:
                inside = any(t in self.annotated_inside_tags for t in self._stack)
                style = self.vue_styles.get("inside") if inside else self.vue_styles.get("text", "default")
                result.append(raw[pos:m.start()], style=style)

            tag_name = m.group("tag")
            is_open = not m.group("leadslash")
            is_selfclose = bool(m.group("selfclose"))
            is_annotated = tag_name in self.annotated_tags

            if is_annotated:
                # left bracket
                result.append(m.group("bracket"), style=self.vue_styles.get("bracket", "vue_warning"))
                # optional leading slash
                if m.group("leadslash"):
                    result.append("/", style=self.vue_styles.get("punct", "vue_warning"))
                # tag name
                result.append(tag_name, style=self.vue_styles.get("tag", "vue_primary"))
                # attributes
                attrs_str = m.group("attrs") or ""
                last_end = 0
                for am in self.ATTR_RE.finditer(attrs_str):
                    if am.start() > last_end:
                        result.append(attrs_str[last_end:am.start()], style=self.vue_styles.get("text", "default"))
                    result.append(am.group("name"), style=self.vue_styles.get("attr", "vue_info"))
                    mid = attrs_str[am.start("name") + len(am.group("name")) : am.start("val")]
                    if mid:
                        result.append(mid, style=self.vue_styles.get("punct", "vue_warning"))
                    result.append(am.group("val"), style=self.vue_styles.get("value", "vue_success"))
                    last_end = am.end()
                if last_end < len(attrs_str):
                    result.append(attrs_str[last_end:], style=self.vue_styles.get("text", "default"))
                # optional self-close slash
                if is_selfclose:
                    result.append("/", style=self.vue_styles.get("punct", "vue_warning"))
                # right bracket
                result.append(m.group("end"), style=self.vue_styles.get("bracket", "vue_warning"))
            else:
                # Non-annotated tag: render as gray block
                result.append(raw[m.start():m.end()], style=self.xml_gray_style)

            # Maintain stack
            if is_open and (not is_selfclose):
                self._stack.append(tag_name)
            elif not is_open:
                # pop the nearest same-named tag from the right
                for i in range(len(self._stack) - 1, -1, -1):
                    if self._stack[i] == tag_name:
                        del self._stack[i]
                        break

            pos = m.end()

        # Trailing text
        if pos < len(raw):
            inside = any(t in self.annotated_inside_tags for t in self._stack)
            style = self.vue_styles.get("inside") if inside else self.vue_styles.get("text", "default")
            result.append(raw[pos:], style=style)

        return result
