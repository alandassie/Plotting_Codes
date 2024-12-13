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
figratiox = float(data[theline+6])
figratioy = float(data[theline+7])
# Experimental Energy of the core. This is used to plot positive energies
theline = searchline(readfilename,"EXP BINDING ENERGY") 
exp0 = float(data[theline+1])
# Number of data for plot
theline = searchline(readfilename,"NUM DATA") 
cols = int(data[theline+1])
#.-
# Prepare possible link array
link_data = []

# Begin the plot
figure = ED() # This is the Figure where we gonna add energy levels
# Config the figure
figure.fig_parameters(figratiox,figratioy,dpi,x_figsize,y_figsize, yminor, ymajor)

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
        state_index = int(line.split()[0])
        ene = float(line.split()[1])
        jj = line.split()[2]
        parity = int(line.split()[3])
        if parity == 0:
            pp = '-'
        elif parity == 1:
            pp = '+'
        index = int(line.split()[4])
        jpi_pos = line.split()[5]
        bttm = line.split()[6]
        if bttm == 'None':
            bttm = ''
        top = line.split()[7]
        if top == 'None':
            top = ''
        level_color = data_color
        level_ls = data_ls
        # Any aditional information
        if len(line.split()) > 8:
            link_set = 0
            link_color = -1
            link_style = '--'
            link_width = 0.75
            n_add = len( line.split()[8::] )
            for j in range(0,n_add):
                if line.split()[8+j].split('#')[0] == 'C': # Specific color line
                    level_color = int(line.split()[8+j].split('#')[1])
                if line.split()[8+j].split('#')[0] == 'LS': # Specific line style
                    level_ls = line.split()[8+j].split('#')[1]
                # Possible linking information
                if line.split()[8+j].split('#')[0] == 'L': # Set link destination
                    link_out = int(line.split()[8+j].split('#')[1])
                    link_set = 1
                if line.split()[8+j].split('#')[0] == 'LC': # Set link color
                    link_color = int(line.split()[8+j].split('#')[1])
                if line.split()[8+j].split('#')[0] == 'LLS': # Set link style
                    link_style = line.split()[8+j].split('#')[1]
                if line.split()[8+j].split('#')[0] == 'LLW': # Set link width
                    link_width = float(line.split()[8+j].split('#')[1])
                if link_set == 1 and j+1 == n_add :
                    # Save link information
                    link_data.append( [state_index, link_out, link_color, link_style, link_width] )
        #
        if i == 0:   
            if index >= 0:
                if jpi_pos == 'left':
                    figure.add_level(ene, top_text=top, bottom_text=data, left_text='${0:s}^{1:s}_{2:1d}$'.format(jj,pp,index), set_title=data_name, color=level_color, linestyle=level_ls)
                elif jpi_pos == 'right':
                    figure.add_level(ene, top_text=top, bottom_text=bttm, right_text='${0:s}^{1:s}_{2:1d}$'.format(jj,pp,index), set_title=data_name, color=level_color, linestyle=level_ls)
                else:
                    figure.add_level(ene, top_text=top, bottom_text=bttm, set_title=data_name, color=level_color, linestyle=level_ls)
            else:
                if jpi_pos == 'left':
                    figure.add_level(ene, top_text=top, bottom_text=bttm, left_text='${0:s}^{1:s}$'.format(jj,pp), set_title=data_name, color=level_color, linestyle=level_ls)
                elif jpi_pos == 'right':
                    figure.add_level(ene, top_text=top, bottom_text=bttm, right_text='${0:s}^{1:s}$'.format(jj,pp), set_title=data_name, color=level_color, linestyle=level_ls)
                else:
                    figure.add_level(ene, top_text=top, bottom_text=bttm, set_title=data_name, color=level_color, linestyle=level_ls)
        else:
            if index >= 0:
                if jpi_pos == 'left':
                    figure.add_level(ene, top_text=top, bottom_text=bttm, left_text='${0:s}^{1:s}_{2:1d}$'.format(jj,pp,index), color=level_color, linestyle=level_ls, position='last')
                elif jpi_pos == 'right':
                    figure.add_level(ene, top_text=top, bottom_text=bttm, right_text='${0:s}^{1:s}_{2:1d}$'.format(jj,pp,index), color=level_color, linestyle=level_ls, position='last')
                else:
                    figure.add_level(ene, top_text=top, bottom_text=bttm, color=level_color, linestyle=level_ls, position='last')
            else:
                if jpi_pos == 'left':
                    figure.add_level(ene, top_text=top, bottom_text=bttm, left_text='${0:s}^{1:s}$'.format(jj,pp), color=level_color, linestyle=level_ls, position='last')
                elif jpi_pos == 'right':
                    figure.add_level(ene, top_text=top, bottom_text=bttm, right_text='${0:s}^{1:s}$'.format(jj,pp), color=level_color, linestyle=level_ls, position='last')
                else:
                    figure.add_level(ene, top_text=top, bottom_text=bttm, color=level_color, linestyle=level_ls, position='last')

