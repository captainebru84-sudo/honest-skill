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
| `timeframe` | auto-detected | The Skill picks `scalp` / `swing` / `position` from realised volatility (ATR over the last 30 daily candles relative to its 1-year distribution). Detection logic and the chosen bucket are reported in the output so the user can override. |
| `max_drawdown_pct` | numeric, default `15` | Hard cap on per-trade loss. Drives the stop-loss placement in the guard-rail block. |
| `position_cap_pct` | numeric, default `5` | Maximum portfolio weight. Scaled down further by the confidence score. |

## Output Schema

Every run produces the following structured block. Sections are non-negotiable — a run that cannot fill a section says so explicitly rather than dropping it.

1. **Thesis** — one-sentence directional bias (long / short / flat) with the primary signal.
2. **Entry & Exit Rules** — precise, backtestable conditions. Levels quoted in price; indicators named with parameter (e.g. `SMA(200, 1d)`).
3. **Reversal Conditions (the falsifiers)** — the conditions that, if met, invalidate the thesis. At least two independent signals (price-based + flow-based). This is the honest core.
4. **Cited Failure Regimes** — 3–5 historical periods where this same rule would have lost money, each with: date range, what triggered the failure, the CMC data point that flags it (link to the metric, not just the claim).
5. **Confidence Score (0–100)** — derived from signal cleanliness: agreement across timeframes, distance from regime boundaries, news/event noise, derivatives stress. The formula is published, not hand-waved.
6. **Guard Rails** — position size (scaled by confidence), stop-loss (from `max_drawdown_pct`), known event risk windows from `get_upcoming_macro_events`, and a re-check trigger (when the Skill should be re-run).

## Workflow

### Step 1: Resolve the Token
Always call `search_cryptos` first. If multiple matches, surface them and ask. Record the resolved CMC id for every downstream call.

### Step 2: Detect the Timeframe Regime
> TODO (day 3) — pull recent quotes + percent-change windows, compute realised vol, classify into scalp/swing/position. Report the bucket and the input numbers.

### Step 3: Build the Signal Stack
> TODO (day 3) — call `get_crypto_technical_analysis` and read SMA/EMA, MACD, RSI, Fibonacci levels, pivots at the chosen timeframe. Cross-check against `get_crypto_marketcap_technical_analysis` (is the broader market trending or chopping?) and `get_global_metrics_latest` (BTC dominance, fear/greed).

### Step 4: Surface the Failure Regimes
> TODO (day 4) — the honest core. Given the signal stack, find 3–5 past windows where the same configuration produced a losing trade. Cite the CMC data point that distinguishes them from now (e.g. "RSI(14) was 72 like today, but derivatives funding was +0.08% vs today's -0.02% — see [funding chart]").

### Step 5: Generate Rules Conditioned on the Failures
> TODO (day 5) — write the entry/exit rules so they explicitly avoid the failure regimes surfaced in Step 4. Every rule traces back to a falsifier from Step 4.

### Step 6: Score Confidence
> TODO (day 5) — combine: timeframe agreement (3 points each, max 9), distance from regime boundary (0–10), event-window proximity (`get_upcoming_macro_events`, penalty −20 if a major event lies inside the trade horizon), derivatives stress (`get_global_crypto_derivatives_metrics`, penalty −15 if funding extreme). Document the formula in the output.

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
