# Stress-test: RSI mean-reversion on BTC

Second cell of the day-6 2×2 backtest. Same strategy as `bnb-rsi-mean-reversion`, different token. Live data captured 2026-06-12 08:07 UTC.

## Strategy under test

```
BUY  when RSI(14) crosses below 30
SELL when RSI(14) crosses above 70
otherwise flat
```

## Today's signal stack (BTC, 2026-06-12)

| Metric | Value |
|---|---|
| Price | $63,142.86 |
| Rank | 1 |
| RSI(14) | **32.89** — **near-trigger, strategy not yet signaling** |
| RSI(7) | 39.33 |
| MACD | line −3988.76, signal −3513.35, histogram −475.4 (bearish) |
| SMA(200) | 78,008.13 — price 19% below |
| Pivot | 62,953.66 — price just above |
| 30d change | −22.01% |
| BTC dominance | 58.54% (rising) |
| Holder distribution | available (`get_crypto_metrics` returned full data — unlike for BNB) |

## Mechanical similarity (top 5 candidate regimes)

Strategy signal class = RSI extreme. Today's macro: F&G Extreme Fear (17), BTC dominance rising 7d, funding near-zero. Asset: rank top-10, swing volatility.

| Regime | Failure mode | S | M | A | similarity |
|---|---|---|---|---|---|
| `btc-2022-11-ftx-collapse` | leverage-cascade | 1.0 | 0.67 | 1.0 | **0.835** |
| `btc-2022-06-celsius-3ac` | leverage-cascade | 1.0 | 0.67 | 1.0 | **0.835** |
| `btc-2020-03-covid-crash` | leverage-cascade | 1.0 | 0.67 | 0.5 | **0.685** |
| `btc-2021-05-china-ban` | regulatory-shock | 1.0 | 0.33 | 0.5 | **0.517** |
| `btc-2017-12-parabolic-top` | trend-persistence | 1.0 | 0.0 | 0.5 | 0.35 (below cutoff) |

Citations follow the same `[CMC-HISTORICAL]` + `[TRAINING-DATA]` pattern. `percent_change_3y = +144%` on `get_crypto_quotes_latest` anchors the Jun 2023 price level; older anchors lean on `percent_change_all` + training-data narrative.

## Dominant failure mode

Above-cutoff regimes: 4 (FTX 0.835, Celsius 0.835, COVID 0.685, China-ban 0.517).

| Mode | Cumulative similarity |
|---|---|
| `leverage-cascade` | 2.355 |
| `regulatory-shock` | 0.517 |

**Dominant: `leverage-cascade`** — by a wide margin. Three of the top four regimes are deleveraging crises.

## Generated rule set

**Entry guard (leverage-cascade)**: blocked when canonical funding rate `< −0.02%` OR 30d derivatives OI down `>20%` AND falling on the day.
- Today: funding `+0.00034%` (not blocking), but **30d OI change −22.08% AND 24h OI change −1.83%** (falling). **Guard fires. Entry blocked even if RSI dips below 30.**
- `because:` `btc-2022-11-ftx-collapse` and `btc-2022-06-celsius-3ac`, both leverage-cascade, both at similarity 0.835 — the strongest match the procedure has produced in any worked example so far.

**Exit**: RSI(14) crosses above 50 OR breach of falsifier (price-based: daily close < SMA(200) − 2% AND MACD hist still negative; flow-based: funding < −0.02% OR BTC dominance > 60%).

**Stop-loss**: cap-bound at 15% from any entry (no structural level closer in the down direction; pivot $62,953 is essentially at price).

## Confidence (Step 6, new component A and B definitions)

- **A** (signal consistency): trend bearish (price < SMA(200)), momentum bearish (MACD < 0), structure bullish (price > pivot, just). 2 of 3 same direction → **A = 0.67**.
- **B** (regime distance):
  - RSI: `min(|32.89 − 30|, |32.89 − 70|) / 30 = 2.89 / 30 = 0.096`
  - Price vs SMA(200): `14866 / (0.05 × 63143) = 4.71`, capped at `1.0`
  - MACD hist: `|−475.4| / (0.005 × 63143) = 1.51`, capped at `1.0`
  - Average: `(0.096 + 1.0 + 1.0) / 3 = 0.699`
- **C** (event risk): FOMC Jun 16–17 inside 14-day horizon → `C = 1 − 2/14 = 0.857`
- **D** (derivatives stress): canonical funding `+0.00034%`, `|rate| < 0.02%` → **D = 1.0**

`raw = 35·0.67 + 25·0.699 + 20·0.857 + 20·1.0 = 23.45 + 17.475 + 17.14 + 20 = 78.07`

Caps: no 60-cap (5 regimes surfaced); no 50-cap (2 falsifier classes); **no 40-DEGRADED cap** (all components computable under new defs).

**Final confidence: 78**

```json
{"A": 0.67, "B": 0.699, "C": 0.857, "D": 1.0, "raw": 78.07, "applied_cap": null, "final_confidence": 78}
```

## Guard rails

1. **Position size**: `5% × (78/100) = 3.9%` — **but entry blocked by leverage-cascade guard, so emit `do_not_size` regardless.**
2. **Stop-loss**: cap-bound at 15% from any entry.
3. **Event windows**: Jun 16–17 FOMC + Fed decision → action `flat_until_after`.
4. **Re-check trigger**: funding flips, OI turns positive, quality≥8 BTC-specific news, or any falsifier breach.

## What this cell proves

1. **The procedure generalizes from BNB to BTC without modification.** Same workflow, same formulas, different inputs, coherent output.
2. **The leverage-cascade guard correctly fires for both tokens** because it's keyed on *global* derivatives metrics (OI change) — not asset-specific data. That's a feature, not a bug: when the global derivatives system is deleveraging, RSI mean-reversion is dangerous on any token.
3. **Component A is now computable end-to-end** with the new single-timeframe definition. No `DEGRADED` cap. Final score 78 is the real confidence number, not a self-handicap.
4. **`get_crypto_metrics` works on BTC**, confirming day-3 gotcha 1 is an asset-coverage issue, not a tool failure. Day 6 cross-check should document which tier of assets the holder-data branch covers.
5. **BTC has higher similarity to its dominant failure regime (FTX/Celsius at 0.835)** than BNB does (FTX at 0.83). Same regime, but BTC's volatility-bucket match boosts it slightly. The procedure produces stable, comparable similarity scores across tokens.
