.. _demo_notes:

Demonstration application
=========================

There are a number of pages in the demo application in the
source repository.

#. Direct insertion of one or more dash applications
#. Initial state storage within Django
#. Enhanced callbacks
#. Live updating
#. Injection without using an iframe
#. Simple html injection
#. Bootstrap components
#. Session state storage
#. Local serving of assets
#. Multiple callback values

The templates that drive each of these can be found in
the `github repository <https://github.com/GibbsConsulting/django-plotly-dash/tree/master/demo/demo/templates>`_.

There is a more details walkthrough of the :ref:`session state storage <session_example>` example. This example also
shows the use of `dash bootstrap components <https://pypi.org/project/dash-bootstrap-components/>`_.

The demo application can also be viewed `online <https://djangoplotlydash.com>`_.


.. _session_example:

Session state example walkthrough
---------------------------------

The session state example has three separate components in the demo application

* A template to render the application
* The ``django-plotly-dash`` application itself
* A view to render the template having initialised the session state if needed

The first of these is a standard Django template, containing instructions to
render the Dash application::

    {%load plotly-dash%}

    ...

    <div class="{%plotly_class name="DjangoSessionState"%}">
      {%plotly_app name="DjangoSessionState" ratio=0.3 %}
    </div>

The view sets up the initial state of the application prior to rendering. For this example
we have a simple variant of rendering a template view::

  def session_state_view(request, template_name, **kwargs):

      # Set up a context dict here
      context = { ... values for template go here, see below ... }

      return render(request, template_name=template_name, context=context)

and it suffices to register this view at a convenient URL as it does not
use any parameters::

    ...
    url('^demo-eight',
        session_state_view,
        {'template_name':'demo_eight.html'},
        name="demo-eight"),
    ...

In passing, we note that accepting parameters as part of the URL and passing them as initial
parameters to the app through the template is a straightforward extension of this example.

The session state can be accessed in the app as well as the view. The app is essentially formed
from a layout function and a number of callbacks. In this particular example,
`dash-bootstrap-components <https://dash-bootstrap-components.opensource.asidatascience.com/>`_
are used to form the layout::

    dis = DjangoDash("DjangoSessionState",
                     add_bootstrap_links=True)

    dis.layout = html.Div(
        [
            dbc.Alert("This is an alert", id="base-alert", color="primary"),
            dbc.Alert(children="Danger", id="danger-alert", color="danger"),
            dbc.Button("Update session state", id="update-button", color="warning"),
        ]
    )

Within the :ref:`expanded callback <extended_callbacks>`, the session state is passed as an extra
argument compared to the standard ``Dash`` callback::

    @dis.expanded_callback(
        dash.dependencies.Output("danger-alert", 'children'),
        [dash.dependencies.Input('update-button', 'n_clicks'),]
        )
    def session_demo_danger_callback(n_clicks, session_state=None, **kwargs):
        if session_state is None:
            raise NotImplementedError("Cannot handle a missing session state")
        csf = session_state.get('bootstrap_demo_state', None)
        if not csf:
            csf = dict(clicks=0)
            session_state['bootstrap_demo_state'] = csf
        else:
            csf['clicks'] = n_clicks
        return "Button has been clicked %s times since the page was rendered" %n_clicks

The session state is also set during the view::

   def session_state_view(request, template_name, **kwargs):

       session = request.session

       demo_count = session.get('django_plotly_dash', {})

       ind_use = demo_count.get('ind_use', 0)
       ind_use += 1
       demo_count['ind_use'] = ind_use
       session['django_plotly_dash'] = demo_count

       # Use some of the information during template rendering
       context = {'ind_use' : ind_use}

       return render(request, template_name=template_name, context=context)

Reloading the demonstration page will cause the page render count to be incremented, and the
button click count to be reset. Loading the page in a different session, for example by using
a different browser or machine, will have an independent render count.


