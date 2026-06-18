# Demo video script — The Honest Skill

**Target length:** 2:30–3:00 (BNB Hack submission video).
**Tone:** plain, no hype, screen-recording first, voice-over second.
**VO dubbed in CapCut over silent OBS clips; cuts in the video.**

---

## The frame

Other Track 2 entries will demo a confident BUY signal. We open with the
opposite move: an agent that finds the hidden failure in a strategy that
looks great. That contrast is the whole pitch — the narration just lets the
screen do the work.

Two committed meta-moves from the project plan:
1. **Open with a strategy that looks great** and have the Skill surface a
   hidden failure mode. (covered by Acts 1–2 below)
2. **Audit other contestants' likely builds** to prove the Skill is useful
   to the broader hackathon ecosystem, not just our own demo. (Act 4)

Both are non-obvious and judge-facing.

---

## Cold open (0:00 – 0:12)

**On screen:** clean terminal. User types:
```
> Give me a strategy for BNB.
```

A confident, glossy output appears:
- **BUY**: RSI(14) cross below 30 → long
- Win rate (in-sample): 67%
- Compounded P&L (5.4y): +98%
- Confidence: high

Bottom-of-screen text card, 1.5s:
> Most strategy agents stop here.

**VO (0:00 – 0:12):**
> Most trading agents will give you this. A confident signal, a backtest
> number, a confidence score. The thing they don't tell you is what would
> change their mind.

---

## Act 1 — Same prompt, different agent (0:12 – 0:45)

**On screen:** same prompt, but routed through `/honest-skill`:
```
> /honest-skill BNB RSI mean-reversion
```

Output scrolls. We hold on three sections, each ~6–8s:

1. **Counterfactuals** — the conditions that flip the signal.
   *Highlight:* "Reversal: funding rate below −0.02% AND open interest
   falling — block entry."

2. **Cited failure regimes** — 3–5 historical periods where this same rule
   lost money, each with a one-line `distinguishing_data_point`.
   *Highlight:* one row with `[CMC-HISTORICAL]` citation tag visible.

3. **Confidence formula** — the numeric breakdown.
   *Highlight:* `35·A + 25·B + 20·C + 20·D = 92.72 → 93` with a caption:
   "computed, not guessed."

**VO (0:12 – 0:45):**
> The Honest Skill ships the same strategy with three things attached.
> The conditions that reverse it. Three to five historical regimes where
> the same rule lost money, cited from CoinMarketCap. And a confidence
> score that's a published formula, not a vibe. Every rule traces back to
> a prior failure. That's what `because:` means in the output.

---

## Act 2 — The backtest receipts (0:45 – 1:30)

**On screen:** split view, three columns: BNB / BTC / ETH. Top half shows
RSI mean-reversion equity curves; bottom half shows trend-following.

Numbers animate in as VO hits them:

| | BNB | BTC | ETH |
|---|---|---|---|
| RSI MR vanilla | +98% | +13% | **−56%** |
| RSI MR + funding guard | **+175%** | +13% | −63% |
| Trend vanilla | +191% | +182% | +109% |
| Trend + funding guard | **+227%** | +182% | +109% |

Hold 2s on the ETH RSI MR column with **−56% in red**.

**VO (0:45 – 1:30):**
> We backtested this on three tokens and two strategies. Real Binance
> daily klines back to 2021. Real funding-rate history, six thousand
> events. Four guard modes side by side. The Skill's claims are
> backtestable, and we mean it — every cell here is reproducible from
> the repo.
>
> Two cells matter most. RSI mean-reversion on ETH loses fifty-six
> percent over five years. No guard rescues it. That's the Skill telling
> you the strategy is wrong for the token. Trend-following on the same
> ETH makes a hundred and nine percent. Same window, different signal.
> Strategy-token fit is the signal — and the Skill surfaces it before
> you size the position.

---

## Act 3 — Three findings the demo wouldn't have surfaced (1:30 – 2:10)

**On screen:** three cards, ~12s each, plain text. No charts.

> **Finding 1.** The funding-rate guard fires only on BNB. Across
> *both* strategies. Zero entries blocked on BTC or ETH over 5.4 years.
> That's a token-level signal about funding distribution shape — not a
> strategy-level finding.

> **Finding 2.** The price-cascade proxy is mechanically inert on
> trend strategies. Trend entries require uptrend; cascade requires
> downtrend. The two signals are orthogonal by construction.

