import sys, numpy as np, pandas as pd, lib
pd.set_option("display.width", 250)
IS_END = "2024-01-01"
def prep(sym, itv, htf):
    df = lib.load(sym, itv); f = lib.features(df)
    hd = lib.load(sym, htf); hf = lib.features(hd)
    g = lambda a: lib.htf_feature(df.index, hd, np.asarray(a, float))
    f["h_up50"] = g(hd.close.to_numpy() > hf["e50"]) > 0.5
    f["h_ribbon"] = g(hf["e5"] > hf["e34"]) > 0.5
    f["h_mf"] = g(hf["mf"]); f["h_wt2"] = g(hf["wt2"]); f["h_wt1"] = g(hf["wt1"])
    f["h_wtup"] = g(hf["wt1"] > hf["wt2"]) > 0.5
    f["h_e200"] = g(hd.close.to_numpy() > hf["e200"]) > 0.5
    return df, f
def table(sym, itv, htf, hz):
    df, f = prep(sym, itv, htf)
    up, dn, wt2, mf = f["up"], f["dn"], f["wt2"], f["mf"]
    c = df.close.to_numpy()
    mfr = mf > np.roll(mf, 3)
    base_l = up & (wt2 <= -53); base_s = dn & (wt2 >= 53)
    S = {
      "L green": base_l,
      "L green+HTFup50": base_l & f["h_up50"],
      "L green+HTFribbon": base_l & f["h_ribbon"],
      "L green+HTFup50+MF>0": base_l & f["h_up50"] & (mf > 0),
      "L green+HTFup50+hMF>0": base_l & f["h_up50"] & (f["h_mf"] > 0),
      "L green+HTFup50+>EMA200": base_l & f["h_up50"] & (c > f["e200"]),
      "L green+HTFup50+hWTup": base_l & f["h_up50"] & f["h_wtup"],
      "L up<=-30+HTFup50": up & (wt2 <= -30) & f["h_up50"],
      "L up<0+HTFup50": up & (wt2 < 0) & f["h_up50"],
      "L up<0+HTFup50+hMF>0": up & (wt2 < 0) & f["h_up50"] & (f["h_mf"] > 0),
      "L green+HTFdown50": base_l & ~f["h_up50"],
      "S red": base_s,
      "S red+HTFdown50": base_s & ~f["h_up50"],
      "S red+HTFdown50+MF<0": base_s & ~f["h_up50"] & (mf < 0),
      "S red+HTFdown50+hMF<0": base_s & ~f["h_up50"] & (f["h_mf"] < 0),
      "S dn>0+HTFdown50": dn & (wt2 > 0) & ~f["h_up50"],
      "S red+HTFup50": base_s & f["h_up50"],
    }
    isd = df.index < pd.Timestamp(IS_END)
    rows = []
    for k, s in S.items():
        side = 1 if k.startswith("L") else -1
        a = lib.forward_stats(df[isd], s[isd], horizons=(hz,), side=side)
        b = lib.forward_stats(df[~isd], s[~isd], horizons=(hz,), side=side)
        rows.append({"signal": k, "IS n": a["n"], "IS x": a[f"x{hz}"], "IS win": a[f"w{hz}"], "OOS n": b["n"], "OOS x": b[f"x{hz}"], "OOS win": b[f"w{hz}"]})
    print(f"\n=== {sym} {itv} / HTF {htf} / horizon {hz} bars   IS = 2020–2023, OOS = 2024–Nov 2026   (x = excess % over any bar)")
    print(pd.DataFrame(rows).set_index("signal").round(2).to_string())
for sym in sys.argv[1].split(","):
    for itv, htf, hz in [("1h", "1d", 24), ("4h", "1d", 24), ("15m", "4h", 32)]:
        try: table(sym, itv, htf, hz)
        except FileNotFoundError as e: print("no data yet:", sym, itv)
