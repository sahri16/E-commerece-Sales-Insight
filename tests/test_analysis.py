import io
import numpy as np
import pandas as pd
import pytest
from analysis import load_data, kpis, monthly_sales, customer_rfm, forecast_sales


def csv(text):
    return io.BytesIO(text.encode())


def test_sample_known_totals_and_order_grain():
    d, q, _ = load_data()
    k = kpis(d)
    assert len(d) == 9994
    assert k['Sales'] == pytest.approx(2297200.8603)
    assert k['Profit'] == pytest.approx(286397.0217)
    assert k['Orders'] == 5009
    assert k['Customers'] == 793
    assert len(monthly_sales(d)) == 48
    assert q['invalid_rows_excluded'] == 0


def test_validation_preserves_lines_and_losses():
    d, q, rejected = load_data(csv('Order ID,Order Date,Customer ID,Sales,Profit,Ship Date,Discount\na,2024-01-01,x,10,-2,2023-12-31,2\na,2024-01-01,x,10,-2,2023-12-31,2\na,2024-01-01,x,20,3,2024-01-03,0.2\nb,bad,y,5,1,,0\nc,2024-01-02,z,inf,1,,0\nd,2024-01-03,z,-1,1,,0\n'))
    assert len(d) == 2 and len(rejected) == 3
    assert q['exact_duplicates_removed'] == 1
    assert q['negative_ship_lags_ignored'] == 1
    assert q['invalid_discounts_ignored'] == 1
    assert d.iloc[0]['Profit'] == -2
    assert pd.isna(d.iloc[0]['Days to Ship'])
    assert kpis(d)['Average Order Value'] == 30


def test_missing_columns_actionable():
    with pytest.raises(ValueError, match='Missing columns'):
        load_data(csv('Sales\n10\n'))


def test_optional_fields_and_date_format():
    d, _, _ = load_data(csv('Order ID,Order Date,Customer ID,Sales,Profit\na,04/05/2024,x,0,0\n'), '%d/%m/%Y')
    assert d.iloc[0]['Order Date'] == pd.Timestamp('2024-05-04')
    assert d.iloc[0]['Category'] == 'Unknown'
    assert kpis(d)['Profit Margin %'] is None
    assert customer_rfm(d).iloc[0]['Recency Days'] == 1


def test_months_are_not_combined_across_years():
    d, _, _ = load_data(csv('Order ID,Order Date,Customer ID,Sales,Profit\na,2023-01-01,x,10,1\nb,2024-01-01,x,20,2\n'))
    m = monthly_sales(d)
    assert len(m) == 13
    assert m.iloc[0]['Sales'] == 10 and m.iloc[-1]['Sales'] == 20
    assert m.iloc[1]['Sales'] == 0


def test_forecast_is_future_and_holdout_is_chronological():
    d, _, _ = load_data()
    future, validation, stats = forecast_sales(d, 6)
    assert len(future) == 6 and len(validation) == 6
    assert future['Month'].min() > validation['Month'].max()
    assert future['Month'].min() == pd.Timestamp('2017-12-01')
    assert np.isfinite(future['Forecast Sales']).all()
    assert future['Forecast Sales'].ge(0).all()
    assert stats['training_months'] == 47
    assert stats['smoothing_mae'] >= 0 and stats['baseline_mae'] >= 0
    full, _, _ = forecast_sales(d, 12, False)
    assert full['Month'].min() == pd.Timestamp('2018-01-01')


def test_short_forecast_message():
    d, _, _ = load_data()
    with pytest.raises(ValueError, match='18 monthly'):
        forecast_sales(d.head(20))
