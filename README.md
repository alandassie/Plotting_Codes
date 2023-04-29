# Plotting Codes
This is a set of python codes used for the Plotting of calculated observables and its experimental values.

## This is the full list of codes

### Energy Levels
This code is originally of Giacomo Marchioro (https://github.com/giacomomarchioro/PyEnergyDiagrams). Is a simple script to plot energy profile diagram using matplotlib.
```
E|          4__
n|   2__    /  \
e|1__/  \__/5   \
r|  3\__/       6\__
g|
y|
```
In the file energydiagram.py you can change the ticks spacing, the size of the figure, the colors, the axes limits, etc. This is founded in the function plot.

The following python packages are needed:\
    - scienceplots\
    - matplotlib\
    And the xetex package for save pgf files