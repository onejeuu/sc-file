# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path

from sphinx.ext import autodoc
from sphinx.locale import _


PATH = Path("../../scfile").absolute()
sys.path.insert(0, PATH.as_posix())


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "sc-file"
copyright = "2025, onejeuu"
author = "onejeuu"
release = "4.0.0"
html_title = f"{project} {release}"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx_autodoc_typehints",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_css_files = ["custom.css"]
html_static_path = ["_static"]
html_extra_path = ["data"]

napoleon_google_docstring = True
napoleon_numpy_docstring = True

autodoc_member_order = "bysource"
add_module_names = False


# -- Remove "Bases: object" from classes -------------------------------------

useless_bases = _("Bases: %s") % ":py:class:`object`"


class MockedClassDocumenter(autodoc.ClassDocumenter):
    def add_line(self, line: str, source: str, *lineno: int) -> None:
        if useless_bases not in line:
            super().add_line(line, source, *lineno)


autodoc.ClassDocumenter = MockedClassDocumenter
