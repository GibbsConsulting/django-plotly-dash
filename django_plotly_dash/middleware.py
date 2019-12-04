'''
Django-plotly-dash middleware

This middleware enables the collection of items from templates for inclusion in the header and footer

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

from .util import serve_locally, static_path

#pylint: disable=too-few-public-methods

class EmbeddedHolder:
    'Hold details of embedded content from processing a view'
    def __init__(self):
        self.css = ""
        self.config = ""
        self.scripts = ""
    def add_css(self, css):
        'Add css content'
        if css:
            self.css = css
    def add_config(self, config):
        'Add config content'
        if config:
            self.config = config
    def add_scripts(self, scripts):
        'Add js content'
        if scripts:
            self.scripts += scripts

class ContentCollector:
    '''
    Collect content during view processing, and substitute in response by finding magic strings.

    This enables view functionality, such as template tags, to introduce content such as css and js
    inclusion into the header and footer.
    '''
    def __init__(self):
        self.header_placeholder = "DJANGO_PLOTLY_DASH_HEADER_PLACEHOLDER"
        self.footer_placeholder = "DJANGO_PLOTLY_DASH_FOOTER_PLACEHOLDER"

        self.embedded_holder = EmbeddedHolder()
        self._encoding = "utf-8"

    def adjust_response(self, response):
        'Locate placeholder magic strings and replace with content'

        try:
            c1 = self._replace(response.content,
                               self.header_placeholder,
                               self.embedded_holder.css)

            response.content = self._replace(c1,
                                             self.footer_placeholder,
                                             "\n".join([self.embedded_holder.config,
                                                        self.embedded_holder.scripts]))
        except AttributeError:
            # Catch the "FileResponse instance has no `content` attribute" error when serving media files in the Django development server.
            pass

        return response

    def _replace(self, content, placeholder, substitution):
        return content.replace(self._encode(placeholder),
                               self._encode(substitution if substitution else ""))

    def _encode(self, string):
        return string.encode(self._encoding)

class BaseMiddleware:
    'Django-plotly-dash middleware'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request.dpd_content_handler = ContentCollector()
        response = self.get_response(request)
        response = request.dpd_content_handler.adjust_response(response)

        return response


# Bootstrap4 substitutions, if available
dpd_substitutions = []
try:
    from dpd_static_support.mappings import substitutions as dpd_direct_substitutions
    dpd_substitutions += dpd_direct_substitutions
    from dpd_static_support.mappings import static_substitutions as dpd_ss_substitutions
    dpd_substitutions += [(x, static_path(y)) for x, y in dpd_ss_substitutions]
except Exception as e:
    pass


class ExternalRedirectionMiddleware:
    'Middleware to force redirection in third-party content through rewriting'

    def __init__(self, get_response):
        self.get_response = get_response

        substitutions = []

        if serve_locally():
            substitutions += dpd_substitutions

        self._encoding = "utf-8"

        self.substitutions = [(self._encode(source),
                               self._encode(target)) for source, target in substitutions]

    def __call__(self, request):

        response = self.get_response(request)

        try:
            content = response.content

            for source, target in self.substitutions:
                content = content.replace(source, target)

            response.content = content

        except AttributeError:
            # Not all files can contain substitutions, so ignore them
            pass

        return response

    def _encode(self, string):
        return string.encode(self._encoding)

