import sys, itertools, numpy as np, pandas as pd, lib
pd.set_option("display.width", 260); pd.set_option("display.max_rows", 200)
IS = ("2020-03-01", "2024-01-01"); OOS = ("2024-01-01", None)
_cache = {}
def prep(sym, itv, htf):
    k = (sym, itv, htf)
    if k in _cache: return _cache[k]
    df = lib.load(sym, itv); f = lib.features(df)
    hd = lib.load(sym, htf); hf = lib.features(hd)
    g = lambda a: lib.htf_feature(df.index, hd, np.asarray(a, float))
    f["h_up"] = g(hd.close.to_numpy() > hf["e50"]) > 0.5
    f["h_dn"] = g(hd.close.to_numpy() < hf["e50"]) > 0.5
    f["h_mf"] = g(hf["mf"])
    _cache[k] = (df, f); return df, f
def rules(df, f, lvl=53, need_mf=False, exit_mode="dot", shorts=True, trend=True):
    up, dn, wt2, mf = f["up"], f["dn"], f["wt2"], f["mf"]
    le = up & (wt2 <= -lvl); se = dn & (wt2 >= lvl)
    if trend: le &= f["h_up"]; se &= f["h_dn"]
    if need_mf: le &= mf > 0; se &= mf < 0
    if exit_mode == "dot":      lx = dn & (wt2 >= lvl); sx = up & (wt2 <= -lvl)
    elif exit_mode == "cross0": lx = dn & (wt2 > 0);    sx = up & (wt2 < 0)
    elif exit_mode == "any":    lx = dn.copy();         sx = up.copy()
    else:                       lx = np.zeros(len(up), bool); sx = lx.copy()
    if trend: lx = lx | ~f["h_up"]; sx = sx | ~f["h_dn"]
    return le, lx, (se if shorts else None), (sx if shorts else None)
def run(sym, itv, htf, period, stop=None, tp=None, trail=None, **kw):
    df, f = prep(sym, itv, htf)
    le, lx, se, sx = rules(df, f, **kw)
    st, tr = lib.backtest(df, le, lx, se, sx, stop_atr=stop, tp_atr=tp, trail_atr=trail, atr_arr=f["atr"], start=period[0], end=period[1])
    return st
if __name__ == "__main__":
    itv, htf = sys.argv[1], sys.argv[2]
    syms = sys.argv[3].split(",")
    grid = list(itertools.product([53, 40], [False, True], ["dot", "cross0", "any", "none"], [None, 2.0, 3.0], [None, 3.0], [True, False]))
    rows = []
    for lvl, need_mf, ex, stop, trail, shorts in grid:
        if ex == "none" and trail is None: continue
        r = {"lvl": lvl, "mf": need_mf, "exit": ex, "stop": stop, "trail": trail, "shorts": shorts}
        for tag, per in (("IS", IS), ("OOS", OOS)):
            ss = [run(s, itv, htf, per, stop=stop, trail=trail, lvl=lvl, need_mf=need_mf, exit_mode=ex, shorts=shorts) for s in syms]
            r[f"{tag} n"] = sum(x["trades"] for x in ss)
            r[f"{tag} pf"] = np.mean([min(x["pf"], 9) for x in ss])
            r[f"{tag} cagr"] = np.mean([x["cagr%"] for x in ss])
            r[f"{tag} dd"] = np.mean([x["maxdd%"] for x in ss])
            r[f"{tag} win"] = np.mean([x["win%"] for x in ss])
            r[f"{tag} expo"] = np.mean([x["expo%"] for x in ss])
        rows.append(r)
    t = pd.DataFrame(rows)
    t["IS calmar"] = t["IS cagr"] / t["IS dd"].abs()
    t = t.sort_values("IS calmar", ascending=False)
    print(f"{itv}/{htf} {syms}: top 14 by IN-SAMPLE Calmar (parameters chosen without looking at OOS)")
    print(t.head(14).round(2).to_string(index=False))
    print("\nbottom 4:"); print(t.tail(4).round(2).to_string(index=False))
    print("\nOOS profit factor > 1 in %.0f%% of %d configs; median OOS PF %.2f, median OOS CAGR %.1f%%" % (100 * (t["OOS pf"] > 1).mean(), len(t), t["OOS pf"].median(), t["OOS cagr"].median()))
    for s in syms:
        a = run(s, itv, htf, IS, exit_mode="none", trail=None, shorts=False, trend=False)
        b = run(s, itv, htf, OOS, exit_mode="none", trail=None, shorts=False, trend=False)
        print(f"buy&hold {s}: IS {a['bh%']:.0f}% (dd {a['bh_dd%']:.0f}%)  OOS {b['bh%']:.0f}% (dd {b['bh_dd%']:.0f}%)")
