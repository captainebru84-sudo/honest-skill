# Stress-test: trend-following on ETH

Sixth cell of the day-7 3×3 expansion. Same strategy as `bnb-trend-following` and `btc-trend-following`. ETH data 2026-06-12.

## Strategy

```
BUY  when (price > SMA(200, 1d)) AND (MACD line > 0)
SELL when either breaks
otherwise flat
```

## Today's stack (ETH)

| Metric | Value | Signal |
|---|---|---|
| Price | $1,672.49 | |
| SMA(200) | $2,427.24 | price 31% below — BUY blocked |
| MACD line | −143.01 | below zero — BUY blocked |

Strategy is **flat by definition**.

## Similarity (top 3)

| Regime | Failure mode | similarity |
|---|---|---|
| `eth-2018-q1-distribution` (SMA-200 reclaim after Jan 2018 top) | trend-persistence | **0.52** |
| `eth-2019-summer-chop` (oscillation around $200 SMA-200) | low-volume-noise | **0.52** |
| `eth-2022-04-bear-onset` (SMA-200 lost in Apr 2022 fake reclaim) | trend-persistence | 0.35 (below) |

**Dominant**: `trend-persistence` / `low-volume-noise` tied at 0.52.

## Rules

- Entry blocked by strategy conditions.
- Guard: `low-volume-noise` unverified (same tool gap as BNB/BTC trend cells).
- Exit: strategy's own conditions.

## Confidence

- **A**: trend bearish, momentum bearish, structure bullish → **0.67**
- **B**: `(0.04 + 1.0 + 1.0) / 3 = 0.68`
- **C**: `0.857`
- **D**: `1.0`
- `raw = 23.45 + 17.0 + 17.14 + 20 = 77.59`
- No caps. **Final: 78**.

## Guard rails

1. Position size: would be 3.9%, but strategy flat → `not_signaling`.
2. Stop: SMA(200) at $2,427 if triggered.
3. Event windows: FOMC Jun 16–17 → `flat_until_after`.
4. Re-check: reclaim of SMA(200) AND MACD > 0, or falsifier breach.

## What this cell proves

1. ETH's confidence with trend-following (78) matches ETH+RSI (78) and BTC+trend (78). The signal stack dominates the strategy choice when both strategies read the same TA inputs. Honest output.
2. Third token × second strategy = same procedure shape, same output structure.
3. No new gotchas.
