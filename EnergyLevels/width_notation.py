# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 16:33 2025

@author: Alan D.K.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path


def plot_width_boxes (ax,x,y,state_width, color, box_side, width_spacing_f ):
    Xi = x - box_side*0.5 + box_side*width_spacing_f
    Yi = y - state_width

    #plot the rectangle
    square =  patches.Rectangle(
    (Xi, Yi), # X,Y
    box_side*(1-width_spacing_f*2),
    state_width*2,
    fill=True,
    fc = color,
    alpha = 0.4,
    ec = None,
    zorder=10)
    ax.add_patch(square)

if __name__ == '__main__':
    fig = plt.figure()
    ax = fig.add_subplot(111,aspect = 'equal')
    ax.set_xlim(10,14)
    ax.set_ylim(8,12)
    plot_width_boxes(ax,12,10, 3,4)
    plt.grid()
