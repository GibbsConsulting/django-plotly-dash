'''dash_wrapper

This module provides a DjangoDash class that can be used to
expose a Plotly Dasb application through a Django server
'''

import json

from dash import Dash
from flask import Flask

from django.urls import reverse
from django.utils.text import slugify

from plotly.utils import PlotlyJSONEncoder

from .app_name import app_name, main_view_label

uid_counter = 0

usable_apps = {}

def add_usable_app(name, app):
    'Add app to local registry by name'
    name = slugify(name)
    global usable_apps # pylint: disable=global-statement
    usable_apps[name] = app
    return name

def get_local_stateless_by_name(name):
    '''
    Locate a registered dash app by name, and return a DjangoDash instance encapsulating the app.
    '''
    name = slugify(name)
    # TODO wrap this in raising a 404 if not found
    return usable_apps[name]

class Holder:
    'Helper class for holding configuration options'
    def __init__(self):
        self.items = []
    def append_css(self, stylesheet):
        'Add extra css file name to component package'
        self.items.append(stylesheet)
    def append_script(self, script):
        'Add extra script file name to component package'
        self.items.append(script)

class DjangoDash:
    '''
    Wrapper class that provides Dash functionality in a form that can be served by Django

    To use, construct an instance of DjangoDash() in place of a Dash() one.
    '''
    def __init__(self, name=None, serve_locally=False,
                 expanded_callbacks=False,
                 add_bootstrap_links=False,
                 **kwargs): # pylint: disable=unused-argument
        if name is None:
            global uid_counter # pylint: disable=global-statement
            uid_counter += 1
            self._uid = "djdash_%i" % uid_counter
        else:
            self._uid = name
        self.layout = None
        self._callback_sets = []

        self.css = Holder()
        self.scripts = Holder()

        add_usable_app(self._uid,
                       self)

        self._expanded_callbacks = expanded_callbacks
        self._serve_locally = serve_locally

        if add_bootstrap_links:
            from bootstrap4.bootstrap import css_url
            bootstrap_source = css_url()['href']
            self.css.append_script({'external_url':[bootstrap_source,]})

    def as_dash_instance(self):
        '''
        Form a dash instance, for stateless use of this app
        '''
        return self.do_form_dash_instance()

    def handle_current_state(self):
        'Do nothing impl - only matters if state present'
        pass
    def update_current_state(self, wid, key, value):
        'Do nothing impl - only matters if state present'
        pass
    def have_current_state_entry(self, wid, key):
        'Do nothing impl - only matters if state present'
        pass

    def get_base_pathname(self, specific_identifier):
        'Base path name of this instance, taking into account any state or statelessness'
        if not specific_identifier:
            app_pathname = "%s:app-%s"% (app_name, main_view_label)
            ndid = self._uid
        else:
            app_pathname = "%s:%s" % (app_name, main_view_label)
            ndid = specific_identifier

        full_url = reverse(app_pathname, kwargs={'ident':ndid})
        return ndid, full_url

    def do_form_dash_instance(self, replacements=None, specific_identifier=None):
        'Perform the act of constructing a Dash instance taking into account state'

        ndid, base_pathname = self.get_base_pathname(specific_identifier)
        return self.form_dash_instance(replacements, ndid, base_pathname)

    def form_dash_instance(self, replacements=None, ndid=None, base_pathname=None):
        'Construct a Dash instance taking into account state'

        if ndid is None:
            ndid = self._uid

        rd = WrappedDash(base_pathname=base_pathname,
                         expanded_callbacks=self._expanded_callbacks,
                         replacements=replacements,
                         ndid=ndid,
                         serve_locally=self._serve_locally)

        rd.layout = self.layout

        for cb, func in self._callback_sets:
            rd.callback(**cb)(func)
        for s in self.css.items:
            rd.css.append_css(s)
        for s in self.scripts.items:
            rd.scripts.append_script(s)

        return rd

    def callback(self, output, inputs=None, state=None, events=None):
        'Form a callback function by wrapping, in the same way as the underlying Dash application would'
        callback_set = {'output':output,
                        'inputs':inputs and inputs or dict(),
                        'state':state and state or dict(),
                        'events':events and events or dict()}
        def wrap_func(func, callback_set=callback_set, callback_sets=self._callback_sets): # pylint: disable=dangerous-default-value, missing-docstring
            callback_sets.append((callback_set, func))
            return func
        return wrap_func

    def expanded_callback(self, output, inputs=[], state=[], events=[]): # pylint: disable=dangerous-default-value
        '''
        Form an expanded callback.

        This function registers the callback function, and sets an internal flag that mandates that all
        callbacks are passed the enhanced arguments.
        '''
        self._expanded_callbacks = True
        return self.callback(output, inputs, state, events)

