# 0x9 Wave Suite: TradingView indicators (Pine Script v6)

A set of three confluence indicators plus a backtest strategy. These are original scripts: they are built from public formulas (WaveTrend by LazyBear, EMA, RSI, MFI, Stoch RSI and VWAP), and every signal rule is our own.

> **Not Market Cipher.** Market Cipher is a closed-source, paid product. Its code and tuning are not public, so no outside script can match it exactly, and this suite does not try to copy it. The suite follows the same *kind* of analysis (trend ribbon, momentum waves, intraday levels) with its own rules, which you can tune.

| File | Where it draws | What it is for |
|---|---|---|
| `1-trend-ribbon.pine` | On the price chart | 8-EMA trend ribbon + trend symbols |
| `2-momentum-waves.pine` | Its own pane | Momentum waves, money flow, RSI/Stoch, dots, divergences (the core script) |
| `3-intraday-levels.pine` | On the price chart | Range, daily VWAP, S/R dots (1H and lower, regular candles) |
| `strategies/backtest_strategy.pine` | On the price chart | Trend-aligned `strategy()`: buys wave dips while the higher-timeframe trend is up |

## Install

1. In TradingView, open **Pine Editor**, then **New**, then **Blank indicator**.
2. Paste the contents of one `.pine` file and click **Save**, then **Add to chart**.
3. Repeat for each script. A signal is strongest when the ribbon and the waves agree.

## 1. Trend Ribbon

Ribbon: EMAs 5, 11, 15, 18, 21, 24, 28 and 34 (all editable), with an optional Heikin Ashi source. It is blue/white while EMA 1 is above EMA 8 and grey otherwise. *Constricted* means the ribbon width, (max EMA − min EMA) / close, is below its 20-bar average.

| Symbol | Meaning | Rule |
|---|---|---|
| Yellow diamond | Bull continuation | Bull ribbon + WaveTrend cross up while the slow wave is above 0 |
| Red diamond | Trend weakening | WaveTrend cross down while the ribbon is still bull |
| Red X | Bearish | EMA 1 crosses under EMA 2 while the ribbon is constricted |
| Yellow X | Long squeeze / wick trap | Volume > 2× average, lower wick ≥ 50% of the candle, red close. Shown on 1H+ only |
| Blood diamond (BD) | Strong bearish | Red X + red diamond on the same bar, with a yellow diamond in the last 10 bars |
| Blue triangle | Early reversal warning | EMA 2 crosses EMA 8 against the EMA 8 slope |
| Green dot | Bullish | Blue triangle up in the last 3 bars + an oversold WaveTrend cross up. Shown on 6H+ only |
| ✓ / ✗ diamond | Confirmation | A yellow (✓) or red (✗) diamond 1–3 bars after a green dot |

## 2. Momentum Waves

- **Waves:** `esa = ema(hlc3, 9)`, `d = ema(|hlc3 − esa|, 9)`, `ci = (hlc3 − esa) / (0.015·d)`, `wt1 = ema(ci, 12)` (light blue, fast), `wt2 = sma(wt1, 3)` (blue, slow).
- **VWAP momentum wave:** `wt1 − wt2` (yellow). Crossing 0 is an alert.
- **Money flow wave:** `sma((close − open) / (high − low) × 200, 60)`, clamped to ±100. Green above 0, red below. A thin strip at the top of the pane shows its sign.
- **RSI:** RSI(14) smoothed with EMA(3). **Stoch RSI:** (14, 14, 3, 3), off by default. Both are mapped from 0–100 onto the pane.
- **Levels:** OB ±53/±60, extreme ±80, plus Trigger 1/2 (custom, with alerts).

| Dot | Rule |
|---|---|
| Small dot | Any other wt1/wt2 cross |
| Green dot | Cross up with `wt2 ≤ −53` (optional MFI filter) |
| Red dot | Cross down with `wt2 ≥ 53` (optional MFI filter) |
| Gold dot | Cross up with `wt2 ≤ −75` and RSI < 30 (a recent bullish divergence can be required as an option). It is a **warning ("don't buy yet")**, not an entry: on BTC and ETH 4h, price was lower on average 24 bars later |
| Purple triangle | A divergence in the last 20 bars + a cross in the OB/OS zone |
| A / T diamonds | Anchor wave (first wave low ≤ −60), then trigger wave (a higher wave low below 0) |

**Divergences** compare pivot lows and highs of `wt2` (5 bars on each side) with price at the same bars, and draw a line between the two pivots. A pivot is only confirmed 5 bars after the turn, so **divergences appear late by design**.

## 3. Intraday Levels (1H and lower)

- **Range high / low / mid:** the highest high and lowest low of the last N **completed** days (default 3), so these levels don't repaint.
- **VWAP:** resets daily. The background is green on a *long day* (close above VWAP) and red on a *short day*.
- **Purple resistance / yellow support dots:** a dot is drawn on every bar where the local 20-bar high (or low) did not change. The longer the run of dots, the stronger the level, and the label on the last bar shows the count.
- **VWAP cues:** long on a cross above VWAP or a retest from above, short on the mirror.
- **Previous day** high, low and close.
- The script warns you, and draws nothing, on timeframes above 1H. It also warns you on Heikin Ashi candles.

## Alerts

Each script has an `alertcondition()` for every symbol, dot, level and trigger. The waves script also has one combined `alert()` with a dynamic message (ticker, timeframe, signals, close) for webhooks. To use it, create the alert with **"Any alert() function call"**. For all alerts, choose **"Once per bar close"**.

## Repainting

All signals are taken on confirmed (closed) bars only (`barstate.isconfirmed`). The range and previous-day levels use completed daily bars only. Divergence and anchor/trigger marks are drawn back on the pivot bar, but they are only *known* `pivot right` bars later. The alerts fire at the moment of confirmation.

## Testing checklist

1. Add `strategies/backtest_strategy.pine` (the trend-aligned strategy). It defaults to 0.1% commission and 2 ticks of slippage. The repo README has its tested results and limits.
2. Test BTC and ETH on 15m, 1H, 4H and 1D over 2+ years. Compare with and without the ribbon and divergence filters.
3. Tune the levels on one period, then check them on another (out of sample).
4. Paper-trade for 2–4 weeks before using real money.

*This is for education and research only. It is not financial advice.*
