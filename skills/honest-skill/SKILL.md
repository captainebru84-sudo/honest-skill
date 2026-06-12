---
name: honest-skill
description: |
  Produces a backtestable strategy for a cryptocurrency that ships with the conditions under which it reverses, 3-5 historical regimes where the same rule lost money (cited from CoinMarketCap data), a confidence score derived from signal cleanliness, and guard rails tuned to those failure modes.
  Use when the user wants a strategy they can trust, audit, or backtest — not a one-sided "BUY/SELL" call. Especially useful before sizing a position, before publishing a signal, or when auditing another agent's recommendation.
  Trigger: "honest read on [coin]", "stress test [strategy] on [coin]", "what would invalidate [thesis]", "give me a strategy I can audit", "/honest-skill"
license: MIT
compatibility: ">=1.0.0"
user-invocable: true
allowed-tools:
  - mcp__cmc-mcp__search_cryptos
  - mcp__cmc-mcp__get_crypto_quotes_latest
  - mcp__cmc-mcp__get_crypto_technical_analysis
  - mcp__cmc-mcp__get_crypto_metrics
  - mcp__cmc-mcp__get_crypto_latest_news
  - mcp__cmc-mcp__get_crypto_marketcap_technical_analysis
  - mcp__cmc-mcp__get_global_metrics_latest
  - mcp__cmc-mcp__get_global_crypto_derivatives_metrics
  - mcp__cmc-mcp__get_upcoming_macro_events
  - mcp__cmc-mcp__search_crypto_info
---

# The Honest Skill

A CMC Skill that argues against itself — every strategy ships with the conditions that reverse it.

## Prerequisites

CoinMarketCap MCP server configured. Reference config:

```json
{
  "mcpServers": {
    "cmc-mcp": {
      "type": "http",
      "url": "https://mcp.coinmarketcap.com/mcp",
      "headers": { "X-CMC-MCP-API-KEY": "<your-key>" }
    }
  }
}
```

**Tool-coverage notes** (empirical, 2026-06-12):
- `get_crypto_metrics` returns the `addressesByHoldingValue` / `circulatingSupplyDistribution` / `addressesByHoldingTime` blocks only for higher-tier assets (verified for BTC and ETH; returns empty for BNB). The Skill must check for presence and degrade gracefully rather than fabricate when these are missing.
- `get_crypto_technical_analysis` returns single-timeframe (daily) data only. Cross-timeframe analysis is not available from this tool surface.
- `get_crypto_latest_news` returns the `latest` window only — historical news cannot be queried by date.

## Core Principle

A strategy is only honest if it tells you what would prove it wrong before you take it.

## Inputs

| Field | Type | Notes |
|---|---|---|
| `token` | free-text | Symbol, CMC id, or coin name. Always resolved via `search_cryptos` so ambiguous symbols (e.g. multiple "BNB" matches) are surfaced, not silently picked. |
| `timeframe` | auto-detected | The Skill picks `scalp` / `swing` / `position` from realised volatility. Compute Wilder ATR(14) on the daily series, then `atr_pct = mean(ATR(14) / close, last 30 days)`. Rank `atr_pct` against its own 1-year (252-day) distribution and bucket by tercile: top tercile (≥66th percentile) → `scalp`, middle → `swing`, bottom (≤33rd percentile) → `position`. Fallback: if fewer than 252 daily candles exist, use full available history with a 90-day minimum; below 90 days, force `swing` and label the output `LIMITED-HISTORY`. The chosen bucket, the `atr_pct` value, the percentile rank, and the sample-size flag are reported so the user can override. |
| `max_drawdown_pct` | numeric, default `15` | Hard cap on per-trade loss. Drives the stop-loss placement in the guard-rail block. |
| `position_cap_pct` | numeric, default `5` | Maximum portfolio weight. Scaled down further by the confidence score. |

## Output Schema

Every run produces the following structured block. Sections are non-negotiable — a run that cannot fill a section says so explicitly rather than dropping it.

