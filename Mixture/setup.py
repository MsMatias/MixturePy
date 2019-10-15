from setuptools import setup

setup(name='Mixture',
      version='0.7',
      description='Mixture for Py',
      url='https://github.com/MsMatias/MixturePy',
      author='Mixture',
      license='MIT',
      packages=['Mixture'],
      install_requires=[
            'pandas',
            'numpy',
            'scikit-learn',
            'joblib',
            'xlrd',
            'openpyxl'          
      ],
      zip_safe=False)