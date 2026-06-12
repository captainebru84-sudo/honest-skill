# Stress-test: trend-following on BTC

Fourth cell of the day-6 2×2 backtest. Same strategy as `bnb-trend-following`, same token as `btc-rsi-mean-reversion`. Captures the diagonal — does the procedure stay coherent across both axes of variation?

## Strategy under test

```
BUY  when (price > SMA(200, 1d)) AND (MACD line > 0)
SELL when either condition breaks
otherwise flat
```

## Today's signal stack (BTC, 2026-06-12)

| Metric | Value | Signal |
|---|---|---|
| Price | $63,142.86 | |
| SMA(200) | $78,008.13 | price 19% below — BUY blocked |
| MACD line | −3,988.76 | below zero — BUY blocked |
| RSI(14) | 32.89 | (not used) |

Strategy is **flat by definition** today. Both BUY conditions are violated, same as BNB.

## Similarity (compressed — top 3)

| Regime | Failure mode | similarity |
|---|---|---|
| `btc-2018-q1-distribution` (SMA-200 reclaim Q1 2018 after Dec 2017 top) | trend-persistence | **0.52** |
| `btc-2019-summer-chop` (oscillation around $10k SMA-200) | low-volume-noise | **0.52** |
| `btc-2022-04-bear-onset` (SMA-200 lost in Apr 2022) | trend-persistence | 0.35 (below cutoff) |

**Dominant failure mode**: `trend-persistence` / `low-volume-noise` tied — both at 0.52 cumulative.

## Generated rule set

Entry blocked by strategy definition. Guard is moot but reported.

- **`low-volume-noise` guard**: `unverified` (same tool gap as `bnb-trend-following`).
- **Exit**: strategy's own conditions.
- **Stop**: SMA(200) if entered.

## Confidence

- **A** (signal consistency): trend bearish, momentum bearish, structure bullish (price 63143 > pivot 62954). **2 of 3 → A = 0.67**.
- **B** (regime distance):
  - RSI: `2.89 / 30 = 0.096`
  - Price vs SMA(200): capped `1.0`
  - MACD hist: `|−475.4| / (0.005 × 63143) = 1.51`, capped `1.0`
  - Average: `0.699`
- **C**: `0.857`
- **D**: `1.0`

`raw = 35·0.67 + 25·0.699 + 20·0.857 + 20·1.0 = 78.07`

No caps applied.

**Final confidence: 78**

```json
{"A": 0.67, "B": 0.699, "C": 0.857, "D": 1.0, "raw": 78.07, "applied_cap": null, "final_confidence": 78}
```

## Guard rails

1. **Position size**: scaled would be 3.9%, but strategy flat → `not_signaling`.
2. **Stop**: SMA(200) at $78,008 if entry triggered.
3. **Event windows**: FOMC Jun 16–17 → `flat_until_after`.
4. **Re-check trigger**: BTC reclaims SMA(200) AND MACD > 0, OR a falsifier breach.

## What this cell proves

1. **The procedure is internally consistent across both axes** — BTC + trend-following produces structurally the same output as BNB + trend-following with the BTC-specific numbers substituted.
2. **Component A scores 0.67 here vs 1.0 for BNB**, because BTC's price sits just above its pivot while BNB sits just below. That asymmetry IS visible in the score — the procedure isn't smoothing it away. Honest.
3. **Confidence 78 for BTC vs 93 for BNB on the same strategy**: BTC's mixed structural signal (above pivot, below SMA-200) genuinely is less consistent than BNB's unanimous bear stack. The number reflects that.
4. **No new gotchas** beyond what `bnb-trend-following` already surfaced (the volume-median tool gap).
