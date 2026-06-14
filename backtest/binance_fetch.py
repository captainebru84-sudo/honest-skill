"""
Binance USDT-M public-endpoint fetchers for the Honest Skill backtest.

Funding rate history (/fapi/v1/fundingRate) goes back to ~2020-09 for BNBUSDT,
public, no auth, generous rate limits. Open interest history
(/futures/data/openInterestHist) is capped at the last ~30 days by Binance and
is therefore unusable for multi-year backtesting from this surface.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

FAPI = "https://fapi.binance.com"


def fetch_funding(
    symbol: str = "BNBUSDT",
    start: str = "2020-09-01",
    end: Optional[str] = None,
    cache_dir: str | Path = "backtest/data",
    refresh: bool = False,
) -> pd.DataFrame:
    cache = Path(cache_dir) / f"binance_funding_{symbol}.csv"
    end_ts = pd.Timestamp(end or pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d"))

    if cache.exists() and not refresh:
        cached = pd.read_csv(cache, parse_dates=["fundingTime"])
        last = cached["fundingTime"].max()
        if last >= end_ts - pd.Timedelta(days=2):
            return cached.sort_values("fundingTime").reset_index(drop=True)
        start_cursor_ms = int(last.timestamp() * 1000) + 1
        existing = cached
    else:
        start_cursor_ms = int(pd.Timestamp(start).timestamp() * 1000)
        existing = pd.DataFrame()

    end_ms = int(end_ts.timestamp() * 1000)
    rows = []
    cursor = start_cursor_ms
    while cursor < end_ms:
        r = requests.get(
            f"{FAPI}/fapi/v1/fundingRate",
            params={"symbol": symbol, "limit": 1000, "startTime": cursor, "endTime": end_ms},
            timeout=30,
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        rows.extend(batch)
        cursor = batch[-1]["fundingTime"] + 1
        time.sleep(0.25)
        if len(batch) < 1000:
            break

    fresh = pd.DataFrame(rows)
    if not fresh.empty:
        fresh["fundingTime"] = pd.to_datetime(fresh["fundingTime"], unit="ms")
        fresh["fundingRate"] = fresh["fundingRate"].astype(float)
        fresh = fresh[["symbol", "fundingTime", "fundingRate"]]

    combined = pd.concat([existing, fresh], ignore_index=True)
    combined = (
        combined.drop_duplicates(subset=["fundingTime"])
        .sort_values("fundingTime")
        .reset_index(drop=True)
    )

    cache.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(cache, index=False)
    return combined


def daily_funding(funding_df: pd.DataFrame) -> pd.Series:
    s = funding_df.set_index("fundingTime")["fundingRate"]
    return s.resample("1D").mean().dropna()


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="BNBUSDT")
    ap.add_argument("--start", default="2020-09-01")
    ap.add_argument("--end", default=None)
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()

    df = fetch_funding(args.symbol, args.start, args.end, refresh=args.refresh)
    daily = daily_funding(df)
    print(f"funding events:      {len(df):>6}")
    print(f"first event:         {df['fundingTime'].min()}")
    print(f"last event:          {df['fundingTime'].max()}")
    print(f"daily-mean rows:     {len(daily):>6}")
    print(f"daily mean stats:    min={daily.min():.6f} max={daily.max():.6f} median={daily.median():.6f}")
    neg_thresh = (daily < -0.0002).sum()
    print(f"days under -0.02%:   {neg_thresh}")