1. **Thesis** — one-sentence directional bias (long / short / flat) with the primary signal.
2. **Entry & Exit Rules** — precise, backtestable conditions. Levels quoted in price; indicators named with parameter (e.g. `SMA(200, 1d)`).
3. **Reversal Conditions (the falsifiers)** — the conditions that, if met, invalidate the thesis. At least two independent signals (price-based + flow-based). This is the honest core.
4. **Cited Failure Regimes** — 3–5 historical periods where this same rule would have lost money, each with: date range, what triggered the failure, the CMC data point that flags it (link to the metric, not just the claim).
5. **Confidence Score (0–100)** — published formula. Compute four components, each normalised to `0..1`:
   - `A` *signal consistency* — agreement across three signal dimensions on the primary daily timeframe (the CMC TA tool returns single-timeframe data): **trend** (price vs SMA(200) — bullish if above, bearish if below), **momentum** (MACD line vs zero — bullish if above, bearish if below), and **structure** (price vs pivot point — bullish if above, bearish if below). Count the unanimous-direction sub-signals and divide by 3 (so all three same direction = 1.0; two-of-three same direction = 0.67). With three binary sub-signals A takes effective values in `{0.67, 1.0}` — granularity can be increased by extending the sub-signal set (e.g. volume vs 30-day median, BTC-dominance trend) when those tools become available.
   - `B` *regime distance* — average of three normalised distances from flip boundaries, each capped at 1: RSI(14) distance from the nearer of 30/70 divided by 30; price distance from SMA(200) divided by 5% of price; absolute MACD histogram divided by 0.5% of price (a flip-proximity proxy; replaces the cross-timeframe stddev that the CMC TA tool does not return).
   - `C` *event risk* — `1` if no high-impact macro event from `get_upcoming_macro_events` falls inside the trade horizon; otherwise `1 − (horizon_overlap_days / horizon_days)`, floor `0`.
   - `D` *derivatives stress* — `1` if absolute 8h funding rate < 0.02%; linear ramp to `0` at 0.10%; floor `0`.

   Weighted sum: `raw = 35·A + 25·B + 20·C + 20·D` → already `0..100`. Apply caps (lowest wins): cap at `60` if Step 4 surfaces zero failure regimes; cap at `50` if fewer than 2 distinct falsifier signal classes; cap at `40` if the run is `DEGRADED` (≥2 tool fallbacks or any component cannot be computed). Final `confidence = round(min(raw, applicable caps))`. The four component values, the raw sum, and any cap applied are reported alongside the final score.
6. **Guard Rails** — position size (scaled by confidence), stop-loss (from `max_drawdown_pct`), known event risk windows from `get_upcoming_macro_events`, and a re-check trigger (when the Skill should be re-run).
7. **Signal State** — one of `triggered`, `triggered_marginally`, `flat`, `flat_near_trigger`, `flat_by_definition`. Reported alongside the confidence score so a 93/100 number is never read in isolation from whether the strategy is actually firing. `triggered_marginally` fires when the strategy's continuous-comparison trigger condition is met by less than its magnitude floor (see Step 5). `flat_near_trigger` fires when at least one primary condition sits within ~15% (proportional) of its threshold.

## Workflow

### Step 1: Resolve the Token
Always call `search_cryptos` first. If multiple matches, surface them and ask. Record the resolved CMC id for every downstream call.

### Step 2: Detect the Timeframe Regime
> TODO (day 3) — implementation of the Inputs `timeframe` contract: pull daily closes, compute Wilder ATR(14), derive `atr_pct`, rank against the 1-year distribution, return the bucket. Honour the `LIMITED-HISTORY` fallback. Report `atr_pct`, percentile rank, bucket, and sample-size flag.

### Step 3: Build the Signal Stack
> TODO (day 3) — call `get_crypto_technical_analysis` and read SMA/EMA, MACD, RSI, Fibonacci levels, pivots at the chosen timeframe. Cross-check against `get_crypto_marketcap_technical_analysis` (is the broader market trending or chopping?) and `get_global_metrics_latest` (BTC dominance, fear/greed).

### Step 4: Surface the Failure Regimes

The honest core. Given the signal stack from Step 3, surface 3–5 historical windows where a strategy with this same configuration produced a losing trade on this token (or, if same-token history is thin, on a comparable token in a comparable market regime).

**Selection rule.** Each candidate regime gets a `similarity_to_today` score in `0..1` from a published formula. Rank by descending similarity, take the top 5, drop any below 0.10, then apply the diversity constraint.

`similarity = 0.20·S + 0.50·M + 0.30·A`

- `S` — *signal-class match* (0..1). Fraction of the strategy's distinct signal classes (e.g. RSI extreme, MACD cross, SMA reclaim) that triggered inside the candidate regime. **Gate**: if `S = 0` the regime is disqualified outright, regardless of M and A.
- `M` — *macro-regime fit* (0..1). Average of three binary matches:
  - Fear & Greed bucket match: `<25` Extreme Fear / `25–75` Mid / `>75` Extreme Greed.
  - BTC dominance trend match over the candidate window: rising / flat / falling vs today's.
  - Funding rate sign match: positive / near-zero (|rate| < 0.02%) / negative.

  Sum the three 1/0 matches and divide by 3.
