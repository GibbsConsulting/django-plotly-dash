from dash import Dash
from flask import Flask

from django.urls import reverse

from .app_name import app_name

uid_counter = 0

usable_apps = {}
app_instances = {}
nd_apps = {}

def get_app_by_name(name):
    '''
    Locate a registered dash app by name, and return a DelayedDash instance encapsulating the app.
    '''
    return usable_apps.get(name,None)

def get_app_instance_by_id(id):
    '''
    Locate an instance of a dash app by identifier, or return None if one does not exist
    '''
    return nd_apps.get(id,None)

def get_or_form_app(id, name, **kwargs):
    '''
    Locate an instance of a dash app by identifier, loading or creating a new instance if needed
    '''
    app = get_app_instance_by_id(id)
    if app:
        return app
    dd = get_app_by_name(name)
    return dd.form_dash_instance()

class Holder:
    def __init__(self):
        self.items = []
    def append_css(self, stylesheet):
        self.items.append(stylesheet)
    def append_script(self, script):
        self.items.append(script)

class DelayedDash:
    def __init__(self, name=None, **kwargs):
        if name is None:
            global uid_counter
            uid_counter += 1
            self._uid = "djdash_%i" % uid_counter
        else:
            self._uid = name
        self.layout = None
        self._callback_sets = []

        self.css = Holder()
        self.scripts = Holder()

        global usable_apps
        usable_apps[self._uid] = self

    def form_dash_instance(self):
        rd = NotDash(name_root=self._uid,
                     app_pathname="%s:main" % app_name)
        rd.layout = self.layout

        for cb, func in self._callback_sets:
            rd.callback(**cb)(func)
        for s in self.css.items:
            rd.css.append_css(s)
        for s in self.scripts.items:
            rd.scripts.append_script(s)

        return rd

    def callback(self, output, inputs=[], state=[], events=[]):
        callback_set = {'output':output,
                        'inputs':inputs,
                        'state':state,
                        'events':events}
        def wrap_func(func,callback_set=callback_set,callback_sets=self._callback_sets):
            callback_sets.append((callback_set,func))
            return func
        return wrap_func

class NotFlask:
    def __init__(self):
        self.config = {}
        self.endpoints = {}

    def after_request(self,*args,**kwargs):
        pass
    def errorhandler(self,*args,**kwargs):
        return args[0]
    def add_url_rule(self,*args,**kwargs):
        route = kwargs['endpoint']
        self.endpoints[route] = kwargs
    def before_first_request(self,*args,**kwargs):
        pass
    def run(self,*args,**kwargs):
        pass

class NotDash(Dash):
    def __init__(self, name_root, app_pathname, **kwargs):

        global app_instances
        current_instances = app_instances.get(name_root,None)

        if current_instances is not None:
            self._uid = "%s-%i" % (name_root,len(current_instances)+1)
            current_instances.append(self)
        else:
            self._uid = name_root
            app_instances[name_root] = [self,]

        self._flask_app = Flask(self._uid)
        self._notflask = NotFlask()
        self._base_pathname = reverse(app_pathname,kwargs={'id':self._uid})

        kwargs['url_base_pathname'] = self._base_pathname
        kwargs['server'] = self._notflask

        super(NotDash, self).__init__(**kwargs)
        global nd_apps
        nd_apps[self._uid] = self

        self._adjust_id = False

    def flask_app(self):
        return self._flask_app

    def base_url(self):
        return self._base_pathname

    def app_context(self, *args, **kwargs):
        return self._flask_app.app_context(*args,
                                           **kwargs)

    def test_request_context(self, *args, **kwargs):
        return self._flask_app.test_request_context(*args,
                                                    **kwargs)

    def locate_endpoint_function(self, name=None):
        if name is not None:
            ep = "%s_%s" %(self._base_pathname,
                           name)
        else:
            ep = self._base_pathname
        return self._notflask.endpoints[ep]['view_func']

    @Dash.layout.setter
    def layout(self, value):

        if self._adjust_id:
            self._fix_component_id(value)
        return Dash.layout.fset(self, value)

    def _fix_component_id(self, component):

        theID = getattr(component,"id",None)
        if theID is not None:
            setattr(component,"id",self._fix_id(theID))
        try:
            for c in component.children:
                self._fix_component_id(c)
        except:
            pass

    def _fix_id(self, name):
        if not self._adjust_id:
            return name
        return "%s_-_%s" %(self._uid,
                           name)

    def _fix_callback_item(self, item):
        item.component_id = self._fix_id(item.component_id)
        return item

    def callback(self, output, inputs=[], state=[], events=[]):
        return super(NotDash, self).callback(self._fix_callback_item(output),
                                             [self._fix_callback_item(x) for x in inputs],
                                             [self._fix_callback_item(x) for x in state],
                                             [self._fix_callback_item(x) for x in events])

