# Honest-Skill backtest run

ticker:           BTCUSDT
strategy:         trend — price>SMA(200) AND MACD>0 -> long, exit when either breaks or -15.0% stop
window:           2021-01-01 -> 2026-06-14
bars:             1991
funding symbol:   BTCUSDT
funding threshold: fixed -0.0200%

guard=none:
  trades:        23
  entries blocked: 0
  win_rate:      34.8%
  avg_return:    5.80%
  total (compounded): 182.48%
  max_drawdown:  -21.72%
  avg_hold_days: 29.7
  worst_trade:   -10.61%
  best_trade:    47.45%

guard=proxy:
  trades:        23
  entries blocked: 0
  win_rate:      34.8%
  avg_return:    5.80%
  total (compounded): 182.48%
  max_drawdown:  -21.72%
  avg_hold_days: 29.7
  worst_trade:   -10.61%
  best_trade:    47.45%

guard=funding:
  trades:        23
  entries blocked: 0
  win_rate:      34.8%
  avg_return:    5.80%
  total (compounded): 182.48%
  max_drawdown:  -21.72%
  avg_hold_days: 29.7
  worst_trade:   -10.61%
  best_trade:    47.45%

guard=full:
  trades:        23
  entries blocked: 0
  win_rate:      34.8%
  avg_return:    5.80%
  total (compounded): 182.48%
  max_drawdown:  -21.72%
  avg_hold_days: 29.7
  worst_trade:   -10.61%
  best_trade:    47.45%