# Linking
for link in link_data:
    figure.add_link(link[1],link[0],color=link[2],ls=link[3],linewidth=link[4])

# figure.plot(show_IDs=True) # This is usefull if you want to link two columns
figure.plot()
plt.tight_layout()

# To save Fig, coment the line "plt.rcParams.update({'figure.dpi': '100'})" in file "energydiagram.py" 
plt.savefig(outputfile,format=format_out)

# To Show Fig, uncoment the line "plt.rcParams.update({'figure.dpi': '100'})" in file "energydiagram.py" 
# plt.show()


"""
    Example of data.in file:
_________________________________
OUTPUT FILE # 1 - Name of the figure, 2- Format: png, jpg, eps, pdj, pgf (xenex package needed), 3- Fig dpi resolution, 4- 'x,y' Figsize in pixel, 5- (m,M) minor and major tick.space, 6- Control the distance between plot and y_axes (0 to 1), 7- Control the distance between plot and x_axes (0 to 1)
CC_11C_Spectrum
pdf
200
1200,1200
0.2,2
0.2
0.04

EXP BINDING ENERGY # Experimental binding energy. This is used to plot positive energies. If =0, will plot directly the input energy
-45.145

NUM DATA # Number of data in the figure. For ex., 2, experiment and calculated data
4

DATA-1 # First four lines define 1-number of states, 2-name of the data ('None' for no name), 3-color of the line (number between 0 and 9, see TAB10 python, or -1 for black), 4-line style ('--','-',':','-.')
13
Exp $J^-$
-1
-
# Data must have the following columns:
# INDEX ENERGY  J  PI(0 for '-' and 1 for '+')  INDEX('-1' if not plotting index) JPIPOS('left' or 'right' or 'None') BOTTOMTEXT('None' for nothing) TOPTEXT('None' for nothing) COLOR(optional) LS(optional) LINKINDEX(optional) LINKCOLOR(optional) LINKLS(optional) LINKLW(optional)
  0 -45.145   3/2  0  -1  right  None  None
  1 -43.145   1/2  0  -1  right  None  None
  2 -40.827   5/2  0  -1  right  None  None
  3 -40.341   3/2  0  -1  right  None  None
  4 -38.667   7/2  0  -1  right  None  None
  5 -37.041   3/2  0  -1  right  None  None
  6 -36.725   5/2  0  -1  right  None  None
  7 -35.500   3/2  0  -1  right  None  None
  8 -35.365   5/2  0  -1  right  None  None
  9 -35.175   7/2  0  -1  right  None  None
 10 -37.602   -1   0  -1  None   None  None   C#1 LS#--
 11 -36.456   -1   0  -1  None   None  None   C#1 LS#--
 12 -35.923   -1   0  -1  None   None  None   C#1 LS#--

DATA-2 # First four lines define 1-number of states, 2-name of the data ('None' for no name), 3-color of the line (number between 0 and 9, see TAB10 python, or -1 for black), 4-line style ('--','-',':','-.')
13
CC $J^-$
0
-
# Data must have the following columns:
# INDEX ENERGY  J  PI(0 for '-' and 1 for '+')  INDEX('-1' if not plotting index) JPIPOS('left' or 'right' or 'None') BOTTOMTEXT('None' for nothing) TOPTEXT('None' for nothing) COLOR(optional) LS(optional) LINKINDEX(optional) LINKCOLOR(optional) LINKLS(optional) LINKLW(optional)
 13 -43.478   3/2  0  -1  None  None  None              L#0 LC#-1 LLS#--
 14 -42.382   1/2  0  -1  None  None  None              L#1 LC#-1 LLS#--
 15 -34.131   1/2  0  -1  left  None  None 
 16 -39.528   5/2  0  -1  None  None  None              L#2 LC#-1 LLS#--
 17 -37.934   3/2  0  -1  None  None  None              L#3 LC#-1 LLS#--
 18 -38.168   7/2  0  -1  None  None  None              L#4 LC#-1 LLS#--
 19 -35.222   3/2  0  -1  None  None  None              L#5 LC#-1 LLS#--
 20 -35.157   5/2  0  -1  None  None  None              L#6 LC#-1 LLS#--
 21 -32.186   3/2  0  -1  None  None  None              L#7 LC#-1 LLS#--
 22 -32.255   5/2  0  -1  None  None  None              L#8 LC#-1 LLS#--
 23 -37.602   -1   0  -1  None  None  None   C#1 LS#--  L#10 LC#1 LLS#-- LLW#1.5
 24 -36.456   -1   0  -1  None  None  None   C#1 LS#--  L#11 LC#1 LLS#-- LLW#1.5
 25 -35.923   -1   0  -1  None  None  None   C#1 LS#--  L#12 LC#1 LLS#-- LLW#1.5

DATA-3 # First four lines define 1-number of states, 2-name of the data ('None' for no name), 3-color of the line (number between 0 and 9, see TAB10 python, or -1 for black), 4-line style ('--','-',':','-.')
11
Exp $J^+$
-1
-
# Data must have the following columns:
# INDEX ENERGY  J  PI(0 for '-' and 1 for '+')  INDEX('-1' if not plotting index) JPIPOS('left' or 'right' or 'None') BOTTOMTEXT('None' for nothing) TOPTEXT('None' for nothing) COLOR(optional) LS(optional) LINKINDEX(optional) LINKCOLOR(optional) LINKLS(optional) LINKLW(optional)
 26 -38.806   1/2  1  -1  right  None  None
 27 -38.241   5/2  1  -1  right  None  None
 28 -37.745   3/2  1  -1  right  None  None
 29 -37.646   3/2  1  -1  right  None  None
 30 -36.491   7/2  1  -1  right  None  None
 31 -36.446   5/2  1  -1  right  None  None
 32 -35.945   5/2  1  -1  right  None  None
 33 -35.062   7/2  1  -1  right  None  None
 34 -37.602   -1   0  -1  None   None  None   C#1 LS#--  L#23 LC#1 LLS#-- LLW#1.5
 35 -36.456   -1   0  -1  None   None  None   C#1 LS#--  L#24 LC#1 LLS#-- LLW#1.5
 36 -35.923   -1   0  -1  None   None  None   C#1 LS#--  L#25 LC#1 LLS#-- LLW#1.5

DATA-4 # First four lines define 1-number of states, 2-name of the data ('None' for no name), 3-color of the line (number between 0 and 9, see TAB10 python, or -1 for black), 4-line style ('--','-',':','-.')
13
CC $J^+$
0
-
# Data must have the following columns:
# INDEX ENERGY  J  PI(0 for '-' and 1 for '+')  INDEX('-1' if not plotting index) JPIPOS('left' or 'right' or 'None') BOTTOMTEXT('None' for nothing) TOPTEXT('None' for nothing) COLOR(optional) LS(optional) LINKINDEX(optional) LINKCOLOR(optional) LINKLS(optional) LINKLW(optional)
 37 -39.730   3/2  1  -1  None   None  None                                   L#28 LC#-1 LLS#--
 38 -39.383   3/2  1  -1  None   None  None                                   L#29 LC#-1 LLS#--
 39 -39.805   1/2  1  -1  None   None  None                                   L#26 LC#-1 LLS#--
 40 -39.307   1/2  1  -1  left   None  None
 41 -36.556   1/2  1  -1  left   None  None
 42 -39.808   5/2  1  -1  None   None  None                                   L#27 LC#-1 LLS#--
 43 -35.098   5/2  1  -1  None   None  None                                   L#31 LC#-1 LLS#--
 44 -34.368   5/2  1  -1  None   None  None                                   L#32 LC#-1 LLS#--
 45 -35.009   7/2  1  -1  None   None  None                                   L#30 LC#-1 LLS#--
 46 -33.069   7/2  1  -1  None   None  None                                   L#33 LC#-1 LLS#--
 47 -37.602   -1   0  -1  None   None  $\alpha-th$          C#1 LS#--  L#34 LC#1 LLS#-- LLW#1.5
 48 -36.456   -1   0  -1  None   None  $p-th$               C#1 LS#--  L#35 LC#1 LLS#-- LLW#1.5
 49 -35.923   -1   0  -1  None   None  $^{3}\mathrm{He}-th$ C#1 LS#--  L#36 LC#1 LLS#-- LLW#1.5
_________________________________
"""