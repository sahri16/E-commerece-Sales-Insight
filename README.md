# Sales Insight Studio

Sales Insight Studio is a Python application for analyzing e-commerce sales, profitability, customer purchasing patterns, and monthly revenue trends. It provides an interactive Streamlit dashboard, a reusable analysis module, a command-line reporting tool, and a Jupyter notebook.

Use the bundled Superstore sample to learn, or upload your own CSV. For a beginner-friendly guide in Roman Urdu, start with **[docs/START_HERE_ROMAN_URDU.md](docs/START_HERE_ROMAN_URDU.md)**.

## What you can do

- See sales, profit, unique orders, customers, profit margin and average order value.
- Filter by date, region, category and customer segment.
- Review chronological monthly trends, category performance and loss-making sub-categories.
- Compare discount levels with line profit and examine dispatch lag by shipping mode.
- Explore historical customer spending, recency and repeat purchasing.
- Generate 1–12 months of future point estimates, with a time-ordered holdout and baseline comparison.
- Inspect source data quality, download excluded rows and export filtered data or a report ZIP.
- Run the same analysis from a command line or a revised Jupyter notebook.

## Requirements

- **Python 3.11 or 3.12 recommended**; validated here with Python 3.12.14 on Linux.
- Windows, macOS or Linux, and a modern browser such as Chrome or Edge.
- Internet for the initial package installation. No API key, paid service, database or account is required.
- Practical target: 4 GB RAM and approximately 1 GB free disk space for Python/packages. Actual usage depends on upload size.

Dependencies are in `requirements.txt`. The exact versions used for validation are recorded in `docs/VALIDATION.md`; version ranges in the requirements allow compatible updates rather than freezing an entire machine environment.

## Windows installation

Install Python 3.12 and extract the project ZIP. Open Command Prompt in the project folder, then run the following commands one at a time:

