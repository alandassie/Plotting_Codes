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
    And the xetex package for save pgf files
"""

import os
from energydiagram import ED
from matplotlib import pyplot as plt

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

# INPUT FILE
readfilename = os.getcwd() + '/data.in'
with open(readfilename, 'r') as readfile:
    data = readfile.read().split('\n')

# READING INIT INFORMATION
# Output file
theline = searchline(readfilename,"OUTPUT FILE") 
name_out = data[theline+1]
format_out = data[theline+2]
outputfile = name_out + '.' + format_out
# Fig formats
dpi = float(data[theline+3])
aux_figsize = data[theline+4].split(',')
x_figsize = float(aux_figsize[0])
y_figsize = float(aux_figsize[1])
yminor = float(data[theline+5].split(',')[0])
ymajor = float(data[theline+5].split(',')[1])
figratio = float(data[theline+6])
# Experimental Energy of the core. This is used to plot positive energies
theline = searchline(readfilename,"EXP BINDING ENERGY") 
exp0 = float(data[theline+1])
# Number of data for plot
theline = searchline(readfilename,"NUM DATA") 
cols = int(data[theline+1])

# Begin the plot
figure = ED() # This is the Figure where we gonna add energy levels
# Config the figure
figure.fig_parameters(figratio,dpi,x_figsize,y_figsize, yminor, ymajor)

# Plotting the data
for k in range(1,cols+1):
    theline = searchline(readfilename,"DATA-%s"% k) 
    data_len = int(data[theline+1])
    data_name = data[theline+2]
    if data_name == 'None':
        data_name = None
    data_color = int(data[theline+3])
    data_ls = data[theline+4]
    #
    for i in range(0,data_len):
        # Main information of the level
        line = data[theline+7+i]
        ene = float(line.split()[0])
        jj = line.split()[1]
        parity = int(line.split()[2])
        if parity == 0:
            pp = '-'
        elif parity == 1:
            pp = '+'
        index = int(line.split()[3])
        jpi_pos = line.split()[4]
        bttm = line.split()[5]
        if bttm == 'None':
            bttm = ''
        top = line.split()[6]
        if top == 'None':
            top = ''
        level_color = data_color
        level_ls = data_ls
        # Any aditional information
        if len(line.split()) > 7:
            level_color = int(line.split()[7])
            level_ls = line.split()[8]
        #
        if i == 0:
            if jj != '-1':            
                if index >= 0:
                    if jpi_pos == 'left':
                        figure.add_level(ene, top_text=top, bottom_text=data, left_text='${0:s}^{1:s}_{2:1d}$'.format(jj,pp,index), set_title=data_name, color=level_color, linestyle=level_ls)
                    elif jpi_pos == 'right':
                        figure.add_level(ene, top_text=top, bottom_text=bttm, right_text='${0:s}^{1:s}_{2:1d}$'.format(jj,pp,index), set_title=data_name, color=level_color, linestyle=level_ls)
                else:
                    if jpi_pos == 'left':
                        figure.add_level(ene, top_text=top, bottom_text=bttm, left_text='${0:s}^{1:s}$'.format(jj,pp), set_title=data_name, color=level_color, linestyle=level_ls)
                    elif jpi_pos == 'right':
                        figure.add_level(ene, top_text=top, bottom_text=bttm, right_text='${0:s}^{1:s}$'.format(jj,pp), set_title=data_name, color=level_color, linestyle=level_ls)
            else:
                figure.add_level(ene, top_text=top, bottom_text=bttm, set_title=data_name, color=level_color, linestyle=level_ls)
        else:
            if jj != '-1':  
                if index >= 0:
                    if jpi_pos == 'left':
                        figure.add_level(ene, top_text=top, bottom_text=bttm, left_text='${0:s}^{1:s}_{2:1d}$'.format(jj,pp,index), color=level_color, linestyle=level_ls, position='last')
                    elif jpi_pos == 'right':
                        figure.add_level(ene, top_text=top, bottom_text=bttm, right_text='${0:s}^{1:s}_{2:1d}$'.format(jj,pp,index), color=level_color, linestyle=level_ls, position='last')
                else:
                    if jpi_pos == 'left':
                        figure.add_level(ene, top_text=top, bottom_text=bttm, left_text='${0:s}^{1:s}$'.format(jj,pp), color=level_color, linestyle=level_ls, position='last')
                    elif jpi_pos == 'right':
                        figure.add_level(ene, top_text=top, bottom_text=bttm, right_text='${0:s}^{1:s}$'.format(jj,pp), color=level_color, linestyle=level_ls, position='last')
            else:
                figure.add_level(ene, top_text=top, bottom_text=bttm, color=level_color, linestyle=level_ls, position='last')

# Linking
# # 0^+
# A210.add_link(0,5,linewidth=0.75)
# A210.add_link(5,10,linewidth=0.75)
# A210.add_link(16,21,linewidth=0.75)
# A210.add_link(21,26,linewidth=0.75)
# # 2^+
# A210.add_link(1,6,linewidth=0.75)
# A210.add_link(6,11,linewidth=0.75)
# A210.add_link(17,22,linewidth=0.75)
# A210.add_link(22,27,linewidth=0.75)
# # 4^+
# A210.add_link(2,7,linewidth=0.75)
# A210.add_link(7,12,linewidth=0.75)
# A210.add_link(18,23,linewidth=0.75)
# A210.add_link(23,28,linewidth=0.75)
# # 6^+
# A210.add_link(3,8,linewidth=0.75)
# A210.add_link(8,13,linewidth=0.75)
# A210.add_link(19,24,linewidth=0.75)
# A210.add_link(24,29,linewidth=0.75)
# # 8^+
# A210.add_link(4,9,linewidth=0.75)
# A210.add_link(9,14,linewidth=0.75)
# A210.add_link(20,25,linewidth=0.75)
# A210.add_link(25,30,linewidth=0.75)


# Ca42.plot(show_IDs=True) # This is usefull if you want to link two columns
figure.plot()
plt.tight_layout()

# To save Fig, coment the line "plt.rcParams.update({'figure.dpi': '100'})" in file "energydiagram.py" 
plt.savefig(outputfile,format=format_out)

# To Show Fig, uncoment the line "plt.rcParams.update({'figure.dpi': '100'})" in file "energydiagram.py" 
# plt.show()


"""
    Example of data.in file:
