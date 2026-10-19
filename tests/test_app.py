from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / 'app.py')

def test_dashboard_and_forecast():
    app = AppTest.from_file(APP).run(timeout=60)
    assert not app.exception
    assert len(app.metric) == 4
    app.button[0].click().run(timeout=60)
    assert not app.exception
    assert any('Exponential smoothing' in x.value or 'Seasonal naive' in x.value for x in app.json)


def test_empty_filter_and_missing_dates_are_handled():
    app = AppTest.from_file(APP).run(timeout=60)
    app.multiselect[0].set_value([]).run(timeout=60)
    assert not app.exception
    assert any('No rows' in w.value for w in app.warning)
    app = AppTest.from_file(APP).run(timeout=60)
    app.date_input[0].set_value((app.date_input[0].value[0],)).run(timeout=60)
    assert not app.exception
    assert any('both' in i.value for i in app.info)
