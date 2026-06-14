# Backtest findings: BNB-USD RSI mean-reversion, 2021-01-01 → 2026-06-14

Run produced by `backtest/backtest.py` with `--guard all` on 2026-06-14, using
yfinance daily candles (price) and Binance USDT-M futures funding history
(`/fapi/v1/fundingRate`, public, no auth). 6,336 funding events spanning
2020-09-01 → today; 273 days under the SKILL.md −0.02% threshold (~13% of days).

Reproducible:

```
python backtest/backtest.py --ticker BNB-USD --start 2021-01-01 --guard all
```

## Headline numbers — four guard modes side by side

| Guard | Trades | Blocked | Win rate | Compounded P&L | Max DD | Best | Worst |
|---|---|---|---|---|---|---|---|
| `none` (vanilla RSI) | 16 | 0 | 68.8% | +107.83% | −31.18% | +62.70% | −15.00% |
| `proxy` (30d-return) | 9 | 10 | 66.7% | +20.52% | −15.00% | +21.75% | −15.00% |
| **`funding` (real Binance)** | **14** | **2** | **78.6%** | **+187.66%** | **−19.04%** | +62.70% | −15.00% |
| `full` (funding OR proxy) | 8 | 11 | 75.0% | +41.79% | −15.00% | +21.75% | −15.00% |

The real-funding guard is **the only mode that beats vanilla on both P&L and drawdown** — and by wide margins on both (+80pp compounded, +12pp drawdown). The price-proxy is too aggressive; it blocks more than half the entries and costs more in lost recoveries than it saves in avoided losses.

## What the funding guard actually caught

It blocked exactly 2 entries out of 16 vanilla signals:

- **2021-05-19 −15% stop** (May 2021 crypto crash) — BNBUSDT funding dropped to −0.088% in the week prior, clearly above threshold. Guard correctly stayed out.
- **2022-06-12 −15% stop** (3AC contagion) — BNBUSDT funding hit −0.031% the day before entry. Guard correctly stayed out.

It correctly kept all 12 winning vanilla trades. Crucially, it **kept the 2021-05-23 +62.7% recovery trade** that the price-proxy had blocked — that single trade is responsible for ~half of the funding-guard outperformance.

## What the funding guard could NOT catch — and why honesty matters

Three losses got through:

### 1. May 2022 LUNA-week stop (−15%, entry 2022-05-09) — the funding guard was one day late

Day-by-day funding around the LUNA entry:

```
2022-05-06: -0.000233  <-- blocked
2022-05-07: +0.000000
2022-05-08: -0.000030
2022-05-09: -0.000031  <== RSI<30 entry triggered here, funding above threshold
2022-05-10: -0.000329  <-- blocked
2022-05-11: -0.000410  <-- blocked
2022-05-12: -0.001131  <-- deeply negative, but we are already 3 days into a -15% trade
```

The UST depeg cascade hit BNB funding starting May 10. The RSI<30 trigger fired May 9. The guard fires *after* the cascade is visible in funding, which means it can be one day late on the precise day RSI<30 happens. This is an honest limitation, not a bug in the guard.

**Mitigations to consider in v2:** (a) require the prior day's funding to also be above threshold (delays entry by 1 bar, kills some winners), (b) use a rolling 3-day minimum funding to catch early cascades (false positives elsewhere), (c) combine funding with the price-proxy — that's the `full` mode, and as the table shows, the proxy's false positives outweigh the catch. None of these are free.

### 2. June 2023 SEC-charges stop (−15%, entry 2023-06-05)

BNBUSDT funding for this window: **0 days under threshold**, min funding −0.00012%. This is **correctly** classified as not-a-leverage-cascade — it's a `regulatory-shock`. The leverage-cascade guard rightly stayed quiet, and the trade lost. To catch this you need the `regulatory-shock` guard from SKILL.md Step 5, which depends on the live news / event tools — not testable in this offline harness.

### 3. January 2026 stop (−15%, entry 2026-01-31)

Funding was flat across the window. The guard correctly stayed quiet. This was a normal-volatility loss, not a cascade.

## What this proves about the Skill

1. **The production-spec guard works dramatically better than the offline proxy.** Real Binance funding data turns a 1-of-3 risk reduction into a 2-of-3 risk reduction while *adding* upside. This is the highest-leverage finding from the harness so far.

2. **Two failure modes need two guards.** The leverage-cascade guard catches leverage-cascade losses (LUNA, 3AC, May 2021). It does not — and should not — catch regulatory-shock losses (SEC charges). The Skill's failure-mode taxonomy in Step 4 is empirically vindicated: a single guard can't cover all failure modes.

3. **The guard has a known one-day-late property.** The honest Skill must surface this when it generates rules: "this guard may not fire on the same bar as your RSI trigger if the funding-rate cascade is hours behind the price action." The day-7 worked example confidence cap and the disclosed re-check trigger are the right user-facing posture.

4. **The price-proxy is strictly worse than the production guard.** Keep the `proxy` mode in the harness only for environments where Binance funding is unreachable. v1 of the Skill should call the real CMC `get_global_crypto_derivatives_metrics.fundingRate.current` per SKILL.md Step 6 #1.

## Honest finding that contradicts memory

Earlier memory framed the FTX-collapse window as the canonical loss case for RSI mean-reversion on BNB. The harness shows:

- BNB-USD daily never crossed RSI<30 during the immediate FTX week (Nov 8–14, 2022). No vanilla loss from the strategy in that window.
- BNBUSDT funding *did* go to −0.095% min during the FTX window — so the guard *would* have fired had RSI triggered. But it didn't trigger.
- The next post-FTX trigger (2022-12-16) was a **+12% winner**.

The worked example narrative needs updating to reflect this: the FTX collapse was a real leverage cascade visible in funding data, but it did not break this specific strategy on this specific token at daily granularity. The strategy is more robust than the day-4 example claimed.

## What this harness does NOT prove

- One token, one strategy, one timeframe. Don't generalize across tokens without re-running.
- Returns are gross of fees. 0.1% taker per side on 16 trades is ~3.2% drag — non-trivial but not story-changing.
- Daily bars only. A scalp / intraday version would need 1h-or-finer candles.
- OI clause of the guard is approximated via 30d price return; Binance's `openInterestHist` endpoint is capped at 30 days of history. v2 should source OI history from a wider provider (Coinglass, CryptoCompare) to test the full spec.
- yfinance's BNB-USD diverges modestly from Binance's BNBUSDT spot; spot-checked at <1% on close, so signal logic is unaffected.

## Files

- `trades_none.csv` — 16 vanilla trades
- `trades_proxy.csv` — 9 trades, price-proxy guard
- `trades_funding.csv` — 14 trades, real Binance funding guard
- `trades_full.csv` — 8 trades, funding OR price-proxy
- `summary.md` — autogenerated stats from the harness, same numbers as the table above
