from setuptools import setup, find_packages
setup(
    name='abrox',
    packages=find_packages(),
    package_data={'abrox': ['gui/icons/*']},
    version='0.1.0',
    license='MIT',
    description='A GUI for Approximate Bayesian Computation',
    long_description=open('README.md').read(),
    author='Ulf Mertens',
    author_email='mertens.ulf@gmail.com',
    scripts=['scripts/abrox-gui'],
    # entry_points={
    #       'gui_scripts': [
    #           'abrox-gui = abrox.gui.__main__:main'
    #       ]
    #   },
    url='https://github.com/mertensu/ABrox',  # use the URL to the github repo
    download_url='https://github.com/mertensu/ABrox/archive/0.1.tar.gz',
    setup_requires=['numpy'],
    install_requires=['numpy',
                      'scipy',
                      'statsmodels',
                      'pandas',
                      'pyqt5',
                      'qdarkstyle',
                      'ipython'
                      ],
    classifiers=[],
)