> **Finding 3.** No guard rescues a wrong strategy. ETH RSI
> mean-reversion is negative-expectancy. The best guard reduces losses
> by 18 points but cannot turn it positive. The Skill refuses to
> recommend strategies that backtest negative.

**VO (1:30 – 2:10):**
> The harness surfaced three things the worked examples didn't.
> First — the funding-rate guard fires only on BNB across *both*
> strategies. That makes it a property of the token's funding
> distribution, not of the strategy. A v2 needs token-specific
> thresholds. Second — the cascade proxy is mechanically inert on trend
> strategies. The two signals are opposite by construction. Third —
> and most important — no guard rescues a wrong strategy. The Honest
> Skill should refuse strategies that backtest negative on the target
> token. That refusal is the product.

---

## Act 4 — Auditing other agents (2:10 – 2:35)

**On screen:** terminal. Paste a representative `momentum-agent` config
(public, single-file, the kind of thing Track 1 contestants are likely
shipping). Pipe it into the Skill in audit mode.

```
> /honest-skill stress-test momentum-agent.yaml
```

Output highlights one regime where the agent's rule cascades, with a
cited CMC failure period and a recommended guard rail. Frame as a
service to the ecosystem.

**VO (2:10 – 2:35):**
> The Skill isn't just for our demo strategies. We point it at
> open-source agents — momentum bots, RSI bots, anything with a
> declarable rule — and it returns the same audit: counterfactuals,
> cited failures, a confidence cap. That's real-world relevance.
> DAO treasuries auditing an analyst's call. Self-custody users
> auditing a Telegram alpha. Track 1 contestants auditing their own
> bots before they ship.

---

## Close (2:35 – 2:55)

**On screen:** the tagline, large, no animation.

> **A CMC Skill that argues against itself.**
> Every strategy ships with the conditions that reverse it.
>
> github.com/captainebru84-sudo/honest-skill
> Built for BNB Hack — Track 2

**VO (2:35 – 2:55):**
> The Honest Skill. Built for BNB Hack Track 2. Every claim ships with
> its falsifier. The repo is reproducible end-to-end — backtest, harness,
> findings, refusals. Thanks for watching.

---

## Production checklist

**Screen recordings to capture (~30 min):**
- [ ] Cold-open glossy output mockup (can be hand-typed JSON if no
  real "confident agent" handy)
- [ ] `/honest-skill BNB RSI mean-reversion` run end-to-end
- [ ] Backtest equity curves rendered from `examples/backtest-runs/`
  and `examples/backtest-runs-trend/` summary CSVs
- [ ] `/honest-skill stress-test momentum-agent.yaml` run

**Pre-recorded asset to make (~20 min):**
- [ ] Side-by-side 3×2 table graphic (numbers from the two
  `CROSS-TOKEN-FINDINGS.md` files)
- [ ] Three findings cards (Act 3) as PNG slides

**Voice-over recording (~15 min):**
- [ ] One take of full VO above, ~165 words total
- [ ] Keep a 0.5s gap between paragraphs for editing

**Edit (~45 min):**
- [ ] Cut to screen recordings on each VO segment
- [ ] Hold longer on the ETH −56% / +109% contrast
- [ ] No music; if any, low instrumental, ducks under VO
- [ ] Captions burned in for accessibility

**Sanity check before upload:**
- [ ] No CMC API key visible in any terminal recording
- [ ] No `.claude/settings.local.json` content visible
- [ ] All numbers in the script match the latest `CROSS-TOKEN-FINDINGS.md`

---

## Numbers used (sourced 2026-06-14, commit `63ca683`)

From `examples/backtest-runs/CROSS-TOKEN-FINDINGS.md`:
- BNB RSI MR vanilla +98.39%, funding-guard +174.59%
- BTC RSI MR vanilla +12.63%, funding-guard +12.63% (inert)
- ETH RSI MR vanilla −56.41%, all guards negative

From `examples/backtest-runs-trend/CROSS-TOKEN-FINDINGS.md`:
- BNB trend vanilla +190.86%, funding-guard +227.10%
- BTC trend vanilla +182.48%, all guards equal (inert)
- ETH trend vanilla +109.41%, all guards equal (inert)

If any number changes before Jun 18, update both this script and the
README headline table in lockstep.
