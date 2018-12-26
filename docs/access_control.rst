.. _access_control:

View decoration
===============

The ``django-plotly-dash`` views, as served by Django, can be wrapped with
an arbitrary decoration function. This allows the use
of the Django `login_required <https://docs.djangoproject.com/en/2.1/topics/auth/default/#the-login-required-decorator>`_ view decorator
as well as enabling more specialised and fine-grained control.

The ``login_required`` decorator
----------------------------

The ``login_required`` decorator from the Django authentication system can be used as a view decorator. A wrapper function is provided
in ``django_plotly_dash.access``.

.. code-block:: python

  PLOTLY_DASH = {

      ...
      # Name of view wrapping function
      "view_decorator": "django_plotly_dash.access.login_required",
      ...
  }

Note that the view wrapping is on all of the ``django-plotly-dash`` views.

Fine-grained control
--------------------

The view decoration function is called for each variant exposed in
the ``django_plotly_dash.urls`` file. As well as the
underlying view function, each call to the decorator is given the name of the
route, as used by ``django.urls.reverse``, the specific url fragment for the view, and a name
describing the type of view.

From this information, it is possible to implement view-specific wrapping of the view functions, and
in turn the wrapper functions can then use the request content, along with other information, to control
access to the underlying view function.

.. code-block:: python

  from django.views.decorators.csrf import csrf_exempt

  def check_access_permitted(request, **kwargs):
      # See if access is allowed; if so return True
      # This function is called on each request

      ...

      return True

  def user_app_control(view_function, name=None, **kwargs):
      # This function is called on the registration of each django-plotly-dash view
      # name is one of main component-suites routes layout dependencies update-component

      def wrapped_view(request, *args, **kwargs):
          is_permitted = check_access_permitted(request, **kwargs)
          if not is_permitted:
              # Access not permitted, so raise error or generate an appropriate response

              ...

          else:
              return view_function(request, *args, **kwargs)

      if getattr(view_function,"csrf_exempt",False):
          return csrf_exempt(wrapped_view)

      return wrapped_view

The above sketch highlights how access can be controlled based on each request. Note that the
``csrf_exempt`` property of any wrapped view is preserved by the decoration function and this
approach needs to be extended to other properties if needed. Also, this sketch only passes
``kwargs`` to the permission function.


