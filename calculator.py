from typing import List, Dict

# Minimum OI for a strike to be worth classifying.
# Strikes below this are deep OTM with no real activity.
MIN_OI_THRESHOLD = 50


class SpurtCalculator:
    """
    Classifies per-strike OI + price movement into the 4 standard
    NSE quadrant labels using the DAILY net change provided by NSE.

    NSE's API already computes `changeinOpenInterest` and `change`
    (price change) as the net difference from the previous day's close.
    This means a single snapshot already contains the full intraday
    picture — no need to diff two fetches.

    Example: If terminal opened at 10:00am
        changeinOpenInterest = +12,500  ← net OI added since 9:15am open
        change               = -8.50    ← net price fall since 9:15am open
        → Classification: Short Buildup (correct intraday picture)

    In short, we are calculating from 9.30 a.m to when the terminal was open and then the subsequent time it is still open.
    After 3.30 p.m the data that shows is from 9.30 a.m to 3.30 p.m.


    Classification resets naturally at market open each day because
    NSE resets changeinOpenInterest to 0 at 9:15am.
    """

    @staticmethod
    def classify_spurt(history: List[Dict]) -> str:
        """
        Classifies using the latest snapshot's daily change fields.
        Only needs 1 fetch (not 2) to produce a valid classification.

        Returns one of:
            Long Buildup    — OI ↑, Price ↑  (bullish, fresh longs entering)
            Short Buildup   — OI ↑, Price ↓  (bearish, fresh shorts entering)
            Long Unwinding  — OI ↓, Price ↓  (bearish, longs exiting)
            Short Covering  — OI ↓, Price ↑  (bullish, shorts exiting)
            Neutral         — no net change in OI or price from prev close
            Awaiting Data   — no fetch received yet
            Low OI          — strike has negligible open interest
        """
        if not history:
            return "Awaiting Data"

        curr = history[-1]

        if curr.get('oi', 0) < MIN_OI_THRESHOLD:
            return "Low OI"

        # Daily net change since previous close — provided directly by NSE
        delta_oi    = curr.get('doi', 0)            # change in Open Interest
        delta_price = curr.get('price_change', 0.0) # change (daily price delta)

        if delta_oi > 0 and delta_price > 0:
            return "Long Buildup"
        elif delta_oi > 0 and delta_price < 0:
            return "Short Buildup"
        elif delta_oi < 0 and delta_price < 0:
            return "Long Unwinding"
        elif delta_oi < 0 and delta_price > 0:
            return "Short Covering"

        return "Neutral"