```bat
py -3.12 -m venv .venv312
".venv312\Scripts\python.exe" --version
".venv312\Scripts\python.exe" -m pip install --only-binary=:all: -r requirements.txt
".venv312\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Confirm that the version check displays `Python 3.12.x` before installing packages. Use a fresh environment; do not mix packages from Python 3.12 and Python 3.15.

The dashboard should open automatically. Otherwise, visit <http://localhost:8501>. Keep the terminal open while using the app and press **Ctrl+C** to stop it.

For later sessions, open Command Prompt in the project folder and run only the final command. The existing Windows batch launchers target `.venv`, so they do not use the `.venv312` environment shown here.

### macOS / Linux

```bash
bash start_mac_linux.sh
```

The shell launcher creates an environment if needed, checks/installs dependencies, then opens the app. Alternatively:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

For Linux systems missing venv support, install your distribution's Python venv package first.

## Included dataset

The project includes `data/superstore.csv`, an unchanged copy of the original Sample Superstore dataset. It contains 9,994 order lines from 2014–2017. The application loads this file automatically when no CSV is uploaded; no separate dataset download is required.

This is historical sample retail data, not actual shop data. A three-row fictional digital-product template is provided in `data/upload_template.csv` for preparing a custom upload.

## Use your own data

Start from `data/upload_template.csv`. This small file contains **fictional digital-product sales**, not your real sales. Upload it through the sidebar to try the workflow. Its three rows are intentionally too short for forecasting.

### Required columns

| Column | Meaning | Example |
| --- | --- | --- |
| Order ID | Order identifier; repeats for multiple lines in one order | ORDER-001 |
| Order Date | Purchase date | 2026-10-01 |
| Customer ID | Stable customer identifier | C001 |
| Sales | Total sales amount for this line; not unit price | 12.00 |
| Profit | Profit for this line, calculated consistently | 8.00 |

Optional fields: `Category`, `Sub-Category`, `Region`, `Segment`, `Product Name`, `Quantity`, `Discount`, `Ship Date`, `Ship Mode`. Missing category fields become `Unknown`; unavailable discounts, quantities and shipping dates remain missing.

- Column names are case-sensitive; surrounding spaces are trimmed.
- Numeric cells must contain plain numbers, without currency symbols or thousands separators. Sales must be finite and nonnegative. Negative profit is valid.
- Returns recorded as negative sales are excluded in this version; use a separate returns workflow rather than silently mixing them into this analysis.
- Discount is a fraction: `0.20` means 20%. Out-of-range discounts are ignored and counted.
- Choose the matching date format in the sidebar: US/mixed, DD/MM/YYYY, or YYYY-MM-DD. Prefer ISO dates (`YYYY-MM-DD`) to avoid ambiguity.
- Use one currency per file. The currency label only changes display text; there is no conversion.
- Each row is an order line. Distinct lines within an order are retained; completely identical rows are removed. If legitimately identical lines have no unique identifier, add a line-ID column to distinguish them.
- Missing/invalid IDs, dates or required amounts are excluded and available for download. No missing profit is fabricated and no outliers are automatically deleted.

### Digital-product sales

Prepare an export with the above columns. Compute `Profit` using your chosen cost definition (for example, sales minus platform/payment fees, refunds allocated outside this version, advertising allocations and other applicable costs). Keep that definition consistent. Digital products may leave shipping fields blank.

**This is not a direct Etsy integration.** Raw Etsy CSV exports may have different columns; rename/map and calculate fields before uploading. The bundled Superstore data describes historical US retail orders and cannot establish anything about your shop's actual performance. Never relabel its currency as PKR to imply conversion.

## Export reports without the dashboard

On Windows, run these commands from the project folder:

```bat
".venv312\Scripts\python.exe" run_analysis.py --forecast
".venv312\Scripts\python.exe" run_analysis.py --csv data/upload_template.csv --output my_reports
".venv312\Scripts\python.exe" run_analysis.py --csv your_sales.csv --date-format %d/%m/%Y --output my_reports
```

On macOS/Linux, replace `".venv312\Scripts\python.exe"` with `.venv/bin/python`.

The default output directory is `reports/`. Reports include a plain-text summary, monthly totals, category/region/segment tables, RFM and quality counts. `--forecast` adds future estimates and holdout metrics; short data produces an explanatory file instead. `sample_reports/` contains generated outputs from the bundled sample for immediate inspection.

## Notebook and tests

Install the optional development dependencies with the environment's Python:

```bat
".venv312\Scripts\python.exe" -m pip install -r requirements-dev.txt
".venv312\Scripts\python.exe" -m jupyterlab
```

For macOS/Linux, use `.venv/bin/python` instead of the Windows environment path.

Open `notebooks/sales_analysis.ipynb` and run all cells. The notebook resolves the data path from the project folder rather than relying on the original broken CSV path.

From the project root:

```bat
".venv312\Scripts\python.exe" -m pytest -q
```

Tests verify known sample totals, unique-order counting, invalid input, duplicate handling, date formats, zero-sales margins, year-aware monthly aggregation, forecast timing, dashboard rendering and empty filters.

## Analysis definitions and limits

- **Profit margin:** sum of profit / sum of sales × 100. Zero sales yields unavailable, not infinity.
- **Average order value:** selected line sales / distinct selected orders. Category filters can select only part of an order, so this is selected-order value, not necessarily the full basket.
- **RFM:** descriptive customer recency, distinct-order frequency and observed revenue. Recency is measured from the last selected date + one day. Simple 90/180-day segments are configurable rules, not learned churn probabilities or future lifetime value.
- **Dispatch lag:** Ship Date − Order Date, excluding negative lags. The dashboard uses the last dispatch per order and ship mode before averaging. Arrival dates and delivery performance are unavailable.
- **Forecast:** at least 18 monthly observations after any last-month exclusion. Uses additive Holt-Winters with annual seasonality when training history has at least 24 months; otherwise uses a nonseasonal additive trend. Compares holdout MAE with the previous-year same-month baseline and selects the lower error. The selected method then estimates the next 1–12 months from available history. Negative smoothing predictions are clipped to zero.
- **Completeness:** default exclusion of the latest month is conservative; disable it for a known complete month. If that month is excluded, the forecast begins in that omitted month. Missing intervening months are treated as zero. The first selected month can also be partial; choose full months for forecasts. One holdout is a limited estimate and no prediction intervals are provided.
- Discount/profit correlations are observational. They do not prove discounts caused the change or identify an optimal discount.
- Local operation: uploads are read in memory and not persisted by this app or sent to an analysis API. Downloaded reports contain the selected data; handle them accordingly.

## Improvements over the original notebook

| Original issue | Improvement |
| --- | --- |
| Notebook reads a CSV from the wrong folder | Shared loader with a project-relative sample path |
| No requirements or easy startup | Requirements, Windows launchers, macOS/Linux launcher |
| Monthly numbers merge all years | True calendar-month time series |
| README claims cleaning not implemented by the notebook | Explicit validation, exclusions and auditable counts |
| In-sample fitted values labelled forecast | Future estimates and chronological holdout validation |
| Revenue labelled customer lifetime value | Accurately labelled historical spending and descriptive RFM |
| Ship date labelled delivery | Correct dispatch terminology |
| Sales/profit ratio conclusions invert profitability | Standard profit margin with safe zero handling |
| Static outputs and notebook-only workflow | Interactive dashboard, upload, filters, downloads, CLI and tests |

## Project layout

```text
Sales-Insight-Studio/
  app.py                         Interactive dashboard
  analysis.py                    Shared validation and analytics
  run_analysis.py                 Command-line report export
  requirements.txt               App dependencies
  requirements-dev.txt           Optional notebook/test dependencies
  setup_windows.bat              One-time Windows setup
  start_windows.bat              Windows dashboard launcher
  start_mac_linux.sh             macOS/Linux setup and launcher
  data/                          Original sample and custom CSV template
  notebooks/sales_analysis.ipynb  Revised, executed analysis notebook
  sample_reports/                Reports generated from sample data
  tests/                         Analytics and dashboard tests
  docs/                          Roman Urdu guide, validation, provenance
  reference/original_project.zip Original upload kept unchanged
