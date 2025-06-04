PySimAI
=======
|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |ruff|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-simai-core?logo=pypi
   :target: https://pypi.org/project/ansys-simai-core/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-simai-core.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-simai-core
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/ansys/pysimai/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys/pysimai
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys/pysimai/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/pysimai/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

A Python wrapper for Ansys SimAI


How to install
--------------

At least two installation modes are provided: user and developer.

For users
^^^^^^^^^

In order to install PySimAI, make sure you
have the latest version of `pip`_. To do so, run:

.. code:: bash

    python -m pip install -U pip

Then, you can simply execute:

.. code:: bash

    python -m pip install ansys-simai-core

For developers
^^^^^^^^^^^^^^

Installing PySimAI in developer mode allows
you to modify the source and enhance it.

Before contributing to the project, please refer to the `PyAnsys Developer's guide`_. You will
need to follow these steps:

#. Start by cloning this repository:

    .. code:: bash

       git clone https://github.com/ansys/pysimai

#. `Install uv <https://docs.astral.sh/uv/>`_. NB: If you are a Windows user, make sure that Python is installed on your system and it is added to the Path.

#. Use uv to run commands

    .. code:: shell

       uv run pytest -xlv

#. Finally, verify your development installation by running:

    .. code:: bash

       uv tool install tox --with tox-uv
       tox

#. Alternatively, you can also run tasks defined in `pyproject.toml` using `poethepoet`:

    .. code:: shell

       uv tool install poethepoet
       uv run poe lint
       uv run poe test
       uv run poe doc


How to test
-----------

This project takes advantage of `tox`_. This tool allows to automate common
development tasks (similar to Makefile) but it is oriented towards Python
development.

Using tox
^^^^^^^^^

As Makefile has rules, `tox`_ has environments. In fact, the tool creates its
own virtual environment so anything being tested is isolated from the project in
order to guarantee project's integrity. The following environments commands are provided:

- **tox -e style**: will check for coding style quality.
- **tox -e py**: checks for unit tests.
- **tox -e py-coverage**: checks for unit testing and code coverage.
- **tox -e doc**: checks for documentation building process.


Raw testing
^^^^^^^^^^^

If required, you can always call the style commands (`ruff`_) or unit testing ones (`pytest`_) from the command line. However,
this does not guarantee that your project is being tested in an isolated
environment, which is the reason why tools like `tox`_ exist.


A note on pre-commit
^^^^^^^^^^^^^^^^^^^^

The style checks take advantage of `pre-commit`_. Developers are not forced but
encouraged to install this tool via:

.. code:: bash

    uv tool install pre-commit && pre-commit install


Documentation
-------------

For building documentation, you can either run the usual rules provided in the
`Sphinx`_ Makefile, such as:

.. code:: bash

    uv run make -C doc/ html && open doc/html/index.html

However, the recommended way of checking documentation integrity is using:

.. code:: bash

    tox -e doc && open .tox/doc_out/index.html


Distributing
------------

uv commands can help you build or publish the package

.. code:: bash

   uv build
   uv publish


.. LINKS AND REFERENCES
.. _ruff: https://github.com/astral-sh/ruff
.. _pip: https://pypi.org/project/pip/
.. _pre-commit: https://pre-commit.com/
.. _PyAnsys Developer's guide: https://dev.docs.pyansys.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _tox: https://tox.wiki/
