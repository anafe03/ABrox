from setuptools import setup, find_packages
setup(
    name='abrox',
    packages=find_packages(),
    include_package_data=True,
    version='0.0.5',
    license='MIT',
    description='A GUI for Approximate Bayesian Computation',
    long_description=open('README.md').read(),
    author='Ulf Mertens',
    author_email='mertens.ulf@gmail.com',
    entry_points={
        'gui_scripts': [
            'abrox-gui = abrox.__main__:main'
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
                      'ipython'
                      ],
    classifiers=[],
)
