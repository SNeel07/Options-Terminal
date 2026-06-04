"""
--------------------------------------
switcher.py — Terminal Switcher Modal
--------------------------------------

A modal dropdown to switch between different exchange terminals.
Press 't' or 'escape' to close.
"""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label

class TerminalSwitcherModal(ModalScreen[str | None]):
    """Modal to select which terminal to display."""

    CSS = """
    TerminalSwitcherModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.75);
    }

    #switcher_box {
        width: 40;
        height: auto;
        background: #161b22;
        border: solid #30363d;
        padding: 1 2;
    }

    #switcher_box Label {
        color: #58a6ff;
        text-style: bold;
        margin-bottom: 1;
        width: 100%;
        text-align: center;
        border-bottom: solid #30363d;
        padding-bottom: 1;
    }

    .switch-btn {
        width: 100%;
        margin-bottom: 1;
        background: #21262d;
        color: #c9d1d9;
        border: none;
    }

    .switch-btn:hover {
        background: #30363d;
        color: #ffffff;
    }

    .switch-btn.-active {
        background: #1f6feb;
        color: #ffffff;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("t", "cancel", "Cancel")
    ]

    def __init__(self, current_terminal: str, **kwargs):
        super().__init__(**kwargs)
        self.current_terminal = current_terminal

    def compose(self) -> ComposeResult:
        with Vertical(id="switcher_box"):
            yield Label("Select Terminal")
            
            btn_nse = Button("NSE Options", id="btn_nse", classes="switch-btn")
            btn_bse = Button("BSE Options", id="btn_bse", classes="switch-btn")
            
            if self.current_terminal == "nse":
                btn_nse.add_class("-active")
            elif self.current_terminal == "bse":
                btn_bse.add_class("-active")

            yield btn_nse
            yield btn_bse

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_nse":
            self.dismiss("nse")
        elif event.button.id == "btn_bse":
            self.dismiss("bse")

    def action_cancel(self) -> None:
        self.dismiss(None)