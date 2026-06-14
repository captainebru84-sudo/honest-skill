"""
Minimal backtest harness for the Honest Skill strategies.

Strategies (--strategy):
- rsi-mr (default): RSI(14) cross-below 30 -> long, exit on cross-above 50
                    or -max_drawdown_pct stop. Matches the RSI mean-reversion
                    worked example.
- trend: BUY when price > SMA(200) AND MACD line > 0; SELL when either breaks.
         Matches examples/{bnb,btc,eth}-trend-following/stress-test.md.

Guard modes (--guard):
- none:    no guard, raw strategy
- proxy:   30d price return < -20% AND still falling (offline-friendly proxy)
- funding: real Binance USDT-M funding rate < -0.02% (production-spec leg 1)
- full:    funding-rate guard OR 30d-return proxy (closest to SKILL.md spec
           without paid OI history; OI clause is approximated by price action)
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

sys.path.insert(0, str(Path(__file__).parent))
from binance_fetch import daily_funding, fetch_funding, fetch_klines  # noqa: E402

FIXED_FUNDING_THRESHOLD = -0.0002
DEFAULT_PERCENTILE = 10.0
PERCENTILE_WINDOW_DAYS = 365
PERCENTILE_MIN_DAYS = 90


def wilder_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)


def macd_line(close: pd.Series, fast: int = 12, slow: int = 26) -> pd.Series:
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    return ema_fast - ema_slow


def rsi_mr_signals(df: pd.DataFrame, oversold: float, exit_rsi: float) -> pd.DataFrame:
    out = df.copy()
    out["rsi"] = wilder_rsi(out["Close"])
    rsi_prev = out["rsi"].shift(1)
    out["enter_signal"] = (out["rsi"] < oversold) & (rsi_prev >= oversold)
    out["exit_signal"] = (out["rsi"] >= exit_rsi) & (rsi_prev < exit_rsi)
    out["warmup_ok"] = out["rsi"].notna()
    return out


def trend_signals(df: pd.DataFrame, sma_period: int = 200) -> pd.DataFrame:
    out = df.copy()
    sma = out["Close"].rolling(sma_period).mean()
    macd = macd_line(out["Close"])
    in_trend = (out["Close"] > sma) & (macd > 0)
    in_trend_prev = in_trend.shift(1).fillna(False)
    out["sma"] = sma
    out["macd"] = macd
    out["enter_signal"] = in_trend & ~in_trend_prev
    out["exit_signal"] = ~in_trend & in_trend_prev
    out["warmup_ok"] = sma.notna() & macd.notna()
    return out


def load_prices(ticker: str, start: str, end: str, source: str = "binance") -> pd.DataFrame:
    if source == "binance":
        df = fetch_klines(symbol=ticker, start=start, end=end)
        if df.empty:
            raise SystemExit(f"binance klines empty for {ticker} {start}..{end}")
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.index = pd.to_datetime(df.index)
        return df
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


def _funding_blocked_signal(
    df_index: pd.DatetimeIndex,
    funding_daily: pd.Series,
    threshold_mode: str,
    threshold_value: float,
) -> pd.Series:
    funding_daily = funding_daily.copy()
    funding_daily.index = funding_daily.index.normalize().tz_localize(None)
    idx = pd.DatetimeIndex(df_index).normalize()
    aligned = funding_daily.reindex(idx)

    if threshold_mode == "fixed":
        blocked = aligned < threshold_value
    elif threshold_mode == "percentile":
        rolling = aligned.rolling(window=PERCENTILE_WINDOW_DAYS, min_periods=PERCENTILE_MIN_DAYS)
        threshold_series = rolling.quantile(threshold_value / 100.0)
        threshold_series = threshold_series.shift(1)
        blocked = aligned < threshold_series
    else:
        raise SystemExit(f"unknown threshold mode: {threshold_mode}")

    blocked.index = df_index
    return blocked.fillna(False)


def build_guard(
    df: pd.DataFrame,
    mode: str,
    funding_symbol: str | None,
    threshold_mode: str = "fixed",
    threshold_value: float | None = None,
) -> pd.Series:
    if mode == "none":
        return pd.Series(False, index=df.index)
    if mode == "proxy":
        return leverage_cascade_proxy(df["Close"])
    if mode in ("funding", "full"):
        if funding_symbol is None:
            raise SystemExit(f"--guard {mode} requires --funding-symbol (e.g. BNBUSDT)")
        if threshold_value is None:
            threshold_value = FIXED_FUNDING_THRESHOLD if threshold_mode == "fixed" else DEFAULT_PERCENTILE
        funding_df = fetch_funding(symbol=funding_symbol)
        daily = daily_funding(funding_df)
        funding_blocked = _funding_blocked_signal(df.index, daily, threshold_mode, threshold_value)
        if mode == "funding":
            return funding_blocked
        return (funding_blocked | leverage_cascade_proxy(df["Close"])).fillna(False)
    raise SystemExit(f"unknown --guard mode: {mode}")


def simulate(
    df: pd.DataFrame,
    guard_signal: pd.Series,
    max_drawdown_pct: float = 15.0,
) -> pd.DataFrame:
    df = df.copy()
    df["guard_blocked"] = guard_signal.astype(bool)

    trades = []
    in_pos = False
    entry_date = None
    entry_price = None
    blocked_count = 0

    for ts, row in df.iterrows():
        if not bool(row["warmup_ok"]):
            continue
        if not in_pos:
            if bool(row["enter_signal"]):
                if bool(row["guard_blocked"]):
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
            elif bool(row["exit_signal"]):
                trades.append(_close(entry_date, entry_price, ts, float(row["Close"]), "signal_exit"))
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
    ap.add_argument("--ticker", default="BNBUSDT")
    ap.add_argument("--start", default="2021-01-01")
    ap.add_argument("--end", default=pd.Timestamp.today().strftime("%Y-%m-%d"))
    ap.add_argument(
        "--strategy",
        choices=["rsi-mr", "trend"],
        default="rsi-mr",
        help="rsi-mr: RSI(14) cross-below 30 long; trend: price>SMA(200) AND MACD>0.",
    )
    ap.add_argument("--oversold", type=float, default=30.0, help="rsi-mr only")
    ap.add_argument("--exit-rsi", type=float, default=50.0, help="rsi-mr only")
    ap.add_argument("--sma-period", type=int, default=200, help="trend only")
    ap.add_argument("--max-drawdown-pct", type=float, default=15.0)
    ap.add_argument(
        "--price-source",
        choices=["binance", "yfinance"],
        default="binance",
        help="binance (default) pulls /api/v3/klines for the same symbol as funding; yfinance uses --ticker as a Yahoo symbol",
    )
    ap.add_argument(
        "--guard",
        choices=["none", "proxy", "funding", "full", "all"],
        default="all",
        help="all = run none + proxy + funding + full and produce a comparison table",
    )
    ap.add_argument(
        "--funding-symbol",
        default=None,
        help="Binance USDT-M symbol for funding rate fetch, e.g. BNBUSDT. Defaults to --ticker for binance source, or --ticker with -USD stripped for yfinance source.",
    )
    ap.add_argument(
        "--funding-threshold-mode",
        choices=["fixed", "percentile"],
        default="fixed",
        help="fixed (default): absolute funding rate cutoff (--funding-threshold-value as a rate, e.g. -0.0002). "
        "percentile: rolling-1y N-th percentile per day, calibrated to the token's own distribution. "
        "Cross-token finding: neither dominates. Fixed wins on BNB, percentile fires more on BTC but blocks winners.",
    )
    ap.add_argument(
        "--funding-threshold-value",
        type=float,
        default=None,
        help="With --funding-threshold-mode fixed: absolute rate, e.g. -0.0002 = -0.02%%. "
        "With percentile: the percentile number, e.g. 10 = 10th percentile. "
        "Defaults: -0.0002 for fixed, 10 for percentile.",
    )
    ap.add_argument("--outdir", default="examples/backtest-runs")
    args = ap.parse_args()

    if args.funding_symbol is None:
        if args.price_source == "binance":
            args.funding_symbol = args.ticker
        elif args.ticker.endswith("-USD"):
            args.funding_symbol = args.ticker.replace("-USD", "USDT")

    prices = load_prices(args.ticker, args.start, args.end, source=args.price_source)

    if args.strategy == "rsi-mr":
        prices = rsi_mr_signals(prices, args.oversold, args.exit_rsi)
        strategy_label = (
            f"RSI(14) cross-below {args.oversold} -> long, "
            f"exit on cross-above {args.exit_rsi} or -{args.max_drawdown_pct}% stop"
        )
    else:
        prices = trend_signals(prices, args.sma_period)
        strategy_label = (
            f"price>SMA({args.sma_period}) AND MACD>0 -> long, "
            f"exit when either breaks or -{args.max_drawdown_pct}% stop"
        )

    if args.guard == "all":
        modes = ["none", "proxy", "funding", "full"]
    else:
        modes = [args.guard]

    results = {}
    for mode in modes:
        guard = build_guard(
            prices, mode, args.funding_symbol,
            threshold_mode=args.funding_threshold_mode,
            threshold_value=args.funding_threshold_value,
        )
        trades = simulate(prices, guard, args.max_drawdown_pct)
        results[mode] = trades

    outdir = Path(args.outdir) / f"{args.ticker}_{args.strategy}_{args.start}_{args.end}"
    outdir.mkdir(parents=True, exist_ok=True)

    for mode, trades in results.items():
        trades.to_csv(outdir / f"trades_{mode}.csv", index=False)

    if args.funding_threshold_mode == "percentile":
        tv = args.funding_threshold_value if args.funding_threshold_value is not None else DEFAULT_PERCENTILE
        threshold_label = f"percentile@{tv:g} (rolling {PERCENTILE_WINDOW_DAYS}d, warmup {PERCENTILE_MIN_DAYS}d)"
    else:
        tv = args.funding_threshold_value if args.funding_threshold_value is not None else FIXED_FUNDING_THRESHOLD
        threshold_label = f"fixed {tv:+.4%}"

    report_lines = [
        f"# Honest-Skill backtest run",
        f"",
        f"ticker:           {args.ticker}",
        f"strategy:         {args.strategy} — {strategy_label}",
        f"window:           {args.start} -> {args.end}",
        f"bars:             {len(prices)}",
        f"funding symbol:   {args.funding_symbol or '(not used)'}",
        f"funding threshold: {threshold_label}",
        f"",
    ]
    for mode, trades in results.items():
        report_lines.append(summarize(trades, f"guard={mode}"))
        report_lines.append("")

    report = "\n".join(report_lines).rstrip() + "\n"
    (outdir / "summary.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"artifacts written to: {outdir}")


if __name__ == "__main__":
    main()
