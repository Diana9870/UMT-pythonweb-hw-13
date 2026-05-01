import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "Contacts API"
copyright = "2026"
author = "Student"
release = "1.0.0"


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
]

autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "en"


autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

autodoc_member_order = "bysource"


html_theme = "sphinx_rtd_theme"

html_static_path = ["_static"]

html_title = "Contacts API Documentation"


napoleon_google_docstring = True
napoleon_numpy_docstring = True