from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import OptionList, Label
from textual.containers import Vertical

class ExpiryModal(ModalScreen[str]):
    """A floating modal screen to select the Options Expiry Date."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]
    
    CSS = """
    ExpiryModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7); /* Darkens the background table */
    }
    
    #modal_container {
        width: 30;
        height: 20;
        background: #161b22;
        border: solid #30363d;
        padding: 1 2;
    }
    
    OptionList {
        height: 1fr;
        margin-top: 1;
        background: #0d1117;
    }
    """

    def __init__(self, expiries: list[str]):
        super().__init__()
        self.expiries = expiries

    def compose(self) -> ComposeResult:
        with Vertical(id="modal_container"):
            # Use Rich markup tags directly in the string instead of a kwarg
            yield Label("[bold cyan]Select Expiry Date[/bold cyan]")
            
            # Populate the list with the dates we pulled from NSE
            yield OptionList(*self.expiries, id="expiry_list")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """When the user hits Enter on a date, dismiss the modal and send the date back."""
        self.dismiss(str(event.option.prompt))

    def action_cancel(self) -> None:
        """Dismiss the modal without selecting anything when Escape is pressed."""
        self.dismiss(None)