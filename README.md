# honest-skill

> A CMC Skill that argues against itself — every strategy ships with the conditions that reverse it.

A submission to **BNB Hack: AI Trading Agent Edition**, Track 2 (Strategy Skills). The Skill produces a backtestable strategy for a token alongside the conditions under which it reverses, 3–5 historical regimes where the same rule lost money (cited from CoinMarketCap data), a confidence score derived from signal cleanliness, and guard rails tuned to those failure modes.

## The skill

→ [`skills/honest-skill/SKILL.md`](skills/honest-skill/SKILL.md)

## Backtest harness

The Skill's claims are backtestable, and we mean it. `backtest/backtest.py` runs the Step-5 strategy on real Binance daily klines and reports four guard modes side by side. Funding data is pulled live from Binance's public `/fapi/v1/fundingRate` (6,300+ events back to 2020-09 for BNBUSDT).

### Headline cross-token result: RSI(14) mean-reversion, 2021-01-01 → 2026-06-14

| Token | Vanilla P&L | Vanilla DD | Funding-guard P&L | Funding-guard DD | What it means |
|---|---|---|---|---|---|
| **BNB** | +98.39% | −31.23% | **+174.59%** | **−19.09%** | Guard works as advertised: +76pp return, +12pp DD reduction |
| **BTC** | +12.63% | −27.75% | +12.63% | −27.75% | Guard is **inert** — BTC funding never crossed −0.02% threshold in 5.4 years |
| **ETH** | **−56.41%** | −48.72% | −62.87% | −56.32% | Strategy is **broken** on ETH; no guard rescues it |

Three honest findings the harness surfaced that the worked examples did not:

1. **The leverage-cascade guard works only on BNB at the current threshold.** BTC's funding distribution is too tight; ETH's RSI mean-reversion is negative-expectancy regardless. A production Skill needs **token-specific funding thresholds** (e.g. trailing-1y 5th percentile), not the fixed −0.02% from SKILL.md Step 5.
2. **No guard rescues a wrong strategy.** ETH vanilla loses 56% over the window; the best guard only reduces this to −19% (proxy mode). The Skill should refuse to recommend RSI mean-reversion on ETH at any non-floor confidence.
3. **The funding guard is one day late.** On the May 2022 LUNA cascade, BNB funding was above threshold on the entry day (May 9) and only cascaded May 10-12. Documented day-by-day in [`BNBUSDT_2021-01-01_2026-06-14/findings.md`](examples/backtest-runs/BNB-USD_2021-01-01_2026-06-14/findings.md).

Full cross-token writeup: [`examples/backtest-runs/CROSS-TOKEN-FINDINGS.md`](examples/backtest-runs/CROSS-TOKEN-FINDINGS.md).
Caveats and methodology: [`backtest/README.md`](backtest/README.md).

## Install

This is an MCP Skill — drop the folder into any agent that supports CoinMarketCap MCP and trigger it by phrase or `/honest-skill`.

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

## Why "honest"

Most strategy agents converge on one-sided BUY / SELL calls. This one is built so that every claim ships with its falsifier, every rule traces back to a cited prior failure, and the confidence score is a published formula rather than a vibe. The first thing a judge or treasury manager or self-custody user wants to know is *what would change your mind* — this Skill answers that by construction.

## Status

| Day | Date | Milestone | Status |
|---|---|---|---|
| 1 | Jun 11 | Repo + DoraHacks + MCP setup | done |
| 2 | Jun 12 | Lock Skill schema, stub repo | done |
| 3 | Jun 13 | Wire CMC data pulls end-to-end | |
| 4 | Jun 14 | Failure-regime surfacing | |
| 5 | Jun 15 | Rule generation + confidence | |
| 6 | Jun 16 | Backtest harness (3 tokens × 3 strategies) | |
| 7 | Jun 17 | Buffer | |
| 8 | Jun 18 | Demo video + worked examples | |
| 9 | Jun 19 | Submit (soft) | |
| 10 | Jun 20 | Slack day | |

Hard deadline: **Jun 21 2026 12:00 UTC**.

## License

MIT — see [LICENSE](LICENSE).
