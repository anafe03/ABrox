![Logo](abrox/gui/icons/logo.png)

# ABrox

`ABrox` is a python package for Approximate Bayesian Computation accompanied by a user-friendly graphical interface. 

In the current version, we use the ABC rejection algorithm with a local regression adjustment for the
case of parameter inference, and local logistic (multinomial) regression for model comparison. 

## Features

* Model comparison via approximate Bayes factors
* Parameter inference

![Screenshot](abrox/gui/icons/screen.png)

## Installation

`ABrox` can be installed via pip. Simply type `pip install abrox` into your terminal. It might take
a few seconds since there are several dependencies that you might have to install as well. 

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

Ulf Mertens \& Stefan Radev