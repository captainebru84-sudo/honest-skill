# Stress-test: sentiment-divergence on ETH

Ninth and final cell of the day-7 3×3 expansion. Same strategy as `bnb-sentiment-divergence`. ETH live data 2026-06-12.

## Today's signal stack (ETH)

| Metric | Value | Signal |
|---|---|---|
| Fear & Greed | **17 (Extreme Fear)** | BUY ✓ |
| ETH 7d change | **+0.08%** | BUY ✓ (essentially flat, trigger by epsilon) |
| Price | $1,672.49 | |
| RSI(14) | 31.22 | |

**Strategy is signaling BUY**, but the 7d change is essentially zero (+0.08%). This is the weakest "trigger" in the matrix. The trade is on the threshold — defensible call by the threshold logic, but a trader would want to wait for a clearer divergence.

## Mechanical similarity (top 5)

| Regime | Failure mode | S | M | A | similarity |
|---|---|---|---|---|---|
| `eth-2022-05-terra-fear-rallies` | news-driven-jump | 1.0 | 0.67 | 1.0 | **0.835** |
| `eth-2022-06-celsius-fear-bounces` | leverage-cascade | 1.0 | 0.67 | 1.0 | **0.835** |
| `eth-2022-11-ftx-fear-rallies` | leverage-cascade | 1.0 | 0.67 | 1.0 | **0.835** |
| `eth-2018-12-ico-winter-fear-floors` | trend-persistence | 1.0 | 0.33 | 0.5 | **0.517** |
| `eth-2020-03-covid-fear-bounce` | leverage-cascade | 1.0 | 0.67 | 0.5 | **0.685** |

5 surfaced, all above cutoff. 3 distinct failure modes — diversity satisfied.

## Dominant failure mode

| Mode | Cumulative |
|---|---|
| `leverage-cascade` | 2.355 |
| `news-driven-jump` | 0.835 |
| `trend-persistence` | 0.517 |

**Dominant: `leverage-cascade`** — for the ninth cell in a row. The macro regime is the macro regime.

## Generated rules

**Entry guard (leverage-cascade)**: fires (global). **BUY blocked.**

`because:` `eth-2022-11-ftx-fear-rallies`, `eth-2022-06-celsius-fear-bounces` — both showed F&G < 25 + brief ETH stabilization preceding further leverage-driven lows on the order of $200–$400.

Exit, stop, falsifiers per `bnb-sentiment-divergence` structure.

## Confidence

- **A**: trend bearish, momentum bearish, structure bullish (price 1672 > pivot 1660) → **0.67**
- **B**:
  - RSI: `0.041`
  - Price vs SMA(200): capped `1.0`
  - MACD hist: capped `1.0`
  - Avg: `0.680`
- **C**: `0.857`
- **D**: `1.0`
- `raw = 23.45 + 17.0 + 17.14 + 20 = 77.59`
- **Final: 78**.

```json
{
  "A": 0.67, "B": 0.68, "C": 0.857, "D": 1.0,
  "raw": 77.59, "applied_cap": null, "final_confidence": 78,
  "signal_state": "triggered_marginally",
  "guard_state": "blocking"
}
```

`signal_state: triggered_marginally` because the 7d change of +0.08% is on the threshold of the strategy's BUY condition.

## Guard rails

1. **Position size**: 3.9% scaled, but blocked → `do_not_size`.
2. **Stop**: cap-bound 15%.
3. **Event windows**: FOMC Jun 16–17 → `flat_until_after`.
4. **Re-check**: same as `bnb-sentiment-divergence` plus `7d change > 1%` for clean-trigger upgrade.

## What this cell proves (and what it doesn't)

1. **The procedure scales to N tokens × M strategies without surprises.** Ninth cell, no new issues, no spec edits required.
2. **Confidence 78 for the third time on ETH** — same as ETH+RSI and ETH+trend. ETH's signal stack is the dominant input; the strategy is a thin layer on top. Two tokens (BTC, ETH) and three strategies confirm this finding.
3. **The "marginally triggered" classification has real teeth on ETH** — +0.08% 7d change is functionally zero. A spec polish that requires magnitude floors on divergence conditions would re-classify this cell as `flat` rather than `triggered_marginally`. Day 8 worked example for the demo video could use this exact cell as an illustration of why magnitude floors matter.
4. **What this does NOT prove**: that the strategy is *bad* — only that today's specific macro regime is hostile to it. A different macro snapshot (e.g., Greed regime with weakening price) would surface different failure regimes and yield different confidence numbers. The Skill is a regime-aware filter, not a universal verdict.
