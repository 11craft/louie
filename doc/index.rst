Welcome to Louie's documentation!
=================================

Contents:

.. toctree::
   :maxdepth: 2

   about
   changes
   contributors

Louie provides Python programmers with a straightforward way to
dispatch signals between objects in a wide variety of contexts. It is
based on PyDispatcher_, which in turn was based on a highly-rated
recipe_ in the Python Cookbook.

Louie is licensed under `The BSD License`_.

.. _PyDispatcher: http://pydispatcher.sf.net/

.. _recipe: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/87056

.. _The BSD License: http://opensource.org/licenses/bsd-license.php


Louie Requirements
==================

Python 3.6 or higher.


Installing Louie
================

Louie uses pip_ for installation, and is distributed via
the `Python Package Index`_.

.. _pip: https://pypi.python.org/pypi/pip

.. _Python Package Index: https://pypi.python.org/pypi/Louie

Run this command::

    pip install louie


Upgrading Louie
===============

Run this command to upgrade Louie to the latest release::

    pip install -U Louie


Development
===========

You can track the latest changes in Louie using the Github repo.


Using git
---------

Clone the Louie repo using git, e.g.::

    git clone https://github.com/11craft/louie

Run this command inside your git repo directory to
use Louie directly from source code in that directory::

    cd louie
    pip install -e .

If you want to revert to the version installed in ``site-packages``,
you can do so::

    pip uninstall louie


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
