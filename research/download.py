import subprocess, json, sys, time, os
import pandas as pd
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(OUT, exist_ok=True)
START = int(pd.Timestamp("2020-01-01", tz="UTC").timestamp() * 1000)
def fetch(sym, itv, start):
    url = f"https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval={itv}&limit=1000&startTime={start}"
    for attempt in range(5):
        r = subprocess.run(["curl", "-sS", "-m", "40", url], capture_output=True, text=True)
        try:
            j = json.loads(r.stdout)
            if isinstance(j, list): return j
        except Exception: pass
        time.sleep(2 * (attempt + 1))
    raise RuntimeError("failed " + url + " " + r.stdout[:200] + r.stderr[:200])
for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
    for itv in ["1d", "4h", "1h", "15m"]:
        path = f"{OUT}/{sym}_{itv}.csv"
        if os.path.exists(path): continue
        rows, start = [], START
        while True:
            j = fetch(sym, itv, start)
            if not j: break
            rows += j
            start = j[-1][0] + 1
            if len(j) < 1000: break
        df = pd.DataFrame(rows).iloc[:, :6]
        df.columns = ["time", "open", "high", "low", "close", "volume"]
        df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
        df = df.drop_duplicates("time").iloc[:-1]  # drop the still-forming candle
        df.to_csv(path, index=False)
        print(sym, itv, len(df), pd.to_datetime(df.time.iloc[0], unit="ms"), pd.to_datetime(df.time.iloc[-1], unit="ms"), flush=True)
