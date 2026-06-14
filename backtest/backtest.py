"""
Minimal backtest harness for the Honest Skill's RSI mean-reversion strategy.

Strategy (matches skills/honest-skill/SKILL.md Step 5):
- Entry: RSI(14) crosses below 30 (long)
- Exit:  RSI(14) crosses above 50, OR stop-loss at -max_drawdown_pct from entry

Optional --with-guard layers the leverage-cascade guard from the Skill's
dominant-failure-mode rule using a 30d-price-return proxy. The Skill's
production guard reads funding rate + OI; this harness uses 30d return < -20%
AND still falling as a defensible proxy when historical derivatives data
is not available offline. Documented in README.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf


def wilder_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)


def load_prices(ticker: str, start: str, end: str) -> pd.DataFrame:
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    if df.empty:
        raise SystemExit(f"yfinance returned no data for {ticker} {start}..{end}")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index = pd.to_datetime(df.index)
    return df


def leverage_cascade_proxy(close: pd.Series) -> pd.Series:
    ret_30d = close.pct_change(30)
    falling = ret_30d.diff() < 0
    return (ret_30d < -0.20) & falling


def simulate(
    df: pd.DataFrame,
    oversold: float = 30.0,
    exit_rsi: float = 50.0,
    max_drawdown_pct: float = 15.0,
    with_guard: bool = False,
) -> pd.DataFrame:
    df = df.copy()
    df["rsi"] = wilder_rsi(df["Close"])
    df["rsi_prev"] = df["rsi"].shift(1)
    df["enter_signal"] = (df["rsi"] < oversold) & (df["rsi_prev"] >= oversold)
    df["exit_signal"] = (df["rsi"] >= exit_rsi) & (df["rsi_prev"] < exit_rsi)
    df["guard_blocked"] = leverage_cascade_proxy(df["Close"]) if with_guard else False

    trades = []
    in_pos = False
    entry_date = None
    entry_price = None
    blocked_count = 0

    for ts, row in df.iterrows():
        if np.isnan(row["rsi"]):
            continue
        if not in_pos:
            if row["enter_signal"]:
                if with_guard and bool(row["guard_blocked"]):
                    blocked_count += 1
                    continue
                in_pos = True
                entry_date = ts
                entry_price = float(row["Close"])
        else:
            stop_price = entry_price * (1 - max_drawdown_pct / 100.0)
            hit_stop = float(row["Low"]) <= stop_price
            if hit_stop:
                trades.append(_close(entry_date, entry_price, ts, stop_price, "stop"))
                in_pos = False
                entry_date = entry_price = None
            elif row["exit_signal"]:
                trades.append(_close(entry_date, entry_price, ts, float(row["Close"]), "rsi_exit"))
                in_pos = False
                entry_date = entry_price = None

    if in_pos:
        last_ts = df.index[-1]
        last_close = float(df.iloc[-1]["Close"])
        trades.append(_close(entry_date, entry_price, last_ts, last_close, "open_at_end"))

    trades_df = pd.DataFrame(trades)
    trades_df.attrs["blocked_count"] = blocked_count
    return trades_df


def _close(entry_date, entry_price, exit_date, exit_price, reason):
    return {
        "entry_date": entry_date,
        "entry_price": round(entry_price, 4),
        "exit_date": exit_date,
        "exit_price": round(exit_price, 4),
        "return_pct": round((exit_price - entry_price) / entry_price * 100, 3),
        "hold_days": (exit_date - entry_date).days,
        "exit_reason": reason,
    }


def summarize(trades: pd.DataFrame, label: str) -> str:
    n = len(trades)
    blocked = trades.attrs.get("blocked_count", 0)
    if n == 0:
        return f"{label}: 0 trades (entries blocked: {blocked})"

    wins = trades[trades["return_pct"] > 0]
    win_rate = len(wins) / n
    equity = (1 + trades["return_pct"] / 100).cumprod()
    peak = equity.cummax()
    max_dd = float(((equity - peak) / peak).min() * 100)
    compounded = float(equity.iloc[-1] - 1) * 100

    return (
        f"{label}:\n"
        f"  trades:        {n}\n"
        f"  entries blocked: {blocked}\n"
        f"  win_rate:      {win_rate:.1%}\n"
        f"  avg_return:    {trades['return_pct'].mean():.2f}%\n"
        f"  total (compounded): {compounded:.2f}%\n"
        f"  max_drawdown:  {max_dd:.2f}%\n"
        f"  avg_hold_days: {trades['hold_days'].mean():.1f}\n"
        f"  worst_trade:   {trades['return_pct'].min():.2f}%\n"
        f"  best_trade:    {trades['return_pct'].max():.2f}%"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", default="BNB-USD")
    ap.add_argument("--start", default="2021-01-01")
    ap.add_argument("--end", default=pd.Timestamp.today().strftime("%Y-%m-%d"))
    ap.add_argument("--oversold", type=float, default=30.0)
    ap.add_argument("--exit-rsi", type=float, default=50.0)
    ap.add_argument("--max-drawdown-pct", type=float, default=15.0)
    ap.add_argument("--with-guard", action="store_true")
    ap.add_argument("--outdir", default="examples/backtest-runs")
    args = ap.parse_args()

    prices = load_prices(args.ticker, args.start, args.end)

    vanilla = simulate(prices, args.oversold, args.exit_rsi, args.max_drawdown_pct, with_guard=False)
    guarded = simulate(prices, args.oversold, args.exit_rsi, args.max_drawdown_pct, with_guard=True) if args.with_guard else None

    outdir = Path(args.outdir) / f"{args.ticker}_{args.start}_{args.end}"
    outdir.mkdir(parents=True, exist_ok=True)
    vanilla.to_csv(outdir / "trades_vanilla.csv", index=False)

    report_lines = [
        f"# Honest-Skill backtest run",
        f"",
        f"ticker:           {args.ticker}",
        f"window:           {args.start} -> {args.end}",
        f"bars:             {len(prices)}",
        f"strategy:         RSI(14) cross-below {args.oversold} -> long, exit on cross-above {args.exit_rsi} or -{args.max_drawdown_pct}% stop",
        f"",
        summarize(vanilla, "vanilla (no guard)"),
    ]

    if guarded is not None:
        guarded.to_csv(outdir / "trades_guarded.csv", index=False)
        report_lines.append("")
        report_lines.append(summarize(guarded, "with leverage-cascade guard (price-proxy)"))

    report = "\n".join(report_lines)
    (outdir / "summary.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"\nartifacts written to: {outdir}")


if __name__ == "__main__":
    main()
