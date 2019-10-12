import sys
from setuptools import find_packages
from cx_Freeze import setup, Executable


options = {
    'build_exe': {
        'includes': [
            'cx_Logging', 'idna',
        ],
        'packages': [
            'asyncio', 'flask', 'jinja2', 'dash', 'plotly', 'waitress', 'scipy.signal', 'scipy.sparse',  'scipy.integrate', 'xlsxwriter'
        ],
        'excludes': [
            'tkinter', 'scipy.spatial.cKDTree'
        ],
        'include_files': [
            'assets/',
            'data/'
        ]
    }
}

base = None
if sys.platform == "win32":
    base = "console"
else:
    base = ".py"

print(base)

if sys.platform == "win32":
    executables = [
    Executable('server.py',
               base=base,
               targetName='MixturePy.exe')
]
else:
    executables = [
    Executable('server.py')
]


setup(
    name='MixturePy',
    packages=find_packages(),
    version='0.5.0',
    description='rig',
    executables=executables,
    options=options
)
