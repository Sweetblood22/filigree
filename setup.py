from distutils.core import setup

setup(
    name='filigree',
    version='0.0.2',
    packages=['filigree'],
    url='',
    license='N/A',
    author='Math-Barbarian',
    author_email='cognitive.toxin@gmail.com',
    description="Create complex plot data structures (plottable with Bokeh) from Pandas DataFrames",
    requires=['numpy >= 1.11.3', 'pandas >= 0.20.0', 'bokeh >= 1.1.0', 'scipy >= 1.0.2'],
    package_dir={'filigree': 'filigree'},
    package_data={'filigree': ['examples/*']}
)
