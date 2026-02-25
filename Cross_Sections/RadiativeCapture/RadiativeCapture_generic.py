"""
    Created on 26.02.24 by Alan Dassie K. for
    the different projects of the GSMCC code.
    
    This code is for plotting the radiative capture cross-section and/or 
    astrophysical factor for different projectiles calculated with GSMCC.
    It can also compare with experimental data if available.

    All the information about the calculation data is at the beginning, 
    so this code is generic and can be used for any system. 
    You just need to change the input file and the names of the files with the data to plot.
    
    The following python packages are needed:
    - scienceplots
    - matplotlib
    And the xetex package for save pgf files
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import scienceplots # From https://github.com/garrettj403/SciencePlots
from scipy.interpolate import CubicSpline as CS

##########################################################################################
# Declaration of variables
#_________________________________________________________________________________________
# Information for the plot
save_fig = False # True if you want to save the figure, False if you want to show it
name_figure = "CC_radcap-3Hea"
format_out = "pdf"
outputfile = name_out + '.' + format_out
# Fig formats
dpi = 200 # Dots per inch
x_figsize = 600 # X Size of each subplot in pixel, but it will be converted to inches later
y_figsize = 600 # Y Size of each subplot in pixel, but it will be converted to inches later
yminor = 0.1 # Minor Tick spacing
ymajor = 1 # Major Tick Spacing
xminor = 0.2 # Minor Tick spacing
xmajor = 2 # Major Tick Spacing
xlim_low = 0.1 # Lower limit for the x-axis in MeV
xlim_upp = 3.5 # Upper limit for the x-axis in MeV
#
#_________________________________________________________________________________________
# General information about the reaction
type_frame = 2 # 1 for CM frame, 2 for Lab frame
projectile = "3He" # Only needed if type_frame is 2
if type_frame == 1:
    frame = "CM"
elif type_frame == 2:
    frame = "Lab"
is_cross_section = True # True if you want to plot the cross-section
is_astrophysical_factor = False # True if you want to plot the astrophysical factor
if is_cross_section:
    cross_section_log = True # True if you want to plot the cross-section in log scale, False if you want to plot it in linear scale
    ylim_cs = [1e-3, 1e3] # Y limits for the cross-section plot in mb
if is_astrophysical_factor:
    astrophysical_factor_log = False # True if you want to plot the astrophysical factor in log scale, False if you want to plot it in linear scale
    ylim_af = [0, 1] # Y limits for the astrophysical factor plot in MeV*barn
is_subplots = False
if is_cross_section and is_astrophysical_factor:
    is_subplots = True
#
#_________________________________________________________________________________________
# Files with the GSMCC data to plot
gsm_folder = "7Be_radcap-3He-26.02.17-18.00_3HeV012From-1967npaDunnill-26.02.11-17.00_ECEq"
gsm_files = os.listdir(gsm_folder)
plot_each_gsmcc_component = False # True if you want to plot each component E\lambda,M\lambda of the cross-section and/or astrophysical factor
if plot_each_gsmcc_component:
    num_components = 2 # Set a limit for \lambda, for example if you want to plot only E1 and M1 contributions, set num_components = 1
#
#_________________________________________________________________________________________
# Files with the experimental data to plot
experimental_data = True # True if you want to plot experimental data, False if you want to plot only GSMCC data
exp_folder = "experimental_data"
exp_files = [exp_folder+"/CS-3He-g_1982zpaKrawinkel.exp",exp_folder+"/CS-3He-g_1983zpaVolk-BR1.0exp"]
col_ene_exp = 0 # Column with the energy
if is_cross_section:
    col_cs_exp = 3 # Column with the cross-section in the experimental data files
if is_astrophysical_factor:
    col_af_exp = 4 # Column with the astrophysical factor in the experimental data files
##########################################################################################


##########################################################################################
# Declaration of funcitons
# Idea from https://stackoverflow.com/questions/3961265/get-line-number-of-certain-phrase-in-text-file
def searchline(file,phrase):
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
        if phrase in text:
            phrase_index = text.index(phrase)
            l_num = text[:phrase_index].count('\n')  # Nth line has n-1 '\n's before
        else:
            l_num = None
    return l_num
def searchlinefinal(file,phrase):
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
        if phrase in text:
            phrase_index = text.rindex(phrase)
            l_num = text[:phrase_index].count('\n')  # Nth line has n-1 '\n's before
        else:
            l_num = None
    return l_num
# .-
##########################################################################################

# Prepare plot
n_cols = 1
n_rows = 1
sharex_bool = False
sharey_bool = False
if is_subplots:
    n_cols = 2
    sharex_bool = True

#
plt.style.use(['science','scatter'])
plt.rcParams.update({'figure.dpi': dpi})
px = 1/plt.rcParams['figure.dpi']  # pixel in inches
fig, axs = plt.subplots(n_rows,n_cols, figsize=(x_figsize*px*n_cols, y_figsize*px*n_rows), sharex=sharex_bool, sharey=sharey_bool)
colors = plt.get_cmap('tab10', 10)
for i, ax in enumerate(axs.flatten()):
    # Edit the major and minor ticks of the x and y axes
    ax.xaxis.set_tick_params(which='major', size=7, width=0.5, direction='in',top=True)
    ax.xaxis.set_tick_params(which='minor', size=3, width=0.5, direction='in',top=True)
    ax.yaxis.set_tick_params(which='major', size=7, width=0.5, direction='in',right=True)
    ax.yaxis.set_tick_params(which='minor', size=3, width=0.5, direction='in',right=True)
    # Edit the major and minor tick locations
    ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(xminor))
    ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(xmajor))
    if is_subplots:
        if i == 0 and not cross_section_log:
            ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(yminor))
            ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(ymajor))
        elif i == 0 and cross_section_log:
            ax.set_yscale('log')
        if i == 1 and not astrophysical_factor_log:
            ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(yminor))
            ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(ymajor))
        elif i == 1 and astrophysical_factor_log:
            ax.set_yscale('log')
    else:
        if is_cross_section and not cross_section_log:
            ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(yminor))
            ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(ymajor))
        elif is_cross_section and cross_section_log:
            ax.set_yscale('log')
        if is_astrophysical_factor and not astrophysical_factor_log:
            ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(yminor))
            ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(ymajor))
        elif is_astrophysical_factor and astrophysical_factor_log:
            ax.set_yscale('log')
    #
    ax.set_xlim(xlim_low, xlim_upp)
    #
    for tick in ax.get_xticklabels():
        tick.set_fontsize(11)
    for tick in ax.get_yticklabels():
        tick.set_fontsize(11)  
    #
    if type_frame == 1:
        ax.set_xlabel(r'$E_\mathrm{%s}$ (MeV)'% frame, fontsize=12)
    elif type_frame == 2:
        ax.set_xlabel(r'$E_\mathrm{%s}[%s]$ (MeV)'% (frame,projectile), fontsize=12)
    #
    if is_subplots:
        if i == 0:
            ax.set_ylabel(r'$\sigma$ (mb)', fontsize=12)
        elif i == 1:
            ax.set_ylabel(r'$S$ (MeV b)', fontsize=12)
    else:
        if is_cross_section:
            ax.set_ylabel(r'$\sigma$ (mb)', fontsize=12)
        elif is_astrophysical_factor:
            ax.set_ylabel(r'$S$ (MeV b)', fontsize=12)
    #
    total_gsm_cs = []
    total_gsm_af = []
    # First subplot for the cross-section
    for k, gsm_file in enumerate(gsm_files):
        gsm_data = np.genfromtxt(gsm_file)
        #
        if type_frame == 1:
            energy = gsm_data[:,0]
        elif type_frame == 2:
            energy = gsm_data[:,1]
        #
        cs = gsm_data[:,-1]
        af = gsm_data[:,-2]
        if k == 0:
            total_gsm_cs = cs
            total_gsm_af = af
        else:
            total_gsm_cs += cs
            total_gsm_af += af
        #
        lambda_value = int(gsm_file.find("E")+1) if "E" in gsm_file else int(gsm_file.find("M")+1)
        if "E" in gsm_file:
            em_transition = "E%s" % lambda_value
            ls_case = "--"
        elif "M" in gsm_file:
            em_transition = "M%s" % lambda_value
            ls_case = "-."
        #
        if plot_each_gsmcc_component and lambda_value <= num_components:
            if is_subplots:
                if i == 0:
                    ax.plot(energy,cs, color=colors(lambda_value), marker='', ls=ls_case, label=r'$%s$'% em_transition)
                elif i == 1:
                    ax.plot(energy,af, color=colors(lambda_value), marker='', ls=ls_case, label=r'$%s$'% em_transition)
            else:
                if is_cross_section:
                    ax.plot(energy,cs, color=colors(lambda_value), marker='', ls=ls_case, label=r'$%s$'% em_transition)
                if is_astrophysical_factor:
                    ax.plot(energy,af, color=colors(lambda_value), marker='', ls=ls_case, label=r'$%s$'% em_transition)
        #
    if is_subplots:
        if i == 0:
            ax.set_ylim(ylim_cs[0], ylim_cs[1])
            ax.plot(energy,total_gsm_cs, color='k', marker='', ls='-', label=r'Total GSMCC')
        elif i == 1:
            ax.set_ylim(ylim_cs[0], ylim_cs[1])
            ax.plot(energy,total_gsm_af, color='k', marker='', ls='-', label=r'Total GSMCC')
    else:
        if is_cross_section:
            ax.set_ylim(ylim_cs[0], ylim_cs[1])
            ax.plot(energy,total_gsm_cs, color='k', marker='', ls='-', label=r'Total GSMCC')
        if is_astrophysical_factor:
            ax.set_ylim(ylim_af[0], ylim_af[1])
            ax.plot(energy,total_gsm_af, color='k', marker='', ls='-', label=r'Total GSMCC')
    #
    # Read experimental data
    exp_file = exp_files[i]
    exp_data = np.genfromtxt(exp_file)
    #
    energy_exp = exp_data[:,col_ene_exp]
    if is_subplots:
        if i == 0:
            cs_exp = exp_data[:,col_cs_exp]
            ax.plot(energy_exp,cs_exp, color=colors(0), marker='s', markersize=1.5, ls='', label='Exp')
        elif i == 1:
            af_exp = exp_data[:,col_af_exp]
            ax.plot(energy_exp,af_exp, color=colors(0), marker='s', markersize=1.5, ls='', label='Exp')
    else:
        if is_cross_section:
            cs_exp = exp_data[:,col_cs_exp]
            ax.plot(energy_exp,cs_exp, color=colors(0), marker='s', markersize=1.5, ls='', label='Exp')
        if is_astrophysical_factor:
            af_exp = exp_data[:,col_af_exp]
            ax.plot(energy_exp,af_exp, color=colors(0), marker='s', markersize=1.5, ls='', label='Exp')
    #
    ax.legend()

plt.tight_layout()
if num_subplots == 2:
    plt.subplots_adjust(wspace=0, hspace=0)
# plt.legend()
if save_fig:
    plt.savefig(outputfile, format=format_out)
else:
    plt.show()
# plt.close()

