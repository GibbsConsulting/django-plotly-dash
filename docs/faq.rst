.. _faq:

FAQ
===

* What environment versions are supported?

At least v3.5 of Python, and v2.0 of Django, are needed.

* Is a ``virtualenv`` mandatory?

No, but it is strongly recommended for any Python work.

* What about Windows?

The python package should work anywhere that Python does. Related applications, such as Redis, have their
own requirements but are accessed using standard network protocols.

* How do I report a bug or other issue?

Create a `github issue <https://github.com/GibbsConsulting/django-plotly-dash/issues>`_. See :ref:`bug reporting <bug-reporting>` for details
on what makes a good bug report.

* Where should ``Dash`` layout and callback functions be placed?

In general, the only constraint on the files containing these functions is that they should be imported into the file containing
the ``DjangoDash`` instantiation. This is discussed in
the :ref:`installation` section and also
in this github `issue <https://github.com/GibbsConsulting/django-plotly-dash/issues/58>`_.

* Can per-user or other fine-grained access control be used?

 Yes. See the :ref:`view_decoration` configuration setting.

