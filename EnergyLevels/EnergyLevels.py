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
# Output file name
theline = searchline(readfilename,"OUTPUT FILE") 
name_out = data[theline+1]
format_out = data[theline+2]
outputfile = name_out + '.' + format_out
# Experimental Energy of the core. This is used to plot positive energies
theline = searchline(readfilename,"EXP BINDING ENERGY") 
exp0 = float(data[theline+1])
# Number of data for plot
theline = searchline(readfilename,"NUM DATA") 
cols = int(data[theline+1])

# Begin the plot
figure = ED() # This is the Figure where we gonna add energy levels

# Plotting the data
for k in range(1,cols+1):
    theline = searchline(readfilename,"DATA-%s"% k) 
    data_len = int(data[theline+1])
    data_name = data[theline+2]
    data_color = int(data[theline+3])
    data_ls = data[theline+4]
    #
    for i in range(0,data_len):
        # Main information of the level
        line = data[theline+7+i]
        ene = float(line.split()[0])
        jj = int(line.split()[1])
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
            if index >= 0:
                if jpi_pos == 'left':
                    figure.add_level(ene, top_text=top, bottom_text=bttm, left_text='${0:1d}^{1:s}_{2:1d}$'.format(jj,pp,index), color=level_color, linestyle=level_ls)
                elif jpi_pos == 'right':
                    figure.add_level(ene, top_text=top, bottom_text=bttm, right_text='${0:1d}^{1:s}_{2:1d}$'.format(jj,pp,index), color=level_color, linestyle=level_ls)
            else:
                if jpi_pos == 'left':
                    figure.add_level(ene, top_text=top, bottom_text=bttm, left_text='${0:1d}^{1:s}$'.format(jj,pp), color=level_color, linestyle=level_ls)
                elif jpi_pos == 'right':
                    figure.add_level(ene, top_text=top, bottom_text=bttm, right_text='${0:1d}^{1:s}$'.format(jj,pp), color=level_color, linestyle=level_ls)
        else:
            if index >= 0:
                if jpi_pos == 'left':
                    figure.add_level(ene, top_text=top, bottom_text=bttm, left_text='${0:1d}^{1:s}_{2:1d}$'.format(jj,pp,index), color=level_color, linestyle=level_ls, position='last')
                elif jpi_pos == 'right':
                    figure.add_level(ene, top_text=top, bottom_text=bttm, right_text='${0:1d}^{1:s}_{2:1d}$'.format(jj,pp,index), color=level_color, linestyle=level_ls, position='last')
            else:
                if jpi_pos == 'left':
                    figure.add_level(ene, top_text=top, bottom_text=bttm, left_text='${0:1d}^{1:s}$'.format(jj,pp), color=level_color, linestyle=level_ls, position='last')
                elif jpi_pos == 'right':
                    figure.add_level(ene, top_text=top, bottom_text=bttm, right_text='${0:1d}^{1:s}$'.format(jj,pp), color=level_color, linestyle=level_ls, position='last')

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