```

## Customization

- **Shop title:** change `st.title` and `page_title` in `app.py`.
- **Palette / charts:** adjust the Plotly calls in `app.py`.
- **Customer rules:** edit the 90/180-day thresholds in `customer_rfm` in `analysis.py`.
- **Upload fields:** adapt the CSV or extend `load_data`; keep IDs and financial definitions consistent.
- **New useful work later:** an Etsy-column mapping wizard, fee calculation, budget-versus-actual reporting, returns support, or rolling-window forecast validation. These are future ideas, not included features.

## Troubleshooting

| Problem | What to do |
| --- | --- |
| Python not found | Install Python 3.11/3.12, enable PATH, reopen the terminal |
| Package install fails | Check internet; confirm that `.venv312` uses Python 3.12 |
| NumPy C-extension error mentioning cp312 and Python 3.15 | Recreate a fresh environment with `py -3.12 -m venv .venv312`; install and run using that environment only |
| `No module named ...` | Install requirements using the same environment that runs the app |
| Browser does not open | Open <http://localhost:8501> manually and keep the terminal open |
| Port 8501 is busy | Add `--server.port 8502`, then use <http://localhost:8502> |
| No rows after upload | Check required headers, date format and plain numeric values |
| No rows after filters | Expand dates and select at least one value per group |
| Forecast unavailable | Supply at least 18 months after exclusions; remove narrow filters |
| Postal codes show missing in sample | Optional source values; they are not required for these analyses |

## Acknowledgments and provenance

The original project archive and sample dataset are preserved with provenance notes in [docs/PROVENANCE.md](docs/PROVENANCE.md). The upload did not contain a license file. This update does not claim original authorship or grant rights to third-party material. Add verified attribution and license information before public redistribution.

Official setup reference: <https://docs.streamlit.io/get-started/installation/command-line>.

---

**Prepared for: Sahrish Anfal**