- `A` — *asset-specific fit* (0..1). Average of two binary matches:
  - Token rank bucket match: top-10 / top-50 / top-200 / beyond.
  - Volatility regime bucket match using the same scalp/swing/position tercile as the Inputs `timeframe` contract.

Two runs of the Skill against the same signal stack and the same regime corpus must produce identical similarity scores. If any sub-component cannot be computed for a candidate (e.g. historical funding rate unavailable), substitute the neutral value (0.5 for that sub-component) and label the regime entry `similarity_partial`.

**Hard diversity constraint.** The surfaced 3–5 must span at least **two distinct failure modes** (`trend-persistence`, `regulatory-shock`, `leverage-cascade`, `low-volume-noise`, `news-driven-jump`). A list of five regimes all in the same failure mode is rejected as low-signal — re-rank or report fewer.

**Citation taxonomy.** Each surfaced regime must be cited from one of three source types, labelled explicitly:

- `[LIVE]` — drawn directly from a CMC tool call in this run (e.g. percent-change windows from `get_crypto_quotes_latest`, a story from `get_crypto_latest_news`). Highest trust.
- `[CMC-HISTORICAL]` — anchored to a CMC data point that's verifiable by the user (e.g. "BNB price drop from $X to $Y over date range Z, see `get_crypto_quotes_latest` 1y / 3y window"). Medium trust, points the user to where they can check.
- `[TRAINING-DATA]` — narrative context from the model's training data (e.g. "the FTX collapse of Nov 2022"). Lowest trust on its own, must be paired with a `[CMC-HISTORICAL]` or `[LIVE]` anchor in the same regime entry. Never the sole citation source for a regime.

A regime entry that cannot meet the citation rule is dropped, not weakened. The Skill reports `surfaced N of target 3–5` and the report continues with whatever did make the cut.

**Required fields per regime:**

| Field | Description |
|---|---|
| `id` | Short slug (e.g. `bnb-2023-06-sec-charges`) |
| `date_range` | YYYY-MM-DD → YYYY-MM-DD |
| `failure_mode` | One of: `trend-persistence`, `regulatory-shock`, `leverage-cascade`, `low-volume-noise`, `news-driven-jump` |
| `what_broke` | One sentence on why the strategy lost money |
| `citations` | Array of `{type: LIVE / CMC-HISTORICAL / TRAINING-DATA, source, claim}` — at least one non-`TRAINING-DATA` entry required |
| `similarity_to_today` | 0–1 score from the selection rule. Above 0.7 = "watch closely"; this regime is materially relevant *now* |
| `distinguishing_data_point` | The one number from today's data that would tell the user whether we are or are not in this regime now (e.g. "RSI(14) was 72 like today, but derivatives funding was +0.08% vs today's −0.02%") |

**Honesty rule.** If today's signal stack is in a *no-signal* state (strategy is flat right now), Step 4 still runs — but the framing changes to: "if the strategy were to fire on this token in the next window, here are the regimes the resulting trade would most resemble." Never skip this step on the grounds that there's nothing to invalidate today; the user is asking precisely so they're prepared *when* the signal does fire.

### Step 5: Generate Rules Conditioned on the Failures

For each rule emitted, the Skill must be able to point to the failure regime that would have broken the strategy without that rule. Orphan rules are not allowed.

1. **Identify the dominant failure mode.** Among regimes with `similarity_to_today > 0.5`, pick the failure mode with the highest cumulative similarity score. If no regime exceeds 0.5, mark the dominant mode as `none` and proceed with a base rule set (no failure-specific guard) — but Step 6 caps confidence at 60 in this case, since the absence of a near-similarity failure for a token with history is itself suspicious.

