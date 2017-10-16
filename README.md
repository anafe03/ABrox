![Logo](abrox/gui/icons/readme_logo.png)

# ABrox

`ABrox` is a python package for Approximate Bayesian Computation accompanied by a user-friendly graphical interface. 

In the current version, we use the ABC rejection algorithm with a local regression adjustment for the
case of parameter inference, and local logistic (multinomial) regression for model comparison. 

## Features

* Model comparison via approximate Bayes factors
* Parameter inference

## Installation

`ABrox` can be installed via pip. Simply open a terminal and type:

```
pip install abrox
```

It might take a few seconds since there are several dependencies that you might have to install as well. 

### Windows

Assuming Python is already installed, first install Visual Studio Build Tools from:

1. [here](http://landinghub.visualstudio.com/visual-cpp-build-tools)

Now visit the following page to install the Scipy wheel:

2. [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy)

After the installation, open a console in the download directory and type:

```
python -m pip install #name_of_the_whl_file
``` 

Then:

```
python -m pip install numpy
```

Then:

```
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

We provide a few example project files so you can see how `ABrox` works ([here](https://github.com/mertensu/ABrox/tree/master/templates)). 
Currently, we provide:

* Two-sample t-test
* Levene-Test
* Multinomial Processing tree (comparison)

### Contributors

[Ulf Mertens](http://www.psychologie.uni-heidelberg.de/ae/meth/team/mertens/)
 and Stefan Radev