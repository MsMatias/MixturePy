import sys
from setuptools import find_packages
from cx_Freeze import setup, Executable


options = {
    'build_exe': {
        'includes': [
            'cx_Logging', 'idna',
        ],
        'packages': [
            'asyncio', 'flask', 'jinja2', 'dash', 'plotly', 'waitress'
        ],
        'excludes': ['tkinter']
    }
}

base = None
if sys.platform == "win32":
    base = "console"
else:
    base = ".py"


executables = [
    Executable('server.py',
               base=base)
]

setup(
    name='MixturePy',
    packages=find_packages(),
    version='0.4.0',
    description='rig',
    executables=executables,
    options=options
)
