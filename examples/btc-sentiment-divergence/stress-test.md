# Stress-test: sentiment-divergence on BTC

Eighth cell of the day-7 3×3 expansion. Same strategy as `bnb-sentiment-divergence` (see that file for the full strategy definition and rationale). BTC live data 2026-06-12.

## Today's signal stack (BTC)

| Metric | Value | Signal |
|---|---|---|
| Fear & Greed | **17 (Extreme Fear)** | BUY ✓ |
| BTC 7d change | **+0.53%** | BUY ✓ (marginally) |
| Price | $63,142.86 | |
| RSI(14) | 32.89 | |

**Strategy is signaling BUY**, but only marginally — the +0.53% over 7 days is weak. A future spec polish should consider a magnitude floor on the price-divergence condition (e.g. require >1% over 7d for a clean trigger).

## Mechanical similarity (top 5)

Same macro context. BTC's regime corpus surfaces similar leverage-cascade events as the RSI run, but the *triggering* condition is sentiment-based.

| Regime | Failure mode | S | M | A | similarity |
|---|---|---|---|---|---|
| `btc-2022-06-celsius-fear-rallies` | leverage-cascade | 1.0 | 0.67 | 1.0 | **0.835** |
| `btc-2022-10-fomc-pivot-fear-bounce` | low-volume-noise | 1.0 | 0.67 | 1.0 | **0.835** |
| `btc-2020-03-covid-fear-bounce` | leverage-cascade | 1.0 | 0.67 | 0.5 | **0.685** |
| `btc-2018-11-cap-w-bottom` | trend-persistence | 1.0 | 0.33 | 0.5 | **0.517** |
| `btc-2022-11-ftx-fear-rallies` | leverage-cascade | 1.0 | 0.67 | 1.0 | **0.835** |

5 surfaced, 5 above cutoff (4 at >0.5, 1 at 0.517). Diversity: leverage-cascade × 3, low-volume-noise, trend-persistence. ✓

## Dominant failure mode

| Mode | Cumulative |
|---|---|
| `leverage-cascade` | 2.355 |
| `low-volume-noise` | 0.835 |
| `trend-persistence` | 0.517 |

**Dominant: `leverage-cascade`** — third strategy in a row converging on the same dominant mode for today's macro.

## Generated rules

**Entry guard (leverage-cascade)**: fires today (global OI condition). **BUY blocked.**

`because:` `btc-2022-06-celsius-fear-rallies`, `btc-2022-11-ftx-fear-rallies` — both showed F&G-extreme + brief BTC stabilization preceding further deleveraging-driven lows.

Exit, stop, falsifiers same structure as `bnb-sentiment-divergence`. Stop is `cap-bound` from any entry.

## Confidence

- **A**: trend bearish, momentum bearish, structure bullish (price 63143 > pivot 62954) — 2 of 3 → **0.67**
- **B**: same as `btc-rsi-mean-reversion` since RSI/SMA/MACD didn't change → `0.699`
- **C**: `0.857`
- **D**: `1.0`
- `raw = 23.45 + 17.475 + 17.14 + 20 = 78.07`
- No caps. **Final: 78**.

```json
{
  "A": 0.67, "B": 0.699, "C": 0.857, "D": 1.0,
  "raw": 78.07, "applied_cap": null, "final_confidence": 78,
  "signal_state": "triggered_marginally",
  "guard_state": "blocking"
}
```

The `signal_state` field is annotated `triggered_marginally` because the 7d change of +0.53% only just clears the > 0 threshold. Honest disclosure.

## Guard rails

1. **Position size**: 3.9% scaled, but guard blocking → `do_not_size`.
2. **Stop**: cap-bound 15% from entry.
3. **Event windows**: FOMC Jun 16–17 → `flat_until_after`.
4. **Re-check**: same triggers as BNB+sentiment, plus a clean-trigger check (7d change > 1%).

## What this cell proves

1. **The procedure handles "marginally triggered" signals coherently** by passing the trigger but surfacing the marginal state in `signal_state`. This is the day-6 cross-check's gotcha 1 (add `signal_state` field) playing out here even without the spec edit — informally, by labeling.
2. **Confidence 78 mirrors BTC+RSI and BTC+trend** — BTC's signal stack today produces the same confidence number regardless of which of the three strategies we run. That's the "macro dominates strategy choice" finding from BNB+sentiment, confirmed on a second token.
3. **The leverage-cascade guard remains the operative constraint** across both BNB and BTC sentiment runs. Same mechanism, same outcome.
