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

#pylint: disable=too-few-public-methods
from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware, _sanitize_token, _compare_salted_tokens, get_token
import json

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
            self.scripts = scripts

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


class DPDCsrfViewMiddleware(CsrfViewMiddleware):

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if getattr(request, 'csrf_processing_done', False):
            return None

        # Wait until request.META["CSRF_COOKIE"] has been manipulated before
        # bailing out, so that get_token still works
        if getattr(callback, 'csrf_exempt', False):
            return None

        # Assume that anything not defined as 'safe' by RFC7231 needs protection
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if getattr(request, '_dont_enforce_csrf_checks', False):
                # Mechanism to turn off CSRF checks for test suite.
                # It comes after the creation of CSRF cookies, so that
                # everything else continues to work exactly the same
                # (e.g. cookies are sent, etc.), but before any
                # branches that call reject().
                return self._accept(request)

            if request.is_secure():
                # Suppose user visits http://example.com/
                # An active network attacker (man-in-the-middle, MITM) sends a
                # POST form that targets https://example.com/detonate-bomb/ and
                # submits it via JavaScript.
                #
                # The attacker will need to provide a CSRF cookie and token, but
                # that's no problem for a MITM and the session-independent
                # secret we're using. So the MITM can circumvent the CSRF
                # protection. This is true for any HTTP connection, but anyone
                # using HTTPS expects better! For this reason, for
                # https://example.com/ we need additional protection that treats
                # http://example.com/ as completely untrusted. Under HTTPS,
                # Barth et al. found that the Referer header is missing for
                # same-domain requests in only about 0.2% of cases or less, so
                # we can use strict Referer checking.
                referer = request.META.get('HTTP_REFERER')
                if referer is None:
                    return self._reject(request, REASON_NO_REFERER)

                referer = urlparse(referer)

                # Make sure we have a valid URL for Referer.
                if '' in (referer.scheme, referer.netloc):
                    return self._reject(request, REASON_MALFORMED_REFERER)

                # Ensure that our Referer is also secure.
                if referer.scheme != 'https':
                    return self._reject(request, REASON_INSECURE_REFERER)

                # If there isn't a CSRF_COOKIE_DOMAIN, require an exact match
                # match on host:port. If not, obey the cookie rules (or those
                # for the session cookie, if CSRF_USE_SESSIONS).
                good_referer = (
                    settings.SESSION_COOKIE_DOMAIN
                    if settings.CSRF_USE_SESSIONS
                    else settings.CSRF_COOKIE_DOMAIN
                )
                if good_referer is not None:
                    server_port = request.get_port()
                    if server_port not in ('443', '80'):
                        good_referer = '%s:%s' % (good_referer, server_port)
                else:
                    try:
                        # request.get_host() includes the port.
                        good_referer = request.get_host()
                    except DisallowedHost:
                        pass

                # Create a list of all acceptable HTTP referers, including the
                # current host if it's permitted by ALLOWED_HOSTS.
                good_hosts = list(settings.CSRF_TRUSTED_ORIGINS)
                if good_referer is not None:
                    good_hosts.append(good_referer)

                if not any(is_same_domain(referer.netloc, host) for host in good_hosts):
                    reason = REASON_BAD_REFERER % referer.geturl()
                    return self._reject(request, reason)

            csrf_token = request.META.get('CSRF_COOKIE')
            if csrf_token is None:
                # No CSRF cookie. For POST requests, we insist on a CSRF cookie,
                # and in this way we can avoid all CSRF attacks, including login
                # CSRF.
                return self._reject(request, REASON_NO_CSRF_COOKIE)

            print("App name:")
            print(request.resolver_match.app_name)

            # Check non-cookie token for match.
            request_csrf_token = ""
            if request.method == "POST":
                try:
                    request_csrf_token = request.POST.get('csrfmiddlewaretoken', '')
                except IOError:
                    # Handle a broken connection before we've completed reading
                    # the POST data. process_view shouldn't raise any
                    # exceptions, so we'll ignore and serve the user a 403
                    # (assuming they're still listening, which they probably
                    # aren't because of the error).
                    pass

            if request_csrf_token == "":
                # Fall back to X-CSRFToken, to make things easier for AJAX,
                # and possible for PUT/DELETE.
                request_csrf_token = request.META.get(settings.CSRF_HEADER_NAME, '')

            if request_csrf_token == "undefined" or "" :
                import json
                body = json.loads(request.body.decode('utf-8'))
                for i in body['inputs']:
                    if i['id'] == 'csrfmiddlewaretoken':
                        request_csrf_token = i['value']


            request_csrf_token = _sanitize_token(request_csrf_token)
            if not _compare_salted_tokens(request_csrf_token, csrf_token):
                return self._reject(request, REASON_BAD_TOKEN)

        return self._accept(request)