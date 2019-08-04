from setuptools import setup

setup(name='Mixture',
      version='0.1',
      description='Mixture for Py',
      url='https://github.com/MsMatias/MixturePy',
      author='Mixture',
      license='MIT',
      packages=['Mixture'],
      install_requires=[
            'pandas',
            'numpy',
            'sklearn',
            'rpy2'
      ],
      zip_safe=False)