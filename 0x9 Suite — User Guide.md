# 0x9 Suite — User Guide

Nov 12, 2026 · @SKS

## Overview

The 0x9 Suite is one TradingView indicator that grades every momentum signal against a higher-timeframe trend, and only labels a signal BUY or SELL when it agrees with that trend. Its full name is "0x9 Wave Suite (All-in-One)", written in Pine Script v6. This guide is taken from the script's own source and settings as loaded on the chart.

It draws in two places:

- **Price chart:** the higher-timeframe trend line, BUY / SELL labels, an 8-EMA ribbon with warning symbols, intraday levels (range, VWAP, support and resistance dots), and a dashboard table in the top-right corner.
- **Pane below:** momentum waves, money flow, RSI, signal dots, divergence lines and anchor / trigger labels.

Three rules apply to everything the suite prints:

- Signals print only when a bar closes. A dot or label never appears and then vanishes mid-bar.
- The trend filter reads the last completed higher-timeframe bar, so it does not repaint.
- Dots that go against the trend are drawn faded. The script's notes say these lost money on average in the author's BTC / ETH 4h tests.

## Setup

Add the script once and it fills both the price chart and its own pane; there is nothing else to install.

1. Open a chart, click **Indicators**, and pick "0x9 Wave Suite (All-in-One)" from your scripts. It shows in the legend as "0x9 Suite".
2. Use regular candles. On Heikin Ashi the dashboard warns "Levels: use regular candles", because the intraday levels are built from real prices.
3. Pick the timeframe for what you want to see (table below).
4. Double-click "0x9 Suite" in the pane legend to open its settings.

| Chart timeframe | Trend filter reads | What is available |
| --- | --- | --- |
| Below 1h | 4h | Everything except Yellow X and the ribbon green dot |
| 1h | Daily | Adds Yellow X. Intraday levels still shown |
| 2h to below 1D | Daily | Intraday levels hidden. The script's note says Trend BUY / SELL tested best on 4h |
| 6h and above | Daily | Adds the ribbon green dot |
| 1D | Weekly | Trend signals and ribbon only |
| 1W and above | Monthly | Trend signals and ribbon only |

The trend timeframe is chosen automatically. To fix it yourself, untick "Auto trend timeframe" and set "Manual trend timeframe".

## Dashboard table

The table in the top-right corner is the summary to read first: it tells you which side the trend filter allows. Green values favour buyers, red values favour sellers.

| Row | What it shows | How it is calculated |
| --- | --- | --- |
| Header | Symbol and chart timeframe | For example "XAUUSDT.P 60" |
| Trend (D) | UP or DOWN. The letter in brackets is the trend timeframe | Last completed higher-timeframe close above or below its 50 EMA |
| Trend money flow | Money flow on the trend timeframe | Same formula as the row below, read from the last completed higher-timeframe bar |
| Money flow | Money flow on the chart timeframe, from −100 to +100 | 60-bar average of (close − open) ÷ (high − low), times 200 |
| Wave | Zone and value of the slow wave | Oversold at −53 or lower, Overbought at +53 or higher, otherwise Neutral |
| Strength (context) | "X bull / Y bear of 14" | 14 momentum checks, counted separately for each side. Context only, not a signal |
| Bias | One-line reading of trend plus trend money flow | See the four messages below |
| Note | Warnings about the current chart | For example "Trend BUY/SELL tested best on 4h" on charts below 4h |

The Bias row prints one of four messages:

- "Uptrend: look for BUY dips": trend up and trend money flow positive.
- "Uptrend, weak money flow": trend up, but trend money flow at zero or negative.
- "Downtrend: avoid longs": trend down and trend money flow negative.
- "Downtrend, flow improving": trend down, but trend money flow at zero or positive.

The 14 strength checks are: close above the 20 EMA, 20 EMA above 50 EMA, close above the 200 EMA, RSI above 50, RSI rising over 3 bars, MACD histogram positive, MACD histogram rising, fast wave above slow wave, slow wave rising, money flow positive, money flow rising over 3 bars, Stoch K above D, 10-bar rate of change positive, and OBV above its 20 EMA. The bear count uses the opposite of each.

