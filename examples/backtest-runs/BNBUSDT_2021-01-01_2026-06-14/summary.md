# Honest-Skill backtest run

ticker:           BNBUSDT
window:           2021-01-01 -> 2026-06-14
bars:             1991
funding symbol:   BNBUSDT
strategy:         RSI(14) cross-below 30.0 -> long, exit on cross-above 50.0 or -15.0% stop

guard=none:
  trades:        15
  entries blocked: 0
  win_rate:      66.7%
  avg_return:    6.41%
  total (compounded): 98.39%
  max_drawdown:  -31.23%
  avg_hold_days: 9.5
  worst_trade:   -15.00%
  best_trade:    64.34%

guard=proxy:
  trades:        8
  entries blocked: 10
  win_rate:      62.5%
  avg_return:    2.77%
  total (compounded): 14.53%
  max_drawdown:  -15.00%
  avg_hold_days: 8.8
  worst_trade:   -15.00%
  best_trade:    21.69%

guard=funding:
  trades:        13
  entries blocked: 2
  win_rate:      76.9%
  avg_return:    9.71%
  total (compounded): 174.59%
  max_drawdown:  -19.09%
  avg_hold_days: 10.8
  worst_trade:   -15.00%
  best_trade:    64.34%

guard=full:
  trades:        7
  entries blocked: 11
  win_rate:      71.4%
  avg_return:    5.30%
  total (compounded): 34.74%
  max_drawdown:  -15.00%
  avg_hold_days: 9.9
  worst_trade:   -15.00%
  best_trade:    21.69%
