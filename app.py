"""Run using python -m streamlit run app.py."""
import io
import zipfile
import pandas as pd
import plotly.express as px
import streamlit as st
from analysis import load_data, kpis, monthly_sales, breakdown, customer_rfm, forecast_sales, insight_text, SAMPLE

st.set_page_config(page_title='Sales Insight Studio', page_icon='📊', layout='wide')
st.title('Sales Insight Studio')
st.caption('Your sales, profit and customer trends — in one workspace.')
st.sidebar.header('Your workspace')
source = st.sidebar.file_uploader('Upload your sales CSV', type=['csv'])
st.sidebar.caption('Without an upload, the bundled Superstore sample is used.')
fmt = st.sidebar.selectbox('Date format', ['US / mixed (month first)', 'DD/MM/YYYY', 'YYYY-MM-DD'])
date_format = {'US / mixed (month first)': 'mixed', 'DD/MM/YYYY': '%d/%m/%Y', 'YYYY-MM-DD': '%Y-%m-%d'}[fmt]
try:
    data, quality, rejected = load_data(io.BytesIO(source.getvalue()) if source else SAMPLE, date_format)
except (ValueError, pd.errors.ParserError, UnicodeError) as e:
    st.error(str(e)); st.info('Required columns: Order ID, Order Date, Customer ID, Sales, Profit. See data/upload_template.csv.'); st.stop()
st.sidebar.caption('Source: ' + (source.name if source else 'Superstore sample (historical demo, not your shop)'))
period = st.sidebar.date_input('Order date range', value=(data['Order Date'].min().date(), data['Order Date'].max().date()), min_value=data['Order Date'].min().date(), max_value=data['Order Date'].max().date())
filtered = data.copy()
if len(period) == 2:
    filtered = filtered[filtered['Order Date'].dt.date.between(*period)]
else:
    st.info('Select both the start and end date.'); st.stop()
for col in ['Region', 'Category', 'Segment']:
    opts = sorted(data[col].unique())
    selected = st.sidebar.multiselect(col, opts, default=opts)
    filtered = filtered[filtered[col].isin(selected)]
if filtered.empty:
    st.warning('No rows match these filters. Expand your dates or select a group.'); st.stop()
unit = st.sidebar.text_input('Currency / unit label', value='source currency', max_chars=20)
st.sidebar.caption('This label does not convert amounts.')
k = kpis(filtered)
metrics = st.columns(4)
for box, name in zip(metrics, ['Sales', 'Profit', 'Orders', 'Customers']):
    box.metric(name, f'{k[name]:,.2f}' if name in ['Sales', 'Profit'] else f'{k[name]:,}')
st.caption(f"Amounts: {unit} · Profit margin: {k['Profit Margin %']:.2f}%" if k['Profit Margin %'] is not None else f'Amounts: {unit} · Margin unavailable (zero sales)')
st.caption(f"Average selected-order value: {k['Average Order Value']:,.2f} · Loss-making lines: {k['Loss-making Lines']:,}")
tabs = st.tabs(['Overview', 'Products & discounts', 'Customers', 'Forecast', 'Data & downloads'])
with tabs[0]:
    monthly = monthly_sales(filtered)
    st.plotly_chart(px.line(monthly, x='Month', y=['Sales', 'Profit'], markers=True, title='Monthly performance (year preserved)'), use_container_width=True)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.bar(breakdown(filtered, 'Category'), x='Category', y=['Sales', 'Profit'], barmode='group', title='Category performance'), use_container_width=True)
    with col2:
        st.plotly_chart(px.bar(breakdown(filtered, 'Region'), x='Region', y='Profit', title='Profit by region'), use_container_width=True)
    st.text(insight_text(filtered))
    shipping = filtered.groupby(['Order ID', 'Ship Mode'], as_index=False)['Days to Ship'].max().groupby('Ship Mode', as_index=False)['Days to Ship'].mean().dropna()
    if not shipping.empty:
        st.plotly_chart(px.bar(shipping, x='Ship Mode', y='Days to Ship', title='Average dispatch lag by order and ship mode'), use_container_width=True)
        st.caption('For split shipments, uses the latest dispatch per order/mode. This is not delivery time.')
