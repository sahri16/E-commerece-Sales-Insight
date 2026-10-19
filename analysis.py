"""Shared, UI-independent sales analysis. Values retain the CSV's currency."""
from pathlib import Path
import io
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
SAMPLE = ROOT / 'data' / 'superstore.csv'
REQUIRED = ['Order ID', 'Order Date', 'Customer ID', 'Sales', 'Profit']
OPTIONAL = ['Region', 'Category', 'Sub-Category', 'Segment', 'Product Name', 'Ship Mode']


def load_data(source=SAMPLE, date_format='mixed'):
    """Validate input, quarantine invalid required values, retain valid loss rows."""
    raw = source.read() if hasattr(source, 'read') else Path(source).read_bytes()
    if isinstance(raw, str):
        raw = raw.encode('utf-8')
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('latin1')
    df = pd.read_csv(io.StringIO(text), dtype=str)
    df.columns = df.columns.str.strip()
    if df.columns.duplicated().any():
        raise ValueError('Column names must be unique after trimming spaces.')
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError('Missing columns: ' + ', '.join(missing))
    report = {'input_rows': len(df)}
    duplicates = df.duplicated()
    report['exact_duplicates_removed'] = int(duplicates.sum())
    df = df.loc[~duplicates].copy()
    for col in ['Order ID', 'Customer ID'] + [c for c in OPTIONAL if c in df]:
        df[col] = df[col].str.strip().replace('', pd.NA)
    df['Order Date'] = pd.to_datetime(df['Order Date'], format=date_format, errors='coerce')
    for col in ['Sales', 'Profit']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    invalid = df[REQUIRED].isna().any(axis=1) | ~np.isfinite(df['Sales']) | ~np.isfinite(df['Profit']) | df['Sales'].lt(0)
    rejected = df.loc[invalid].copy()
    report['invalid_rows_excluded'] = int(invalid.sum())
    df = df.loc[~invalid].copy()
    if df.empty:
        raise ValueError('No valid rows remain. Check dates, IDs and numeric Sales/Profit.')
    for col in OPTIONAL:
        df[col] = df[col].fillna('Unknown') if col in df else 'Unknown'
    for col in ['Discount', 'Quantity']:
        df[col] = pd.to_numeric(df[col], errors='coerce') if col in df else np.nan
    # Do not silently turn unavailable profit, discount or quantity into zero.
    bad_discount = df['Discount'].notna() & (~np.isfinite(df['Discount']) | ~df['Discount'].between(0, 1))
    report['invalid_discounts_ignored'] = int(bad_discount.sum())
    df.loc[bad_discount, 'Discount'] = np.nan
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format=date_format, errors='coerce') if 'Ship Date' in df else pd.NaT
    lag = (df['Ship Date'] - df['Order Date']).dt.days
    report['negative_ship_lags_ignored'] = int(lag.lt(0).sum())
    df['Days to Ship'] = lag.where(lag.ge(0))
    report['valid_rows'] = len(df)
    report['missing_ship_dates'] = int(df['Ship Date'].isna().sum())
    return df.sort_values('Order Date').reset_index(drop=True), report, rejected


def kpis(df):
    sales, profit = df['Sales'].sum(), df['Profit'].sum()
    orders = df['Order ID'].nunique()
    return {'Sales': float(sales), 'Profit': float(profit), 'Orders': int(orders),
            'Customers': int(df['Customer ID'].nunique()),
            'Profit Margin %': float(profit / sales * 100) if sales else None,
            'Average Order Value': float(sales / orders) if orders else None,
            'Loss-making Lines': int(df['Profit'].lt(0).sum())}


def monthly_sales(df):
    if df.empty:
        return pd.DataFrame(columns=['Month', 'Sales', 'Profit'])
    return df.set_index('Order Date')[['Sales', 'Profit']].resample('MS').sum().rename_axis('Month').reset_index()


def breakdown(df, column):
    result = df.groupby(column, dropna=False).agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum'), Orders=('Order ID', 'nunique')).reset_index()
    result['Profit Margin %'] = result['Profit'].div(result['Sales'].replace(0, np.nan)) * 100
    return result.sort_values('Sales', ascending=False)


