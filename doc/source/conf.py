# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# ruff: noqa: INP001, ERA001
#
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
from datetime import datetime
from pathlib import Path

from ansys_sphinx_theme import ansys_favicon, get_version_match, pyansys_logo_black
from sphinx_gallery.sorting import FileNameSortKey

from ansys.simai.core import __version__

# -- Project information -----------------------------------------------------

project = "ansys-simai-core"
author = "ANSYS, Inc."
release = version = __version__
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
cname = os.getenv("DOCUMENTATION_CNAME", "simai.docs.pyansys.com")

SOURCE_PATH = Path(__file__).parent.resolve().absolute()
ANSYS_SIMAI_THUMBNAIL = str(os.path.join(SOURCE_PATH, "_static", "ansys_simai.png"))

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx_design",
    "sphinxcontrib.autodoc_pydantic",
    "sphinx_gallery.gen_gallery",
]
# Sphinx Gallery Options

sphinx_gallery_conf = {
    # default png file for thumbnails
    "default_thumb_file": ANSYS_SIMAI_THUMBNAIL,
    # path to your examples scripts
    "examples_dirs": ["examples/pysimai_ex", "examples/generative_design_ex"],
    # path where to save gallery generated examples
    "gallery_dirs": ["_examples/pysimai_ex", "_examples/generative_design_ex"],
    # Remove the "Download all examples" button from the top level gallery
    "download_all_examples": False,
    # Sort gallery example by file name instead of number of lines (default)
    "within_subsection_order": FileNameSortKey,
}
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# Do not display todos in the documentation
todo_include_todos = False

# Autodoc settings
autodoc_typehints = "both"
autodoc_typehints_description_target = "documented"
autodoc_member_order = "groupwise"
autoclass_content = "both"

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
    ("py:obj", "ansys.simai.core.data.base.DataModelType"),
    ("py:class", "_io.BytesIO"),
    ("py:class", "pydantic_core._pydantic_core.Url"),
    ("py:class", "pydantic_core._pydantic_core.Annotated"),
    ("py:class", "annotated_types.Gt"),
    ("py:class", "pydantic.networks.UrlConstraints"),
}

source_suffix = ".rst"
master_doc = "index"

# -- Options for HTML output -------------------------------------------------

html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "simai"
html_logo = pyansys_logo_black
html_favicon = ansys_favicon
html_static_path = ["_static"]

suppress_warnings = ["config.cache"]

html_context = {
    "github_user": "ansys",
    "github_repo": "pysimai",
    "github_version": "main",
    "doc_path": "doc",
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
    "check_switcher": False,
    "use_meilisearch": {
        "api_key": os.getenv("MEILISEARCH_PUBLIC_API_KEY", ""),
        "index_uids": {
            f"pysimai-v{get_version_match(version).replace('.', '-')}": "PySimAI",
        },
    },
    "navbar_end": ["version-switcher", "theme-switcher", "navbar-icon-links"],
    "navigation_depth": -1,
    "collapse_navigation": True,
}

# -- Options for LaTeX output -------------------------------

# Remove blank pages
# https://stackoverflow.com/questions/5422997/sphinx-docs-remove-blank-pages-from-generated-pdfs/5741112#5741112

latex_elements = {"extraclassoptions": "openany,oneside"}
