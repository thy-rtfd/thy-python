# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conf_global import *

project = "Thy's Notes"
project_copyright = '2021, Thierry Humphrey'
author = 'Thierry Humphrey'

intersphinx_mapping_enabled = (
    'thy_main',

    'py3',
    'pydevguide',
    'python_guide_org',
    'rtfd',
    'sphinx',
)
intersphinx_mapping = {k: v for k, v in intersphinx_mapping.items() if k in intersphinx_mapping_enabled}
