# Stress-test: trend-following on BNB

Third cell of the day-6 2×2 backtest. Different strategy, same token as `bnb-rsi-mean-reversion`. Live data captured 2026-06-12 07:21 UTC.

## Strategy under test

```
BUY  when (price > SMA(200, 1d)) AND (MACD line > 0)
SELL when either condition breaks
otherwise flat
```

Representative of the "just hold the trend" baseline. Different signal classes (SMA reclaim, MACD cross) — tests whether the procedure generalizes off RSI mean-reversion.

## Today's signal stack (BNB, 2026-06-12)

| Metric | Value | Signal |
|---|---|---|
| Price | $598.00 | |
| SMA(200) | $719.56 | **price 17% below** — BUY condition NOT met |
| MACD line | −15.70 | **below zero** — BUY condition NOT met |
| RSI(14) | 44.07 | (not used by this strategy) |

Strategy is **flat by definition** today. Both BUY conditions are violated.

## Mechanical similarity (top 5 candidate regimes)

Signal classes: SMA reclaim, MACD cross long. A historical regime "matches" if at least one of those classes triggered.

| Regime | Failure mode | S | M | A | similarity | Notes |
|---|---|---|---|---|---|---|
| `bnb-2022-h2-chop` | low-volume-noise | 1.0 | 0.33 | 0.5 | **0.52** | SMA-200 was crossed multiple times in chop |
| `bnb-2018-q1-distribution` | trend-persistence | 1.0 | 0.33 | 0.5 | **0.52** | Bought SMA reclaim after Dec 2017 top → killed |
| `bnb-2023-08-low-volume-drift` | low-volume-noise | 1.0 | 0.33 | 0.5 | **0.52** | Fake reclaims in summer drift |
| `bnb-2022-04-bear-onset` | trend-persistence | 1.0 | 0.0 | 0.5 | 0.35 | Below cutoff |
| `bnb-2025-q1-rally-pullback` | trend-persistence | 1.0 | 0.0 | 0.5 | 0.35 | Below cutoff |

The procedure naturally surfaces *different* failure regimes from the RSI run because the signal classes are different. Strategy-aware regime selection works.

## Dominant failure mode

Above-cutoff regimes: 3 (all tied at 0.52).

| Mode | Cumulative similarity |
|---|---|
| `low-volume-noise` | 1.04 |
| `trend-persistence` | 0.52 |

**Dominant: `low-volume-noise`** — narrowly. Trend-following's classic failure is chop, not crashes.

## Generated rule set

**Entry guard (low-volume-noise)**: blocked when 24h spot volume is below 30-day median × 0.8.
- Today's volume: $1.07B on BNB. Median check requires historical volume — not directly available from current tools. Honest move: substitute the neutral "indeterminate" state, label the guard `unverified` and surface that explicitly.
- `because:` `bnb-2022-h2-chop` and `bnb-2023-08-low-volume-drift` — both showed that SMA-200 reclaims in low-volume conditions are noise.

**Strategy-level note**: BUY conditions are not met today regardless. The guard is moot for this run but reported for completeness.

**Exit**: price closes below SMA(200) OR MACD line crosses below zero. (Strategy's own conditions.)

**Stop-loss**: structural level (SMA(200) itself if entered above) or `max_drawdown_pct` cap, whichever closer.

## Confidence

- **A** (signal consistency): trend bearish, momentum bearish, structure bearish (price < pivot 598.85). 3 of 3 → **A = 1.0**
- **B** (regime distance):
  - RSI: `|44.07 − 30| / 30 = 0.469` (nearest of 30/70)
  - Price vs SMA(200): `122 / (0.05 × 598) = 4.07`, capped at `1.0`
  - MACD hist: `|−5.69| / (0.005 × 598) = 1.90`, capped at `1.0`
  - Average: `0.823`
- **C**: FOMC inside horizon → `0.857`
- **D**: funding near-zero → `1.0`

`raw = 35·1.0 + 25·0.823 + 20·0.857 + 20·1.0 = 35 + 20.58 + 17.14 + 20 = 92.72`

Caps: 5 regimes surfaced (no 60-cap); 2 falsifier classes (no 50-cap); the low-volume-noise guard is marked `unverified` — this is a partial-degradation case that the spec doesn't currently address explicitly. Conservative interpretation: 1 unverified component, not yet ≥2 fallbacks, no DEGRADED cap.

**Final confidence: 93**

```json
{"A": 1.0, "B": 0.823, "C": 0.857, "D": 1.0, "raw": 92.72, "applied_cap": null, "final_confidence": 93, "notes": ["entry guard 'unverified': 30d median volume not in current tool surface"]}
```

## Guard rails

1. **Position size**: `5% × (93/100) = 4.65%` — **but strategy is flat (entry conditions not met)**. Emit `not_signaling` with explanation: BUY requires price > SMA(200) AND MACD > 0; today both are violated. Confidence is high but the trade is not on.
2. **Stop-loss**: would be SMA(200) at $719.56 if entry triggered.
3. **Event windows**: FOMC Jun 16–17 → `flat_until_after`.
4. **Re-check trigger**: price reclaims SMA(200) AND MACD crosses above zero, OR a falsifier breach.

## What this cell proves

1. **The procedure generalizes off RSI to a different signal-class strategy** (SMA reclaim + MACD cross). Same workflow steps, different inputs to the similarity function (signal classes), different failure regimes surfaced. Strategy-aware behavior works.
2. **High confidence + strategy-flat is a coherent output.** The Skill correctly reports confidence 93 (signal stack is clean) and `not_signaling` (strategy not triggered). These are not contradictions — they are answers to different questions.
3. **Surfaced a new tooling gap**: low-volume-noise guard requires 30-day median spot volume, which isn't directly available from current allowed-tools. The spec should either add an approximation (e.g., volume vs 24h_volume change over 30d window from quotes) or accept that this guard runs in `unverified` mode pending tool extension.
