"""Export reports without opening the dashboard."""
import argparse
import json
from pathlib import Path
from analysis import SAMPLE, load_data, monthly_sales, breakdown, customer_rfm, insight_text, forecast_sales

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--csv', type=Path, default=SAMPLE)
    p.add_argument('--output', type=Path, default=Path('reports'))
    p.add_argument('--date-format', default='mixed')
    p.add_argument('--forecast', action='store_true')
    a = p.parse_args()
    df, quality, rejected = load_data(a.csv, a.date_format)
    a.output.mkdir(parents=True, exist_ok=True)
    (a.output / 'summary.txt').write_text(insight_text(df), encoding='utf-8')
    (a.output / 'quality.json').write_text(json.dumps(quality, indent=2), encoding='utf-8')
    monthly_sales(df).to_csv(a.output / 'monthly.csv', index=False)
    customer_rfm(df).to_csv(a.output / 'customers_rfm.csv', index=False)
    rejected.to_csv(a.output / 'excluded_rows.csv', index=False)
    for col in ['Category', 'Sub-Category', 'Region', 'Segment']:
        breakdown(df, col).to_csv(a.output / (col.lower().replace(' ', '_') + '.csv'), index=False)
    if a.forecast:
        try:
            future, validation, stats = forecast_sales(df)
            future.to_csv(a.output / 'forecast.csv', index=False)
            validation.to_csv(a.output / 'forecast_holdout.csv', index=False)
            (a.output / 'forecast_metrics.json').write_text(json.dumps(stats, indent=2), encoding='utf-8')
        except ValueError as e:
            (a.output / 'forecast_unavailable.txt').write_text(str(e), encoding='utf-8')
    print(insight_text(df))
    print('Reports saved:', a.output.resolve())

if __name__ == '__main__':
    main()
