# Honest-Skill backtest run

ticker:           BNB-USD
window:           2021-01-01 -> 2026-06-14
bars:             1989
funding symbol:   BNBUSDT
strategy:         RSI(14) cross-below 30.0 -> long, exit on cross-above 50.0 or -15.0% stop

guard=none:
  trades:        16
  entries blocked: 0
  win_rate:      68.8%
  avg_return:    6.27%
  total (compounded): 107.83%
  max_drawdown:  -31.18%
  avg_hold_days: 9.4
  worst_trade:   -15.00%
  best_trade:    62.70%

guard=proxy:
  trades:        9
  entries blocked: 10
  win_rate:      66.7%
  avg_return:    3.04%
  total (compounded): 20.52%
  max_drawdown:  -15.00%
  avg_hold_days: 8.7
  worst_trade:   -15.00%
  best_trade:    21.75%

guard=funding:
  trades:        14
  entries blocked: 2
  win_rate:      78.6%
  avg_return:    9.31%
  total (compounded): 187.66%
  max_drawdown:  -19.04%
  avg_hold_days: 10.6
  worst_trade:   -15.00%
  best_trade:    62.70%

guard=full:
  trades:        8
  entries blocked: 11
  win_rate:      75.0%
  avg_return:    5.30%
  total (compounded): 41.79%
  max_drawdown:  -15.00%
  avg_hold_days: 9.6
  worst_trade:   -15.00%
  best_trade:    21.75%