with tabs[1]:
    products = breakdown(filtered, 'Sub-Category')
    st.plotly_chart(px.bar(products, x='Sub-Category', y='Profit', color='Profit', color_continuous_scale='RdYlGn', title='Profit / loss by sub-category'), use_container_width=True)
    st.dataframe(products, use_container_width=True, hide_index=True)
    discounts = filtered.dropna(subset=['Discount'])
    if not discounts.empty:
        st.plotly_chart(px.scatter(discounts, x='Discount', y='Profit', color='Category', title='Discount and line profit'), use_container_width=True)
        st.caption('Discount is a fraction: 0.20 means 20%. Association does not establish a causal effect.')
with tabs[2]:
    rfm = customer_rfm(filtered)
    st.caption('Historical spending and descriptive recency/frequency. Recency is relative to the latest selected order + 1 day. Segments use simple 90/180-day rules; this is not a churn prediction model.')
    st.dataframe(rfm, use_container_width=True, hide_index=True)
    st.plotly_chart(px.bar(rfm.head(10), x='Customer ID', y='Monetary', title='Top customers by observed sales'), use_container_width=True)
with tabs[3]:
    st.caption('Forecast uses the current filters. Missing months count as zero; only use this when the export covers the full period. Narrow filters and partial months can distort results.')
    horizon = st.slider('Months ahead', 1, 12, 6)
    exclude = st.checkbox('Exclude latest month (may be incomplete)', value=True)
    if st.button('Calculate forecast'):
        try:
            future, validation, stats = forecast_sales(filtered, horizon, exclude)
            st.write(stats)
            st.plotly_chart(px.line(future, x='Month', y='Forecast Sales', markers=True, title='Future point estimates'), use_container_width=True)
            st.plotly_chart(px.line(validation, x='Month', y=['Actual', 'Smoothing', 'Baseline'], title='Chronological holdout comparison'), use_container_width=True)
            st.dataframe(future, hide_index=True)
            st.download_button('Download forecast CSV', future.to_csv(index=False), 'forecast.csv', 'text/csv')
            st.caption('MAE is in source currency; lower is better. Selects the lower holdout MAE. One holdout is a limited estimate, not a guarantee. No confidence intervals are estimated.')
        except (ValueError, RuntimeError) as e:
            st.warning(str(e))
with tabs[4]:
    st.subheader('Source data quality')
    st.json(quality)
    st.caption('Quality counts refer to the entire uploaded source, before filters. Exact duplicate rows are removed; distinct order lines remain. Invalid required fields are excluded; negative profit is retained.')
    st.dataframe(filtered.head(500), use_container_width=True, hide_index=True)
    st.download_button('Download selected clean data', filtered.to_csv(index=False), 'clean_sales.csv', 'text/csv')
    if not rejected.empty:
        st.download_button('Download excluded rows', rejected.to_csv(index=False), 'excluded_rows.csv', 'text/csv')
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('summary.txt', insight_text(filtered))
        z.writestr('monthly.csv', monthly_sales(filtered).to_csv(index=False))
        z.writestr('customers_rfm.csv', customer_rfm(filtered).to_csv(index=False))
        for dim in ['Category', 'Sub-Category', 'Region', 'Segment']:
            z.writestr(dim.lower().replace(' ', '_') + '.csv', breakdown(filtered, dim).to_csv(index=False))
    st.download_button('Download analysis report ZIP', output.getvalue(), 'sales_report.zip', 'application/zip')
    st.info('Runs locally. Uploaded data stays in this Python process; the app does not save uploads or send them to an analytics API.')
