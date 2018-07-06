'''
Tests of django_plotly_dash.

These tests can be directly used or imported into eg the tests of the demo app
'''

def test_dash_app():
    'Test the import and formation of the dash app orm wrappers'

    from django_plotly_dash.models import StatelessApp
    sa = StatelessApp(app_name="Some name")

    assert sa
    assert sa.app_name