## Price chart overlays

The price chart carries three layers: the trend filter with its BUY / SELL labels, the EMA ribbon with its symbols, and the intraday levels. Each layer has its own master switch in the settings.

### Trend line and BUY / SELL labels

| Item | Looks like | Rule |
| --- | --- | --- |
| Trend EMA | Thick stepped line, green or red | 50 EMA of the trend timeframe. Green when the last completed higher-timeframe close is above it, red when below |
| BUY | Green label under the bar | Fast wave crosses above the slow wave while the slow wave is at −40 or lower, and the trend is up |
| SELL | Red label above the bar | Fast wave crosses below the slow wave while the slow wave is at +40 or higher, and the trend is down |

BUY and SELL are the only signals the suite treats as trade signals. Everything else is context or warning.

### Ribbon and ribbon symbols

The ribbon is 8 EMAs (5, 11, 15, 18, 21, 24, 28, 34). The fill is blue when the fastest EMA is above the slowest (bull) and grey when it is below (bear).

| Symbol | Position | Rule | Reading |
| --- | --- | --- | --- |
| Yellow diamond | Below bar | Ribbon is bull and the wave crosses up with the slow wave above zero | Momentum renewing inside an up ribbon |
| Red diamond | Above bar | Ribbon is bull and the wave crosses down | Momentum fading inside an up ribbon |
| Red X | Above bar | EMA 1 crosses below EMA 2 while the ribbon is narrower than its 20-bar average width | Squeezed ribbon starting to turn down |
| Blood diamond "BD" | Above bar | Red X and red diamond on the same bar, with a yellow diamond in the last 10 bars | Strongest bearish ribbon warning. Replaces the red X and red diamond on that bar |
| Yellow X | Below bar | Red candle, volume above 2 × its 20-bar average, lower wick at least half the candle. 1h charts and above | Heavy selling that was bought back off the low |
| Blue triangle up | Below bar | EMA 2 crosses above EMA 8 while EMA 8 is lower than 5 bars ago | Early turn up against a falling ribbon |
| Blue triangle down | Above bar | EMA 2 crosses below EMA 8 while EMA 8 is higher than 5 bars ago | Early turn down against a rising ribbon |
| Ribbon green dot | Below bar | Wave crosses up at −53 or lower within 3 bars of a blue triangle up. 6h charts and above | Oversold cross confirming a ribbon turn |

### Intraday levels (1h charts and lower)

| Item | Looks like | Rule |
| --- | --- | --- |
| Range high / low | Two thick grey lines | Highest high and lowest low of the last 3 completed days |
| Range mid | Thin pale line | Midpoint of range high and low |
| VWAP | Thick orange line | Volume-weighted average price, reset each day |
| Long day / short day | Faint green or red background | Green while price closes above the daily VWAP, red while below |
| Previous day high / low | Light blue lines | Yesterday's high and low |
| Resistance dots | Purple dots above price | The 20-bar high while it holds. Solid once it has held 10 bars in a row |
| Support dots | Yellow dots below price | The 20-bar low while it holds. Solid once it has held 10 bars in a row |
| VWAP long cue | Small green triangle under the bar | Close crosses above VWAP, or the low touches VWAP and the bar closes back above it |
| VWAP short cue | Small red triangle above the bar | Close crosses below VWAP, or the high touches VWAP and the bar closes back below it |

## Oscillator pane

The pane shows where momentum is and where it just turned; every dot marks a cross of the fast wave over or under the slow wave.

### Waves and lines

