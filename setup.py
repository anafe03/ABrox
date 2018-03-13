from setuptools import setup, find_packages
setup(
    name='abrox',
    packages=find_packages(),
    package_data={'abrox': ['gui/icons/*']},
    version='2.0.2',
    license='MIT',
    description='A tool for Approximate Bayesian Computation',
    long_description=open('README.md').read(),
    author='Ulf Mertens',
    author_email='mertens.ulf@gmail.com',
    entry_points={
        'console_scripts': [
            'abrox-gui = abrox.gui.main:main'
        ]
    },
    url='https://github.com/mertensu/ABrox',  # use the URL to the github repo
    download_url='https://github.com/mertensu/ABrox/archive/0.1.tar.gz',
    setup_requires=['numpy'],
    install_requires=['numpy',
                      'scipy',
                      'statsmodels',
                      'pandas',
                      'pyqt5',
                      'qdarkstyle',
                      'ipython',
					  'scikit-learn',
                      'matplotlib',
                      'qtconsole'
                      ],
    classifiers=[],
)
