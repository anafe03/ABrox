![Logo](abrox/gui/icons/readme_logo.png)

# Approximate Bayes rocks!

`ABrox` is a python package for Approximate Bayesian Computation accompanied by a user-friendly graphical interface. 

## Features

* Model comparison via approximate Bayes factors
    + rejection
    + random forest
* Parameter inference
    + rejection
    + MCMC
 * Cross-validation

## Installation

Note that `ABrox`only works with Python 3.

`ABrox` can be installed via pip. Simply open a terminal and type:

```bash
pip install abrox
```

It might take a few seconds since there are several dependencies that you might have to install as well. 

### MacPorts

If you installed Python via MacPorts, the `abrox-gui` command after installation of `abrox` does not work.
You can alternatively start the GUI via (assuming Python version 3.5):

```bash
cd /Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/abrox/gui/
python3.5 main.py
```

### Windows

Unfortunately, the installation under Windows is a bit cumbersome. We explain the relevant steps below.

If not already done, install a Python3 version from [here](https://www.python.org/).

Check the version of Python that is installed by typing `python` into the console.

![Python on Windows](abrox/gui/icons/python_windows2.png)

Now, install Visual Studio Build Tools from:

1. [here](http://landinghub.visualstudio.com/visual-cpp-build-tools)

Now visit the following page to install the Scipy wheel. Choose the link that fits
your Python version (see picture above). `cp` should be followed by the actual version (e.g. `cp36`) while
the last part of the link should match the bit-version (e.g. `win32`).  

2. [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy)

After the installation, open a console in the directory the wheel has been downloaded into and type:

```bash
python -m pip install #name_of_the_whl_file
``` 

Repeat the same steps for the Numpy wheel:

3. [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy)

Now, open a terminal and type:

```bash
python -m pip install abrox
```

You are now ready to use `ABrox`!

## ABrox using the GUI

After `ABrox` has been installed, you can start the user interface by typing `abrox-gui`.
We provide several templates in order to get more familiar with the GUI. 

## ABrox using Python

If you are more comfortable with plain Python, you can run your project once from the GUI and
continue working with the Python-file that has been generated in the output folder.

## Templates

We provide a few example project files so you can see how `ABrox` works ([here](https://github.com/mertensu/ABrox/tree/master/project_files)). 
Currently, we provide:

* Two-sample t-test
* Levene-Test

### Contributors

* [Ulf Mertens](http://www.psychologie.uni-heidelberg.de/ae/meth/team/mertens/)
* Stefan Radev