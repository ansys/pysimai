# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

from datetime import datetime

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

from ansys_sphinx_theme import ansys_favicon, get_version_match, pyansys_logo_black
import tomli

from ansys.simai.core import __version__

# -- Project information -----------------------------------------------------

project = "ansys-simai-core"
author = "ANSYS Inc."
release = version = __version__
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
cname = os.getenv("DOCUMENTATION_CNAME", "simai.docs.pyansys.com")

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinxcontrib.autodoc_pydantic",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# Do not display todos in the documentation
todo_include_todos = False

# Autodoc settings
autodoc_typehints = "both"
autodoc_member_order = "groupwise"
autoclass_content = "class"

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Don't always include full modules names to all descriptions
add_module_names = False

# Complain about all broken links
nitpicky = True

nitpick_ignore_regex = {
    (r"py:obj", "ansys.simai.core.data.base.DataModelType"),
    (r"py:class", "_io.BytesIO"),
    (r"py:class", "pydantic_core._pydantic_core.Url"),
    # FIXME: This shouldn't be ignored but it's not clear why it's failing to find it in some cases
    (r"py:class", "Directory"),
}

# -- Options for HTML output -------------------------------------------------

html_theme = "ansys_sphinx_theme"
html_logo = pyansys_logo_black
html_favicon = ansys_favicon
html_static_path = ["_static"]

html_context = {
    "github_user": "ansys",
    "github_repo": "pysimai",
    "github_version": "main",
    "doc_path": "docs",
}
html_theme_options = {
    "github_url": "https://github.com/ansys/pysimai",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": get_version_match(version),
    },
    # TODO
    # "use_meilisearch": {
    #     "api_key": os.getenv("MEILISEARCH_PUBLIC_API_KEY", ""),
    #     "index_uids": {
    #         f"pyfluent-v{get_version_match(version).replace('.', '-')}": "PyFluent",
    #     },
    # },
    "navbar_end": ["version-switcher", "theme-switcher", "navbar-icon-links"],
    "navigation_depth": -1,
    "collapse_navigation": True,
}

# -- Options for LaTeX output -------------------------------

# Remove blank pages
# https://stackoverflow.com/questions/5422997/sphinx-docs-remove-blank-pages-from-generated-pdfs/5741112#5741112

latex_elements = {"extraclassoptions": "openany,oneside"}
