# TradingView Wave Suite

A collection of TradingView Pine Script (v5) indicators for wave / swing analysis.

## Indicators

| File | Description |
| --- | --- |
| `indicators/swing_waves.pine` | Pivot-based swing detection. Connects alternating highs/lows and labels them 1-2-3-4-5-A-B-C. |
| `indicators/trend_ribbon.pine` | 0x9 Trend Ribbon (Pine v6): 8-EMA ribbon + trend symbols, on the price chart. |
| `indicators/momentum_waves.pine` | 0x9 Momentum Waves (Pine v6): WaveTrend, money flow, RSI/Stoch, dots, divergences, in its own pane. |
| `indicators/intraday_levels.pine` | 0x9 Intraday Levels (Pine v6): range, daily VWAP, S/R dots. For 1H and lower. |
| `strategies/backtest_strategy.pine` | `strategy()` copy that backtests the waves dots with the ribbon filter. |

The full rules for the four 0x9 scripts are in [`docs-0x9-wave-suite.md`](docs-0x9-wave-suite.md). They are original scripts, not Market Cipher.

## Usage

1. Open the TradingView Pine Editor.
2. Paste the contents of an indicator file and click **Add to chart**.

## Notes

- The wave labels are a cyclic visual aid; they do not validate Elliott Wave rules.
- Indicators have not been compiled against TradingView from this repo's CI; report any compile errors as issues.
