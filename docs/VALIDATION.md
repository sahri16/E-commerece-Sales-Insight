# Validation

Environment: Linux, Python 3.12.14. Validation date: 2026-10-19.

- pandas: 2.2.3
- numpy: 2.3.5
- streamlit: 1.66.0
- plotly: 6.9.0
- statsmodels: 0.14.6
- pytest: 9.1.1
- nbformat: 5.11.1
- nbclient: 0.11.0
- ipykernel: 7.4.0

Results:

- 9 automated tests passed, including shared analytics and Streamlit AppTest checks.
- Verified sample totals: 9,994 lines, 5,009 distinct orders, 793 customers, sales 2,297,200.8603 and profit 286,397.0217 (source currency).
- CLI sample report export and future forecast completed; outputs are in `sample_reports/`.
- Revised notebook schema validated and all 14 code cells executed sequentially using in-process IPython. Execution outputs are included.
- Python source compilation and shell launcher syntax checked.

Limits of validation:

- Windows and macOS launchers were not executed on those operating systems.
- A standalone Jupyter kernel could not start in this restricted runtime. Notebook code was executed in-process instead; a full JupyterLab browser session was not tested.
- Dashboard behavior was exercised through Streamlit AppTest, not a real browser screenshot or end-to-end browser session. A server start emitted its local URL, but local HTTP connectivity was unavailable here; no successful live-browser access is claimed.
- No live Etsy connection or real user transaction data was used.
- Forecast accuracy on one historical holdout does not establish performance on a different business.

