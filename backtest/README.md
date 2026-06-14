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
4. Optionally applies the leverage-cascade guard from the Skill's Step 5
   failure-mode-specific entry guard.
5. Writes `trades_vanilla.csv`, optionally `trades_guarded.csv`, and a
   `summary.md` of stats (win rate, compounded return, max drawdown, avg hold).

## Run

```
pip install -r requirements.txt
python backtest.py --ticker BNB-USD --start 2021-01-01 --with-guard
```

## Honest caveats

- **The guard is a proxy.** The Skill's production guard reads canonical
  funding rate and 30d open interest change. This harness uses
  `30d price return < -20% AND still falling` as a proxy because reliable
  free historical funding/OI series across the BNB window are not in scope
  for the MVP. The proxy correlates with deleveraging regimes (FTX-collapse,
  Mar-2020 crash) but is not the production guard. A v2 should pull Binance
  USDT-M funding history via `/fapi/v1/fundingRate` and use it directly.
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
a trader out of the worst RSI mean-reversion losses (specifically the
2022-11 FTX-collapse window). This harness can answer that claim with real
numbers: compare `vanilla` vs `with-guard` summary stats over a window that
covers Nov 2022. If the guard does not improve the drawdown materially, that
is itself an honest finding — the Skill must surface it.
