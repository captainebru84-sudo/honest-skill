# Honest-Skill backtest run

ticker:           ETHUSDT
window:           2021-01-01 -> 2026-06-14
bars:             1991
funding symbol:   ETHUSDT
strategy:         RSI(14) cross-below 30.0 -> long, exit on cross-above 50.0 or -15.0% stop

guard=none:
  trades:        13
  entries blocked: 0
  win_rate:      30.8%
  avg_return:    -5.37%
  total (compounded): -56.41%
  max_drawdown:  -48.72%
  avg_hold_days: 13.7
  worst_trade:   -15.00%
  best_trade:    17.39%

guard=proxy:
  trades:        6
  entries blocked: 11
  win_rate:      33.3%
  avg_return:    -2.58%
  total (compounded): -19.32%
  max_drawdown:  -38.59%
  avg_hold_days: 13.7
  worst_trade:   -15.00%
  best_trade:    17.39%

guard=funding:
  trades:        12
  entries blocked: 1
  win_rate:      25.0%
  avg_return:    -7.26%
  total (compounded): -62.87%
  max_drawdown:  -56.32%
  avg_hold_days: 13.1
  worst_trade:   -15.00%
  best_trade:    13.85%

guard=full:
  trades:        5
  entries blocked: 12
  win_rate:      20.0%
  avg_return:    -6.57%
  total (compounded): -31.27%
  max_drawdown:  -38.59%
  avg_hold_days: 12.2
  worst_trade:   -15.00%
  best_trade:    13.85%
