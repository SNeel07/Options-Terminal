"""
-------------------------------------------
  app.py — Multi-Exchange Options Terminal
-------------------------------------------

Live options OI terminal built with Textual.
Supports NSE (live) and BSE (coming soon) terminals.

Keybindings (global):
    q — Quit
    s — Toggle quick links sidebar
    t — Switch terminal
    i — Change fetch interval

Keybindings (NSE screen):
    r — Force refresh
    f — Filter expiry date
"""

import time
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Header, Footer, Static

from fetcher import NSEDataFetcher
from store import OptionsDataStore
from calculator import SpurtCalculator
from widgets.oi_table import OITable
from widgets.header import MarketHeader
from widgets.expiry_modal import ExpiryModal
from widgets.sidebar import LinkSidebar
from widgets.switcher import TerminalSwitcherModal
from widgets.interval_modal import IntervalModal, INTERVALS



# --------------- CONSTANTS ----------------

SYMBOL           = "NIFTY"
DEFAULT_INTERVAL = 60       # Default poll interval - 60 seconds
ATM_WING         = 70
IST              = ZoneInfo("Asia/Kolkata")




# --------------- NSE TRADING HOLIDAYS 2026 ----------------------

# Update this list every year(at the beginning) to get the updated market open/close status
NSE_HOLIDAYS_2026 = {
    "2026-01-15",  # Municipal Corporation Election Maharashtra
    "2026-01-26",  # Republic Day
    "2026-03-03",  # Holi
    "2026-03-26",  # Ram Navami
    "2026-03-31",  # Shri Mahavir Jayanti
    "2026-04-03",  # Good Friday
    "2026-04-14",  # Dr. Baba Saheb Ambedkar Jayanti
    "2026-05-01",  # Maharashtra Day
    "2026-05-28",  # Bakri Id
    "2026-06-26",  # Muharram
    "2026-09-14",  # Ganesh Chaturthi
    "2026-10-02",  # Mahatma Gandhi Jayanti
    "2026-10-20",  # Dussehra
    "2026-11-08",  # Diwali laxmi Pujan
    "2026-11-10",  # Diwali - Balipratipada
    "2026-11-24",  # Prakash Gurpurb Sri Guru Nanak Dev
    "2026-12-25",  # Christmas
}

BSE_HOLIDATS_2026 = NSE_HOLIDAYS_2026


# Check Market open/close status
def is_trading_holiday(date: "datetime") -> bool:
    return date.strftime("%Y-%m-%d") in NSE_HOLIDAYS_2026

BSE_EXPIRY_DATES = [
    "20-May-2026", "27-May-2026", "04-Jun-2026",
    "11-Jun-2026", "18-Jun-2026", "25-Jun-2026",
]


def is_market_open() -> bool:
    """
    Returns True only when NSE is actually trading:
    - Weekday (Mon - Fri)
    - Between 09:15 and 15:30 IST
    """
    now = datetime.now(IST)
    if now.weekday() >= 5:
        return False
    if is_trading_holiday(now):
        return False
    hhmm = now.hour * 100 + now.minute
    return 915 <= hhmm < 1530


# ------------- SCREENS --------------------


