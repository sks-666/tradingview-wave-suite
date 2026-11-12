# TradingView Wave Suite

A collection of TradingView Pine Script indicators and a strategy for trend, momentum-wave and swing analysis.

## Indicators

| File | Description |
| --- | --- |
| `indicators/swing_waves.pine` | Pivot-based swing detection. Connects alternating highs/lows and labels them 1-2-3-4-5-A-B-C. |
| `indicators/trend_ribbon.pine` | 0x9 Trend Ribbon (Pine v6): 8-EMA ribbon + trend symbols, on the price chart. |
| `indicators/momentum_waves.pine` | 0x9 Momentum Waves (Pine v6): WaveTrend, money flow, RSI/Stoch, dots, divergences, in its own pane. |
| `indicators/intraday_levels.pine` | 0x9 Intraday Levels (Pine v6): range, daily VWAP, S/R dots. For 1H and lower. |
| `indicators/wave_suite_all_in_one.pine` | **All-in-one (Pine v6):** ribbon + symbols + intraday levels on the price chart, and momentum waves in the pane below, from a single script. |
| `strategies/backtest_strategy.pine` | **Trend-aligned strategy (v2):** buys wave dips only while the higher-timeframe trend is up. See *Tested results* below. |
| `research/` | The Python backtest used to design and check the rules. Reproducible from public Binance candles. |

The full rules for the four 0x9 scripts are in [`docs-0x9-wave-suite.md`](docs-0x9-wave-suite.md). They are original scripts, not Market Cipher.

## Usage

1. Open the TradingView Pine Editor.
2. Paste the contents of an indicator file and click **Add to chart**.

## Notes

- The wave labels are a cyclic visual aid; they do not validate Elliott Wave rules.
- The scripts were run end to end in a local open-source Pine runtime (PineTS), and the strategy's trades were matched one for one against the Python backtest. They have **not** been compiled by TradingView itself, so report any compile error.

## All-in-one script

`indicators/wave_suite_all_in_one.pine` combines the ribbon, momentum waves and intraday levels in one script, so you add a single indicator to the chart. The oscillator is drawn in the pane and everything else on the price chart (`force_overlay=true`). TradingView allows 64 plot/alert slots per script, so all signals are sent through one `alert()` call: create the alert with **Any alert() function call** and **Once per bar close**. Each section has a master switch in the settings. Use the separate scripts instead if you want one `alertcondition()` per signal.

## Trend filter and Trend BUY / SELL (v2)

The all-in-one script and the strategy share one rule set, built around "higher-timeframe signal, lower-timeframe entry":

1. **Trend:** the higher timeframe decides direction. Up = its last completed close is above its EMA 50. The timeframe is picked automatically (chart below 1h → 4h, 1h to below 1D → daily, daily → weekly) or set by hand.
2. **Trend BUY:** a wave cross up at or below −40 while the trend is up. **Trend SELL** is the mirror, in a downtrend.
3. **Exit (strategy):** a wave cross down at or above +40, the trend flipping, or a stop 2 × ATR below the signal bar's close.

In the all-in-one script, BUY / SELL labels mark these on the price chart, dots that go **against** the trend are faded, and a dashboard shows the trend, money flow, wave zone and a 14-check strength count.

The **gold dot** is now a cross up from extreme oversold (slow wave ≤ −75, RSI < 30). It is a warning, not an entry.

## Tested results

Binance spot candles, Jan 2020 to Nov 2026. Fees 0.1% per side plus 0.02% slippage. Signals on bar close, fills on the next open. Rules were chosen on 2020–2023 (in-sample) and then checked on 2024–2026 (out-of-sample). Long only, 4h chart, daily trend.

| Market | Period | Trades | Win rate | Profit factor | Return / year | Max drawdown | Buy & hold (max drawdown) |
|---|---|---|---|---|---|---|---|
| BTC | 2020–23 (in-sample) | 63 | 51% | 1.78 | +21.5% | −20% | +396% (−77%) |
| BTC | 2024–26 (out-of-sample) | 59 | 47% | 1.31 | +7.6% | −19% | +75% (−53%) |
| ETH | 2020–23 (in-sample) | 74 | 65% | 2.39 | +50.9% | −23% | +950% (−81%) |
| ETH | 2024–26 (out-of-sample) | 47 | 57% | 1.43 | +10.1% | −23% | −10% (−68%) |
| SOL | 2020–23 (not used for tuning) | 55 | 45% | 1.39 | +16.2% | −58% | +5079% (−97%) |
| SOL | 2024–26 (not used for tuning) | 46 | 39% | 0.84 | −11.1% | −44% | −18% (−78%) |

What this does and does not show:

- **It works as a risk-reducer, not a return-maximiser.** The strategy is in the market about 13% of the time. On BTC and ETH it was profitable in both periods with roughly a third of buy-and-hold's drawdown, but it made far less than holding in bull years.
- **Results fade out-of-sample.** Profit factor fell from about 1.8–2.4 to about 1.3–1.4. Expect live results to be weaker again.
- **It lost money on SOL in 2024–26.** The rules do not carry over cleanly to every coin.
- **It lost money on 1h charts** on all three coins (profit factor 0.75–1.08), because fees outweigh the small edge. 15m showed no edge either. Use 4h.
- **Shorts are off by default.** Adding them lowered the profit factor in five of the six tests and deepened the drawdown in all six.
- **The dots alone have no edge.** A green or red dot without the trend filter did no better than a random bar. The old strategy default (green dot plus same-timeframe bullish ribbon) took 0 trades on the BTC 4h chart in six years, because the two conditions almost never happen together.
- The 14-check strength count showed only a weak link to later returns. It is on the dashboard as context, not as a signal.

Past results do not predict future results. This is a research tool, not financial advice.

### Reproduce

```bash
cd research
pip install pandas numpy
python3 download.py            # public Binance candles into research/data
python3 validate.py            # the table above, plus the old rules and long+short
python3 strategy_grid.py 4h 1d BTCUSDT,ETHUSDT   # the parameter grid, in-sample vs out-of-sample
python3 signal_edge.py BTCUSDT,ETHUSDT           # forward returns after each signal type
```
