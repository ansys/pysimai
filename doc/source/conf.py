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
import sys
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
sys.path.insert(0, str(SOURCE_PATH / "_ext"))
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
    "sphinx_copybutton",
    "sphinx_sitemap",
    "sphinx_markdown_builder",
    "llms_outputs",
    "sphinx_reredirects",
]
# Sphinx Gallery Options

sphinx_gallery_conf = {
    # default png file for thumbnails
    "default_thumb_file": ANSYS_SIMAI_THUMBNAIL,
    # path to your examples scripts
    "examples_dirs": ["examples"],
    # path where to save gallery generated examples
    "gallery_dirs": ["_examples"],
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

nitpick_ignore = [
    ("py:obj", "ansys.simai.core.data.base.DataModelType"),
    ("py:class", "_io.BytesIO"),
    ("py:class", "gt=0"),
    ("py:class", "pydantic_core._pydantic_core.Url"),
    ("py:class", "pydantic_core._pydantic_core.Annotated"),
    ("py:class", "annotated_types.Gt"),
    ("py:class", "pydantic.networks.UrlConstraints"),
    # httpx cannot be linked: https://github.com/encode/httpx/discussions/3091
    ("py:class", "Request"),
]
nitpick_ignore_regex = {
    ("py:class", r"httpx\..+"),
}

source_suffix = ".rst"
master_doc = "index"

# -- Options for HTML output -------------------------------------------------

html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "simai"
html_logo = pyansys_logo_black
html_favicon = ansys_favicon
html_static_path = ["_static"]

# Canonical URL of the published documentation, used by the sitemap and llms.txt.
html_baseurl = f"https://{cname}/version/{'dev' if 'dev' in version else 'stable'}/"
sitemap_url_scheme = "{link}"
sitemap_excludes = [
    "search.html",
    "genindex.html",
    "py-modindex.html",
    "sg_execution_times.html",
    "_examples/sg_execution_times.html",
    "_examples/00_basic_simai_ex/sg_execution_times.html",
    "_examples/01_pysimai_ex/sg_execution_times.html",
    "_examples/02_generative_design_ex/sg_execution_times.html",
]

# -- Outputs for AI assistants -----------------------------------------------
# Build the Markdown pages first (see the doc environment in tox.ini), then the
# HTML. The llms_outputs extension publishes each page as <page>.md and writes
# llms.txt and llms-full.txt.

llms_markdown_dir = os.getenv("LLMS_MARKDOWN_DIR")
llms_txt_title = "PySimAI"
llms_txt_exclude = ["sg_execution_times", "*/sg_execution_times"]
llms_txt_summary = (
    "PySimAI (package ansys-simai-core) is the Python SDK for Ansys SimAI. "
    "Use it to upload training data, build SimAI models and GeomAI models, "
    "run predictions and postprocessings, and generate geometries."
)
llms_txt_rules = [
    (
        "Install the package with `pip install ansys-simai-core` and import it with "
        "`import ansys.simai.core as asc`."
    ),
    (
        "Create the PySimAI client and name it `simai_client`: "
        '`simai_client = asc.SimAIClient(organization="<your_organization>")`.'
    ),
    (
        "GeomAI models have their own client, `GeomAIClient`: get it with "
        "`geomai_client = simai_client.geomai`, then use its directories, such as "
        "`geomai_client.projects` and `geomai_client.models`."
    ),
    (
        "`wait()` returns False on timeout and raises "
        "`ansys.simai.core.errors.ProcessingError` when the processing fails."
    ),
    (
        "Never pass `build_on_top` or `boundary_conditions`: both are deprecated. "
        "Use `workspace.model_manifest`, not `workspace.model`."
    ),
    (
        "For SimAI models, always pass `build_preset` explicitly: `debug` is a test build; "
        "`1_day`, `2_days` and `7_days` are production builds with that build duration. "
        "The default of `ModelConfiguration` is `debug`."
    ),
]

suppress_warnings = ["config.cache"]

html_context = {
    "github_user": "ansys",
    "github_repo": "pysimai",
    "github_version": "main",
    "doc_path": "doc",
    "pyansys_tags": ["AI"],
}
html_theme_options = {
    "logo": "pyansys",
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
    "show_nav_level": 1,
    "header_links_before_dropdown": 6,
    "navigation_depth": -1,
    "collapse_navigation": False,
}

# -- Options for LaTeX output -------------------------------

# Remove blank pages
# https://stackoverflow.com/questions/5422997/sphinx-docs-remove-blank-pages-from-generated-pdfs/5741112#5741112

latex_elements = {"extraclassoptions": "openany,oneside"}

# -- Redirects from the URLs of the previous documentation structure -----------

redirects = {
    "user_guide": "/user-guide/index.html",
    "user_guide/configuration_guide/index": "/getting-started/index.html",
    "user_guide/configuration_guide/installation": "/getting-started/install.html",
    "user_guide/configuration_guide/configuration": "/getting-started/configure-the-client.html",
    "user_guide/configuration_guide/config_file": "/getting-started/use-a-configuration-file.html",
    "user_guide/configuration_guide/proxy": "/getting-started/work-behind-a-proxy.html",
    "user_guide/pysimai_ug/index": "/user-guide/simai-models/index.html",
    "user_guide/pysimai_ug/building_a_model": "/user-guide/simai-models/build-a-model.html",
    "user_guide/pysimai_ug/data_exploration": "/user-guide/simai-models/explore-predictions-with-selections.html",
    "user_guide/pysimai_ug/best_practices": "/user-guide/common-tasks/work-asynchronously.html",
    "user_guide/optimization_guide/index": "/user-guide/simai-models/optimization-overview.html",
    "user_guide/optimization_guide/non-parametric_optimization": "/user-guide/simai-models/optimize-a-design.html",
    "user_guide/optimization_guide/configure_npo": "/user-guide/simai-models/configure-an-optimization.html",
    "user_guide/generative_design_ug/index": "/user-guide/geomai-models/index.html",
    "user_guide/generative_design_ug/data_preparation": "/user-guide/geomai-models/prepare-training-data.html",
    "user_guide/generative_design_ug/model_setup_and_goals": "/user-guide/geomai-models/configure-a-model.html",
    "user_guide/generative_design_ug/evaluation_and_workflows": "/user-guide/geomai-models/evaluate-a-model.html",
}