| Item | Looks like | What it is |
| --- | --- | --- |
| Fast wave | Light blue area | WaveTrend of the typical price (channel 9, average 12) |
| Slow wave | Dark blue area | 3-bar average of the fast wave. All zones and levels are measured on this one |
| VWAP momentum wave | Yellow area around zero | Fast wave minus slow wave. Above zero means momentum is rising |
| Money flow wave | Green or red area | Same value as the dashboard's Money flow row. Green above zero, red below |
| RSI | Purple line | 14-period RSI, smoothed and rescaled so RSI 50 sits on the zero line |
| Stoch RSI | Green and red lines | Off by default. Turn on under "Oscillator dots" |
| Dotted lines at +53 and −53 | Red and green | Overbought and oversold zones |
| Grey lines at +30 and −30 | Grey | Trigger levels. A slow-wave cross of either one sends an alert token |

### Dots, triangles and labels

| Mark | Rule | Reading |
| --- | --- | --- |
| Small green or red dot | Any wave cross that does not qualify as a larger dot | Minor momentum turn |
| Green dot | Wave crosses up with the slow wave at −53 or lower | Oversold turn up. Faded when the trend is not up |
| Red dot | Wave crosses down with the slow wave at +53 or higher | Overbought turn down. Faded when the trend is not down |
| Gold dot (large) | Wave crosses up with the slow wave at −75 or lower and RSI below 30 | A warning, not a buy. The script's note says price was lower on average 24 bars later in tests |
| Green triangle below the wave | Same bar as a BUY label | Pane copy of Trend BUY |
| Red triangle above the wave | Same bar as a SELL label | Pane copy of Trend SELL |
| Purple triangle up / down | Green-dot or red-dot conditions, with a matching divergence in the last 20 bars | Oversold or overbought cross backed by a divergence |
| Green line between two wave lows | Slow wave makes a higher low while price makes a lower low. The first low must be at −53 or lower | Bullish divergence |
| Red line between two wave highs | Slow wave makes a lower high while price makes a higher high. The first high must be at +53 or higher | Bearish divergence |
| "A" label (blue) | Slow-wave pivot low at −60 or lower | Anchor wave: the deep oversold low |
| "T" label (gold) | Next pivot low that is higher than the anchor, still below zero, within 60 bars | Trigger wave: sellers are weaker on the retest |

Divergence lines and the A / T labels need 5 bars after the pivot to confirm, so they appear 5 bars late and are drawn back on the pivot bar.

## Settings

The defaults work as loaded; most users only need the three master switches and the trend filter group. Defaults are shown in brackets.

| Group | Inputs (default) | Change it when |
| --- | --- | --- |
| Master switches | Show trend ribbon + symbols (on), Show intraday levels (on), Show momentum waves (on) | You want a cleaner chart. Each switch hides a whole layer and mutes its alert tokens |
| Alerts | Send alert() messages (on) | You want the script silent without deleting your alert |
| Trend filter | Auto trend timeframe (on), Manual trend timeframe (1 day), Trend EMA length (50), Trend BUY / SELL wave level (40), Show trend line + BUY / SELL (on), Fade dots that go against the trend (on), Show dashboard (on) | Raise the wave level for fewer, deeper signals; lower it for more. Untick Auto to pin the trend timeframe |
| WaveTrend | Channel length (9), Average length (12), Slow wave length (3) | Larger numbers smooth the waves and give fewer crosses |
| Oscillator levels | Overbought 1 (53), Overbought 2 (60), Oversold 1 (−53), Oversold 2 (−60), Trigger 1 (30), Trigger 2 (−30) | A market rarely reaches ±53, or sits there too often. Oversold 2 sets how deep an anchor wave must be |
| Money flow | Length (60), Multiplier (200) | Shorter length makes money flow react faster |
| RSI / MFI / Stoch | RSI length (14), RSI smoothing (3), MFI length (14), Use MFI filter on green/red dots (off), MFI oversold (40), MFI overbought (60), Stoch RSI length (14), K (3), D (3), display scale (0.8) | Tick the MFI filter to require volume-weighted confirmation on green and red dots |
| Divergences | Pivot left bars (5), Pivot right bars (5), Max bars between pivots (60), Divergence needs OB/OS zone (on), Counts as recent for (20 bars) | Fewer right bars confirm sooner but give more false pivots |
| Oscillator dots | Gold dot: RSI below (30), slow wave at or below (−75), also needs a recent bullish divergence (off). Show toggles for small dots, green / red / gold dots, purple triangles, divergence lines, anchor / trigger labels, RSI, Stoch RSI | Hide marks you do not use |
| Ribbon | EMA 1 to 8 (5, 11, 15, 18, 21, 24, 28, 34), Use Heikin Ashi close as source (off), Constriction width average (20) | Heikin Ashi source smooths the ribbon on choppy charts |
| Ribbon symbol rules | Yellow X volume multiple (2), volume average (20), lower wick share (0.5), min timeframe (60 min). Blood diamond lookback (10). Blue triangle slope bars (5). Ribbon green dot window (3 bars), min timeframe (360 min). One show toggle per symbol | Tighten or loosen a single symbol, or hide it |
| Intraday levels | Range days (3), Block levels above (60 min), VWAP retest tolerance (0 ticks), Local high / low lookback (20), Strong level after (10 dots). Show toggles for range, VWAP, background, resistance, support, VWAP cues, previous day high / low | Raise the tolerance if VWAP retests miss by a tick or two |

