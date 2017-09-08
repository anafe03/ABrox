from setuptools import setup
setup(
    name='abrox',
    packages=['abrox'],  # this must be the same as the name above
    version='0.1',
    license='MIT',
    description='A GUI for Approximate Bayesian Computation',
    long_description=open('README.md').read(),
    author='Ulf Mertens',
    author_email='mertens.ulf@gmail.com',
    scripts=['abrox/gui/abrox-gui.py'],
    url='https://github.com/mertensu/ABrox',  # use the URL to the github repo
    download_url='https://github.com/mertensu/ABrox/archive/0.1.tar.gz',
    setup_requires=['numpy'],
    install_requires=['numpy',
                      'scipy',
                      'statsmodels',
                      'pandas',
                      'pyqt5',
                      'ipython'
                      ],
    classifiers=[],
)
