# Honest-Skill backtest run

ticker:           BTCUSDT
window:           2021-01-01 -> 2026-06-14
bars:             1991
funding symbol:   BTCUSDT
strategy:         RSI(14) cross-below 30.0 -> long, exit on cross-above 50.0 or -15.0% stop

guard=none:
  trades:        18
  entries blocked: 0
  win_rate:      61.1%
  avg_return:    1.34%
  total (compounded): 12.63%
  max_drawdown:  -27.75%
  avg_hold_days: 14.0
  worst_trade:   -15.00%
  best_trade:    18.42%

guard=proxy:
  trades:        12
  entries blocked: 6
  win_rate:      66.7%
  avg_return:    3.42%
  total (compounded): 40.35%
  max_drawdown:  -19.72%
  avg_hold_days: 16.1
  worst_trade:   -15.00%
  best_trade:    18.42%

guard=funding:
  trades:        18
  entries blocked: 0
  win_rate:      61.1%
  avg_return:    1.34%
  total (compounded): 12.63%
  max_drawdown:  -27.75%
  avg_hold_days: 14.0
  worst_trade:   -15.00%
  best_trade:    18.42%

guard=full:
  trades:        12
  entries blocked: 6
  win_rate:      66.7%
  avg_return:    3.42%
  total (compounded): 40.35%
  max_drawdown:  -19.72%
  avg_hold_days: 16.1
  worst_trade:   -15.00%
  best_trade:    18.42%
