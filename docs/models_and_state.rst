.. _models_and_state:

Django models and application state
===================================

The ``django_plotly_dash`` application defines ``DashApp`` and ``StatelessApp`` models.

The ``StatelessApp`` model
--------------------------

An instance of the ``StatelessApp`` model represents a single dash application. Every instantiation of
a ``DjangoDash`` object is registered, and any object that is referenced through the ``DashApp`` model - this
includes all template access as well as model instances themselves - causes a ``StatelessApp`` model instance to
be created if one does not already exist.

.. code-block:: python

    class StatelessApp(models.Model):
        '''
        A stateless Dash app.

        An instance of this model represents a dash app without any specific state
        '''

        app_name = models.CharField(max_length=100, blank=False, null=False, unique=True)
        slug = models.SlugField(max_length=110, unique=True, blank=True)

        def as_dash_app(self):
            '''
            Return a DjangoDash instance of the dash application
            '''

The main role of a ``StatelessApp`` instance is to manage access to the associated ``DjangoDash`` object, as
exposed through the ``as_dash_app`` member
function.

In the Django admin, an action is provided to check all of the known stateless instances. Those that cannot be instantiated
are logged; this is a useful quick check to see what apps are avalilable. Also, in the same admin an additional button
is provided to create ``StatelessApp`` instances for any known instance that does not have an ORM entry.


The ``DashApp`` model
---------------------

An instance of the ``DashApp`` model represents an instance of application state.

.. code-block:: python

    class DashApp(models.Model):
        '''
        An instance of this model represents a Dash application and its internal state
        '''
        stateless_app = models.ForeignKey(StatelessApp, on_delete=models.PROTECT,
                                          unique=False, null=False, blank=False)
        instance_name = models.CharField(max_length=100, unique=True, blank=True, null=False)
        slug = models.SlugField(max_length=110, unique=True, blank=True)
        base_state = models.TextField(null=False, default="{}")
        creation = models.DateTimeField(auto_now_add=True)
        update = models.DateTimeField(auto_now=True)
        save_on_change = models.BooleanField(null=False,default=False)

        ... methods, mainly for managing the Dash application state ...

        def current_state(self):
            '''
            Return the current internal state of the model instance
            '''

        def update_current_state(self, wid, key, value):
            '''
            Update the current internal state, ignorning non-tracked objects
            '''

        def populate_values(self):
            '''
            Add values from the underlying dash layout configuration
            '''

The ``stateless_app`` references an instance of the ``StatelessApp`` model described above. The ``slug`` field provides a unique identifier
that is used in URLs to identify the instance of an application, and also its associated server-side state.

The persisted state of the instance is contained, serialised as JSON, in the ``base_state`` variable. This is an arbitrary subset of the internal state of the
object. Whenever a ``Dash`` application requests its state (through the ``<app slug>_dash-layout`` url), any values from the underlying application that are present in
``base_state``  are overwritten with the persisted values.

The ``populate_values`` member function can be used to insert all possible initial values into ``base_state``. This functionality is also exposed in the Django
admin for these model instances, as a ``Populate app`` action.

From callback code, the ``update_current_state`` method can be called to change the initial value of any variable tracked within the ``base_state``. Variables not tracked
will be ignored. This function is automatically called for any callback argument and return value.

Finally, after any callback has finished, and after any result stored through ``update_current_state``, then the application model instance will be persisted by means
of a call to its ``save`` method, if any changes have been detected and the ``save_on_change`` flag is ``True``.
