'''
Test django_plotly_dash functionality by use of demo pages

Copyright (c) 2018 Gibbs Consulting and others - see CONTRIBUTIONS.md

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
import re

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

        for src in re.findall('iframe src="(.*?)"', response.content.decode("utf-8")):
            response = client.get(src + "_dash-layout")
            assert response.status_code == 200, ""


@pytest.mark.django_db
def test_add_to_session(client):
    'Check use of session variable access helper'

    url = reverse('session-variable-example')
    response = client.get(url)

    assert response.content
    assert response.status_code == 200