class PseudoFlask:
    'Dummy implementation of a Flask instance, providing stub functionality'
    def __init__(self):
        self.config = {}
        self.endpoints = {}

    # pylint: disable=unused-argument, missing-docstring

    def after_request(self, *args, **kwargs):
        pass
    def errorhandler(self, *args, **kwargs): # pylint: disable=no-self-use
        return args[0]
    def add_url_rule(self, *args, **kwargs):
        route = kwargs['endpoint']
        self.endpoints[route] = kwargs
    def before_first_request(self, *args, **kwargs):
        pass
    def run(self, *args, **kwargs):
        pass
    def register_blueprint(*args, **kwargs):
        pass

class WrappedDash(Dash):
    'Wrapper around the Plotly Dash application instance'
    # pylint: disable=too-many-arguments, too-many-instance-attributes
    def __init__(self,
                 base_pathname=None, replacements=None, ndid=None,
                 expanded_callbacks=False, serve_locally=False, **kwargs):

        self._uid = ndid

        self._flask_app = Flask(self._uid)
        self._notflask = PseudoFlask()
        self._base_pathname = base_pathname

        kwargs['url_base_pathname'] = self._base_pathname
        kwargs['server'] = self._notflask

        super(WrappedDash, self).__init__(**kwargs)

        self.css.config.serve_locally = serve_locally
        self.scripts.config.serve_locally = serve_locally

        self._adjust_id = False
        self._dash_dispatch = not expanded_callbacks
        if replacements:
            self._replacements = replacements
        else:
            self._replacements = dict()
        self._use_dash_layout = len(self._replacements) < 1

    def use_dash_dispatch(self):
        'Indicate if dispatch is using underlying dash code or the wrapped code'
        return self._dash_dispatch

    def use_dash_layout(self):
        '''
        Indicate if the underlying dash layout can be used.

        If application state is in use, then the underlying dash layout functionality has to be
        augmented with the state information and this function returns False
        '''
        return self._use_dash_layout

    def augment_initial_layout(self, base_response):
        'Add application state to initial values'
        if self.use_dash_layout() and False:
            return base_response.data, base_response.mimetype
        # Adjust the base layout response
        baseDataInBytes = base_response.data
        baseData = json.loads(baseDataInBytes.decode('utf-8'))
        # Walk tree. If at any point we have an element whose id
        # matches, then replace any named values at this level
        reworked_data = self.walk_tree_and_replace(baseData)
        response_data = json.dumps(reworked_data,
                                   cls=PlotlyJSONEncoder)

        return response_data, base_response.mimetype

    def walk_tree_and_extract(self, data, target):
        'Walk tree of properties and extract identifiers and associated values'
        if isinstance(data, dict):
            for key in ['children', 'props',]:
                self.walk_tree_and_extract(data.get(key, None), target)
            ident = data.get('id', None)
            if ident is not None:
                idVals = target.get(ident, {})
                for key, value in data.items():
                    if key not in ['props', 'options', 'children', 'id']:
                        idVals[key] = value
                if idVals:
                    target[ident] = idVals
        if isinstance(data, list):
            for element in data:
                self.walk_tree_and_extract(element, target)

    def walk_tree_and_replace(self, data):
        '''
        Walk the tree. Rely on json decoding to insert instances of dict and list
        ie we use a dna test for anatine, rather than our eyes and ears...
        '''
        if isinstance(data, dict):
            response = {}
            replacements = {}
            # look for id entry
            thisID = data.get('id', None)
            if thisID is not None:
                replacements = self._replacements.get(thisID, {})
            # walk all keys and replace if needed
            for k, v in data.items():
                r = replacements.get(k, None)
                if r is None:
                    r = self.walk_tree_and_replace(v)
                response[k] = r
            return response
        if isinstance(data, list):
            # process each entry in turn and return
            return [self.walk_tree_and_replace(x) for x in data]
        return data

    def flask_app(self):
        'Underlying flask application for stub implementation'
        return self._flask_app

    def base_url(self):
        'Base url of this omponent'
        return self._base_pathname

    def app_context(self, *args, **kwargs):
        'Extract application context from underlying flask application'
        return self._flask_app.app_context(*args,
                                           **kwargs)

    def test_request_context(self, *args, **kwargs):
        'Request context for testing from underluying flask application'
        return self._flask_app.test_request_context(*args,
                                                    **kwargs)

    def locate_endpoint_function(self, name=None):
        'Locate endpoint function given name of view'
        if name is not None:
            ep = "%s_%s" %(self._base_pathname,
                           name)
        else:
            ep = self._base_pathname
        return self._notflask.endpoints[ep]['view_func']

    # pylint: disable=no-member
    @Dash.layout.setter
    def layout(self, value):
        'Overloaded layoyt function to fix component names as needed'

        if self._adjust_id:
            self._fix_component_id(value)
        return Dash.layout.fset(self, value)

    def _fix_component_id(self, component):
        'Fix name of component ad all of its children'

        theID = getattr(component, "id", None)
        if theID is not None:
            setattr(component, "id", self._fix_id(theID))
        try:
            for c in component.children:
                self._fix_component_id(c)
        except: #pylint: disable=bare-except
            pass

    def _fix_id(self, name):
        'Adjust identifier to include component name'
        if not self._adjust_id:
            return name
        return "%s_-_%s" %(self._uid,
                           name)

    def _fix_callback_item(self, item):
        'Update component identifier'
        item.component_id = self._fix_id(item.component_id)
        return item

    def callback(self, output, inputs=[], state=[], events=[]): # pylint: disable=dangerous-default-value
        'Invoke callback, adjusting variable names as needed'
        return super(WrappedDash, self).callback(self._fix_callback_item(output),
                                                 [self._fix_callback_item(x) for x in inputs],
                                                 [self._fix_callback_item(x) for x in state],
                                                 [self._fix_callback_item(x) for x in events])

    def dispatch(self):
        'Perform dispatch, using request embedded within flask global state'
        import flask
        body = flask.request.get_json()
        return self. dispatch_with_args(body, argMap=dict())

    #pylint: disable=too-many-locals
    def dispatch_with_args(self, body, argMap):
        'Perform callback dispatching, with enhanced arguments and recording of response'
        inputs = body.get('inputs', [])
        state = body.get('state', [])
        output = body['output']

        target_id = '{}.{}'.format(output['id'], output['property'])
        args = []

        da = argMap.get('dash_app', None)

        for component_registration in self.callback_map[target_id]['inputs']:
            for c in inputs:
                if c['property'] == component_registration['property'] and c['id'] == component_registration['id']:
                    v = c.get('value', None)
                    args.append(v)
                    if da:
                        da.update_current_state(c['id'], c['property'], v)

        for component_registration in self.callback_map[target_id]['state']:
            for c in state:
                if c['property'] == component_registration['property'] and c['id'] == component_registration['id']:
                    v = c.get('value', None)
                    args.append(v)
                    if da:
                        da.update_current_state(c['id'], c['property'], v)

        # Special: intercept case of insufficient arguments
        # This happens when a propery has been updated with a pipe component
        # TODO see if this can be attacked from the client end

        if len(args) < len(self.callback_map[target_id]['inputs']):
            return 'EDGECASEEXIT'

        res = self.callback_map[target_id]['callback'](*args, **argMap)
        if da and da.have_current_state_entry(output['id'], output['property']):
            response = json.loads(res.data.decode('utf-8'))
            value = response.get('response', {}).get('props', {}).get(output['property'], None)
            da.update_current_state(output['id'], output['property'], value)

        return res