In the current code "Overbought 2" is not used by any rule, so changing it has no effect.

## Step-by-step workflow

Read the suite top-down: trend first, then location, then the trigger. This is how the tool is designed to be read, not a recommendation to take any trade.

1. **Read the dashboard.** Trend and Bias tell you which side is allowed. "Uptrend: look for BUY dips" means only BUY labels count; "Downtrend: avoid longs" means only SELL labels count.
2. **Wait for the wave to reach the far side.** In an uptrend the slow wave has to drop to −40 or lower. In a downtrend it has to rise to +40 or higher. The Wave row shows the live value.
3. **Wait for the label on bar close.** A BUY or SELL label on the price chart, with a matching triangle in the pane, is the trigger. Nothing prints until the bar closes.
4. **Check the context around it.**
   - Money flow and Trend money flow on the same side as the signal.
   - Ribbon colour: blue for buys, grey for sells.
   - On 1h and lower: background colour and VWAP side agree with the signal.
   - A purple triangle, divergence line or "T" label nearby adds weight.
   - Strength row leaning the same way.
5. **Use the levels as reference prices.** Support and resistance dots, range high / mid / low, VWAP and the previous day's high and low mark where price reacted before.
6. **Watch for warnings against an open position.** For a long: red diamond, red X, blood diamond, a red dot, a bearish divergence line, or the Trend row flipping to DOWN. For a short, the opposites.
7. **Leave these alone.** Faded dots go against the trend. A gold dot is a "do not buy yet" warning; the pattern the suite looks for after it is an "A" label followed by a "T" label.

## Worked example

On the XAUUSDT.P 1h chart at about 05:30 UTC on 12 November 2026, the suite was saying "wait": the trend was down and the wave was nowhere near a SELL level. Price was about 3,979.

| Dashboard row | Value on the chart | Reading |
| --- | --- | --- |
| Trend (D) | DOWN | Last daily close is below the daily 50 EMA. Only SELL labels can print |
| Trend money flow | −17.0 | Daily money flow agrees with the downtrend |
| Money flow | −23.7 | 1h money flow is negative too |
| Wave | Neutral −52 | One point above the oversold zone at −53 |
| Strength (context) | 1 bull / 13 bear of 14 | Almost every momentum check is bearish |
| Bias | Downtrend: avoid longs | Trend down and trend money flow negative |
| Note | Trend BUY/SELL tested best on 4h | Shown because the chart is below 4h |

How the rules apply to that picture:

- No BUY can print. A BUY needs the daily trend up, and it is down.
- No SELL is close. A SELL needs the wave to cross down from +40 or higher, and the slow wave is at −52.
- If the wave crosses up from here at −53 or lower, the pane prints a green dot, but faded, because it goes against the trend.
- On the price chart, price sits under a grey ribbon and under the orange VWAP, with a red "short day" background. All three agree with the dashboard.

