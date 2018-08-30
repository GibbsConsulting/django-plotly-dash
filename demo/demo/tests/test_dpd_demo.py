'''
Test django_plotly_dash functionality by use of demo pages
'''

import pytest

from django.urls import reverse

@pytest.mark.django_db
def test_template_tag_use(client):
    'Check use of template tag'

    for name in ['demo-one', 'demo-two', 'demo-three', 'demo-four', 'demo-five', 'demo-six',]:
        url = reverse(name, kwargs={})

        response = client.get(url)

        assert response.content
        assert response.status_code == 200

@pytest.mark.django_db
def test_add_to_session(client):
    'Check use of session variable access helper'

    url = reverse('session-variable-example')
    response = client.get(url)

    assert response.content
    assert response.status_code == 200