2. **Attach the failure-mode-specific entry guard** per the dominant mode:
   - `regulatory-shock` → entry blocked when a high-impact event from `get_upcoming_macro_events` lies in the next 7 days, OR a quality≥8 enforcement/regulatory headline appears in the last 24h via `get_crypto_latest_news`.
   - `leverage-cascade` → entry blocked when canonical funding rate < −0.02%, OR derivatives `open_interest` is down >20% over 30d AND still falling on the day.
   - `trend-persistence` → entry blocked when SMA(50) slope disagrees with the signal direction (e.g. buying a mean-reversion long into an SMA(50) downtrend).
   - `low-volume-noise` → entry blocked when 24h spot volume is below 30-day median × 0.8. **`unverified` mode**: if the 30-day median is not derivable from the current tool surface (e.g. `get_crypto_quotes_latest` returns only the current 24h volume, not the distribution), the guard runs `unverified` — it neither blocks nor passes entry, and the Report Structure surfaces `low-volume-noise: unverified` explicitly. The trader is informed that this specific failure mode could not be checked.
   - `news-driven-jump` → entry blocked for 24h after any quality≥8 asset-specific news in `get_crypto_latest_news`.

3. **Construct the exit condition.** Trigger on EITHER the strategy's primary signal-reversal (e.g. RSI crossing back above 50 for a mean-reversion long) OR breach of any reversal-condition falsifier from Output Schema #3.

4. **Construct the stop-loss.** Place at the nearest structural level (pivot point or SMA-200, whichever is closer in the direction of risk) but never further than `max_drawdown_pct` from entry. If the structural level is closer than the drawdown cap, use it; if further, use the cap and label the stop `cap-bound`.

5. **Trace every rule.** Each emitted entry guard, exit condition, and stop-loss must carry a one-line `because:` annotation pointing to the failure regime that motivated it. The Report Structure surfaces these traces.

A rule without a `because:` is dropped; the report continues with whichever rules trace cleanly and states explicitly when a rule was dropped and why.

**Magnitude floors for continuous-comparison triggers.** When a strategy's trigger compares a continuous value against a threshold (e.g. `7d change > 0`, `price > SMA(50)`, `F&G < 25`), the rule generator must attach a magnitude floor proportional to the typical noise level of the input. Sub-floor triggers are classified `triggered_marginally` (per Output Schema #7), not `triggered`. Defaults: ≥1% for 7d-change comparisons; ≥0.5% (of price) for price-vs-SMA distance; ≥3 points for Fear & Greed below/above its threshold. Strategies may override these. Without a magnitude floor, the BUY signal would fire on a 0.08% 7d change indistinguishably from a 3.5% 7d change — a difference that materially changes the trade.

### Step 6: Score Confidence

Implements the published formula in Output Schema #5. The formula is the contract; this step is the procedure.

1. **Canonical funding rate source.** Use `get_global_crypto_derivatives_metrics.fundingRate.current` for component `D`. `get_global_metrics_latest.funding_rate.average.current` differs in averaging window and is not used in the confidence formula (it remains valid for narrative context elsewhere).

2. **Compute components in order** so partial failure of a tool degrades only the affected component:
   - `A` (signal consistency) — needs price, SMA(200), MACD line, and pivot point from Step 3. Sign each sub-signal (bull/bear), count unanimity, divide by 3.
   - `B` (regime distance) — needs RSI(14), price, SMA(200), and MACD histogram (from Step 3). MACD-flip term is `|histogram| / (0.005 × price)`, capped at 1.
   - `C` (event risk) — needs `get_upcoming_macro_events` filtered to high-impact and the trade horizon.
   - `D` (derivatives stress) — needs the canonical funding rate above.

3. **Cast strings to numbers.** All TA fields return as strings. Cast at the boundary of every component computation, not inline.

4. **Apply caps in order, lowest wins.** Compute every applicable cap independently; the final confidence is `round(min(raw_sum, caps[]))`.

5. **Emit the full breakdown.** The report includes: `{A, B, C, D, raw, applied_cap, final_confidence}`. Do not hide which cap (if any) bound the score — that disclosure is part of the honest contract.

6. **Degraded-mode handling.** If `D` cannot be computed (derivatives tool failure), drop the `D` term and renormalize: `raw_renorm = (35·A + 25·B + 20·C) × (100/80)`. Apply the `DEGRADED` cap of 40 from Output Schema #5.

### Step 7: Emit Guard Rails

The final block of the report. All four sub-blocks must appear; partial failure is reported explicitly, not hidden.

1. **Position size.** `position_size_pct = position_cap_pct × (final_confidence / 100)`. Round to one decimal place. Floor at 0.5% — if scaled size rounds below 0.5%, emit `do_not_size` and explain (the strategy may be informative but not actionable at this confidence).

2. **Stop-loss.** Use the stop computed in Step 5 (structural level capped by `max_drawdown_pct`). Report both the price and the basis, e.g. `stop: $562 — SMA(200) at 1d, capped by 6% drawdown rule`.

