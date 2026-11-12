"""Python re-implementation of the 0x9 Wave Suite maths, for research/backtesting.
Mirrors the Pine code: same formulas, signals on bar close, fills on the next bar's open."""
import numpy as np
import pandas as pd

import os
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TF_MS = {"15m": 900_000, "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000}


def load(sym, itv):
    df = pd.read_csv(f"{DATA}/{sym}_{itv}.csv")
    df.index = pd.to_datetime(df.time, unit="ms")
    return df


# ───────────── Pine-accurate building blocks ─────────────
def _recursive(x, n, alpha):
    x = np.asarray(x, float)
    out = np.full(len(x), np.nan)
    valid = np.flatnonzero(~np.isnan(x))
    if len(valid) < n:
        return out
    s = valid[0]
    seed_end = s + n - 1
    if seed_end >= len(x):
        return out
    tmp = x[seed_end:].copy()
    tmp[0] = np.nanmean(x[s:seed_end + 1])
    out[seed_end:] = pd.Series(tmp).ewm(alpha=alpha, adjust=False).mean().to_numpy()
    return out


def ema(x, n):
    return _recursive(x, n, 2.0 / (n + 1))


def rma(x, n):
    return _recursive(x, n, 1.0 / n)


def sma(x, n):
    return pd.Series(np.asarray(x, float)).rolling(n).mean().to_numpy()


def highest(x, n):
    return pd.Series(np.asarray(x, float)).rolling(n).max().to_numpy()


def lowest(x, n):
    return pd.Series(np.asarray(x, float)).rolling(n).min().to_numpy()


def rsi(x, n):
    x = np.asarray(x, float)
    d = np.diff(x, prepend=np.nan)
    up = rma(np.where(d > 0, d, 0.0) + np.where(np.isnan(d), np.nan, 0.0), n)
    dn = rma(np.where(d < 0, -d, 0.0) + np.where(np.isnan(d), np.nan, 0.0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = up / dn
        out = 100.0 - 100.0 / (1.0 + rs)
    out[dn == 0] = 100.0
    return out


def atr(h, l, c, n):
    pc = np.roll(c, 1)
    pc[0] = np.nan
    tr = np.nanmax(np.vstack([h - l, np.abs(h - pc), np.abs(l - pc)]), axis=0)
    return rma(tr, n)


def crossover(a, b):
    a = np.asarray(a, float)
    b = np.broadcast_to(np.asarray(b, float), a.shape)
    pa, pb = np.roll(a, 1), np.roll(b, 1)
    r = (a > b) & (pa <= pb)
    r[0] = False
    return r


def crossunder(a, b):
    a = np.asarray(a, float)
    b = np.broadcast_to(np.asarray(b, float), a.shape)
    pa, pb = np.roll(a, 1), np.roll(b, 1)
    r = (a < b) & (pa >= pb)
    r[0] = False
    return r


def barssince(cond):
    out = np.full(len(cond), np.inf)
    last = -1
    for i, c in enumerate(cond):
        if c:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def pivots(x, left, right, kind):
    """Value of the pivot (confirmed `right` bars later, reported on the confirmation bar) else nan."""
    x = np.asarray(x, float)
    n = len(x)
    out = np.full(n, np.nan)
    w = left + right + 1
    s = pd.Series(x)
    ext = (s.rolling(w).min() if kind == "low" else s.rolling(w).max()).to_numpy()
    c = np.roll(x, right)
    c[:right] = np.nan
    hit = (c == ext) & ~np.isnan(ext)
    out[hit] = c[hit]
    return out


def wavetrend(hlc3, ch=9, avg=12, sig=3):
    esa = ema(hlc3, ch)
    dev = ema(np.abs(hlc3 - esa), ch)
    with np.errstate(divide="ignore", invalid="ignore"):
        ci = np.where(dev == 0, 0.0, (hlc3 - esa) / (0.015 * dev))
    wt1 = ema(ci, avg)
    wt2 = sma(wt1, sig)
    return wt1, wt2


def money_flow(o, h, l, c, length=60, mult=200.0):
    rng = h - l
    with np.errstate(divide="ignore", invalid="ignore"):
        raw = np.where(rng == 0, 0.0, (c - o) / rng * mult)
    return np.clip(sma(raw, length), -100, 100)


def divergences(osc, price_low, price_high, left, right, max_bars, os_lvl, ob_lvl, need_zone=True):
    """Regular + hidden divergences on oscillator pivots vs price at the same bars (as in the Pine code)."""
    n = len(osc)
    pl = pivots(osc, left, right, "low")
    ph = pivots(osc, left, right, "high")
    bull = np.zeros(n, bool)
    bear = np.zeros(n, bool)
    hbull = np.zeros(n, bool)
    hbear = np.zeros(n, bool)
    pw = pp = pb = None
    qw = qp = qb = None
    for i in range(n):
        if not np.isnan(pl[i]):
            cb = i - right
            cp = price_low[cb]
            if pw is not None and cb - pb <= max_bars:
                if pl[i] > pw and cp < pp and (not need_zone or pw <= os_lvl):
                    bull[i] = True
                if pl[i] < pw and cp > pp and pl[i] < 0:
                    hbull[i] = True
            pw, pp, pb = pl[i], cp, cb
        if not np.isnan(ph[i]):
            cb = i - right
            cp = price_high[cb]
            if qw is not None and cb - qb <= max_bars:
                if ph[i] < qw and cp > qp and (not need_zone or qw >= ob_lvl):
                    bear[i] = True
                if ph[i] > qw and cp < qp and ph[i] > 0:
                    hbear[i] = True
            qw, qp, qb = ph[i], cp, cb
    return bull, bear, hbull, hbear, pl, ph


def htf_feature(ltf_index, htf_df, values):
    """Value of the last COMPLETED higher-timeframe bar, aligned to the lower timeframe (no look-ahead)."""
    s = pd.Series(values, index=htf_df.index).shift(1)
    return s.reindex(ltf_index, method="ffill").to_numpy()


def features(df, p=None):
    p = p or {}
    o, h, l, c, v = (df[k].to_numpy(float) for k in ["open", "high", "low", "close", "volume"])
    hlc3 = (h + l + c) / 3.0
    f = {}
    f["wt1"], f["wt2"] = wavetrend(hlc3, p.get("ch", 9), p.get("avg", 12), p.get("sig", 3))
    f["vw"] = f["wt1"] - f["wt2"]
    f["mf"] = money_flow(o, h, l, c, p.get("mf_len", 60))
    f["rsi"] = ema(rsi(c, 14), 3)
    f["rsi_raw"] = rsi(c, 14)
    for n in (5, 11, 34, 50, 200):
        f[f"e{n}"] = ema(c, n)
    f["atr"] = atr(h, l, c, 14)
    f["up"] = crossover(f["wt1"], f["wt2"])
    f["dn"] = crossunder(f["wt1"], f["wt2"])
    macd = ema(c, 12) - ema(c, 26)
    f["macd_h"] = macd - ema(macd, 9)
    r = rsi(c, 14)
    lo, hi = lowest(r, 14), highest(r, 14)
    with np.errstate(divide="ignore", invalid="ignore"):
        st = np.where(hi - lo == 0, 0.0, 100 * (r - lo) / (hi - lo))
    f["k"] = sma(st, 3)
    f["d"] = sma(f["k"], 3)
    return f


# ───────────── Evaluation helpers ─────────────
def forward_stats(df, sig, horizons=(6, 12, 24, 48), side=1):
    """Mean forward return (entry next open) after a signal vs the unconditional mean."""
    o, c = df.open.to_numpy(float), df.close.to_numpy(float)
    n = len(c)
    idx = np.flatnonzero(sig)
    idx = idx[idx + 1 < n]
    row = {"n": len(idx)}
    for hz in horizons:
        ok = idx[idx + hz < n]
        if len(ok) < 5:
            row[f"r{hz}"] = np.nan
            row[f"x{hz}"] = np.nan
            row[f"w{hz}"] = np.nan
            continue
        r = side * (c[ok + hz] / o[ok + 1] - 1.0)
        allr = side * (c[hz + 1:] / o[1:n - hz] - 1.0)
        row[f"r{hz}"] = 100 * r.mean()
        row[f"x{hz}"] = 100 * (r.mean() - allr.mean())      # excess over "any bar"
        row[f"w{hz}"] = 100 * (r > 0).mean()
    return row


def backtest(df, long_entry, long_exit, short_entry=None, short_exit=None, stop_atr=None, tp_atr=None,
             atr_arr=None, trail_atr=None, fee=0.001, slip=0.0002, start=None, end=None, stop_price=None, stop_from_close=True):
    """Bar-close signals, fill at next open. Stops/targets checked intrabar (stop first if both hit).
    Returns dict of stats and the list of trade returns (net of fees+slippage)."""
    o, h, l, c = (df[k].to_numpy(float) for k in ["open", "high", "low", "close"])
    t = df.index
    n = len(c)
    i0 = 0 if start is None else int(np.searchsorted(t, pd.Timestamp(start)))
    i1 = n if end is None else int(np.searchsorted(t, pd.Timestamp(end)))
    cost = fee + slip
    pos = 0
    entry = stop = tp = peak = 0.0
    eq = 1.0
    curve = np.ones(n)
    trades = []
    bars_in = 0
    pending = 0  # 1 = open long next bar, -1 = open short, 2 = close
    for i in range(max(i0, 1), i1):
        # fills at this bar's open from the previous bar's signals
        if pending == 2 and pos != 0:
            r = pos * (o[i] / entry - 1.0) - 2 * cost
            trades.append(r)
            eq *= 1.0 + r
            pos = 0
        elif pending in (1, -1) and pos == 0:
            pos = pending
            entry = o[i]
            a = atr_arr[i - 1] if atr_arr is not None else np.nan
            base = c[i - 1] if stop_from_close else entry
            stop = base - pos * stop_atr * a if stop_atr else np.nan
            if stop_price is not None and not np.isnan(stop_price[i - 1]):
                sp = stop_price[i - 1]
                if (pos == 1 and sp < entry) or (pos == -1 and sp > entry):
                    stop = sp
            tp = base + pos * tp_atr * a if tp_atr else np.nan
            peak = entry
        pending = 0
        if pos != 0:
            bars_in += 1
            exit_px = np.nan
            if pos == 1:
                if not np.isnan(stop) and l[i] <= stop:
                    exit_px = min(o[i], stop)
                elif not np.isnan(tp) and h[i] >= tp:
                    exit_px = max(o[i], tp)
            else:
                if not np.isnan(stop) and h[i] >= stop:
                    exit_px = max(o[i], stop)
                elif not np.isnan(tp) and l[i] <= tp:
                    exit_px = min(o[i], tp)
            if not np.isnan(exit_px):
                r = pos * (exit_px / entry - 1.0) - 2 * cost
                trades.append(r)
                eq *= 1.0 + r
                pos = 0
            elif trail_atr and atr_arr is not None and not np.isnan(atr_arr[i]):
                if pos == 1:
                    peak = max(peak, h[i])
                    ns = peak - trail_atr * atr_arr[i]
                    stop = ns if np.isnan(stop) else max(stop, ns)
                else:
                    peak = min(peak, l[i])
                    ns = peak + trail_atr * atr_arr[i]
                    stop = ns if np.isnan(stop) else min(stop, ns)
        # signals on this bar's close
        if pos == 1 and long_exit[i]:
            pending = 2
        elif pos == -1 and short_exit is not None and short_exit[i]:
            pending = 2
        elif pos == 0:
            if long_entry[i]:
                pending = 1
            elif short_entry is not None and short_entry[i]:
                pending = -1
        curve[i] = eq * (1.0 + (pos * (c[i] / entry - 1.0) - cost if pos != 0 else 0.0))
    curve[:max(i0, 1)] = 1.0
    seg = curve[max(i0, 1):i1]
    years = max((t[i1 - 1] - t[max(i0, 1)]).days / 365.25, 1e-9)
    tr = np.array(trades) if trades else np.array([0.0])
    wins, losses = tr[tr > 0], tr[tr <= 0]
    dd = (seg / np.maximum.accumulate(seg) - 1.0).min() if len(seg) else 0.0
    bh = c[i1 - 1] / o[max(i0, 1)] - 1.0
    bh_curve = c[max(i0, 1):i1] / o[max(i0, 1)]
    bh_dd = (bh_curve / np.maximum.accumulate(bh_curve) - 1.0).min()
    ret = seg[-1] - 1.0 if len(seg) else 0.0
    stats = {
        "trades": len(trades),
        "win%": 100 * len(wins) / max(len(trades), 1),
        "pf": wins.sum() / abs(losses.sum()) if losses.sum() != 0 else np.inf,
        "avg%": 100 * tr.mean(),
        "ret%": 100 * ret,
        "cagr%": 100 * ((1 + ret) ** (1 / years) - 1) if ret > -1 else -100,
        "maxdd%": 100 * dd,
        "expo%": 100 * bars_in / max(i1 - max(i0, 1), 1),
        "bh%": 100 * bh,
        "bh_dd%": 100 * bh_dd,
    }
    stats["calmar"] = stats["cagr%"] / abs(stats["maxdd%"]) if stats["maxdd%"] != 0 else np.nan
    return stats, tr
