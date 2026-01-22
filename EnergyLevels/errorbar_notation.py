# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 13:13 2026

@author: Alan D.K.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches


def plot_errorbar (ax,x,y,state_uncertainty, colorin, box_side ):
    X = x
    Yi = y - state_uncertainty
    Yf = y + state_uncertainty
    head_width = box_side *10  # Width of the arrow heads

    #plot a symmetric errorbar using the function FancyArrowPatch 
    errorbar =  patches.FancyArrowPatch(
    (X, Yi), (X, Yf), # Start and end points
    arrowstyle='|-|',
    color = colorin,
    mutation_scale=head_width)
    ax.add_patch(errorbar)

if __name__ == '__main__':
    fig = plt.figure()
    ax = fig.add_subplot(111,aspect = 'equal')
    ax.set_xlim(10,14)
    ax.set_ylim(8,12)
    plot_errorbar(ax,12,10, 3)
    plt.grid()
