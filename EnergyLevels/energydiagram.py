# -*- coding: utf-8 -*-
r"""
Created on Mon Jan 23 13:09:19 2017

--- Energy profile diagram---
This is a simple script to plot energy profile diagram using matplotlib.
E|          4__
n|   2__    /  \
e|1__/  \__/5   \
r|  3\__/       6\__
g|
y|
@author: Giacomo Marchioro giacomomarchioro@outlook.com
https://github.com/giacomomarchioro/PyEnergyDiagrams

"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import ConnectionPatch
from box_notation import plot_orbital_boxes
from width_notation import plot_width_boxes
from errorbar_notation import plot_errorbar
try: # Import for nicer plots, only if you have it
    import scienceplots # From https://github.com/garrettj403/SciencePlots
    using_scienceplots = True
except ImportError:
    using_scienceplots = False


class ED:
    def __init__(self, aspect='equal'):
        # plot parameters
        self.ratio = 1.6181
        self.dimension = 'auto'
        self.space = 'auto'
        self.column_width = 0.7  # level-line length as a fraction of the column pitch
        self.axis_break = None  # None or flat tuple (low1, high1, low2, high2, ...) of displayed-energy gaps
        self.ylabel_pad = 4.0  # padding between the y-axis label and the axis, in points
        self.errorbar_head = 10.0  # error-bar cap size as a multiple of the level-line length
        self.offset = 'auto'
        self.offset_ratio = 0.008
        self.color_bottom_text = 'k'
        self.color_left_text = 'k'
        self.aspect = aspect
        # data
        self.pos_number = 0
        self.energies = []
        self.widths = []
        self.positions = []
        self.colors = []
        self.top_texts = []
        self.bottom_texts = []
        self.left_texts = []
        self.right_texts = []
        self.set_title = []
        self.links = []
        self.linestyle = []
        self.label_lines = []
        self.arrows = []
        self.electons_boxes = []
        self.widths_boxes = []
        self.errorbars = []
        # matplotlib figure handlers
        self.fig = None
        self.ax = None
        self.ax2 = None  # bottom panel when an axis break is active
        self.axs = []
        self.supylabel_text = None  # figure-level y label (axis-break mode)
        # Figure parameters
        self.fig_ratiox = 0.06
        self.fig_ratioy = 0.08
        self.fig_dpi = 600
        self.fig_xsize = 6
        self.fig_ysize = 6
        self.fig_yaxis_major = 1
        self.fig_yaxis_minor = 0.2
        self.fig_yaxis_label = "Energy (MeV)"
        self.use_tex = False
        self.font_size = 10
        self.title_size = 11
        self.label_offsets = []
        self.label_dx_offsets = []
        # white space at each end of a label connector (level-line side and
        # label side), as a fraction of the level-line length; clamped to 40%
        # of the connector span so a visible line always remains
        self.label_line_gap = 0.03
        
    def fig_parameters(self, figratiox, figratioy, dpi, x_figsize, y_figsize, yminor, ymajor):
        '''
        Defing parameters for the output figure
        '''
        self.fig_ratiox = figratiox
        self.fig_ratioy = figratioy
        self.fig_dpi = dpi
        self.fig_xsize = x_figsize
        self.fig_ysize = y_figsize
        self.fig_yaxis_minor = yminor
        self.fig_yaxis_major = ymajor

    def add_level(self, energy, bottom_text='', position=None, color='k',
                  top_text='Energy', right_text='', left_text='', set_title=None,linestyle='-', label_dy=0,
                  label_dx=0, label_line=False):
        '''
        Method of ED class
        This method add a new energy level to the plot.

        Parameters
        ----------
        energy : float
                 The energy of the level in MeV
         bottom_text  : str
                 The text on the bottom of the level (label of the level)
                 (default '')
         position  : str
                 The position of the level in the plot. Keep it empty to add
                 the level on the right of the previous level use 'last' as
                 argument for adding the level to the last position used.
                 (default  None)
         color  : str
                 Color of the level  (default  'k')
         top_text  : str
                 Text on the top of the level. By default it will print the
                 energy of the level. (default  'Energy')
         label_dx : float
                 Horizontal shift of the side label (left_text/right_text) in
                 x data units, on top of its default position just past the
                 end of the level line (default 0)
         label_line : bool
                 Draw a thin black connector from the end of the level line
                 to the side label (left_text/right_text) of this level. The
                 connector is inset by label_line_gap (fraction of the
                 level-line length) at BOTH ends, leaving a white gap next to
                 the level line and next to the label. (default False)



        Returns
        -------
        Append to the calss data all the informations regarding the level added
        '''

        if position is None:
            position = self.pos_number + 1
            self.pos_number += 1
        elif position == 'last':
            position = self.pos_number
        if top_text == 'Energy':
            top_text = energy

        link = []
        self.colors.append(color)
        self.energies.append(energy)
        self.positions.append(position)
        self.top_texts.append(top_text)
        self.bottom_texts.append(bottom_text)
        self.left_texts.append(left_text)
        self.right_texts.append(right_text)
        self.set_title.append(set_title)
        self.links.append(link)
        self.arrows.append([])
        self.label_offsets.append(label_dy)
        self.label_dx_offsets.append(label_dx)
        self.linestyle.append(linestyle)
        self.label_lines.append(bool(label_line))

    def add_arrow(self, start_level_id, end_level_id):
        '''
        Method of ED class
        Add a arrow between two energy levels using IDs of the level. Use
        self.plot(show_index=True) to show the IDs of the levels.

        Parameters
        ----------
        start_level_id : int
                 Starting level ID
        end_level_id : int
                 Ending level ID

        Returns
        -------
        Append arrow to self.arrows

        '''
        self.arrows[start_level_id].append(end_level_id)

    def add_link(self, start_level_id, end_level_id,
                 color='k',
                 ls='--',
                 linewidth=1,
                 ):
        '''
        Method of ED class
        Add a link between two energy levels using IDs of the level. Use
        self.plot(show_index=True) to show the IDs of the levels.

        Parameters
        ----------
        start_level_id : int
                 Starting level ID
        end_level_id : int
                 Ending level ID
        color : str
                color of the line
        ls : str
                line styple e.g. -- , ..
        linewidth : int
                line width

        Returns
        -------
        Append link to self.links

        '''
        self.links[start_level_id].append((end_level_id, ls, linewidth, color))

    def add_errorbar(self,
                     level_id,
                     uncertainty):
        self.__auto_adjust()
        x = self.positions[level_id]*(self.dimension+self.space)+self.dimension*0.5
        y = self.energies[level_id]
        side = self.dimension
        high = uncertainty
        color = self.colors[level_id]
        self.errorbars.append((x, y, high, color, side, self.errorbar_head))

    def add_widthbox(self,
                     level_id,
                     width,
                     width_spacing_f,
                     width_alpha):
        self.__auto_adjust()
        x = self.positions[level_id]*(self.dimension+self.space)+self.dimension*0.5
        y = self.energies[level_id]
        side = self.dimension
        high = width
        color = self.colors[level_id]
        self.widths_boxes.append((x, y, high, color, side, width_spacing_f, width_alpha))

    def add_electronbox(self,
                        level_id,
                        boxes,
                        electrons,
                        side=0.5,
                        spacing_f=5):
        '''
        Method of ED class
        Add a link between two energy levels using IDs of the level. Use
        self.plot(show_index=True) to show the IDs of the levels.

        Parameters
        ----------
        start_level_id : int
                 Starting level ID
        end_level_id : int
                 Ending level ID

        Returns
        -------
        Append link to self.links

        '''
        self.__auto_adjust()
        x = self.positions[level_id]*(self.dimension+self.space)+self.dimension*0.5
        y = self.energies[level_id]
        self.electons_boxes.append((x, y, boxes, electrons, side, spacing_f))


    def plot(self, show_IDs=False):
        r'''
        Method of ED class
        Plot the energy diagram. Use show_IDs=True for showing the IDs of the
        energy levels and allowing an easy linking.
        E|          4__
        n|   2__    /  \
        e|1__/  \__/5   \
        r|  3\__/       6\__
        g|
        y|

        If self.axis_break is a flat tuple (low1, high1, low2, high2, ...), the
        energy axis is broken inside every (low, high) gap: one stacked panel
        per energy range, all sharing the x axis, the spines facing each gap
        are hidden and // marks are drawn, as in a classic broken-axis plot.
        Levels, boxes, error bars and labels are clipped at each gap; links are
        drawn once as continuous straight lines across the gaps, so they never
        show a discontinuity at a break.

        Parameters
        ----------
        show_IDs : bool
            show the IDs of the energy levels

        Returns
        -------
        fig (plt.figure) and ax (the top panel; self.ax2 is the bottom panel
        when an axis break is active, None otherwise)

        '''
        if using_scienceplots is True:
            plt.style.use(['science','ieee', 'no-latex'] if not self.use_tex else ['science','ieee'])
        else:
            plt.rcParams.update({
                "font.family": "serif",
                "mathtext.fontset": "dejavuserif",
                "text.usetex": self.use_tex,
                "text.latex.preamble": r"\usepackage{amsmath} \usepackage{amssymb}"
            })
        #
        plt.rcParams.update({'figure.dpi': '%s'% self.fig_dpi})
        px = 1/plt.rcParams['figure.dpi']  # pixel in inches
        fig = plt.figure(figsize=(self.fig_xsize*px,self.fig_ysize*px))
        colors = plt.get_cmap('tab10', 10)

        self.__auto_adjust()

        numberoflevels = len(self.energies)
        minenergy = min(self.energies)
        maxenergy = max(self.energies)
        move = max(abs(maxenergy),abs(minenergy),1.0)*self.fig_ratioy
        lower = min([minenergy] + [b[1]-b[2] for b in self.widths_boxes] + [b[1]-b[2] for b in self.errorbars])
        upper = max([maxenergy] + [b[1]+b[2] for b in self.widths_boxes] + [b[1]+b[2] for b in self.errorbars])
        if lower == upper:
            move = max(move, .5)

        # One panel, or one panel per energy range when axis breaks are set
        # (one extra panel per break). With breaks, every artist is drawn on
        # every panel and clipped to each panel's y-range, so lines and links
        # stop at each gap.
        if self.axis_break is None:
            axes = [fig.add_subplot(111)]
            ylims = [(lower-move, upper+move)]
            clip_texts = False
        else:
            breaks = [(self.axis_break[i], self.axis_break[i+1])
                      for i in range(0, len(self.axis_break), 2)]  # ascending (lo, hi) gaps
            for e in self.energies:
                for bl, bh in breaks:
                    if bl < e < bh:
                        raise ValueError(f'level energy {e} lies inside the axis break ({bl}, {bh}); '
                                         'move the break or the level')
            npanels = len(breaks) + 1
            top_range = max(upper+move-breaks[-1][1], 1e-3)
            bottom_lo = lower-move
            bottom_range = breaks[0][0]-bottom_lo
            if bottom_range <= 0:  # nothing below the lowest break: keep a thin bottom panel
                bottom_range = 0.05*top_range
                bottom_lo = breaks[0][0]-bottom_range
            # panel y-ranges, top -> bottom: top panel, one middle panel
            # between consecutive gaps, bottom panel
            ylims = [(breaks[-1][1], upper+move)]
            ranges = [top_range]
            for j in range(1, npanels-1):
                ylo, yhi = breaks[len(breaks)-1-j][1], breaks[len(breaks)-j][0]
                ylims.append((ylo, yhi))
                ranges.append(max(yhi-ylo, 1e-3))
            ylims.append((bottom_lo, breaks[0][0]))
            ranges.append(bottom_range)
            gs = fig.add_gridspec(npanels, 1, height_ratios=ranges)
            ax_first = fig.add_subplot(gs[0])
            axes = [ax_first] + [fig.add_subplot(gs[j], sharex=ax_first)
                                 for j in range(1, npanels)]
            clip_texts = True
            # hide the spines facing each gap, then draw the // break marks
            d = 0.5  # slant of the break marks
            marks = dict(marker=[(-1, -d), (1, d)], markersize=12, linestyle='none',
                         color='k', mec='k', mew=1, clip_on=False)
            for j, ax in enumerate(axes):
                if j < npanels-1:
                    ax.spines['bottom'].set_visible(False)
                    ax.plot([0, 1], [0, 0], transform=ax.transAxes, **marks)
                if j > 0:
                    ax.spines['top'].set_visible(False)
                    ax.plot([0, 1], [1, 1], transform=ax.transAxes, **marks)
            if hasattr(fig, 'supylabel'):
                self.supylabel_text = fig.supylabel(self.fig_yaxis_label, fontsize=self.title_size)
            else:
                axes[-1].set_ylabel(self.fig_yaxis_label, fontsize=self.title_size,
                                    labelpad=self.ylabel_pad)

        # Column names (the dataset titles) are drawn as x tick labels below
        # the bottom panel, so tight_layout reserves room for them and they are
        # never clipped by the figure edge. On shared-x panels only the bottom
        # one shows the labels.
        titles = {}
        for pos, title in zip(self.positions, self.set_title):
            if title:
                titles.setdefault(pos, str(title))
        for j, ax in enumerate(axes):
            if titles:
                order = sorted(titles)
                centers = [p*(self.dimension+self.space) + self.dimension/2. for p in order]
                ax.set_xticks(centers)
                ax.set_xticklabels([titles[p] for p in order], fontsize=self.title_size)
                if j < len(axes)-1:
                    ax.xaxis.set_tick_params(labelbottom=False)
            else:
                ax.set_xticks([])

        # Return fig and ax
        self.ax = axes[0]
        self.ax2 = axes[-1] if len(axes) > 1 else None  # bottom panel when breaks are active
        self.axs = axes
        self.fig = fig

        for ax, (ylo, yhi) in zip(axes, ylims):
            self.__decorate_axis(ax)
            ax.set_ylim(ylo, yhi)
            if self.axis_break is None:
                ax.set_ylabel(self.fig_yaxis_label, fontsize=self.title_size, labelpad=self.ylabel_pad)
            self.__draw(ax, colors, show_IDs, minenergy, clip_texts)

        if self.axis_break is not None:
            # With breaks, each link is drawn once as a straight line in display
            # space between its two endpoint panels (ConnectionPatch), so a
            # link crossing a gap stays continuous instead of stopping at each
            # panel edge. Added to the last panel (drawn last) with clipping
            # off, so it can span the gaps.
            for idx, link in enumerate(self.links):
                for i in link:
                    # i is a tuple: (end_level_id,ls,linewidth,color)
                    start = self.positions[idx]*(self.dimension+self.space)
                    x1 = start + self.dimension
                    x2 = self.positions[i[0]]*(self.dimension+self.space)
                    y1 = self.energies[idx]
                    y2 = self.energies[i[0]]
                    color = 'k' if i[3] == -1 else colors(i[3])
                    con = ConnectionPatch((x1, y1), (x2, y2),
                                          coordsA='data', coordsB='data',
                                          axesA=self.ax_for_energy(y1),
                                          axesB=self.ax_for_energy(y2),
                                          ls=i[1], linewidth=i[2], color=color,
                                          clip_on=False, zorder=3)
                    axes[-1].add_patch(con)

    def ax_for_energy(self, y):
        '''Return the panel that displays the given data energy.'''
        if self.ax2 is None:
            return self.ax
        for ax in self.axs:
            ylo, yhi = ax.get_ylim()
            if ylo <= y <= yhi:
                return ax
        return self.axs[-1]

    def adjust_figure_ylabel(self):
        '''Reposition the figure-level y label (axis-break mode) so it sits
        self.ylabel_pad points left of the y tick labels. Call after the
        figure layout is final (tight_layout / subplots_adjust).'''
        t = self.supylabel_text
        if t is None or self.fig is None or not self.axs:
            return
        fig = self.fig
        x0 = None
        try:
            renderer = fig.canvas.get_renderer()
            inv = fig.transFigure.inverted()
            for ax in self.axs:
                bb = ax.yaxis.get_tightbbox(renderer)
                if bb is not None:
                    fx = inv.transform((bb.x0, bb.y0))[0]
                    x0 = fx if x0 is None else min(x0, fx)
        except Exception:
            x0 = None
        if x0 is None:
            x0 = min(ax.get_position().x0 for ax in self.axs)
        width_in = fig.get_size_inches()[0]
        t.set_x(max(x0 - self.ylabel_pad/72.0/width_in, 0.001))

    def __decorate_axis(self, ax):
        '''Tick and label layout shared by every panel.'''
        # Edit the major and minor ticks of the x and y axes. The x tick marks
        # are hidden (size 0): the x axis only carries the column-name labels.
        ax.xaxis.set_tick_params(which='major', size=0, width=0, top=True)
        ax.xaxis.set_tick_params(which='minor', size=0, width=0, top=True)
        ax.yaxis.set_tick_params(which='major', size=7, width=0.5, direction='in',right=True)
        ax.yaxis.set_tick_params(which='minor', size=3, width=0.5, direction='in',right=True)
        # Edit the major and minor tick locations
        ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(self.fig_yaxis_major))
        ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(self.fig_yaxis_minor))
        for tick in ax.get_yticklabels():
            tick.set_fontsize(self.font_size)

    def __draw(self, ax, colors, show_IDs, minenergy, clip_texts):
        '''Draw all levels, labels, leader lines, links and decorations on one panel.'''
        data = list(zip(self.energies,  # 0
                   self.positions,  # 1
                   self.bottom_texts,  # 2
                   self.top_texts,  # 3
                   self.colors,  # 4
                   self.left_texts,  # 5
                   self.right_texts,  # 6
                   self.linestyle, # 7
                   self.set_title)) # 8

        numberoflevels = len(self.energies)
        i = 1
        for level in data:
            start = level[1]*(self.dimension+self.space)
            if i == 1:
                len_aux = start*self.fig_ratiox
                ax.hlines(level[0], start*(1-self.fig_ratiox), start, linewidth=0)
            if i == numberoflevels:
                ax.hlines(level[0], start + self.dimension, (start + self.dimension)+len_aux, linewidth=0)
            if level[4] == -1:
                ax.hlines(level[0], start, start + self.dimension, color='k',linestyle=level[7], linewidth=1.5)
            else:
                ax.hlines(level[0], start, start + self.dimension, color=colors(level[4]),linestyle=level[7], linewidth=1.5)
            ax.text(start+self.dimension/2.,  # X
                    level[0]+self.offset,  # Y
                    level[3],  # self.top_texts
                    horizontalalignment='center',
                    fontsize=self.font_size,
                    verticalalignment='bottom',
                    clip_on=clip_texts)

            ax.text((start + self.dimension)*1.01 + self.label_dx_offsets[i-1],  # X
                    level[0] + self.label_offsets[i-1],  # Y
                    level[5],  # self.left_text
                    horizontalalignment='left',
                    fontsize=self.font_size,
                    verticalalignment='center',
                    color=self.color_left_text,
                    clip_on=clip_texts)

            ax.text(start*0.97 + self.label_dx_offsets[i-1],  # X
                    level[0] + self.label_offsets[i-1],  # Y
                    level[6],  # self.right_text
                    horizontalalignment='right',
                    fontsize=self.font_size,
                    verticalalignment='center',
                    color=self.color_bottom_text,
                    clip_on=clip_texts)

            ax.text(start + self.dimension/2.,  # X
                    level[0] - self.offset*2,  # Y
                    level[2],  # self.bottom_text
                    horizontalalignment='center',
                    fontsize=self.font_size,
                    verticalalignment='top',
                    color=self.color_bottom_text,
                    clip_on=clip_texts)

            if self.label_lines[i-1]:
                # thin black connector between the level line and the side
                # label; it is inset by label_line_gap at BOTH ends (white
                # space next to the level line and next to the label), and it
                # follows the label_dx/label_dy label shift. The inset is
                # clamped to 40% of the span so a visible line remains.
                dy = self.label_offsets[i-1]
                dx = self.label_dx_offsets[i-1]
                def _leader(x_line_end, x_label_anchor):
                    span = x_label_anchor - x_line_end
                    g = min(self.label_line_gap*self.dimension, 0.4*abs(span))
                    s = 1 if span >= 0 else -1
                    return Line2D([x_line_end + s*g, x_label_anchor - s*g],
                                  [level[0], level[0]+dy],
                                  color='k', linewidth=0.75, zorder=4)
                if level[5]:  # left_text is drawn just past the right end of the line
                    ax.add_line(_leader(start + self.dimension, (start + self.dimension)*1.01 + dx))
                if level[6]:  # right_text is drawn just before the left end of the line
                    ax.add_line(_leader(start, start*0.97 + dx))
            i += 1

        if show_IDs:
            # for showing the ID allowing the user to identify the level
            for ind, level in enumerate(data):
                start = level[1]*(self.dimension+self.space)
                ax.text(start, level[0]+self.offset, str(ind),
                        horizontalalignment='right', color='red', clip_on=clip_texts)

        for idx, arrow in enumerate(self.arrows):
            # by Kalyan Jyoti Kalita: put arrows between to levels
            # x1, x2   y1, y2
            for i in arrow:
                start = self.positions[idx]*(self.dimension+self.space)
                x1 = start + 0.5*self.dimension
                x2 = start + 0.5*self.dimension
                y1 = self.energies[idx]
                y2 = self.energies[i]
                gap = y1-y2
                gapnew = '{0:.2f}'.format(gap)
                middle= y1-0.5*gap          #warning: this way works for negative HOMO/LUMO energies
                ax.annotate("", xy=(x1,y1), xytext=(x2,middle), arrowprops=dict(color='green', width=1.5, headwidth=5))
                ax.annotate(s= gapnew, xy=(x2, y2), xytext=(x1, middle), color='green', arrowprops=dict(width=6, headwidth=15, color='green'),
                        bbox=dict(boxstyle='round', fc='white'),
                        ha='center', va = 'center')

        if not clip_texts:
            # Links in data coordinates per panel. With axis breaks they are
            # drawn once as continuous ConnectionPatch lines in plot() instead,
            # so they cross the gaps without a discontinuity.
            for idx, link in enumerate(self.links):
                # here we connect the levels with the links
                # x1, x2   y1, y2
                for i in link:
                    # i is a tuple: (end_level_id,ls,linewidth,color)
                    start = self.positions[idx]*(self.dimension+self.space)
                    x1 = start + self.dimension
                    x2 = self.positions[i[0]]*(self.dimension+self.space)
                    y1 = self.energies[idx]
                    y2 = self.energies[i[0]]
                    if i[3] == -1:
                        line = Line2D([x1, x2], [y1, y2],
                                    ls=i[1],
                                    linewidth=i[2],
                                    color='k')
                    else:
                        line = Line2D([x1, x2], [y1, y2],
                                    ls=i[1],
                                    linewidth=i[2],
                                    color=colors(i[3]))
                    ax.add_line(line)

        for box in self.electons_boxes:
            # here we add the boxes
            # x,y,boxes,electrons,side,spacing_f
            x, y, boxes, electrons, side, spacing_f = box
            plot_orbital_boxes(ax, x, y, boxes, electrons, side, spacing_f)

        for box in self.widths_boxes:
            # here we add the boxes for each width
            # x,y,high,side,spacing_f,alpha
            x, y, high, color_id, side, spacing_f, alpha = box
            if color_id == -1:
                color = 'k'
            else:
                color = colors(color_id)
            plot_width_boxes(ax, x, y, high, color, side, spacing_f, alpha)

        for errorbar in self.errorbars:
            # here we add the errorbars
            # x,y,high,color,side,head
            x, y, high, color_id, side, head = errorbar
            if color_id == -1:
                color = 'k'
            else:
                color = colors(color_id)
            plot_errorbar(ax, x, y, high, color, side, head)

    def __auto_adjust(self):
        '''
        Method of ED class
        This method use the ratio to set the best dimension and space between
        the levels.

        Affects
        -------
        self.dimension
        self.space
        self.offset

        '''
        # Max range between the energy
        if not self.energies:
            raise ValueError('Add at least one energy level before plotting.')
        Energy_variation = max(abs(max(self.energies) - min(self.energies)), 1e-3)
        w = self.column_width  # line length as a fraction of the column pitch
        if self.dimension == 'auto' or self.space == 'auto':
            # Unique positions of the levels
            unique_positions = float(len(set(self.positions)))
            space_for_level = Energy_variation*self.ratio/unique_positions
            self.dimension = space_for_level*w
            self.space = space_for_level*(1-w)

        if self.offset == 'auto':
            self.offset = Energy_variation*self.offset_ratio

if __name__ == '__main__':
        a = ED()
        a.add_level(0,'Separated Reactants')
        a.add_level(-5.4,'mlC1')
        a.add_level(-15.6,'mlC2','last',)
        a.add_level(28.5,'mTS1',color='g')
        a.add_level(-9.7,'mCARB1')
        a.add_level(-19.8,'mCARB2','last')
        a.add_level(20,'mCARBX','last')
        a.add_link(0,1,color='r')
        a.add_link(0,2)
        a.add_link(2,3,color='b')
        a.add_link(1,3)
        a.add_link(3,4,color='g')
        a.add_link(3,5)
        a.add_link(0,6)
        a.add_electronbox(2,3,5,3,3)
        #a.add_arrow(2,1)
        #a.offset *= 2
        a.plot(show_IDs=True)
