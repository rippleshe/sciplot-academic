# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "SciPlot Academic"
author = "SciPlot Team"
copyright = "2024, SciPlot Team"

# Read version from pyproject.toml dynamically
def _get_version() -> str:
    """Read version from pyproject.toml."""
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]

    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


release = _get_version()
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_design",
    "sphinx_copybutton",
    "numpydoc",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]

# -- Language configuration --------------------------------------------------

language = "zh_CN"

# -- Theme options -----------------------------------------------------------

html_theme_options = {
    "github_url": "https://github.com/rippleshe/sciplot-academic",
    "navbar_align": "left",
    "header_links_before_dropdown": 4,
    "secondary_sidebar_items": ["page-toc", "edit-this-page"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/rippleshe/sciplot-academic",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
    ],
    "use_edit_page_button": True,
}

html_context = {
    "github_user": "rippleshe",
    "github_repo": "sciplot-academic",
    "github_version": "main",
    "doc_path": "docs",
}

# -- Autodoc configuration ---------------------------------------------------

autodoc_member_order = "bysource"
autodoc_typehints = "description"

# -- Numpydoc configuration --------------------------------------------------

numpydoc_show_class_members = False
