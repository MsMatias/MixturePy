from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='Mixture',
      version='0.8',
      description='Mixture for Py',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/MsMatias/MixturePy',
      include_package_data = True,
      author='Mixture',
      license='MIT',
      packages=['Mixture'],
      package_data = {
            'Mixture': ['data/*']
      },
      install_requires=[
            'pandas',
            'numpy',
            'scikit-learn',
            'joblib',
            'xlrd',
            'openpyxl',
            'xlsxwriter'
      ],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
      python_requires='>=3.6',
      zip_safe=False)
