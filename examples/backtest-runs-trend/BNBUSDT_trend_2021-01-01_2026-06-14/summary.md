# Honest-Skill backtest run

ticker:           BNBUSDT
strategy:         trend — price>SMA(200) AND MACD>0 -> long, exit when either breaks or -15.0% stop
window:           2021-01-01 -> 2026-06-14
bars:             1991
funding symbol:   BNBUSDT
funding threshold: fixed -0.0200%

guard=none:
  trades:        33
  entries blocked: 0
  win_rate:      27.3%
  avg_return:    5.53%
  total (compounded): 190.86%
  max_drawdown:  -34.39%
  avg_hold_days: 22.2
  worst_trade:   -10.71%
  best_trade:    131.03%

guard=proxy:
  trades:        33
  entries blocked: 0
  win_rate:      27.3%
  avg_return:    5.53%
  total (compounded): 190.86%
  max_drawdown:  -34.39%
  avg_hold_days: 22.2
  worst_trade:   -10.71%
  best_trade:    131.03%

guard=funding:
  trades:        31
  entries blocked: 8
  win_rate:      29.0%
  avg_return:    6.25%
  total (compounded): 227.10%
  max_drawdown:  -27.99%
  avg_hold_days: 23.4
  worst_trade:   -10.71%
  best_trade:    131.03%

guard=full:
  trades:        31
  entries blocked: 8
  win_rate:      29.0%
  avg_return:    6.25%
  total (compounded): 227.10%
  max_drawdown:  -27.99%
  avg_hold_days: 23.4
  worst_trade:   -10.71%
  best_trade:    131.03%
