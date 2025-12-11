# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 16:33 2025

@author: Alan D.K.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path


def plot_width_boxes (ax,x,y,state_width, box_side = 1, spacing_f = 5 ):
    Xi = x - box_side/2.
    Yi = y - state_width

    #plot the rectangles
    for i in range(boxes_number):
        square =  patches.Rectangle(
        (Xi+box_side*i, Yi), # X,Y
        box_side,
        box_side,
        fill=True,
        fc = 'w',
        zorder=10)
        ax.add_patch(square)
    #plot the spins using Aufbau
    if electrons_number > 0:
        moduloelectrons = electrons_number%boxes_number
        print(moduloelectrons)
        if moduloelectrons > boxes_number:
            Warning ("electrons_number grater than boxes number")
        if electrons_number <= boxes_number:
            for j in range(electrons_number):
                ax.add_patch(add_spin(Xi+box_side*j,Yi,box_side,direction='up'))
        else:
            for e in range(moduloelectrons):
                ax.add_patch(add_spin(Xi+box_side*e,Yi,box_side,direction='down'))
            for j in range(boxes_number):
                ax.add_patch(add_spin(Xi+box_side*j,Yi,box_side,direction='up'))

if __name__ == '__main__':
    fig = plt.figure()
    ax = fig.add_subplot(111,aspect = 'equal')
    ax.set_xlim(10,14)
    ax.set_ylim(8,12)
    plot_orbital_boxes(ax,12,10, 3,4)
    plt.grid()
