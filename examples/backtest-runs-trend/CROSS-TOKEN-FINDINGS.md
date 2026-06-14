# Cross-token findings: trend-following on BNB / BTC / ETH

Three runs of `backtest/backtest.py --strategy trend --guard all`, same window
(2021-01-01 → 2026-06-14), `price > SMA(200) AND MACD line > 0` long-only,
exit when either condition breaks or −15% stop. Daily Binance klines
(`/api/v3/klines`) for prices; Binance USDT-M funding history for the guard
(`/fapi/v1/fundingRate`). Reproducible:

```
python backtest/backtest.py --ticker BNBUSDT --strategy trend --start 2021-01-01 --guard all
python backtest/backtest.py --ticker BTCUSDT --strategy trend --start 2021-01-01 --guard all
python backtest/backtest.py --ticker ETHUSDT --strategy trend --start 2021-01-01 --guard all
```

Sibling to `examples/backtest-runs/CROSS-TOKEN-FINDINGS.md` (RSI mean-reversion).
Together these are the 3×2 leg of the project's original 3×3 commitment;
sentiment-divergence is the remaining strategy.

## Headline matrix

| Token | Guard | Trades | Blocked | Win rate | Compounded P&L | Max DD |
|---|---|---|---|---|---|---|
| **BNB** | none | 33 | 0 | 27.3% | +190.86% | −34.39% |
| BNB | proxy | 33 | 0 | 27.3% | +190.86% | −34.39% |
| **BNB** | **funding** | **31** | **8** | **29.0%** | **+227.10%** | **−27.99%** |
| BNB | full | 31 | 8 | 29.0% | +227.10% | −27.99% |
| **BTC** | none | 23 | 0 | 34.8% | +182.48% | −21.72% |
| BTC | proxy | 23 | 0 | 34.8% | +182.48% | −21.72% |
| **BTC** | **funding** | **23** | **0** | **34.8%** | **+182.48%** | **−21.72%** |
| BTC | full | 23 | 0 | 34.8% | +182.48% | −21.72% |
| **ETH** | none | 23 | 0 | 34.8% | +109.41% | −24.26% |
| ETH | proxy | 23 | 0 | 34.8% | +109.41% | −24.26% |
| **ETH** | **funding** | **23** | **0** | **34.8%** | **+109.41%** | **−24.26%** |
| ETH | full | 23 | 0 | 34.8% | +109.41% | −24.26% |

## The four findings

### 1. Trend-following is positive across all three tokens

Vanilla compounded P&L: BNB **+191%**, BTC **+182%**, ETH **+109%**. No token
broke this strategy. Compared with RSI mean-reversion, where ETH was −56%, the
strategy-token fit is much more forgiving for trend-following — the signal is
directional and only fires when both conditions agree, so it sits out the
losing regimes by construction.

Cost: win rate is low (27%–35%), avg hold is ~3–4 weeks, and a small number of
trend rides supply most of the P&L. BNB's best trade is +131%, ETH's is +65%.
This is a different P&L shape from RSI MR (66.7% win rate on BNB but smaller
magnitudes) and the Honest Skill should label that explicitly in the report:
"high-strike, low-frequency" vs. "low-strike, high-frequency."

### 2. The funding guard fires only on BNB — and only on this strategy

Eight blocks on BNB, zero on BTC, zero on ETH. The fixed −0.02% threshold
remains BNB-calibrated, as found in the RSI MR run. The trend-strategy gives
the funding guard fewer opportunities to fire (33 entries on BNB vs 15 for
RSI MR over the same window) because trend entries are not concentrated at
the same volatile regime points as RSI<30 crossings. But the guard *does*
still improve BNB results: +191% → +227%, max DD 34% → 28%.

The cross-strategy regularity matters: on BNB, the funding guard helped both
strategies. On BTC/ETH, the guard helped neither. **This is a token-level
signal about funding distributions, not a strategy-level finding.** The Skill
should attach the guard to the token's funding-distribution profile, not to
the strategy.

### 3. The proxy guard is inert on every trend cell

Across all 3 tokens, the 30d-return-cascade proxy blocked zero trend entries.
This is mechanically expected: trend entries require `price > SMA(200) AND
MACD > 0`, which rules out the cascade condition (30d return < −20% AND still
falling) by definition. The two signals are nearly orthogonal: trend says "up
and accelerating," proxy says "down hard and accelerating."

This means on trend strategies, the SKILL.md `funding OR OI` guard reduces to
*just* the funding leg — the OI proxy clause carries no weight. Step 5 of the
spec should call this out: for long-only directional strategies, the
leverage-cascade guard collapses to its derivatives-stress component.

### 4. Trend-following rescues ETH; nothing rescued RSI on ETH

ETH trend: **+109%** vanilla. ETH RSI MR: **−56%** vanilla.

Strategy choice dominated token choice on ETH over this window. This is the
inverse of the RSI MR finding that "no guard can rescue a wrong strategy" —
here, the *right* strategy doesn't need a guard. On ETH, the funding guard is
unhelpful for RSI MR (slightly negative), inert for trend, and the strategy
itself is what makes the difference.

The honest read for the Skill: when the strategy is well-matched to the
token's behavior, guards are confidence-narrowers, not return-rescuers. When
the strategy is *not* well-matched, guards reduce damage but cannot reverse
sign. The Skill should refuse strategies that backtest negative on the target
token at any reasonable confidence level.

## What this adds to the project narrative

| Question | RSI MR (3×1) | Trend (3×1) | Synthesis |
|---|---|---|---|
| Does the strategy work on every token? | No — broken on ETH | Yes, all three | Strategy-token fit dominates |
| Does the funding guard help? | BNB +76pp, BTC 0pp, ETH −6pp | BNB +36pp, BTC 0pp, ETH 0pp | Token-keyed, not strategy-keyed |
| Does the proxy help? | BTC +28pp | Inert everywhere | Strategy-keyed (only fires on contrarian setups) |
| Win rate vs magnitude shape | High-rate, low-mag (66.7% / +6%) | Low-rate, high-mag (27%–35% / +5%) | Different P&L distributions |

The day-7 confidence-score claim (BNB 93 / BTC 78 / ETH 78) is *still* not
the P&L claim. Trend on BTC and ETH score the same on confidence but yield
+182% and +109% respectively. The Skill should treat **confidence** and
**expected P&L distribution** as two separate axes in the output.

## What's still missing

- **Sentiment-divergence backtest.** The third strategy from the day-7 hand
  scoring. Would close the original 3×3 commitment and exercise the
  magnitude-floor guidance from SKILL.md Step 5.
- **Token-aware funding threshold.** Demonstrated as needed in the RSI MR
  Addendum; still v2 work.
- **OI clause.** Same gap as the RSI MR run — needs Coinglass or
  CryptoCompare for multi-year coverage.

## Files

Each per-token run dir contains `trades_none.csv`, `trades_proxy.csv`,
`trades_funding.csv`, `trades_full.csv`, and `summary.md`:

- `examples/backtest-runs-trend/BNBUSDT_trend_2021-01-01_2026-06-14/`
- `examples/backtest-runs-trend/BTCUSDT_trend_2021-01-01_2026-06-14/`
- `examples/backtest-runs-trend/ETHUSDT_trend_2021-01-01_2026-06-14/`
