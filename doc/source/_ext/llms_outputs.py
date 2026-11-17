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
# ruff: noqa: INP001

"""Publish the documentation for AI assistants.

After the HTML build, this extension:

- copies the Markdown version of each page next to its HTML page, so that
  ``<page>.html`` is also available as ``<page>.md``;
- writes ``llms.txt``, an index of all pages in table-of-contents order, with
  rules for code generation. A page can set its description in ``llms.txt``
  with a ``:description:`` field at the top of its source file;
- writes ``llms-full.txt``, all pages in one file.

The Markdown pages come from a previous build with the ``markdown`` builder
(sphinx-markdown-builder), whose output folder is set by ``llms_markdown_dir``.
The Markdown builder renders autodoc, so the API reference is complete.
"""

import re
import shutil
from fnmatch import fnmatch
from pathlib import Path

from sphinx.util import logging

logger = logging.getLogger(__name__)


def _ordered_docnames(env, root):
    """Return the docnames in table-of-contents order, starting from ``root``."""
    seen, order = set(), []

    def visit(docname):
        if docname in seen:
            return
        seen.add(docname)
        order.append(docname)
        for child in env.toctree_includes.get(docname, []):
            visit(child)

    visit(root)
    order.extend(sorted(d for d in env.found_docs if d not in seen))
    return order


def _description(markdown):
    """Return the first paragraph after the title, as plain text."""
    lines = markdown.splitlines()
    paragraph = []
    for line in lines:
        stripped = line.strip()
        if not paragraph and (
            not stripped or stripped.startswith(("#", "<", "!", "*", "|", "```", ">"))
        ):
            continue
        if not stripped or stripped.startswith(("#", "```")):
            break
        paragraph.append(stripped)
    text = " ".join(paragraph)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_`]", "", text)
    return text if len(text) <= 200 else text[:197].rsplit(" ", 1)[0] + "..."


def _write_outputs(app, exception):
    if exception or app.builder.name not in ("html", "dirhtml"):
        return
    config = app.config
    md_dir = Path(config.llms_markdown_dir) if config.llms_markdown_dir else None
    if not md_dir or not md_dir.is_dir():
        logger.info("llms_outputs: no Markdown build found in %s, skipping.", md_dir)
        return

    outdir = Path(app.outdir)
    env = app.env
    base_url = (config.html_baseurl or "").rstrip("/") + "/"
    docnames = [
        d
        for d in _ordered_docnames(env, config.root_doc)
        if not any(fnmatch(d, pattern) for pattern in config.llms_txt_exclude)
    ]

    pages = []
    for docname in docnames:
        source = md_dir / f"{docname}.md"
        if not source.is_file():
            continue
        target = outdir / f"{docname}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        text = source.read_text(encoding="utf-8")
        title = env.titles[docname].astext() if docname in env.titles else docname
        pages.append((docname, title, f"{base_url}{docname}.md", text))

    # Group the pages under the top-level entries of the root table of contents.
    sections = {}
    top_level = env.toctree_includes.get(config.root_doc, [])
    owner = {}
    for top in top_level:
        stack = [top]
        while stack:
            current = stack.pop()
            owner.setdefault(current, top)
            stack.extend(env.toctree_includes.get(current, []))
    for docname, title, url, text in pages:
        group = owner.get(docname)
        group_title = env.titles[group].astext() if group in env.titles else "Other pages"
        if docname == config.root_doc:
            group_title = "Overview"
        description = env.metadata.get(docname, {}).get("description") or _description(text)
        sections.setdefault(group_title, []).append((title, url, description))

    lines = [f"# {config.llms_txt_title}", "", f"> {config.llms_txt_summary}", ""]
    if config.llms_txt_rules:
        lines += ["Rules for generating code with this library:", ""]
        lines += [f"- {rule}" for rule in config.llms_txt_rules]
        lines.append("")
    lines += [
        (
            "Every page is available as Markdown: replace `.html` with `.md` in its URL. "
            f"All pages in one file: {base_url}llms-full.txt"
        ),
        "",
    ]
    for group_title, entries in sections.items():
        lines += [f"## {group_title}", ""]
        for title, url, description in entries:
            lines.append(f"- [{title}]({url})" + (f": {description}" if description else ""))
        lines.append("")
    (outdir / "llms.txt").write_text("\n".join(lines), encoding="utf-8")

    full = [f"# {config.llms_txt_title}", "", f"> {config.llms_txt_summary}", ""]
    for _docname, _title, url, text in pages:
        full += ["", "---", "", f"Source: {url}", "", text.strip(), ""]
    (outdir / "llms-full.txt").write_text("\n".join(full), encoding="utf-8")

    logger.info("llms_outputs: wrote llms.txt, llms-full.txt and %d Markdown pages.", len(pages))


def _add_meta_description(app, pagename, templatename, context, doctree):
    """Add the page's ``:description:`` field as an HTML meta description."""
    description = app.env.metadata.get(pagename, {}).get("description")
    if description:
        escaped = description.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
        context["metatags"] = context.get("metatags", "") + f'\n<meta name="description" content="{escaped}">'


def setup(app):
    app.add_config_value("llms_markdown_dir", None, "env")
    app.add_config_value("llms_txt_title", "Documentation", "env")
    app.add_config_value("llms_txt_summary", "", "env")
    app.add_config_value("llms_txt_rules", [], "env")
    app.add_config_value("llms_txt_exclude", [], "env")
    app.connect("build-finished", _write_outputs)
    app.connect("html-page-context", _add_meta_description)
    return {"version": "0.1", "parallel_read_safe": True, "parallel_write_safe": True}
