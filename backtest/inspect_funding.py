"""Daily funding around the May 2022 LUNA entry to see if guard fired late."""
import pandas as pd
from binance_fetch import daily_funding, fetch_funding

df = fetch_funding("BNBUSDT")
daily = daily_funding(df)
daily.index = daily.index.normalize().tz_localize(None)

print("BNBUSDT daily-mean funding, May 5-16 2022 (LUNA window):")
print()
window = daily.loc["2022-05-05":"2022-05-16"]
for date, rate in window.items():
    flag = "  <-- BLOCKED by funding guard" if rate < -0.0002 else ""
    entry_flag = "  <== RSI<30 entry triggered here" if date.strftime("%Y-%m-%d") == "2022-05-09" else ""
    print(f"  {date.strftime('%Y-%m-%d')}: {rate:+.6f}{flag}{entry_flag}")
