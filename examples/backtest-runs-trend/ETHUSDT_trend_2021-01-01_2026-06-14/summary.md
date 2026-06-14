# Honest-Skill backtest run

ticker:           ETHUSDT
strategy:         trend — price>SMA(200) AND MACD>0 -> long, exit when either breaks or -15.0% stop
window:           2021-01-01 -> 2026-06-14
bars:             1991
funding symbol:   ETHUSDT
funding threshold: fixed -0.0200%

guard=none:
  trades:        23
  entries blocked: 0
  win_rate:      34.8%
  avg_return:    4.69%
  total (compounded): 109.41%
  max_drawdown:  -24.26%
  avg_hold_days: 25.2
  worst_trade:   -15.00%
  best_trade:    65.03%

guard=proxy:
  trades:        23
  entries blocked: 0
  win_rate:      34.8%
  avg_return:    4.69%
  total (compounded): 109.41%
  max_drawdown:  -24.26%
  avg_hold_days: 25.2
  worst_trade:   -15.00%
  best_trade:    65.03%

guard=funding:
  trades:        23
  entries blocked: 0
  win_rate:      34.8%
  avg_return:    4.69%
  total (compounded): 109.41%
  max_drawdown:  -24.26%
  avg_hold_days: 25.2
  worst_trade:   -15.00%
  best_trade:    65.03%

guard=full:
  trades:        23
  entries blocked: 0
  win_rate:      34.8%
  avg_return:    4.69%
  total (compounded): 109.41%
  max_drawdown:  -24.26%
  avg_hold_days: 25.2
  worst_trade:   -15.00%
  best_trade:    65.03%
