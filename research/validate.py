import numpy as np, pandas as pd, lib, strategy_grid as strat
pd.set_option("display.width", 250)
cols = ["trades", "win%", "pf", "avg%", "cagr%", "maxdd%", "expo%", "bh%", "bh_dd%"]
def old_rules(df, f, ribbon=True):
    up, dn, wt2 = f["up"], f["dn"], f["wt2"]; bull = f["e5"] > f["e34"]
    le = up & (wt2 <= -53); 
    if ribbon: le &= bull
    lx = (dn & (wt2 >= 53)) | (~bull if ribbon else False)
    return le, lx
rows = []
for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
    for itv, htf in [("4h", "1d"), ("1h", "1d")]:
        try: df, f = strat.prep(sym, itv, htf)
        except FileNotFoundError: continue
        for tag, per in [("IS 2020-23", strat.IS), ("OOS 2024-26", strat.OOS), ("ALL", ("2020-03-01" if sym != "SOLUSDT" else "2020-12-01", None))]:
            if sym == "SOLUSDT" and tag.startswith("IS"): per = ("2020-12-01", "2024-01-01")
            le, lx = old_rules(df, f, True)
            st, _ = lib.backtest(df, le, lx, stop_atr=None, atr_arr=f["atr"], start=per[0], end=per[1]); rows.append({"sym": sym, "tf": itv, "period": tag, "rules": "OLD default (ribbon)", **{k: st[k] for k in cols}})
            le, lx = old_rules(df, f, False)
            st, _ = lib.backtest(df, le, lx, stop_atr=None, atr_arr=f["atr"], start=per[0], end=per[1]); rows.append({"sym": sym, "tf": itv, "period": tag, "rules": "OLD dots only", **{k: st[k] for k in cols}})
            st = strat.run(sym, itv, htf, per, stop=2.0, lvl=40, exit_mode="dot", shorts=False); rows.append({"sym": sym, "tf": itv, "period": tag, "rules": "NEW long-only", **{k: st[k] for k in cols}})
            st = strat.run(sym, itv, htf, per, stop=2.0, lvl=40, exit_mode="dot", shorts=True); rows.append({"sym": sym, "tf": itv, "period": tag, "rules": "NEW long+short", **{k: st[k] for k in cols}})
t = pd.DataFrame(rows)
for itv in ["4h", "1h"]:
    print(f"\n################ chart {itv}, trend from daily; fees 0.1%/side + 0.02% slippage")
    print(t[t.tf == itv].drop(columns="tf").round(2).to_string(index=False))
