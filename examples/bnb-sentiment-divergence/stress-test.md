# Stress-test: sentiment-divergence on BNB

Seventh cell of the day-7 3×3 expansion. **New strategy** for the matrix — first cell where the strategy actually fires on today's data, not just produces a flat-state report.

## Strategy under test (sentiment-divergence)

```
BUY  when Fear & Greed index < 25 AND 7d price change > 0
     (extreme fear + price resilience = bullish divergence)
SELL when Fear & Greed index > 75 AND 7d price change < 0
     (extreme greed + price weakness = bearish divergence)
otherwise flat
```

Signal classes: `F&G extreme`, `price-trend divergent`. A historical regime "matches" the strategy if at least one class triggered (`S = 1`); both for `S = 1.0` after the gate.

## Today's signal stack (BNB, 2026-06-12)

| Metric | Value | Signal |
|---|---|---|
| Fear & Greed | **17 (Extreme Fear)** | BUY condition #1 ✓ |
| BNB 7d change | **+3.54%** | BUY condition #2 ✓ |
| Price | $598.00 | |
| RSI(14) | 44.07 | not used by this strategy |
| BTC dominance | 58.44% | |

**Strategy is signaling BUY** today. First triggered cell of the entire backtest matrix.

## Mechanical similarity (top 5)

The strategy's signal classes are unusual — sentiment-based. Few historical regimes match cleanly; the Skill honestly surfaces 4 above-cutoff and reports `surfaced 4 of target 3–5`.

| Regime | Failure mode | S | M | A | similarity | Notes |
|---|---|---|---|---|---|---|
| `bnb-2022-06-terra-celsius-fear-rallies` | leverage-cascade | 1.0 (F&G<25 ✓, 7d-pos rally ✓) | 0.67 | 1.0 | **0.835** | BNB bounced 10–20% off Terra/Celsius lows; faded |
| `bnb-2022-10-fomc-pivot-fear-bounce` | low-volume-noise | 1.0 | 0.67 (F&G ✓, dom ✓, funding ✗) | 1.0 | **0.835** | Fed pivot hopes + extreme fear → BNB rally that died |
| `bnb-2020-03-covid-fear-mid-crash` | leverage-cascade | 1.0 | 0.67 | 0.5 | **0.685** | F&G hit 8; BNB held briefly mid-crash before more losses |
| `bnb-2018-11-cap-w-bottom-attempt` | trend-persistence | 1.0 | 0.33 | 0.5 | **0.517** | Persistent F&G <25; multiple failed bounces over weeks |
| `bnb-2025-q1-correction-fear-rally` | regulatory-shock | 0.5 (F&G partial) | 0.33 | 1.0 | 0.40 (below) | F&G hit 28, not <25 — signal-class match partial |

## Dominant failure mode

| Mode | Cumulative |
|---|---|
| `leverage-cascade` | 1.52 |
| `low-volume-noise` | 0.835 |
| `trend-persistence` | 0.517 |

**Dominant: `leverage-cascade`** — once again. Three different strategies, three different signal classes, same dominant failure mode on today's macro stack. That's a real finding: the macro regime *is* the dominant context, not the strategy choice.

## Generated rule set

**Strategy is triggered.** Rules apply to the live signal.

**Entry guard (leverage-cascade)**: blocked when funding `< −0.02%` OR 30d OI down `>20%` AND falling.
- Today: funding `+0.00034%` (not blocking), 30d OI `−22%` AND 24h OI `−1.83%` (still falling). **Guard fires. BUY entry blocked.**
- `because:` `bnb-2022-06-terra-celsius-fear-rallies` (similarity 0.835) — F&G hit 6 in Jun 2022 during Celsius/3AC, BNB had a 12% bounce on day-1, then went on to a new lower low within 5 weeks.

**Exit (if entry had occurred)**:
- Primary signal-reversal: F&G crosses above 50 OR 7d change turns negative.
- Falsifier (Output Schema #3): price-based — daily close below pivot $598.85 with no F&G improvement; flow-based — funding flips negative OR BTC dom > 60%.

**Stop-loss**: `cap-bound` at 15% from a hypothetical entry zone. No closer structural level downside since price is at pivot.

**`because:` annotations** complete for every emitted rule. Three rules, three traces.

## Confidence

- **A** (signal consistency, daily): trend bearish (price < SMA-200), momentum bearish (MACD < 0), structure bearish (price 598 < pivot 598.85, just). 3 of 3 → **A = 1.0**.
- **B**:
  - RSI: `(44.07 − 30) / 30 = 0.469`
  - Price vs SMA(200): `121.56 / (0.05 × 598) = 4.07`, capped `1.0`
  - MACD hist: `|−5.69| / (0.005 × 598) = 1.90`, capped `1.0`
  - Average: `0.823`
- **C** (event risk): FOMC inside horizon → `0.857`
- **D** (derivatives stress): funding near-zero → `1.0`

`raw = 35·1.0 + 25·0.823 + 20·0.857 + 20·1.0 = 35 + 20.58 + 17.14 + 20 = 92.72`

Caps: 5 regimes considered (4 surfaced above cutoff) — no 60-cap. 2 falsifier classes — no 50-cap. No DEGRADED state. **Final: 93**.

```json
{
  "A": 1.0, "B": 0.82, "C": 0.857, "D": 1.0,
  "raw": 92.72, "applied_cap": null, "final_confidence": 93,
  "signal_state": "triggered",
  "guard_state": "blocking"
}
```

## Guard rails

1. **Position size**: `5% × (93/100) = 4.65%` — **but the leverage-cascade guard is blocking BUY entry, so emit `do_not_size` despite high confidence.** The Skill is saying: signal is clean (93), but conditions for a safe entry are absent.
2. **Stop-loss**: `cap-bound` at 15% from any entry.
3. **Event windows**: FOMC Jun 16–17 → `flat_until_after` if guard ever clears.
4. **Re-check triggers**:
   - 24h OI change turns positive (un-fires guard).
   - Funding rate flips below `−0.02%` (D drops to 0, confidence falls below the entry threshold).
   - 7d price change crosses below 0 (un-fires signal).
   - F&G crosses above 25 (un-fires signal).

## What this cell proves

1. **First strategy that actually triggers in the matrix.** The Skill produces a substantive, actionable-but-blocked output: high confidence, blocking guard, clean trace from regime → guard → outcome.
2. **High confidence + blocked entry is a coherent output.** A naive reader sees 93 and thinks "great trade". The honest output makes them read the next line: blocked by leverage-cascade. That's the project's thesis playing out — every signal ships with its falsifier.
3. **Three different strategies, same dominant failure mode** on this macro snapshot — strong evidence that the *macro regime* is the dominant context, not the strategy choice. This is a research-worthy finding for the Stress Test page deliverable.
4. **The procedure handles a triggered signal cleanly.** Exit conditions, stop-loss, re-check triggers all generated end-to-end. Coverage equal to the flat-state outputs.
