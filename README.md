# honest-skill

> A CMC Skill that argues against itself — every strategy ships with the conditions that reverse it.

A submission to **BNB Hack: AI Trading Agent Edition**, Track 2 (Strategy Skills). The Skill produces a backtestable strategy for a token alongside the conditions under which it reverses, 3–5 historical regimes where the same rule lost money (cited from CoinMarketCap data), a confidence score derived from signal cleanliness, and guard rails tuned to those failure modes.

## The skill

→ [`skills/honest-skill/SKILL.md`](skills/honest-skill/SKILL.md)

## Backtest harness

The Skill's claims are backtestable, and we mean it. `backtest/backtest.py` runs the Step-5 strategy on real daily candles and reports four guard modes side by side.

Headline run on **BNB-USD, 2021-01-01 → 2026-06-14** (16 vanilla entry signals over 5.4 years):

| Guard | Trades | Win rate | Compounded P&L | Max drawdown |
|---|---|---|---|---|
| `none` (vanilla RSI) | 16 | 68.8% | +107.83% | −31.18% |
| `proxy` (30d-return) | 9 | 66.7% | +20.52% | −15.00% |
| **`funding` (real Binance)** | **14** | **78.6%** | **+187.66%** | **−19.04%** |
| `full` (funding OR proxy) | 8 | 75.0% | +41.79% | −15.00% |

The real Binance funding-rate guard (`/fapi/v1/fundingRate`, 6,336 events back to 2020-09) is the only mode that beats vanilla on both axes: +80pp compounded return, +12pp drawdown reduction.

Honest tradeoffs the harness surfaces:
- The guard caught the **May 2021 crash** and **June 2022 3AC contagion** entries.
- The guard was **one day late** on the **May 2022 LUNA-week** entry — funding hadn't cascaded yet on the trigger day.
- The guard correctly did **NOT** fire on the **June 2023 SEC-charges** entry — that's `regulatory-shock`, not `leverage-cascade`. Two failure modes need two guards.

Trade-level findings at [`examples/backtest-runs/BNB-USD_2021-01-01_2026-06-14/findings.md`](examples/backtest-runs/BNB-USD_2021-01-01_2026-06-14/findings.md), full caveats at [`backtest/README.md`](backtest/README.md).

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
