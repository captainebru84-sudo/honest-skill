# Data pull verification — BNB, 2026-06-12

End-to-end exercise of every tool the Skill declares in `allowed-tools`, run in parallel against `id=1839` (BNB).

**Verdict: all 10 tools returned in parallel, no rate-limit / auth / timeout issues.** Pipes work. Several real gotchas surfaced that day 4–5 must handle, captured below.

## Resolved token

```json
{"id": 1839, "name": "BNB", "symbol": "BNB", "slug": "bnb", "rank": 4}
```

`search_cryptos("BNB", limit=3)` returns a single match — the ambiguity branch of Step 1 of the workflow does not fire for this symbol. Worth re-testing with a known-ambiguous symbol (e.g. `LUNA`, `SOL` historically) before locking the contract.

## Snapshot of what came back

| Tool | Status | Key fields |
|---|---|---|
| `search_cryptos` | ok | 1 match (above) |
| `get_crypto_quotes_latest` | ok | price 598.00, mcap 80.6B, rank 4, dominance 3.73%, 24h vol 1.07B; pct-change windows 1h/24h/7d/30d/60d/90d/1y/ytd present |
| `get_crypto_technical_analysis` | ok | SMA 7/30/200 = 590.85 / 641.70 / 719.56 (death-cross stack); EMA 7/30/200 = 601.45 / 629.20 / 695.99; MACD line −15.70, signal −10.01, hist −5.69 (bearish, widening); RSI 7/14/21 = 45.6 / 44.1 / 44.9; Fib swing 743.36 → 558.39; pivot 598.85 |
| `get_crypto_metrics` | **degraded** | only `definitions` present; `coinMarketCapCryptoTotalHolderData` is empty `{}` — see gotcha 1 |
| `get_crypto_latest_news` | ok | 5 rows; quality scores 7.0–9.0; mixed relevance (3/5 are macro stories that only mention BNB in passing) — see gotcha 4 |
| `get_crypto_marketcap_technical_analysis` | ok | total mcap 2.16 T at pivot 2.16 T; RSI(7) 62.18 vs RSI(14) 25.86 vs RSI(21) 27.32 — see gotcha 5 |
| `get_global_metrics_latest` | ok | Fear & Greed 17 (Extreme Fear); BTC dom 58.44%; altcoin season 47; OI 30d −21%; funding avg −0.00081991% |
| `get_global_crypto_derivatives_metrics` | ok | OI 369.64 B; funding rate 0.00033885%; BTC liquidations 24h 63.32M |
| `get_upcoming_macro_events` | ok | 15 events; **FOMC Jun 16–17 + Fed decision Jun 17 are 4–5 days out** — see gotcha 6 |
| `search_crypto_info` | ok | 2 BNB Chain fundamentals articles for the Fundamentals section |

## Honest-read first draft (manual, against the locked schema)

> Not the Skill output — this is a paper exercise to test whether the locked schema actually produces a coherent report from real data.

**Thesis (manual):** Bias short / flat on swing horizon. Price 598 sits ~17% below SMA(200) 720, MACD bearish and widening, RSI neutral-bearish at 44, market sentiment Extreme Fear (17/100), OI deleveraging.

**Reversal conditions (manual):**
1. Price-based: daily close above EMA(30) 629.20 with MACD histogram turning positive.
2. Flow-based: BTC dominance breaks below 57% AND Fear & Greed reads neutral (≥40) for 3 consecutive days.

**Event risk:** FOMC Jun 16–17 is inside the trade window — should drag component `C` of the confidence formula below 1.0 for any horizon ≥ 4 days.

The schema produces a coherent narrative from real data — encouraging.

## Gotchas (must address day 4–5)

### 1. `get_crypto_metrics` returns no holder data for BNB
The response carries only the `definitions` block; `coinMarketCapCryptoTotalHolderData` is an empty object. Holder distribution (whales/cruisers/traders) is one of the sources the Skill leans on for guard-rail and confidence work. **Action day 4:** test the same tool against BTC (id=1) and ETH (id=1027). If it works there, the Skill must label BNB-class assets as "holder-data unavailable" and degrade the relevant confidence/guard-rail components rather than fabricate. If it fails on BTC/ETH too, the tool may need a different parameter or a tier we don't have — escalate.

### 2. TA numeric fields come back as strings
Every value under `moving_averages`, `macd`, `rsi`, `fibonacciLevels`, and `pivotPoint` is a string (`"590.85"`, not `590.85`). The published confidence formula in SKILL.md does arithmetic on these. **Action day 5:** define a clean cast layer at the boundary of every TA tool call. Document in Step 3 of the workflow.

### 3. Funding-rate source ambiguity
`get_global_metrics_latest` reports `funding_rate.average.current = −0.00081991%`. `get_global_crypto_derivatives_metrics` reports `fundingRate.current = 0.00033885%`. They have opposite signs at the same minute. Neither tool labels its window as 8h. The published confidence formula references "absolute 8h funding rate" with thresholds at 0.02% and 0.10%. **Action day 5:** pin which source is canonical for component `D`. Likely the derivatives endpoint, since `global_metrics` averages across more instruments. Note in Step 6.

### 4. News results include off-topic macro
3 of 5 news rows are stories about Iran tensions / BTC / market rally that mention BNB only in passing. The Skill's Step 4 (failure regimes) and Step 6 (event risk) both consume news. **Action day 4:** add a relevance filter — minimum quality score and/or symbol-match in title/description before counting toward fail-case citations.

### 5. Marketcap RSI divergence
RSI(7) 62.18 vs RSI(14) 25.86 vs RSI(21) 27.32 on total crypto mcap. RSI(7) above RSI(14) by 36 points is an extreme reading — suggests a sharp rebound off a multi-week oversold low. The Skill should *flag* this as a regime-fragility signal rather than treat it as cleanliness. **Action day 5:** when scoring component `B` for a single coin, cross-reference market RSI divergence — if the market just bounced from oversold, single-coin trend signals are less reliable.

### 6. Imminent FOMC inside any swing horizon
FOMC Jun 16–17 and the Fed interest-rate decision Jun 17 both fall 4–5 days out from today. Any `swing` horizon (typically 1–3 weeks) starts with an event window overlap. **No action needed in code** — the formula handles it correctly via component `C`. **Action for the demo:** this makes BNB a *good* example token to demo on, because the Skill will properly shrink position size based on the impending Fed decision without being told.

## Parallel-call verification

All 10 calls were issued in a single batch and all returned. No exponential backoff, no auth challenge, no truncated response. The MCP server handled the burst cleanly.

## Sample-size flag (for the `LIMITED-HISTORY` fallback)

BNB was added 2017-07-25 → 8.9 years of daily history available. Well above the 252-day threshold; not a fallback case. Need a different token (a recent listing) to verify the `LIMITED-HISTORY` path in a future run.

## What's locked in after this verification

- Pipes work. 10 tools, parallel batch, real shapes captured.
- Schema produces a coherent narrative from real data.
- Six concrete gotchas surfaced for day 4–5, all fixable inside the existing schema.
- BNB-on-2026-06-12 is a useful demo token: bearish-but-not-broken regime, Extreme Fear backdrop, FOMC in 4 days, price right at pivot.
