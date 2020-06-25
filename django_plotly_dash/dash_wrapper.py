'''
dash_wrapper

This module provides a DjangoDash class that can be used to
expose a Plotly Dasb application through a Django server

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

import json
import inspect

import dash
from dash import Dash
from dash._utils import split_callback_id, inputs_to_dict

from flask import Flask

from django.urls import reverse
from django.utils.text import slugify

from plotly.utils import PlotlyJSONEncoder

from .app_name import app_name, main_view_label
from .middleware import EmbeddedHolder

from .util import static_asset_path
from .util import serve_locally as serve_locally_setting
from .util import stateless_app_lookup_hook

try:
    from dataclasses import dataclass
    from typing import Dict, List

    @dataclass(frozen-True)
    class CallbackContext:
        inputs_list : List
        inputs: Dict
        states_list: List
        states: Dict
        outputs_list: List
        outputs: Dict
        triggered: List

except:
    # Not got python 3.7 or dataclasses yet
    class CallbackContext:
        def __init__(self, **kwargs):
            self._args = kwargs

        @property
        def inputs_list(self):
            return self._args['inputs_list']

        @property
        def inputs(self):
            return self._args['inputs']

        @property
        def states_list(self):
            return self._args['states_list']

        @property
        def states(self):
            return self._args['states']

        @property
        def outputs(self):
            return self._args['outputs']

        @property
        def outputs_list(self):
            return self._args['outputs_list']
        @property
        def triggered(self):
            return self._args['triggered']


uid_counter = 0

usable_apps = {}

_stateless_app_lookup_func = None

def add_usable_app(name, app):
    'Add app to local registry by name'
    name = slugify(name)
    global usable_apps # pylint: disable=global-statement
    usable_apps[name] = app
    return name

def all_apps():
    'Return a dictionary of all locally registered apps with the slug name as key'
    return usable_apps

def get_local_stateless_list():
    """Return a list of all locally registered stateless apps
    """
    return list(usable_apps)

def get_local_stateless_by_name(name):
    '''
    Locate a registered dash app by name, and return a DjangoDash instance encapsulating the app.
    '''
    name = slugify(name)

    sa = usable_apps.get(name, None)

    if not sa:

        global _stateless_app_lookup_func # pylint: disable=global-statement

        if _stateless_app_lookup_func is None:
            _stateless_app_lookup_func = stateless_app_lookup_hook()

        sa = _stateless_app_lookup_func(name)

    if not sa:
        # TODO wrap this in raising a 404 if not found
        raise KeyError("Unable to find stateless DjangoApp called %s"%name)

    return sa


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
    #pylint: disable=too-many-instance-attributes
    def __init__(self, name=None, serve_locally=None,
                 expanded_callbacks=False,
                 add_bootstrap_links=False,
                 suppress_callback_exceptions=False,
                 **kwargs): # pylint: disable=unused-argument, too-many-arguments

        if name is None:
            global uid_counter # pylint: disable=global-statement
            uid_counter += 1
            self._uid = "djdash_%i" % uid_counter
        else:
            self._uid = name
        self.layout = None
        self._callback_sets = []
        self._clientside_callback_sets = []

        self.css = Holder()
        self.scripts = Holder()

        add_usable_app(self._uid,
                       self)

        if serve_locally is None:
            self._serve_locally = serve_locally_setting()
        else:
            self._serve_locally = serve_locally

        self._expanded_callbacks = expanded_callbacks
        self._suppress_callback_exceptions = suppress_callback_exceptions

        if add_bootstrap_links:
            from bootstrap4.bootstrap import css_url
            bootstrap_source = css_url()['href']

            if self._serve_locally:
                # Ensure package is loaded; if not present then pip install dpd-static-support
                import dpd_static_support
                hard_coded_package_name = "dpd_static_support"
                base_file_name = bootstrap_source.split('/')[-1]

                self.css.append_script({'external_url':        [bootstrap_source,],
                                        'relative_package_path' : base_file_name,
                                        'namespace':              hard_coded_package_name,
                                        })
            else:
                self.css.append_script({'external_url':[bootstrap_source,],})

        # Remember some caller info for static files
        caller_frame = inspect.stack()[1]
        self.caller_module = inspect.getmodule(caller_frame[0])
        try:
            self.caller_module_location = inspect.getfile(self.caller_module)
        except:
            self.caller_module_location = None
        self.assets_folder = "assets"

    def get_asset_static_url(self, asset_path):
        module_name = self.caller_module.__name__
        return static_asset_path(module_name, asset_path)

    def as_dash_instance(self, cache_id=None):
        '''
        Form a dash instance, for stateless use of this app
        '''
        return self.do_form_dash_instance(cache_id=cache_id)

    def handle_current_state(self):
        'Do nothing impl - only matters if state present'
        pass
    def update_current_state(self, wid, key, value):
        'Do nothing impl - only matters if state present'
        pass
    def have_current_state_entry(self, wid, key):
        'Do nothing impl - only matters if state present'
        pass

    def get_base_pathname(self, specific_identifier, cache_id):
        'Base path name of this instance, taking into account any state or statelessness'
        if not specific_identifier:
            app_pathname = "%s:app-%s"% (app_name, main_view_label)
            ndid = self._uid
        else:
            app_pathname = "%s:%s" % (app_name, main_view_label)
            ndid = specific_identifier

        kwargs = {'ident': ndid}

        if cache_id:
            kwargs['cache_id'] = cache_id
            app_pathname = app_pathname + "--args"

        full_url = reverse(app_pathname, kwargs=kwargs)
        if full_url[-1] != '/':
            full_url = full_url + '/'
        return ndid, full_url

    def do_form_dash_instance(self, replacements=None, specific_identifier=None, cache_id=None):
        'Perform the act of constructing a Dash instance taking into account state'

        ndid, base_pathname = self.get_base_pathname(specific_identifier, cache_id)
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
        rd.config['suppress_callback_exceptions'] = self._suppress_callback_exceptions

        for cb, func in self._callback_sets:
            rd.callback(**cb)(func)
        for cb in self._clientside_callback_sets:
            rd.clientside_callback(**cb)
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

    def clientside_callback(self, clientside_function, output, inputs=None, state=None):
        'Form a callback function by wrapping, in the same way as the underlying Dash application would'
        callback_set = { 'clientside_function': clientside_function,
                         'output': output,
                         'inputs': inputs and inputs or dict(),
                         'state': state and state or dict() }

        self._clientside_callback_sets.append(callback_set)


    def get_asset_url(self, asset_name):
        '''URL of an asset associated with this component

        Use a placeholder and insert later
        '''

        return "assets/" + str(asset_name)

        #return self.as_dash_instance().get_asset_url(asset_name)

class PseudoFlask(Flask):
    'Dummy implementation of a Flask instance, providing stub functionality'
    def __init__(self):
        self.config = {}
        self.endpoints = {}
        self.name = "PseudoFlaskDummyName"
        self.blueprints = {}

    # pylint: disable=unused-argument, missing-docstring

    def after_request(self, *args, **kwargs):
        pass
    def errorhandler(self, *args, **kwargs): # pylint: disable=no-self-use
        def eh_func(f):
            return args[0]
        return eh_func
    def add_url_rule(self, *args, **kwargs):
        route = kwargs['endpoint']
        self.endpoints[route] = kwargs
    def before_first_request(self, *args, **kwargs):
        pass
    def run(self, *args, **kwargs):
        pass
    def register_blueprint(self, *args, **kwargs):
        pass

class WrappedDash(Dash):
    'Wrapper around the Plotly Dash application instance'
    # pylint: disable=too-many-arguments, too-many-instance-attributes
    def __init__(self,
                 base_pathname=None, replacements=None, ndid=None,
                 expanded_callbacks=False, serve_locally=False,
                 **kwargs):

        self._uid = ndid

        self._flask_app = Flask(self._uid)
        self._notflask = PseudoFlask()
        self._base_pathname = base_pathname

        kwargs['url_base_pathname'] = self._base_pathname
        kwargs['server'] = self._notflask

        super(WrappedDash, self).__init__(__name__,
                                          **kwargs)

        self.css.config.serve_locally = serve_locally
        self.scripts.config.serve_locally = serve_locally

        self._adjust_id = False
        self._dash_dispatch = not expanded_callbacks
        if replacements:
            self._replacements = replacements
        else:
            self._replacements = dict()
        self._use_dash_layout = len(self._replacements) < 1

        self._return_embedded = False

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

    def augment_initial_layout(self, base_response, initial_arguments=None):
        'Add application state to initial values'
        if self.use_dash_layout() and not initial_arguments and False:
            return base_response.data, base_response.mimetype

        # Adjust the base layout response
        baseDataInBytes = base_response.data
        baseData = json.loads(baseDataInBytes.decode('utf-8'))

        # Also add in any initial arguments
        if initial_arguments:
            if isinstance(initial_arguments, str):
                initial_arguments = json.loads(initial_arguments)

        # Walk tree. If at any point we have an element whose id
        # matches, then replace any named values at this level
        reworked_data = self.walk_tree_and_replace(baseData, initial_arguments)

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

    def walk_tree_and_replace(self, data, overrides):
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
                replacements = overrides.get(thisID, None) if overrides else None
                if not replacements:
                    replacements = self._replacements.get(thisID, {})
            # walk all keys and replace if needed
            for k, v in data.items():
                r = replacements.get(k, None)
                if r is None:
                    r = self.walk_tree_and_replace(v, overrides)
                response[k] = r
            return response
        if isinstance(data, list):
            # process each entry in turn and return
            return [self.walk_tree_and_replace(x, overrides) for x in data]
        return data

    def flask_app(self):
        'Underlying flask application for stub implementation'
        return self._flask_app

    def base_url(self):
        'Base url of this component'
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
        'Overloaded layout function to fix component names as needed'

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

        if isinstance(output, (list, tuple)):
            fixed_outputs = [self._fix_callback_item(x) for x in output]
        else:
            fixed_outputs = self._fix_callback_item(output)

        return super(WrappedDash, self).callback(fixed_outputs,
                                                 [self._fix_callback_item(x) for x in inputs],
                                                 [self._fix_callback_item(x) for x in state])

    def clientside_callback(self, clientside_function, output, inputs=[], state=[]): # pylint: disable=dangerous-default-value
        'Invoke callback, adjusting variable names as needed'

        if isinstance(output, (list, tuple)):
            fixed_outputs = [self._fix_callback_item(x) for x in output]
            # Temporary check; can be removed once the library has been extended
            raise NotImplementedError("django-plotly-dash cannot handle multiple callback outputs at present")
        else:
            fixed_outputs = self._fix_callback_item(output)

        return super(WrappedDash, self).clientside_callback(clientside_function,
                                                            fixed_outputs,
                                                            [self._fix_callback_item(x) for x in inputs],
                                                            [self._fix_callback_item(x) for x in state])

    def dispatch(self):
        'Perform dispatch, using request embedded within flask global state'
        import flask
        body = flask.request.get_json()
        return self.dispatch_with_args(body, argMap=dict())

    #pylint: disable=too-many-locals
    def dispatch_with_args(self, body, argMap):
        'Perform callback dispatching, with enhanced arguments and recording of response'
        inputs = body.get('inputs', [])
        input_values = inputs_to_dict(inputs)
        states = body.get('state', [])
        output = body['output']
        outputs_list = body.get('outputs') or split_callback_id(output)
        changed_props = body.get('changedPropIds', [])
        triggered_inputs = [{"prop_id": x, "value": input_values.get(x)} for x in changed_props]

        callback_context_info = {
            'inputs_list': inputs,
            'inputs': input_values,
            'states_list': states,
            'states': inputs_to_dict(states),
            'outputs_list': outputs_list,
            'outputs': outputs_list,
            'triggered': triggered_inputs,
            }

        callback_context = CallbackContext(**callback_context_info)

        # Overload dash global variable
        dash.callback_context = callback_context

        # Add context to arg map, if extended callbacks in use
        if len(argMap) > 0:
            argMap['callback_context'] = callback_context

        outputs = []
        try:
            if output[:2] == '..' and output[-2:] == '..':
                # Multiple outputs
                outputs = output[2:-2].split('...')
                target_id = output
                # Special case of a single output
                if len(outputs) == 1:
                    target_id = output[2:-2]
        except:
            pass

        single_case = False
        if len(outputs) < 1:
            try:
                output_id = output['id']
                output_property = output['property']
                target_id = "%s.%s" %(output_id, output_property)
            except:
                target_id = output
                output_id, output_property = output.split(".")
            single_case = True
            outputs = [output,]

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
            for c in states:
                if c['property'] == component_registration['property'] and c['id'] == component_registration['id']:
                    v = c.get('value', None)
                    args.append(v)
                    if da:
                        da.update_current_state(c['id'], c['property'], v)

        # Dash 1.11 introduces a set of outputs
        outputs_list = body.get('outputs') or split_callback_id(output)
        argMap['outputs_list'] = outputs_list

        # Special: intercept case of insufficient arguments
        # This happens when a propery has been updated with a pipe component
        # TODO see if this can be attacked from the client end

        if len(args) < len(self.callback_map[target_id]['inputs']):
            return 'EDGECASEEXIT'

        res = self.callback_map[target_id]['callback'](*args, **argMap)
        if da:
            if single_case and da.have_current_state_entry(output_id, output_property):
                response = json.loads(res.data.decode('utf-8'))
                value = response.get('response', {}).get('props', {}).get(output_property, None)
                da.update_current_state(output_id, output_property, value)

            response = json.loads(res)
            root_value = response.get('response', {})
            for output_item in outputs:
                if isinstance(output_item, str):
                    output_id, output_property = output_item.split('.')
                    if da.have_current_state_entry(output_id, output_property):
                        value = root_value.get(output_id,{}).get(output_property, None)
                        da.update_current_state(output_id, output_property, value)

        return res

    def slugified_id(self):
        'Return the app id in a slug-friendly form'
        pre_slugified_id = self._uid
        return slugify(pre_slugified_id)

    def extra_html_properties(self, prefix=None, postfix=None, template_type=None):
        '''
        Return extra html properties to allow individual apps to be styled separately.

        The content returned from this function is injected unescaped into templates.
        '''

        prefix = prefix if prefix else "django-plotly-dash"

        post_part = "-%s" % postfix if postfix else ""
        template_type = template_type if template_type else "iframe"

        slugified_id = self.slugified_id()

        return "%(prefix)s %(prefix)s-%(template_type)s %(prefix)s-app-%(slugified_id)s%(post_part)s" % {'slugified_id':slugified_id,
                                                                                                         'post_part':post_part,
                                                                                                         'template_type':template_type,
                                                                                                         'prefix':prefix,
                                                                                                        }

    def index(self, *args, **kwargs):  # pylint: disable=unused-argument
        scripts = self._generate_scripts_html()
        css = self._generate_css_dist_html()
        config = self._generate_config_html()
        metas = self._generate_meta_html()
        renderer = self._generate_renderer()
        title = getattr(self, 'title', 'Dash')
        if self._favicon:
            import flask
            favicon = '<link rel="icon" type="image/x-icon" href="{}">'.format(
                flask.url_for('assets.static', filename=self._favicon))
        else:
            favicon = ''

            _app_entry = '''
<div id="react-entry-point">
  <div class="_dash-loading">
    Loading...
  </div>
</div>
'''
        index = self.interpolate_index(
            metas=metas, title=title, css=css, config=config,
            scripts=scripts, app_entry=_app_entry, favicon=favicon,
            renderer=renderer)

        return index

    def interpolate_index(self, **kwargs): #pylint: disable=arguments-differ

        if not self._return_embedded:
            resp = super(WrappedDash, self).interpolate_index(**kwargs)
            return resp

        self._return_embedded.add_css(kwargs['css'])
        self._return_embedded.add_config(kwargs['config'])
        self._return_embedded.add_scripts(kwargs['scripts'])

        return kwargs['app_entry']

    def set_embedded(self, embedded_holder=None):
        'Set a handler for embedded references prior to evaluating a view function'
        self._return_embedded = embedded_holder if embedded_holder else EmbeddedHolder()

    def exit_embedded(self):
        'Exit the embedded section after processing a view'
        self._return_embedded = False
