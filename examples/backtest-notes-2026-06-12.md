# Day 6 cross-check notes — 2×2 backtest, 2026-06-12

Reviewed all four cells of the 2×2 backtest matrix to see what generalizes, what doesn't, and what the SKILL.md procedures need next.

## The matrix

|  | RSI mean-reversion | Trend-following (SMA-200 + MACD) |
|---|---|---|
| **BNB** | `examples/bnb-rsi-mean-reversion/` | `examples/bnb-trend-following/` |
| **BTC** | `examples/btc-rsi-mean-reversion/` | `examples/btc-trend-following/` |

## Summary table

| Cell | A | B | C | D | raw | cap | final | dominant mode | guard fires? |
|---|---|---|---|---|---|---|---|---|---|
| BNB + RSI | 1.00 | 0.82 | 0.86 | 1.00 | 92.7 | — | **93** | leverage-cascade | yes (OI cascade) |
| BTC + RSI | 0.67 | 0.70 | 0.86 | 1.00 | 78.1 | — | **78** | leverage-cascade | yes (OI cascade) |
| BNB + trend | 1.00 | 0.82 | 0.86 | 1.00 | 92.7 | — | **93** | low-volume-noise | unverified |
| BTC + trend | 0.67 | 0.70 | 0.86 | 1.00 | 78.1 | — | **78** | low-volume-noise | unverified |

## What generalizes

1. **The full Step 1–7 workflow runs without modification on all four cells.** No code paths broken; no extra steps needed. The Skill spec is asset-agnostic and strategy-agnostic by construction.

2. **The mechanical similarity scoring produces reproducible, stable numbers.** Two engineers running the Skill against the same data should land on the same scores. We tested this implicitly by computing similarity twice for BNB (day 4 hand-score vs day 5 mechanical) and the day-5 numbers replicated cleanly when recomputed today.

3. **Strategy-aware regime selection works.** RSI runs surface deleveraging crises (FTX, Celsius, COVID) as the dominant similarity hits; trend-following runs surface chop and distribution periods. The signal-class gate (`S`) in the similarity formula does its job.

4. **The leverage-cascade guard correctly fires on both tokens** because it depends on *global* derivatives metrics (`get_global_crypto_derivatives_metrics`). When global OI is in multi-week deleveraging, RSI mean-reversion is dangerous on any token. The guard fires for the right structural reason, not by accident.

5. **The new component-A definition (intra-timeframe consistency) yields meaningful score variation across tokens.** BNB scores A=1.0 because all three sub-signals align bearish; BTC scores A=0.67 because price sits just above its pivot. That difference is real and is reflected. Component A is no longer permanently degraded.

6. **The new component-B MACD term (`|hist| / (0.5% × price)`) saturates fast** — both tokens cap that sub-term at 1.0 today. That's defensible behavior in a bearish regime (large MACD histograms relative to price) but the term won't differentiate well in calmer regimes. Worth re-evaluating with a low-volatility token in a future test.

## What doesn't generalize cleanly

1. **`get_crypto_metrics` holder data is asset-coverage-limited.** Confirmed: returns full data for BTC (rank 1), empty for BNB (rank 4). Day-3 gotcha 1 closed. **Action**: the Skill must explicitly check for `coinMarketCapCryptoTotalHolderData` presence and route around it for assets that lack it. Step 3 of SKILL.md should be amended to document this graceful degradation.

2. **`low-volume-noise` guard is unverified** in both trend-following cells. The procedure asks for "24h spot volume below 30-day median × 0.8" but the current tool surface gives only the *current* 24h volume, not the historical 30-day distribution. **Decision needed**: either (a) approximate using the `market_cap_percent_change_30d` proxy, (b) accept the guard runs `unverified` until tool extension, or (c) rewrite the guard to use the current 24h `volume_change_24h` percent vs zero as a coarse proxy.

3. **Confidence number alone is misleading for strategies that are flat.** Both trend-following cells produced 93 / 78 — high numbers — even though the strategy is not signaling. The Skill should pair `final_confidence` with a `signal_state` field (one of `triggered` / `near-trigger` / `flat` / `flat-by-definition`) to keep the headline number honest. **Add to Output Schema #5 in day 7.**

4. **Component A is binary-discrete in practice.** Because the three sub-signals (trend, momentum, structure) are each binary directions and there are only three of them, A can only take values `1.0` or `0.67`. The earlier "or `0.33` for one-of-three" case is actually impossible with three binary signals (the count of the majority direction is always 2 or 3 out of 3). This isn't broken but it's a smaller signal than the formula's spec implies. Day-7 polish item: state explicitly that A is in `{0.67, 1.0}` for the 3-sub-signal case and what would change to add granularity (more sub-signals).

## New gotchas surfaced for day 7

1. **Add `signal_state` field to Output Schema #5** (`triggered` / `near-trigger` / `flat` / `flat-by-definition`) — pair with `final_confidence`.
2. **Document the `coinMarketCapCryptoTotalHolderData` asset-coverage limitation** in SKILL.md Step 3 / Prerequisites.
3. **Resolve the `low-volume-noise` guard's missing 30-day median**: pick a defensible proxy or accept `unverified` mode with explicit reporting.
4. **State component A's effective range** (`{0.67, 1.0}` for the current 3-sub-signal definition) in Output Schema #5 to avoid implying false granularity.
5. **The day-5 worked example reported final_confidence=40 due to DEGRADED**. Under today's new component-A definition that cap no longer fires. The BNB+RSI example's "Day 5 extension" section now reads slightly inconsistent with the SKILL.md spec. **Action**: add a one-paragraph note at the top of the day-5 extension acknowledging that it was written against the prior component-A definition and pointing readers to the corrected day-6 backtest table for the current-spec numbers. Do not rewrite the section — the historical drift is itself informative as a record of the Skill's evolution.

## What this day-6 work proves end-to-end

The procedures locked in SKILL.md Steps 1–7 (a) produce coherent reports on multiple tokens, (b) produce coherent reports on multiple strategies, (c) surface different failure regimes appropriate to the strategy under test, (d) yield reproducible confidence scores from mechanical computation, and (e) self-handicap honestly when components can't be computed or guards can't be verified.

That's the core deliverable for Track 2 — a backtestable strategy spec that argues against itself.

The remaining day-7 polish is real but bounded (5 items above, all schema-level not architectural).
