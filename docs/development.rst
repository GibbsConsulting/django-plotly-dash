.. _development:

Development
===========

The application and demo are developed, built and tested in a virtualenv enviroment, supported by
a number of ``bash`` shell scripts. The resultant package should work on any Python installation
that meets the requirements.

Automatic builds have been set up on `Travis-CI <https://travis-ci.org/GibbsConsulting/django-plotly-dash>`_ including
running tests and reporting code coverage.

Current status: |Travis Badge|

.. |Travis Badge| image:: https://travis-ci.org/GibbsConsulting/django-plotly-dash.svg?branch=master

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
locally. Whilst passing ``serve_locally=True`` to a ``DjangoDash`` constructor will cause all of the
css and javascript files for the components in that application from the
local server, it is recommended to use the global ``serve_locally`` configuration setting.

Note that it is not good practice to serve static content in production through Django.

Coding and testing
------------------

The ``pylint`` and ``pytest`` packages are important tools in the development process. The global configuration
used for ``pylint`` is in the ``pylintrc`` file in the root directory of the codebase.

Tests of the package are
contained within the ``django_plotly_dash/tests.py`` file, and are invoked using the Django
settings for the demo. Running the tests from the perspective of the demo also enables
code coverage for both the application and the demo to be measured together, simplifying the bookkeeping.

Two helper scripts are provided for running the linter and test code::

  # Run pylint on django-plotly-dash module
  ./check_code_dpd

  # Run pylint on the demo code, and then execute the test suite
  ./check_code_demo

It is also possible to run all of these actions together::

  # Run all of the checks
  ./check_code

The goal is for complete code coverage within the test suite and for maximal ('ten out of ten') marks from the
linter. Perfection is however very hard and expensive to achieve, so the working requirement is for every release to
keep the linter score above 9.5, and ideally improve it, and for the level of code coverage of the tests to increase.

Documentation
-------------

Documentation lives in the ``docs`` subdirectory as reStructuredText and is built using
the ``sphinx`` toolchain.

Automatic local building of the documentation is possible with the development environment::

  source env/bin/activate
  cd docs && sphinx-autobuild . _build/html

In addition, the ``grip`` tool can be used to serve a rendered version of the ``README`` file::

  source env/bin/activate
  grip

The online documentation is automatically built by the ``readthedocs`` infrastructure when a release is
formed in the main ``github`` repository.

Release builds
--------------

This section contains the recipe for building a release of the project.

First, update the version number appropriately
in ``django_plotly_dash/version.py``, and then
ensure that the checks and tests have been run::

  ./check_code

Next, construct the ``pip`` packages and push them to `pypi <https://pypi.org/project/django-plotly-dash/>`_::

  source env/bin/activate

  python setup.py sdist
  python setup.py bdist_wheel

  twine upload dist/*

Committing a new release to the main github repository will invoke a build of the online documentation, but
first a snapshot of the development environment used for the build should be generated::

  pip freeze > frozen_dev.txt

  git add frozen_dev.txt
  git add django_plotly_dash/version.py

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

To report a bug, create a `github issue <https://github.com/GibbsConsulting/django-plotly-dash/issues>`_.

