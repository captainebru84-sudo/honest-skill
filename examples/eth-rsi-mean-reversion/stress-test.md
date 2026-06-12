# Stress-test: RSI mean-reversion on ETH

Fifth cell of the day-7 3×3 expansion. Same strategy as `bnb-rsi-mean-reversion` and `btc-rsi-mean-reversion`. ETH live data captured 2026-06-12 08:29 UTC.

## Strategy under test

```
BUY  when RSI(14) crosses below 30
SELL when RSI(14) crosses above 70
otherwise flat
```

## Today's signal stack (ETH, 2026-06-12)

| Metric | Value |
|---|---|
| Price | $1,672.49 |
| Rank | 2 |
| RSI(14) | **31.22** — closest of any token tested to triggering |
| RSI(7) | 36.30 |
| MACD | line −143.01, signal −128.48, histogram −14.53 (bearish) |
| SMA(200) | 2,427.24 — price 31% below |
| Pivot | 1,660.94 — price just above |
| 30d change | −27.35% |
| ETH dominance | 9.29% |

## Mechanical similarity (top 5)

Same macro context as BNB and BTC runs: F&G Extreme Fear (17), BTC dominance rising 7d, funding near-zero. Asset: ETH is top-10 (rank 2), swing volatility.

| Regime | Failure mode | S | M | A | similarity |
|---|---|---|---|---|---|
| `eth-2022-11-ftx-collapse` | leverage-cascade | 1.0 | 0.67 | 1.0 | **0.835** |
| `eth-2022-06-celsius-3ac` | leverage-cascade | 1.0 | 0.67 | 1.0 | **0.835** |
| `eth-2022-05-terra-collapse` | news-driven-jump | 1.0 | 0.67 | 1.0 | **0.835** |
| `eth-2020-03-covid-crash` | leverage-cascade | 1.0 | 0.67 | 0.5 | **0.685** |
| `eth-2018-12-ico-winter-bottom` | trend-persistence | 1.0 | 0.0 | 0.5 | 0.35 (below) |

Citations: `[CMC-HISTORICAL]` via `percent_change_3y = −4.26%` anchors the Jun 2023 price level; `[TRAINING-DATA]` for the event narratives, paired one-to-one with the price anchor as required by Step 4.

## Dominant failure mode

Above-cutoff regimes: 4. Cumulative similarity:

| Mode | Cumulative |
|---|---|
| `leverage-cascade` | 2.355 |
| `news-driven-jump` | 0.835 |

**Dominant: `leverage-cascade`** — same as BNB and BTC RSI runs. The current macro regime is interpreting as "deleveraging crisis" for any asset by the procedure.

## Generated rules

**Entry guard (leverage-cascade)**: same global condition. **Fires today** (30d OI −22%, still falling). Entry blocked.

**Exit**: RSI(14) > 50 OR falsifier breach (price-based + flow-based).

**Stop**: cap-bound at 15% from any entry.

## Confidence

- **A**: trend bearish, momentum bearish, structure bullish. 2 of 3 → **0.67**
- **B**:
  - RSI: `|31.22 − 30| / 30 = 0.041` (extremely close to flip)
  - Price vs SMA(200): `755 / (0.05 × 1672) = 9.03`, capped at `1.0`
  - MACD hist: `|−14.53| / (0.005 × 1672) = 1.74`, capped at `1.0`
  - Average: `0.680`
- **C**: `0.857` (FOMC inside horizon)
- **D**: `1.0`

`raw = 35·0.67 + 25·0.680 + 20·0.857 + 20·1.0 = 23.45 + 17.00 + 17.14 + 20 = 77.59`

No caps. **Final: 78**.

```json
{"A": 0.67, "B": 0.68, "C": 0.857, "D": 1.0, "raw": 77.59, "applied_cap": null, "final_confidence": 78}
```

## Guard rails

1. **Position size**: 3.9% scaled, but entry blocked → `do_not_size`.
2. **Stop**: cap-bound 15% from entry.
3. **Event windows**: FOMC Jun 16–17 → `flat_until_after`.
4. **Re-check**: funding flip, OI turn positive, ETH-specific quality≥8 news, or any falsifier breach.

## What this cell proves

1. **Third token, same procedure** — works without modification.
2. **The three top regimes for ETH (FTX, Celsius, Terra) all tie at 0.835**, showing the procedure properly identifies a *cluster* of comparable conditions, not just a single nearest neighbor.
3. **Confidence converges around 78 for both BTC and ETH** despite different price action and different historical regimes. The macro and global derivatives signals dominate the local TA differences when the trade is on a bearish stack of major tokens. Defensible behavior.
4. **ETH's RSI(14) at 31.22 is closer to the strategy's trigger than BTC's 32.89** — yet the confidence and the entry-blocking guard outputs are identical. A trader might be tempted to act on ETH first because the signal is "almost there"; the Skill's output flatly says no — the macro regime is wrong regardless of which name fires first.