3. **Event windows to avoid.** List every high-impact event from `get_upcoming_macro_events` that intersects the trade horizon, each with its date and the recommended action: `reduce_size`, `flat_until_after`, or `re_check`.

4. **Re-check trigger.** State the conditions that should cause the user (or an agent running the Skill on a schedule) to re-run the Skill before the trade exits naturally:
   - `final_confidence` would change by ±15 if recomputed (proxy: any one of A/B/C/D changes by >0.30).
   - Any reversal-condition falsifier from Output Schema #3 is breached.
   - A new high-impact macro event lands inside the active trade window.
   - A quality≥8 news item touching the asset appears in `get_crypto_latest_news`.

Re-check triggers are advisory — the Skill states them, the user (or scheduler) acts on them.

## Analysis Framework

### Signal Cleanliness
Agreement of trend, momentum, and structure across the three timeframes inside the detected regime bucket. Disagreement is not failure — it is reported and it drags confidence down.

### Regime Fit
Is the broader market in the same regime as the token? A trend signal on a single coin during a market chop window is a documented failure mode (see Step 4 output).

### Event Risk
Macro events (`get_upcoming_macro_events`) and protocol events (news, unlocks via `get_crypto_metrics`) that fall inside the trade horizon. These do not block the trade — they shrink position size.

### Counterfactual Stress
Every rule is paired with a falsifier from Step 4. If the falsifier list is shorter than 2 distinct signal classes, confidence is capped at 50.

## Report Structure

```markdown
# Honest read: {SYMBOL} ({timeframe_bucket})

## Thesis
{one sentence}

## Rules
- Entry: ...
- Take profit: ...
- Stop: ...

## What would prove this wrong
1. {falsifier 1 — price-based}
2. {falsifier 2 — flow-based}
(...)

## Where this rule has lost before
1. {YYYY-MM-DD → YYYY-MM-DD} — {what broke} — {CMC data citation}
(...)

## Confidence: {0-100}
Breakdown: timeframe agreement {n}, regime distance {n}, event risk {n}, derivatives stress {n}

## Guard rails
- Position size: {n}% of allocation
- Stop-loss: {price} ({basis})
- Event windows to avoid: {list}
- Re-check trigger: {condition}

## Sources
- {tool call} → {what it told us}
(...)
```

## Handling Tool Failures

Deliver partial over nothing. Per-tool fallback policy:

- `search_cryptos` failure → ask the user to provide a CMC id directly; do not guess.
- `get_crypto_technical_analysis` failure → fall back to `get_crypto_quotes_latest` percent-change windows; flag that the technical block is degraded; cap confidence at 40.
- `get_crypto_latest_news` failure → still produce the report; Step 4 fail-case citations must then come from on-chain / market metrics only and the report says so.
- `get_global_crypto_derivatives_metrics` failure → drop derivatives-stress term from the confidence formula; reweight the remaining terms and disclose the reweighting.
- `get_upcoming_macro_events` failure → emit the report with an "event risk: unknown — manual check required" line in the guard rails.

A run that has fallen back on two or more tools must label itself **DEGRADED** in the header.

## Important Notes

- This Skill produces strategy specs, not financial advice. Every output is meant to be backtestable and auditable, not blindly executed.
- The differentiator is epistemic: a run that cannot honestly fill every section says so explicitly and refuses to inflate confidence.
- Surface positive and negative findings with equal weight. A strong signal with no surfaced failure regimes is itself a red flag — the Skill should refuse to score above 60 in that case.
- For very new tokens or thin order books, some metrics will be missing — say so and cap confidence accordingly.
- **Sentiment-divergence and other Fear & Greed-driven strategies depend on a single externally-aggregated value.** If the upstream source has drift or calibration issues, *every* sentiment-divergence Skill run is affected simultaneously. Before deploying a sentiment-divergence trade with real capital, cross-reference the F&G value against an independent source (e.g. alternative.me Fear & Greed Index) and treat the Skill's output as suspect if the two disagree by more than 10 points.
- A single matrix run may surface a finding that no individual cell could: e.g. the day-7 3×3 backtest showed that across three tokens and three strategies, confidence numbers cluster by token (all BNB cells 93, all BTC cells 78, all ETH cells 78), meaning the macro signal stack dominates the strategy choice in the current regime. Read the Skill's output as a regime-aware filter, not a universal verdict on any one strategy.
