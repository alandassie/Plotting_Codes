"""
    Created on 26.02.24 by Alan Dassie K. for
    the different projects of the GSMCC code.
    
    This code is for plotting the elastic scattering cross-section
    of different T+p systems calculated with GSMCC. It can also compare 
    with experimental data if available.

    All the information about the calculation data is at the beginning, 
    so this code is generic and can be used for any T+p system. 
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
name_figure = "CC_elastic-p"
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
#
#_________________________________________________________________________________________
# General information about the reaction
type_frame = 2 # 1 for CM frame, 2 for Lab frame
projectile = "3He" # Only needed if type_frame is 2
if type_frame == 1:
    frame = "CM"
elif type_frame == 2:
    frame = "Lab"
#
rutherford_cross_section = True # True if you want to plot versus Rutherford cross-section, False if you want to plot the cross-section as it is
rutherford_option = 2 # Only needed if rutherford_cross_section is True. 1 for GSMCC Rutherford, 2 for Analytical formula (Messiah)
charge_target = 2 # Only needed if rutherford_option is 2. Charge of the target for the Rutherford formula
charge_projectile = 2 # Only needed if rutherford_option is 2. Charge of the projectile for the Rutherford formula
num_subplots = 2 # 1 for only one plot with all the angles, 2 for one plot for each angle
num_angles = 3 # Number of angles to plot
angles = [90.75,126.1,159.12] # Angles in degrees (Same frame as type of plot)
#
#_________________________________________________________________________________________
# Files with the GSMCC data to plot
gsm_folder = "7Be_cir_elastic-3He-26.02.11-18.00_3HeV012From-1967npaDunnill-26.02.11-17.00"
channel = '0' # Since we are plotting elastic scattering, the entrance and exit channels are the same
gsm_files = ["scattering_excitation_function_%s_entrance_channel_%s_iT_%s_i_theta_%s.dat"% (frame,channel,channel,str(ang)) for ang in angles]
#
#_________________________________________________________________________________________
# Files with the experimental data to plot
experimental_data = True # True if you want to plot experimental data, False if you want to plot only GSMCC data
exp_folder = "experimental_data"
exp_files = ["CS-vs-Ruth_p-elastic_1936McCray_Theta%s.dat"% ang for ang in angles]
col_ene_exp = 0 # Column with the energy
col_cs_exp = 3 # Column with the cross-section (or cross-section vs Rutherford ratio) in the experimental data files
divide_exp_by_ruth = False # True if the experimental data is given as cross-section and you want to divide it by the Rutherford cross-section, False if the experimental data is already given as cross-section vs Rutherford ratio
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
def rutherford_cross_section_calc(theta_cm,
                             E_cm,
                             Z1,
                             Z2,
                             theta_in_degrees=True):
    """
    Calculate Rutherford differential cross section from Messiah's point-like formula (Eq. XI.36 in Quantum Mechanics, Vol. 1, 1962).

    Parameters
    ----------
    theta_cm : float
        Center-of-mass scattering angle.
        Degrees if theta_in_degrees=True, otherwise radians.
    E_cm : array-like
        Center-of-mass energy in MeV.
    Z1, Z2 : int
        Charges of projectile and target.
    theta_in_degrees : bool, optional
        If True, theta_cm is given in degrees (default: True).

    Returns
    -------
    array-like
        Differential cross section in millibarn per steradian (mb/sr).
    """

    # Convert angle to radians if needed
    if theta_in_degrees:
        theta = np.deg2rad(theta_cm)
    else:
        theta = theta_cm

    # dsigma/domega output array
    dsigma_domega_mb = np.zeros(len(E_cm))

    for i, energy in enumerate(E_cm):
        # Rutherford formula in fm^2/sr
        prefactor = (Z1 * Z2 * e2 / (4.0 * energy))**2
        dsigma_domega_fm2 = prefactor / (np.sin(theta / 2.0)**4)
        
        # Convert fm^2 to mb (1 fm^2 = 10 mb)
        dsigma_domega_mb[i] = dsigma_domega_fm2 * fm2_to_mb

    return dsigma_domega_mb
# .-
##########################################################################################

# Prepare plot
n_cols = 1
n_rows = 1
sharex_bool = False
sharey_bool = False
if num_subplots == 2:
    if num_angles <= 3: # If there are less than 3 angles, put them in a single column plot
        n_rows = num_angles
        sharex_bool = True
        sharey_bool = False
    else:
        n_cols = 2
        n_rows = int(num_angles/2)+1
        sharex_bool = True
        sharey_bool = "row"

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
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(yminor))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(ymajor))
    for tick in ax.get_xticklabels():
        tick.set_fontsize(11)
    for tick in ax.get_yticklabels():
        tick.set_fontsize(11)  
    #
    # if i == 1:
    if rutherford_cross_section:
        ax.set_ylabel(r"$d\sigma/d\sigma_R$", fontsize=14)
    else:
        ax.set_ylabel(r"$d\sigma/d\Omega$ (mb/sr)", fontsize=14)
    # if i//2 == 1:
    if type_frame == 1:
        ax.set_xlabel(r"$E_\mathrm{%s}$ (MeV)"% frame, fontsize=14)
    elif type_frame == 2:
        ax.set_xlabel(r"$E_\mathrm{%s}[%s]$ (MeV)"% (frame,projectile), fontsize=14)
    #
    # ax.set_xlim(0.5,2.5)
    #
    if num_subplots == 2:
        ax.set_title(r'$\theta_{%s} = %s^\circ$'% (frame,str(angles[i])), fontsize=12, y=1.0, pad=-14)
    # Read GSMCC data
    gsm_file = gsm_files[i]
    gsm_data = np.genfromtxt(gsm_file)
    if type_frame == 1:
        energy = gsm_data[:,1]
    elif type_frame == 2:
        energy = gsm_data[:,2]
    #
    cs = gsm_data[:,-2]
    if rutherford_cross_section and rutherford_option == 1:
        cs_vs_ruth = gsm_data[:,-1]
    elif rutherford_cross_section and rutherford_option == 2 and type_frame == 1: # Only works for CM frame, since the Rutherford formula is for CM frame.
        cs_vs_ruth = gsm_data[:,-2]/rutherford_cross_section_calc(angles[i], energy, Z1=charge_target, Z2=charge_projectile, theta_in_degrees=True)
    #
    if rutherford_cross_section:
        ax.plot(energy,cs_vs_ruth, color=colors(0), marker='', ls='--', label=r'GSMCC')
    else:
        ax.plot(energy,cs, color=colors(0), marker='', ls='--', label=r'GSMCC')
    #
    if experimental_data:
        exp_file = exp_files[i]
        exp_data = np.genfromtxt(exp_file)
        #
        energy_exp = exp_data[:,col_ene_exp]
        cs_exp = exp_data[:,col_cs_exp]
        #
        if rutherford_cross_section and divide_exp_by_ruth:
            cs_vs_ruth_exp = cs_exp/rutherford_cross_section_calc(angles[i], energy_exp, Z1=charge_target, Z2=charge_projectile, theta_in_degrees=True)
            ax.plot(energy_exp,cs_vs_ruth_exp, color=colors(1), marker='s', markersize=1.5, ls='', label='Exp')
        else:
            ax.plot(energy_exp,cs_exp, color=colors(1), marker='s', markersize=1.5, ls='', label='Exp')
    #
    # Read experimental data
    exp_file = exp_files[i]
    exp_data = np.genfromtxt(exp_file)
    #
    ecm_exp = exp_data[:,2]
    cs_vs_ruth_exp = exp_data[:,3]
    #
    ax.plot(ecm_exp, cs_vs_ruth_exp, color=colors(1), marker='s', markersize=1.5, ls='', label='Exp')
    # ax.set_title(r'$\theta_{CM} = %s$'% ang, fontsize=12)
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

