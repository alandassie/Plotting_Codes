"""
    This is the main file example to use with the
    code energydiagram by Giacomo Marchioro.

    In the file energydiagram.py you can change
    the ticks spacing, the size of the figure,
    the colors, the axes limits, etc.
    This is founded in the function plot.

    The following python packages are needed:
    - scienceplots
    - matplotlib
"""

from energydiagram import ED
from matplotlib import pyplot as plt
import numpy as np # To read energy levels from a file

# Experimental Energy of the core. This is used to plot positive energies
exp0 = -19.843

Ca42 = ED() # This is the Figure where we gonna add energy levels

# First we add the experimental energies
Ca42.add_level(0    ,top_text='', bottom_text='Experimental', left_text='$0^+$') 
Ca42.add_level(1.837, top_text='', bottom_text='', left_text='', position='last') # $0^+$
Ca42.add_level(3.300, top_text='', bottom_text='', left_text='', position='last') # $0^+$
# Ca42.add_level(5.345, top_text='', bottom_text='', left_text='', position='last') # $0^+$
# Ca42.add_level(5.860, top_text='', bottom_text='', left_text='', position='last') # $0^+$
# Ca42.add_level(6.016, top_text='', bottom_text='', left_text='', position='last') # $0^+$
# Ca42.add_level(6.080, top_text='', bottom_text='', left_text='', position='last') # $0^+$
# Ca42.add_level(6.720, top_text='', bottom_text='', left_text='$0^+_2$', position='last') # $0^+$
Ca42.add_level(1.525, top_text='', bottom_text='', left_text='$2^+$', position='last')
Ca42.add_level(2.424, top_text='', bottom_text='', right_text='', position='last') # $2^+$
Ca42.add_level(3.392, top_text='', bottom_text='', left_text='', position='last') # $2^+$
Ca42.add_level(3.654, top_text='', bottom_text='', left_text='', position='last') # $2^+$
Ca42.add_level(4.449, top_text='', bottom_text='', right_text='$2^+$', position='last') # $2^+$
Ca42.add_level(4.760, top_text='', bottom_text='', left_text='', position='last') # $2^+$
Ca42.add_level(4.866, top_text='', bottom_text='', left_text='', position='last') # $2^+$
# Ca42.add_level(5.358, top_text='', bottom_text='', left_text='', position='last') # $2^+$
# Ca42.add_level(5.530, top_text='', bottom_text='', left_text='', position='last') # $2^+$
# Ca42.add_level(5.716, top_text='', bottom_text='', left_text='', position='last') # $2^+$
# Ca42.add_level(5.875, top_text='', bottom_text='', left_text='', position='last') # $2^+$
# Ca42.add_level(6.274, top_text='', bottom_text='', left_text='', position='last') # $2^+$
# Ca42.add_level(7.180, top_text='', bottom_text='', left_text='$2^+_3$', position='last') # $2^+$
Ca42.add_level(2.752, top_text='', bottom_text='', left_text='$4^+$', position='last')
Ca42.add_level(3.254, top_text='', bottom_text='', left_text='', position='last') # $4^+$
Ca42.add_level(4.000, top_text='', bottom_text='', left_text='', position='last') # $4^+$
Ca42.add_level(4.443, top_text='', bottom_text='', left_text='$4^+$', position='last') # $4^+$
# Ca42.add_level(5.017, top_text='', bottom_text='', left_text='', position='last') # $4^+$
# Ca42.add_level(6.113, top_text='', bottom_text='', left_text='', position='last') # $4^+$
# Ca42.add_level(6.746, top_text='', bottom_text='', left_text='', position='last') # $4^+$
# Ca42.add_level(6.895, top_text='', bottom_text='', right_text='$4^+_3$', position='last') # $4^+$
Ca42.add_level(3.189, top_text='', bottom_text='', left_text='$6^+$', position='last') # $6^+_1$
Ca42.add_level(3.447, top_text='', bottom_text='', right_text='', position='last') # $3^-$
Ca42.add_level(4.690, top_text='', bottom_text='', left_text='', position='last') # $3^-$
Ca42.add_level(4.100, top_text='', bottom_text='', left_text='', position='last') # $5^-$
#
# The upper lines can be rewritted in one read from file line:
# exp = np.genfromtxt('42Ca.csv', dtype=None ) # Read the csv file
# A210.add_level(exp['f0'][0], top_text='', bottom_text=r'Exp. $^{210}$Pb', left_text='$0^+$', color='black') # Add the Ground state level, check the correct J^Pi
# for i in range(1,len(exp)):
#     ene = exp['f0'][i]/1000
#     if ene > 5: # Only plot energies under the 1.5 MeV of excitation. This can be modified
#         continue
#     if exp['f2'][i] != 1 or  exp['f3'][i] != 0: # Avoid plotting state with uncertainty, see the input file
#         continue
#     A210.add_level(ene, top_text='', bottom_text='', left_text='${0:s}$'.format(exp['f1'][i].decode('UTF-8')), color='black', position='last')

# Plotting the Calculated energies, read them from a file
calc = np.genfromtxt('NNEnergies.dat')
Ca42.add_level(-exp0+calc[0,3], top_text='', bottom_text='Calculated', left_text='$0^+$', color='red')
for i in range(1,len(calc)):
    line = calc[i]
    if line[3] > 0 :
        continue
    ene = -exp0+line[3]
    if ene > 5: # Only plot energies under the 5 MeV of excitation. This can be modified
        continue
    if line[2] == 1:
        pp = '+'
    else:
        pp = '-'
    jj = int(line[1])
    Ca42.add_level(ene, top_text='', bottom_text='', left_text='${0:1d}^{1:s}$'.format(jj,pp), color='red', position='last')

# Ca42.plot(show_IDs=True) # This is usefull if you want to link two columns
Ca42.plot()
plt.tight_layout()

# To save Fig, coment the line "plt.rcParams.update({'figure.dpi': '100'})" in file "energydiagram.py" 
plt.savefig('TB_NN.pgf',format='pgf')

# To Show Fig, uncoment the line "plt.rcParams.update({'figure.dpi': '100'})" in file "energydiagram.py" 
# plt.show()