def customer_rfm(df):
    """Descriptive RFM relative to last selected order date; not churn prediction."""
    ref = df['Order Date'].max() + pd.Timedelta(days=1)
    r = df.groupby('Customer ID').agg(Last_Order=('Order Date', 'max'), Frequency=('Order ID', 'nunique'), Monetary=('Sales', 'sum'), Profit=('Profit', 'sum'))
    r['Recency Days'] = (ref - r.pop('Last_Order')).dt.days
    r['Segment'] = np.select([(r['Recency Days'] <= 90) & (r['Frequency'] >= 2), r['Recency Days'] > 180], ['Active repeat', 'Inactive >180 days'], default='Other')
    return r.sort_values('Monetary', ascending=False).reset_index()


def forecast_sales(df, horizon=6, exclude_last_month=True):
    """Time-ordered holdout, baseline comparison, then future point estimates."""
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    y = monthly_sales(df).set_index('Month')['Sales'].asfreq('MS', fill_value=0)
    if exclude_last_month:
        y = y.iloc[:-1]  # The latest month may be incomplete.
    if len(y) < 18:
        raise ValueError('Forecast needs at least 18 monthly observations after excluding the last month.')
    if horizon < 1 or horizon > 12:
        raise ValueError('Forecast horizon must be 1–12 months.')
    def predict(train, steps):
        seasonal = len(train) >= 24
        model = ExponentialSmoothing(train, trend='add', seasonal='add' if seasonal else None,
                                     seasonal_periods=12 if seasonal else None, initialization_method='estimated').fit(optimized=True)
        return np.maximum(np.asarray(model.forecast(steps)), 0)
    holdout = min(6, len(y) // 4)
    train, actual = y.iloc[:-holdout], y.iloc[-holdout:]
    pred = predict(train, holdout)
    baseline = np.asarray([train.iloc[-12 + i % 12] for i in range(holdout)]) if len(train) >= 12 else np.repeat(train.iloc[-1], holdout)
    mae = float(np.mean(abs(actual.values - pred)))
    base_mae = float(np.mean(abs(actual.values - baseline)))
    chosen = 'Exponential smoothing' if mae <= base_mae else 'Seasonal naive baseline'
    future = predict(y, horizon) if mae <= base_mae else np.asarray([y.iloc[-12 + i % 12] for i in range(horizon)])
    dates = pd.date_range(y.index[-1] + pd.offsets.MonthBegin(1), periods=horizon, freq='MS')
    validation = pd.DataFrame({'Month': actual.index, 'Actual': actual.values, 'Smoothing': pred, 'Baseline': baseline})
    return pd.DataFrame({'Month': dates, 'Forecast Sales': future}), validation, {
        'smoothing_mae': mae, 'baseline_mae': base_mae, 'selected_model': chosen,
        'training_months': len(y), 'holdout_months': holdout, 'last_month_excluded': exclude_last_month}


def insight_text(df):
    k = kpis(df)
    by = breakdown(df, 'Sub-Category')
    loss = by.loc[by['Profit'] < 0, 'Sub-Category'].tolist()
    margin = f"{k['Profit Margin %']:.2f}%" if k['Profit Margin %'] is not None else 'unavailable (zero sales)'
    return '\n'.join(['SALES INSIGHT STUDIO — SELECTED DATA',
        f"Period: {df['Order Date'].min().date()} to {df['Order Date'].max().date()}",
        f"Sales: {k['Sales']:,.2f}; Profit: {k['Profit']:,.2f}; Margin: {margin}",
        f"Unique orders: {k['Orders']:,}; Customers: {k['Customers']:,}; Loss-making lines: {k['Loss-making Lines']:,}",
        'Loss-making sub-categories: ' + (', '.join(loss) if loss else 'None'),
        'Review prices, costs and discounts in loss-making groups before taking action.',
        'Discount associations do not prove causation. Historical spending is not predicted lifetime value.',
        'Ship Date measures dispatch, not customer delivery. Currency is inherited from the source CSV.'])