# NIFTY Options Terminal
class NSEScreen(Screen):

    BINDINGS = [
        ("r", "force_refresh", "Force Refresh"),
        ("f", "change_expiry", "Filter Expiry"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield MarketHeader(symbol=SYMBOL, id="market_header")
        yield Container(OITable(), id="main_container")
        yield Footer()

    def action_force_refresh(self):
        self.app.action_force_refresh()

    def action_change_expiry(self):
        self.app.action_change_expiry()


# BSE SENSEX Terminal (Under Construction)
class BSEScreen(Screen):

    BINDINGS = [
        ("r", "nse_only", "Force Refresh"),
        ("f", "nse_only", "Filter Expiry"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield MarketHeader(symbol="SENSEX", id="bse_market_header")
        with Container(id="main_container"):
            yield OITable()
            yield Static(
                "BSE Data — Coming Soon\n\n"
                "BSE's option chain API is not publicly documented.\n"
                "Contributors welcome",
                id="bse_overlay"
            )
        yield Footer()

    def on_mount(self) -> None:
        nearest = BSE_EXPIRY_DATES[0] if BSE_EXPIRY_DATES else "—"
        self.app.sub_title = f"SENSEX | Expiry: {nearest} | Spot: —"

    def action_nse_only(self):
        self.app.notify("BSE data not available yet.", severity="warning", timeout=3)


# --------------- MAIN APPLICATION ------------------------

class TradingTerminal(App):

    CSS = """
    Screen { background: #0d1117; }

    MarketHeader {
        height: 2;
        background: #161b22;
        color: #8b949e;
        padding: 0 2;
        border-bottom: solid #30363d;
    }

    #main_container {
        padding: 0 1;
        height: 1fr;
        layers: base overlay;
    }

    DataTable {
        height: 1fr;
        border: solid #30363d;
        layer: base;
    }

    #bse_overlay {
        layer: overlay;
        dock: top;
        width: 100%;
        text-align: center;
        color: #8b949e;
        background: #0d1117;
        padding: 4 2;
        text-style: bold;
        margin-top: 4;
    }

    DataTable > .datatable--header  { background: #161b22; color: #e6edf3; text-style: bold; }
    DataTable > .datatable--cursor  { background: #1f2937; }
    DataTable > .datatable--odd-row  { background: #0d1117; }
    DataTable > .datatable--even-row { background: #111827; }

    Footer { height: 2; }
    """

    BINDINGS = [
        ("q", "quit",             "Quit"),
        ("s", "toggle_sidebar",   "Links"),
        ("t", "switch_terminal",  "Switch Terminal"),
        ("i", "change_interval",  "Interval"),
    ]

    def __init__(self):
        super().__init__()
        self.fetcher          = NSEDataFetcher()
        self.store            = OptionsDataStore()
        self.last_raw_data    = None
        self.target_expiry    = None
        self._refresh_event   = threading.Event()
        self.current_terminal = "nse"
        # Poll interval — mutable at runtime, read by the worker loop
        self.poll_interval    = DEFAULT_INTERVAL

    def on_mount(self) -> None:
        self.title = "Options Terminal"
        self.install_screen(NSEScreen(), name="nse")
        self.install_screen(BSEScreen(), name="bse")
        self.push_screen("nse")
        self.update_data_loop()

    # -------------- GLOBAL ACTIONS -----------------------

    def action_toggle_sidebar(self):
        self.push_screen(LinkSidebar(self.current_terminal))

    def action_switch_terminal(self):
        self.push_screen(
            TerminalSwitcherModal(self.current_terminal),
            self._on_terminal_switched
        )

    def action_change_interval(self):
        self.push_screen(
            IntervalModal(self.poll_interval),
            self._on_interval_selected
        )

    def _on_interval_selected(self, seconds: int | None):
        if seconds and seconds != self.poll_interval:
            self.poll_interval = seconds
            label = next(
                (lbl for lbl, s in INTERVALS if s == seconds),
                f"{seconds}s"
            )
            self.notify(
                f"Fetch interval set to {label}",
                severity="information",
                timeout=3
            )
            # Wake the sleeping loop immediately so it respects the new interval
            self._refresh_event.set()

    def _on_terminal_switched(self, selected: str | None):
        if not selected or selected == self.current_terminal:
            return
        self.current_terminal = selected
        self.switch_screen(selected)
        self.notify(
            f"Switched to {selected.upper()} Terminal",
            severity="information",
            timeout=3
        )
        if selected == "nse":
            self.call_later(self.refresh_ui, is_market_open())

    def action_force_refresh(self):
        self.notify("Force refresh triggered...", severity="warning", timeout=3)
        self._refresh_event.set()

    def action_change_expiry(self):
        expiries = getattr(self.store, 'available_expiries', [])
        if not expiries:
            self.notify("No expiries yet. Waiting for first fetch...", severity="warning")
            return
        self.push_screen(ExpiryModal(expiries), self._apply_expiry)

    def _apply_expiry(self, selected_expiry: str):
        if selected_expiry and selected_expiry != self.target_expiry:
            self.target_expiry = selected_expiry
            self.notify(f"Switched to expiry: {selected_expiry}", severity="information")
            if self.last_raw_data:
                self.store.update_snapshot(self.last_raw_data, self.target_expiry)
                self.refresh_ui(is_market_open())


    # -------------- BACKGROUND POLLING WORKER ---------------------------

    @work(thread=True)
    def update_data_loop(self):
        """
        Persistent NSE polling loop.
        Uses self.poll_interval which can be changed at runtime via the
        interval modal — no restart needed, takes effect on the next cycle.
        Force refresh and interval changes both wake the Event early.
        """
        while True:
            market_open = is_market_open()
            now_str     = datetime.now(IST).strftime("%H:%M:%S")

            self.call_from_thread(self._refresh_header, market_open)

            if self.current_terminal == "nse":
                self.call_from_thread(
                    self.notify,
                    f"Fetching live NSE data... [{now_str}]",
                    severity="information",
                    timeout=4,
                )

            raw_data = self.fetcher.get_option_chain(SYMBOL)

            if raw_data:
                self.last_raw_data = raw_data
                self.store.update_snapshot(raw_data, self.target_expiry)
                if self.current_terminal == "nse":
                    self.call_from_thread(self.refresh_ui, market_open)
            else:
                if self.current_terminal == "nse":
                    self.call_from_thread(
                        self.notify,
                        f"Fetch failed at {now_str}. Retrying in {self.poll_interval}s",
                        severity="error",
                        timeout=8,
                    )

            # Sleep for poll_interval but wake early on force refresh or interval change [both call self._refresh_event.set()]
            self._refresh_event.clear()
            self._refresh_event.wait(timeout=self.poll_interval)

    # ----------------- UI REFRESH ------------------------

    def refresh_ui(self, market_open: bool = True):
        self._refresh_header(market_open)
        self._refresh_table()

    def _refresh_header(self, market_open: bool):
        if self.current_terminal == "nse":
            try:
                header = self.screen.query_one("#market_header", MarketHeader)
                header.refresh_stats(self.store, market_open)
            except Exception:
                pass
        else:
            try:
                header = self.screen.query_one("#bse_market_header", MarketHeader)
                header.refresh_market_status(market_open)
            except Exception:
                pass

    def _refresh_table(self):
        try:
            table = self.screen.query_one("#spurt_table")
        except Exception:
            return

        table.clear()

        strikes     = self.store.get_all_strikes()
        underlying  = self.store.current_underlying
        current_exp = getattr(self.store, 'current_expiry', None) or "Awaiting API"

        self.sub_title = f"{SYMBOL} | Expiry: {current_exp} | Spot: ₹{underlying:,.2f}"

        if underlying == 0 or not strikes:
            return

        closest = min(strikes, key=lambda x: abs(x - underlying))
        idx     = strikes.index(closest)
        lo      = max(0, idx - ATM_WING)
        hi      = min(len(strikes), idx + ATM_WING + 1)
        display = strikes[lo:hi]

        for strike in display:
            ce_hist = self.store.get_history(strike, 'CE')
            pe_hist = self.store.get_history(strike, 'PE')

            ce_trend = SpurtCalculator.classify_spurt(ce_hist)
            pe_trend = SpurtCalculator.classify_spurt(pe_hist)

            ce = ce_hist[-1] if ce_hist else {'price': 0.0, 'oi': 0, 'doi': 0}
            pe = pe_hist[-1] if pe_hist else {'price': 0.0, 'oi': 0, 'doi': 0}

            strike_cell = Text(
                f"{strike:,.0f}",
                style="bold yellow" if strike == closest else "white"
            )

            table.add_row(
                self._style_doi(ce.get('doi', 0)),
                f"{ce.get('oi', 0):,}",
                f"{ce.get('price', 0.0):.2f}",
                self._style_trend(ce_trend),
                strike_cell,
                self._style_trend(pe_trend),
                f"{pe.get('price', 0.0):.2f}",
                f"{pe.get('oi', 0):,}",
                self._style_doi(pe.get('doi', 0)),
            )

    # ---------------- STYLE HELPERS -----------------------

    @staticmethod
    def _style_trend(text: str) -> Text:
        if "Long Buildup" in text or "Short Covering" in text:
            return Text(text, style="bold green")
        elif "Short Buildup" in text or "Long Unwinding" in text:
            return Text(text, style="bold red")
        elif "Low OI" in text:
            return Text(text, style="dim")
        return Text(text, style="bold cyan")

    @staticmethod
    def _style_doi(doi: int) -> Text:
        if doi > 0:
            return Text(f"+{doi:,}", style="green")
        elif doi < 0:
            return Text(f"{doi:,}", style="red")
        return Text("0", style="white")


if __name__ == "__main__":
    app = TradingTerminal()
    app.run()