# honest-skill

> A CMC Skill that argues against itself — every strategy ships with the conditions that reverse it.

A submission to **BNB Hack: AI Trading Agent Edition**, Track 2 (Strategy Skills). The Skill produces a backtestable strategy for a token alongside the conditions under which it reverses, 3–5 historical regimes where the same rule lost money (cited from CoinMarketCap data), a confidence score derived from signal cleanliness, and guard rails tuned to those failure modes.

## The skill

→ [`skills/honest-skill/SKILL.md`](skills/honest-skill/SKILL.md)

## Backtest harness

The Skill's claims are backtestable, and we mean it. `backtest/backtest.py` runs two long-only strategies (RSI mean-reversion and SMA+MACD trend-following) on real Binance daily klines and reports four guard modes side by side. Funding data is pulled live from Binance's public `/fapi/v1/fundingRate` (6,300+ events back to 2020-09 for BNBUSDT).

### Headline cross-token results, 2021-01-01 → 2026-06-14

**Strategy 1: RSI(14) mean-reversion**

| Token | Vanilla P&L | Vanilla DD | Funding-guard P&L | Funding-guard DD | What it means |
|---|---|---|---|---|---|
| **BNB** | +98.39% | −31.23% | **+174.59%** | **−19.09%** | Guard works as advertised: +76pp return, +12pp DD reduction |
| **BTC** | +12.63% | −27.75% | +12.63% | −27.75% | Guard is **inert** — BTC funding never crossed −0.02% threshold in 5.4 years |
| **ETH** | **−56.41%** | −48.72% | −62.87% | −56.32% | Strategy is **broken** on ETH; no guard rescues it |

**Strategy 2: SMA(200) + MACD trend-following**

| Token | Vanilla P&L | Vanilla DD | Funding-guard P&L | Funding-guard DD | What it means |
|---|---|---|---|---|---|
| **BNB** | +190.86% | −34.39% | **+227.10%** | **−27.99%** | Guard helps the same way it does on RSI MR — token-keyed signal |
| **BTC** | +182.48% | −21.72% | +182.48% | −21.72% | Guards inert; strategy carries itself |
| **ETH** | +109.41% | −24.26% | +109.41% | −24.26% | **Same token that broke RSI MR (−56%) makes +109% on trend** |

Three honest findings the harness surfaced that the worked examples did not:

1. **The funding-rate guard fires only on BNB — across both strategies.** Zero entries blocked on BTC or ETH over 5.4 years on either RSI MR or trend-following. That makes it a property of the token's funding distribution, not the strategy. A production Skill needs **token-specific funding thresholds** (e.g. trailing-1y 5th percentile), not the fixed −0.02% from SKILL.md Step 5. *Experiment with `--funding-threshold-mode percentile`: fires on BTC but catches winners; addendum in `CROSS-TOKEN-FINDINGS.md`.*
2. **No guard rescues a wrong strategy.** ETH RSI MR vanilla loses 56%; the best guard only reduces this to −19% (proxy mode). But the same ETH on trend-following makes +109%. **Strategy-token fit dominates guard tuning.** The Skill should refuse strategies that backtest negative on the target token at any non-floor confidence.
3. **The cascade proxy is mechanically inert on trend strategies.** Trend entries require uptrend; cascade requires downtrend. The two signals are orthogonal by construction — so for long-only directional strategies, the SKILL.md `funding OR OI` guard collapses to its funding leg.

Full cross-token writeups:
- RSI MR: [`examples/backtest-runs/CROSS-TOKEN-FINDINGS.md`](examples/backtest-runs/CROSS-TOKEN-FINDINGS.md)
- Trend-following: [`examples/backtest-runs-trend/CROSS-TOKEN-FINDINGS.md`](examples/backtest-runs-trend/CROSS-TOKEN-FINDINGS.md)
- Caveats and methodology: [`backtest/README.md`](backtest/README.md)

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
| 3 | Jun 13 | Wire CMC data pulls end-to-end | done |
| 4 | Jun 14 | Failure-regime surfacing | done |
| 5 | Jun 15 | Rule generation + confidence | done |
| 6 | Jun 16 | Backtest harness (3 tokens × 2 strategies, 24 cells) | done |
| 7 | Jun 17 | Buffer / 3×3 expansion + polish | done |
| 8 | Jun 18 | Demo video + worked examples | done — silent OBS clips + CapCut VO dub |
| 9 | Jun 19 | Submit (soft) | DoraHacks BUIDL updated (description) |
| 10 | Jun 20 | Slack day | done — video uploaded ([YouTube](https://youtu.be/roVjHS5_XmE)), BUIDL video field live, pre-deadline sanity checks passed |

Hard deadline: **Jun 21 2026 12:00 UTC**.

Days 3–7 were front-loaded into Jun 12; trend-following + demo prep front-loaded into Jun 14. See commit history for the actual day-by-day.

## License

MIT — see [LICENSE](LICENSE).
