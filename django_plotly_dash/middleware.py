'''
Django-plotly-dash middleware

This middleware enables the collection of items from templates for inclusion in the header and footer
'''

class EmbeddedHolder(object):
    def __init__(self):
        self.css = ""
        self.config = ""
        self.scripts = ""
    def add_css(self, css):
        if css:
            self.css = css
    def add_config(self, config):
        if config:
            self.config = config
    def add_scripts(self, scripts):
        if scripts:
            self.scripts = scripts

class ContentCollector:
    def __init__(self):
        self.header_placeholder = "DJANGO_PLOTLY_DASH_HEADER_PLACEHOLDER"
        self.footer_placeholder = "DJANGO_PLOTLY_DASH_FOOTER_PLACEHOLDER"

        self.embedded_holder = EmbeddedHolder()
        self._encoding = "utf-8"

    def adjust_response(self, response):

        c1 = self._replace(response.content,
                           self.header_placeholder,
                           self.embedded_holder.css)

        response.content = self._replace(c1,
                                         self.footer_placeholder,
                                         "\n".join([self.embedded_holder.config,
                                                    self.embedded_holder.scripts]))

        return response

    def _replace(self, content, placeholder, substitution):
        return content.replace(self._encode(placeholder),
                               self._encode(substitution if substitution else ""))

    def _encode(self, string):
        return string.encode(self._encoding)

class BaseMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request.dpd_content_handler = ContentCollector()
        response = self.get_response(request)
        response = request.dpd_content_handler.adjust_response(response)

        return response
