# S&P 500 Monthly Forecasting Project
## Overview
This project evaluates whether statistical, machine learning, and deep learning forecasting models can predict the monthly S&P 500 index better than a simple naive benchmark, where the forecast for next month is just the previous month's value.
The analysis was implemented in the executed notebook:
SP500_Forecasting_Production_Executed.ipynb
## Objective
The project answers two business questions:
1. Can any forecasting model outperform the naive random-walk model?
2. If one model had to be deployed, which model should be chosen and why?
## Dataset
- Series: Monthly S&P 500 index
- Frequency: Monthly (MS)
- Sample period: 1990-01-01 to 2026-07-01
- Training window: First 360 months (1990-01-01 to 2019-12-01)
- Test window: 2020-01-01 to 2026-07-01
## Workflow Summary
The notebook covers:
- Data loading and date indexing
- Monthly resampling validation
- Simulated missing values and repairs
- Stationarity testing with ADF and KPSS
- Time-series visualization, ACF, and PACF
- Naive forecasting baseline
- Holt-Winters exponential smoothing
- SARIMA with residual diagnostics
- Prophet forecasting and cross-validation
- Feature engineering for ML models
- Linear Regression, XGBoost, and LightGBM
- MLP and LSTM deep learning models
- 7-metric model comparison
- Error analysis by month and horizon
- Ensemble forecast
- Diebold-Mariano test
- Final CIO investment memo
## Final Result
The naive model was the best out-of-sample model.
Key result:
- Naive MASE: 1.0000
- Best non-naive challenger: Ensemble
- Ensemble MASE: 3.4339
- Diebold-Mariano test vs naive: stat = -5.6639, p = 0.0000
This means none of the more complex models outperformed the naive random-walk benchmark. In fact, the best challenger performed significantly worse.
## Recommendation
The evidence does not support deploying a complex forecasting model for monthly S&P 500 index timing in this dataset. If a model must be used in production, the naive model is the most defensible choice, but only as a benchmark or decision-support baseline rather than as a trading signal.
## Files
- SP500_Forecasting_Production_Executed.ipynb: executed notebook with outputs
- detailed-explanation.md: detailed findings and observations
- outputs/sp500_sarima_v1.pkl: saved SARIMA artifact
