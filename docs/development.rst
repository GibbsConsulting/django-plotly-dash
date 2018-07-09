.. _development:

Development
===========

The application and demo are developed and tested in a virtualenv enviroment on Linux. The resultant package should work on any Python installation
that meets the requirements.

Environment setup
-----------------

To set up a development environment, first clone the repository, and then use the ``make_env`` script::

  git clone https://github.com/GibbsConsulting/django-plotly-dash.git

  cd django-plotly-dash

  ./make_env

The script creates a virtual environment and uses ``pip`` to install the package requirements from the ``requirements.txt`` file, and then
also the extra packages for development listed in the ``dev_requirements.txt`` file. It also installs ``django-plotly-dash`` as a development
package.

Redis is an optional dependency, and is used for live updates of Dash applications through
channels endpoints. The ``prepare_redis`` script can be used to install Redis
using Docker. It essentially pulls the container and launches it::

  # prepare_redis content:
  docker pull redis:4
  docker run -p 6379:6379 -d redis

The use of Docker is not mandatory, and any method to install Redis can be used provided that
the :ref:`configuration <configuration>` of the host and port for channels is set correcty in the ``settings.py`` for
the Django project.

During development, it can be convenient to serve the ``Dash`` components
locally. Passing ``serve_locally=True`` to a ``DjangoDash`` constructor will cause all of the
css and javascript files for the components in that application from the
local server. Additional Django settings are also needed to serve the
static files::

  STATIC_URL = '/static/'
  STATIC_ROOT = os.path.join(BASE_DIR, 'static')

  STATICFILES_DIRS = []  # Or other sources as needed

  if DEBUG:

      import importlib

      for dash_module_name in ['dash_core_components',
                               'dash_html_components',
                               'dash_renderer',
                               'dpd_components',
                              ]:

          module = importlib.import_module(dash_module_name)
          STATICFILES_DIRS.append(("dash/%s"%dash_module_name, os.path.dirname(module.__file__)))

Note that it is not considered best practice to serve static content in production through Django.

Coding and testing
------------------

checks::

  # Run pylint on django-plotly-dash module
  ./check_code_dpd

  # Run pylint on the demo code, and then execute the test suite
  ./check_code_demo

  # Run all of the above checks in one command
  ./check_code


Documentation
-------------

Docs::

  source env/bin/activate
  cd docs && sphinx-autobuild . _build/html

Readme::

  source env/bin/activate
  grip


Release builds
--------------

This section contains the recipe for building a release of the project.

First, update the version number appropriately
in ``django_plotly_dash/__init__.py``, and then
ensure that the checks and tests have been run::

  ./check_code

Next, construct the ``pip`` packages and push them to `pypi <https://pypi.org/project/django-plotly-dash/>`_::

  source env/bin/activate

  python setup.py sdisy
  python setup.py bdist_wheel

  twine upload dist/*

Committing a new release to the main github repository will invoke a build of the online documentation, but
first a snapshot of the development environment used for the build should be generated::

  pip freeze > frozen_dev.txt

  git add frozen_dev.txt
  git add django_plotly_dash/__init__.py

  git commit -m" ... suitable commit message for this release ..."

  # Create PR, merge into main repo, check content on PYPI and RTD

This preserves the state used for building and testing for future reference.

.. _bug-reporting:

Bug reports and other issues
----------------------------

The ideal bug report is a pull request containing the addition of a failing test exhibiting the problem
to the test suite. However, this rarely happens in practice!

The essential requirement of a bug report is that it contains enough information to characterise the issue, and ideally
also provides some way of replicating it. Issues that cannot be replicated within a virtualenv are unlikely to
get much attention, if any.

