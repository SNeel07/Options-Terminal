"""
---------------------------------------------------
interval_modal.py — Custom Poll Interval Selector
---------------------------------------------------

Modal to change how often the terminal fetches data from NSE.
Press 'i' or Escape to close without changing.
"""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label

# Available intervals: (display label, seconds)
INTERVALS = [
    ("1 minute",  60),
    ("2 minutes", 120),
    ("3 minutes", 180),
    ("5 minutes", 300),
    ("10 minutes",600),
]


class IntervalModal(ModalScreen[int | None]):
    """Modal to select the data fetch interval."""

    CSS = """
    IntervalModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.75);
    }

    #interval_box {
        width: 40;
        height: auto;
        background: #161b22;
        border: solid #30363d;
        padding: 1 2;
    }

    #interval_title {
        color: #58a6ff;
        text-style: bold;
        width: 100%;
        text-align: center;
        border-bottom: solid #30363d;
        padding-bottom: 1;
        margin-bottom: 1;
    }

    #interval_subtitle {
        color: #8b949e;
        width: 100%;
        text-align: center;
        margin-bottom: 1;
    }

    .interval-btn {
        width: 100%;
        margin-bottom: 1;
        background: #21262d;
        color: #c9d1d9;
        border: none;
    }

    .interval-btn:hover {
        background: #30363d;
        color: #ffffff;
    }

    .interval-btn.-active {
        background: #1f6feb;
        color: #ffffff;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("i",      "cancel", "Cancel"),
    ]

    def __init__(self, current_interval: int, **kwargs):
        super().__init__(**kwargs)
        self.current_interval = current_interval

    def compose(self) -> ComposeResult:
        with Vertical(id="interval_box"):
            yield Label("Fetch Interval", id="interval_title")
            yield Label("How often to pull data from NSE", id="interval_subtitle")
            for label, seconds in INTERVALS:
                btn = Button(label, id=f"btn_{seconds}", classes="interval-btn")
                if seconds == self.current_interval:
                    btn.add_class("-active")
                yield btn

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Extract seconds from button id e.g. "btn_120" → 120
        try:
            seconds = int(event.button.id.split("_")[1])
            self.dismiss(seconds)
        except (IndexError, ValueError):
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)