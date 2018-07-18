'''
Test django_plotly_dash functionality by use of demo pages
'''

import pytest

@pytest.mark.django_db
def test_template_tag_use(client):
    'Check use of template tag'

    from django.urls import reverse

    for name in ['demo-one', 'demo-two', 'demo-three', 'demo-four',]:
        url = reverse(name, kwargs={})

        response = client.get(url)

        assert response.content
        assert response.status_code == 200