The same chart also shows why the gold dot is treated as a warning. Around 18:00 on 10 November a BUY label printed while the trend line was still green. The pane shows a gold dot and an "A" label on that same low. Price moved sideways, the trend line turned red on 11 November, and price went on to trade lower.

## Alerts

The suite sends every signal through one alert, so you create a single alert per chart and read the signal name from the message.

1. Click **Alert** in the top toolbar.
2. Set Condition to "0x9 Suite", then choose "Any alert() function call".
3. Choose your notification method (app, email, webhook) and create the alert.
4. Repeat on each symbol and timeframe you want to watch.

The script fires once per bar close. A message looks like this:

```
0x9 Suite | XAUUSDT.P | 60 | TREND_SELL RED_DOT | close=3979.44
```

The parts are: script name, symbol, timeframe, the tokens for every signal that fired on that bar, and the closing price.

| Token | Signal | Sent when |
| --- | --- | --- |
| TREND\_BUY, TREND\_SELL | BUY and SELL labels | Always |
| GREEN\_DOT, RED\_DOT, GOLD\_DOT | Oscillator dots, including faded ones | Momentum waves switch is on |
| PURPLE\_UP, PURPLE\_DOWN | Purple triangles | Momentum waves switch is on |
| BULL\_DIV, BEAR\_DIV | Divergence lines | Momentum waves switch is on |
| VWAPWAVE\_UP, VWAPWAVE\_DOWN | Yellow wave crosses zero | Momentum waves switch is on |
| MONEYFLOW\_POS, MONEYFLOW\_NEG | Money flow crosses zero | Momentum waves switch is on |
| TRIGGER1\_CROSS, TRIGGER2\_CROSS | Slow wave crosses +30 or −30 | Momentum waves switch is on |
| YELLOW\_DIAMOND, RED\_DIAMOND, RED\_X, YELLOW\_X, BLOOD\_DIAMOND | Ribbon symbols | Ribbon switch is on |
| BLUE\_TRI\_UP, BLUE\_TRI\_DOWN, RIBBON\_GREEN\_DOT | Ribbon turn symbols | Ribbon switch is on |
| VWAP\_LONG\_CUE, VWAP\_SHORT\_CUE | VWAP cues | Intraday levels switch is on and the chart is 1h or lower |

Things to know:

- You cannot pick single signals in the alert dialog. To act only on trend signals, filter for TREND\_BUY and TREND\_SELL in the message on the receiving side, or turn off the ribbon and wave switches before creating the alert.
- The small "show" toggles hide marks on the chart but do not stop their tokens. Only the master switches and "Send alert() messages" do.
- A GREEN\_DOT or RED\_DOT token does not say whether the dot was faded. Check the trend yourself, or rely on TREND\_BUY / TREND\_SELL.
- An alert keeps the settings it was created with. After changing inputs, delete the alert and create it again.

## Limits and risk

The suite describes trend and momentum; it does not size positions, place stops or predict price, and none of its signals is a guarantee.

- **The trend filter is slow by design.** It updates only when a higher-timeframe bar closes. On a 1h chart the trend can stay "UP" for most of a day while price is already falling, as in the worked example.
- **Confirmation costs time.** Signals wait for the bar close, and divergences and A / T labels arrive 5 bars after the pivot.
- **The test claims are the author's.** The notes in the script (faded dots lost money on BTC / ETH 4h, gold dot followed by lower prices, BUY / SELL best on 4h) are comments in the code. This guide has not re-run or verified them, and the only markets the code names are BTC and ETH on 4h, not gold.
- **Strength is a count, not a forecast.** 13 of 14 bearish checks describes the last bars; it also appears near the end of a move.
- **Volume rules depend on the exchange.** Yellow X and VWAP use the volume of the symbol on the chart, so the same market on another exchange can give different marks.
- **Intraday levels disappear above 1h.** The dashboard Note row says so when it happens.
- **No stop-loss or position size comes from the script.** Decide both before acting on any label.

This document explains how the indicator works. It is not financial advice, and it was not written by a licensed advisor.
