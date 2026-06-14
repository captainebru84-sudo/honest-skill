# Cross-token findings: RSI mean-reversion on BNB / BTC / ETH

Three runs of `backtest/backtest.py --guard all`, same strategy, same window
(2021-01-01 → 2026-06-14), same Wilder RSI(14) parameters, same Binance
USDT-M funding-rate guard at −0.02%. Daily Binance klines (`/api/v3/klines`)
for prices. Reproducible:

```
python backtest/backtest.py --ticker BNBUSDT --start 2021-01-01 --guard all
python backtest/backtest.py --ticker BTCUSDT --start 2021-01-01 --guard all
python backtest/backtest.py --ticker ETHUSDT --start 2021-01-01 --guard all
```

## Headline matrix

| Token | Guard | Trades | Blocked | Win rate | Compounded P&L | Max DD |
|---|---|---|---|---|---|---|
| **BNB** | none | 15 | 0 | 66.7% | +98.39% | −31.23% |
| BNB | proxy | 8 | 10 | 62.5% | +14.53% | −15.00% |
| **BNB** | **funding** | **13** | **2** | **76.9%** | **+174.59%** | **−19.09%** |
| BNB | full | 7 | 11 | 71.4% | +34.74% | −15.00% |
| **BTC** | none | 18 | 0 | 61.1% | +12.63% | −27.75% |
| BTC | proxy | 12 | 6 | 66.7% | +40.35% | −19.72% |
| **BTC** | **funding** | **18** | **0** | **61.1%** | **+12.63%** | **−27.75%** |
| BTC | full | 12 | 6 | 66.7% | +40.35% | −19.72% |
| **ETH** | none | 13 | 0 | **30.8%** | **−56.41%** | −48.72% |
| ETH | proxy | 6 | 11 | 33.3% | −19.32% | −38.59% |
| **ETH** | **funding** | **12** | **1** | **25.0%** | **−62.87%** | **−56.32%** |
| ETH | full | 5 | 12 | 20.0% | −31.27% | −38.59% |

## The four findings that matter

### 1. The funding guard works *only* on BNB

Funding-guard outperformance: BNB **+76pp** vs vanilla. BTC **0pp**. ETH **−6pp** (it *hurts*). The Skill's central claim — "the leverage-cascade guard improves risk-adjusted return" — is conditional on the token. This is exactly the kind of finding the Honest Skill exists to surface: it would be dishonest to ship a single guard and pretend it generalizes.

### 2. The −0.02% threshold never fires on BTC

Over 5.4 years and 18 vanilla RSI<30 triggers on BTCUSDT, daily-mean funding *never crossed −0.02%* on any entry day. The funding-guard run is byte-identical to the vanilla run: 0 entries blocked. The SKILL.md threshold is calibrated against the funding-rate distribution of alts; BTC's funding distribution is much tighter because the BTC futures market is the deepest in crypto and rarely takes on the kind of one-sided leverage that triggers cascades.

**Mitigation for v2:** the threshold needs to be token-specific. A reasonable replacement is "funding rate < 5th percentile of trailing 1y" rather than a fixed −0.02%. The current SKILL.md spec is honest about being calibrated to a regime, but doesn't surface this.

### 3. ETH RSI mean-reversion is a broken strategy

Vanilla ETH: 30.8% win rate, −56.41% compounded, −48.72% max drawdown. **You would have lost more than half your money** running this strategy on ETH over the window. The proxy guard *helps* the bleeding but still loses 19%. The funding guard makes things slightly *worse*. The full guard reduces losses but cannot turn negative expectancy positive.

This is the most important finding for the Skill's honesty thesis: **no guard can rescue a wrong strategy.** If the underlying signal doesn't work on the token, no entry-filter overlay will save it. The Honest Skill should refuse to recommend RSI mean-reversion on ETH at *any* confidence above the floor, and should explicitly cite this backtest as the reason.

### 4. The price-proxy is actually competitive on BTC

On BTC, where the real funding guard is inert, the price-proxy is the *only* working filter and beats vanilla by **+28pp** (+12% → +40%). On BNB the proxy is strictly inferior to real funding. On ETH the proxy reduces losses but doesn't reverse them.

**This vindicates keeping the proxy in the harness.** It's not a stand-in for the production guard — it's a *different* signal that catches *different* regimes. A real production Skill should call both: "did either funding flip or 30d price cascade?"

## Corrections to prior project artifacts

- **Day-7 hand-scored 3×3 finding** (memory): "all BNB cells 93, all BTC cells 78, all ETH cells 78 — macro signal stack dominates strategy choice." This was a confidence-score claim, not a P&L claim. The backtest result is richer and more nuanced. The real cross-token finding for *this* strategy is that vanilla P&L ranges from +98% on BNB to −56% on ETH — the **strategy-token fit dominates** the macro signal stack at the P&L level. The Skill's report structure should call this out: confidence and expected P&L are different axes.

- **Day-4 worked example** (`examples/bnb-rsi-mean-reversion/stress-test.md`) cited FTX-collapse as the canonical failure regime for this strategy on BNB. The harness shows the strategy never triggered during the FTX window on BNB daily (no RSI<30 crossing). The cited regime is a real leverage cascade visible in funding (BNBUSDT funding hit −0.095% min during Nov 2022) but did not break this specific strategy on this specific token. The worked example needs an honest footnote.

## What's still missing

- **OI clause.** Binance's public OI history is capped at 30 days. The `funding OR OI` guard from SKILL.md Step 5 cannot be fully tested over multi-year history without paid data (Coinglass / CryptoCompare). The `full` mode is a partial test.
- **Token-specific thresholds.** Demonstrated as needed but not implemented in this harness yet.
- **More strategies.** Trend-following, sentiment-divergence, etc. The 3×3 promised in earlier project planning is currently 3×1 (three tokens, one strategy).
- **Magnitude floors.** SKILL.md Step 5 mandates them for continuous-comparison triggers. The harness's RSI cross is binary, so it doesn't exercise this — but a sentiment-divergence backtest would.

## Files

Each per-token run dir contains `trades_none.csv`, `trades_proxy.csv`,
`trades_funding.csv`, `trades_full.csv`, and `summary.md`:

- `examples/backtest-runs/BNBUSDT_2021-01-01_2026-06-14/`
- `examples/backtest-runs/BTCUSDT_2021-01-01_2026-06-14/`
- `examples/backtest-runs/ETHUSDT_2021-01-01_2026-06-14/`

The earlier yfinance-sourced run lives at
`examples/backtest-runs/BNB-USD_2021-01-01_2026-06-14/` and is superseded by
the BNBUSDT directory. Trade signals are within one trade of each other
(15 vs 16 vanilla); the story is identical.
