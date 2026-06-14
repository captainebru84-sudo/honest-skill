# Honest-Skill backtest harness

A minimal, runnable backtest of the RSI mean-reversion strategy that
`skills/honest-skill/SKILL.md` ships as a worked example. The point of this
harness is **not** to claim the strategy is good — it is to make the Skill's
output *demonstrably backtestable*, which is the Track 2 deliverable
requirement.

## What it does

1. Pulls daily OHLCV from `yfinance` for the requested ticker (default `BNB-USD`).
2. Computes Wilder RSI(14).
3. Simulates the strategy from `SKILL.md` Step 5:
   - Long on RSI(14) cross below 30
   - Exit on RSI(14) cross above 50, or `-max_drawdown_pct` stop, or end of window.
4. Applies the leverage-cascade guard from the Skill's Step 5 in one of four modes:
   - `none` — no guard
   - `proxy` — 30d price return < −20% AND still falling (offline proxy)
   - `funding` — **real Binance USDT-M funding rate < −0.02%** (production-spec leg 1)
   - `full` — funding OR price-proxy (closest to spec; OI clause approximated by price)
5. Writes one `trades_<mode>.csv` per requested mode plus a `summary.md` with stats
   (win rate, compounded return, max drawdown, avg hold) for each.

## Run

```
pip install -r requirements.txt
python backtest.py --ticker BNB-USD --start 2021-01-01 --guard all
```

Or one mode at a time: `--guard funding`, `--guard proxy`, etc.

The Binance funding fetcher is in `binance_fetch.py` — you can also run it
directly to inspect raw funding data:

```
python binance_fetch.py --symbol BNBUSDT --start 2020-09-01
```

Funding history caches to `backtest/data/binance_funding_BNBUSDT.csv` so
subsequent runs are fast.

## Honest caveats

- **OI clause is still a proxy.** Binance's public `/futures/data/openInterestHist`
  endpoint is capped at the last 30 days of history regardless of params. So the
  full SKILL.md guard (`funding < −0.02% OR 30d OI down >20% AND falling`) cannot
  be fully tested from a free public endpoint over multi-year history. The
  `funding` mode tests only the funding leg; the `full` mode pairs real funding
  with a 30d-price-return proxy for the OI leg. A v2 with Coinglass / CryptoCompare
  OI history would close this gap.
- **Funding guard can be one day late.** Funding rates reflect the leverage state
  *after* it builds. On a sharp same-day cascade (e.g. May 2022 LUNA week on
  BNB), the RSI<30 trigger fires on day 0 while funding doesn't cross threshold
  until day +1. The harness documents this honestly in
  `examples/backtest-runs/.../findings.md`.
- **No fees / slippage.** Returns are gross. A 0.1% taker fee per side on
  every trade would compress equity curves modestly but not change the
  guarded-vs-unguarded delta materially.
- **Daily bars only.** A scalp / intraday RSI strategy would need 1h-or-finer
  candles. The Skill's auto-detected timeframe for BNB at current vol is
  `swing` (per SKILL.md inputs), which the daily bars match.
- **Single instrument at a time.** No portfolio.
- **Yahoo Finance BNB-USD** is sourced from a spot reference price, which
  diverges slightly from Binance's own BNBUSDT. Within 1% on close-to-close
  in all spot-checked windows, so the strategy's signal logic is unaffected.

## What the harness is meant to prove

The Skill's central claim is that the leverage-cascade guard would have kept
a trader out of the worst RSI mean-reversion losses. This harness can answer
that claim with real numbers across four guard configurations and surface the
specific trades each guard caught and missed. Whether the guard improves
risk-adjusted return is then a question with a published answer, not a vibe.