_________________________________
OUTPUT FILE # 1 - Name of the figure, 2- Format: png, jpg, eps, pdj, pgf (xenex package needed), 3- Fig dpi resolution, 4- 'x,y' Figsize in pixel, 5- (m,M) minor and major tick.space, 6- Control the distance between plot and y_axes (0 to 1)
testfile
pdf
200
1200,1200
0.2,2
0.2

EXP BINDING ENERGY # Experimental binding energy. This is used to plot positive energies. If =0, will plot directly the input energy
-19.843

NUM DATA # Number of data in the figure. For ex., 2, experiment and calculated data
3

DATA-1 # First four lines define 1-number of states, 2-name of the data ('None' for no name), 3-color of the line (number between 0 and 9, see TAB10 python, or -1 for black), 4-line style ('--','-',':','-.')
4
Exp $-\,^{4}\mathrm{He}$
-1
-
# Data must have the following columns:
# ENERGY  J('-1' if not plotting j)   PI(0 for '-' and 1 for '+')  INDEX('-1' if not plotting index) JPIPOS('left' or 'right') BOTTOMTEXT('None' for nothing) TOPTEXT('None' for nothing) COLOR(optional) LS(optional)
-20.1072   0  1  -1  left  None  $\Gamma_\alpha=0\,\mathrm{keV}$
-14.5191   2  1  -1  left  None  $\Gamma_\alpha=2\,\mathrm{keV}$
 -8.9191   4  1  -1  left  None  $\Gamma_\alpha=12\,\mathrm{keV}$
 -4.5459   6  1  -1  right  None  None  0  --

DATA-2 # First four lines define 1-number of states, 2-name of the data ('None' for no name), 3-color of the line (number between 0 and 9, see TAB10 python, or -1 for black), 4-line style ('--','-',':','-.')
3
Exp $-\,^{5}\mathrm{He}$
0
-
# Data must have the following columns:
# ENERGY  J('-1' if not plotting j)   PI(0 for '-' and 1 for '+')  INDEX('-1' if not plotting index) JPIPOS('left' or 'right') BOTTOMTEXT('None' for nothing) TOPTEXT('None' for nothing) COLOR(optional) LS(optional)
-18.1072   3/2  0  -1  left  None  None
-10.5191   1/2  0  -1  left  None  None
 -9.9191   7/2  0  -1  left  None  $\alpha+n$
 
DATA-3 # First four lines define 1-number of states, 2-name of the data ('None' for no name), 3-color of the line (number between 0 and 9, see TAB10 python, or -1 for black), 4-line style ('--','-',':','-.')
2
Exp $-\,^{6}\mathrm{He}$
1
-
# Data must have the following columns:
# ENERGY  J('-1' if not plotting j)   PI(0 for '-' and 1 for '+')  INDEX('-1' if not plotting index) JPIPOS('left' or 'right') BOTTOMTEXT('None' for nothing) TOPTEXT('None' for nothing) COLOR(optional) LS(optional)
 -6.5191   0  1  -1  left  None  None
 -2.9191  -1  0  -1  left  None  $\alpha+nn$
_________________________________
"""