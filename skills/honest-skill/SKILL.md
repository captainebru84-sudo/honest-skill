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
   - `A` *timeframe agreement* — count of agreeing pairs (trend direction × momentum sign) across the three timeframes in the regime bucket, divided by 3.
   - `B` *regime distance* — average of three normalised distances from flip boundaries, each capped at 1: RSI(14) distance from the nearer of 30/70 divided by 30; price distance from SMA(200) divided by 5% of price; MACD histogram distance from zero divided by its 30-day standard deviation.
   - `C` *event risk* — `1` if no high-impact macro event from `get_upcoming_macro_events` falls inside the trade horizon; otherwise `1 − (horizon_overlap_days / horizon_days)`, floor `0`.
   - `D` *derivatives stress* — `1` if absolute 8h funding rate < 0.02%; linear ramp to `0` at 0.10%; floor `0`.

   Weighted sum: `raw = 35·A + 25·B + 20·C + 20·D` → already `0..100`. Apply caps (lowest wins): cap at `60` if Step 4 surfaces zero failure regimes; cap at `50` if fewer than 2 distinct falsifier signal classes; cap at `40` if the run is `DEGRADED` (≥2 tool fallbacks). Final `confidence = round(min(raw, applicable caps))`. The four component values, the raw sum, and any cap applied are reported alongside the final score.
6. **Guard Rails** — position size (scaled by confidence), stop-loss (from `max_drawdown_pct`), known event risk windows from `get_upcoming_macro_events`, and a re-check trigger (when the Skill should be re-run).

## Workflow

### Step 1: Resolve the Token
Always call `search_cryptos` first. If multiple matches, surface them and ask. Record the resolved CMC id for every downstream call.

### Step 2: Detect the Timeframe Regime
> TODO (day 3) — implementation of the Inputs `timeframe` contract: pull daily closes, compute Wilder ATR(14), derive `atr_pct`, rank against the 1-year distribution, return the bucket. Honour the `LIMITED-HISTORY` fallback. Report `atr_pct`, percentile rank, bucket, and sample-size flag.

### Step 3: Build the Signal Stack
> TODO (day 3) — call `get_crypto_technical_analysis` and read SMA/EMA, MACD, RSI, Fibonacci levels, pivots at the chosen timeframe. Cross-check against `get_crypto_marketcap_technical_analysis` (is the broader market trending or chopping?) and `get_global_metrics_latest` (BTC dominance, fear/greed).

### Step 4: Surface the Failure Regimes

The honest core. Given the signal stack from Step 3, surface 3–5 historical windows where a strategy with this same configuration produced a losing trade on this token (or, if same-token history is thin, on a comparable token in a comparable market regime).

**Selection rule.** Rank candidate regimes by similarity to *today's* signal stack along three dimensions and pick the top-N by descending similarity, subject to diversity:

1. **Signal-class match** — the candidate regime triggered the same primary signal type (e.g. RSI(14) oversold; MACD-cross long; SMA-200 reclaim). At least one matching class is required for the regime to qualify.
2. **Macro-regime fit** — broader market state matches today's: Fear & Greed bucket, BTC dominance bucket (rising/flat/falling), funding-rate sign. Weight 50%.
3. **Asset-specific fit** — token rank, token mcap bucket, token volatility bucket from the timeframe contract. Weight 30%.

Hard diversity constraint: the surfaced 3–5 must span at least **two distinct failure modes** (trend-persistence-against-signal, regulatory-shock, leverage-cascade, low-volume-noise, news-driven-jump). A list of five regimes all in the same failure mode is rejected as low-signal — re-rank or report fewer.

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
> TODO (day 5) — write the entry/exit rules so they explicitly avoid the failure regimes surfaced in Step 4. Every rule traces back to a falsifier from Step 4.

### Step 6: Score Confidence
> TODO (day 5) — implementation of the published formula in Output Schema #5. Compute `A`, `B`, `C`, `D`, the weighted sum, and any applicable caps. Emit the four component values, the raw sum, the final score, and the cap reason if any cap fired.

### Step 7: Emit Guard Rails
> TODO (day 5) — position size = `position_cap_pct` × (confidence / 100). Stop-loss derived from `max_drawdown_pct` and the structural level (pivot / SMA-200, whichever is nearer). Re-check trigger fires on: confidence-score change of ±15, breach of a falsifier, or a new macro event entering the trade window.

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
