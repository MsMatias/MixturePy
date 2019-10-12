from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='Mixture',
      version='0.5',
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
            'multiprocessing',
            'joblib'          
      ],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
      python_requires='>=3.6',
      zip_safe=False)