"""Regression checks: python3 -m unittest -v test_energy_levels.py."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from input_format import InputError, read_input, write_input
from EnergyLevels import main

ROOT = Path(__file__).resolve().parent

class Inputs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)/'input.in'
        self.text = (ROOT/'data.in').read_text()
        self.addCleanup(self.tmp.cleanup)

    def parse(self, text):
        self.path.write_text(text)
        return read_input(self.path)

    def bad(self, text, match):
        with self.assertRaisesRegex(InputError, match):
            self.parse(text)

    def test_example_and_legacy(self):
        new = self.parse(self.text)
        old = read_input(ROOT/'data_legacy.in')
        self.assertEqual(new.datasets[0].levels, old.datasets[0].levels)
        self.assertEqual(sum(len(d.levels) for d in new.datasets), 16)

    def test_conversion_round_trip(self):
        old = read_input(ROOT/'data_legacy.in')
        write_input(old, self.path)
        new = read_input(self.path)
        self.assertEqual(new.figure, old.figure)
        self.assertEqual(new.datasets, old.datasets)

    def test_id_not_row_position(self):
        config = self.parse(self.text.replace('\n0  ', '\n100  ').replace('link=0 ', 'link=100 '))
        self.assertEqual(config.datasets[0].levels[0].id, 100)
        self.assertEqual(config.datasets[1].levels[0].options['link'], 100)

    def test_line_field_and_section(self):
        text = self.text.replace('0  0.0  ', '0  wrong  ')
        with self.assertRaises(InputError) as caught:
            self.parse(text)
        line = next(i for i,s in enumerate(text.splitlines(),1) if 'wrong' in s)
        self.assertIn(f':{line} [levels 1] energy:', str(caught.exception))

    def test_duplicate_ids(self):
        self.bad(self.text.replace('\n1  0.467', '\n0  0.467'), 'duplicate state ID')

    def test_missing_link(self):
        self.bad(self.text.replace('link=0 ', 'link=999 '), 'unknown destination 999')

    def test_missing_columns(self):
        self.bad(self.text.replace('3/2  1  -1  left  None  None','3/2  1  -1  left'), 'missing bottom, top')

    def test_invalid_values(self):
        for old,new,match in [('dpi = 350.0','dpi = nan','finite'),
                              ('color = -1','color = 10','allowed range'),
                              ('ticks = 0.02, 0.2','ticks = 0.2, 0.02','minor spacing'),
                              ('width_spacing = 0.1','width_spacing = 0.5','less than 0.5'),
                              ('linestyle = -','linestyle = typo','choose one'),
                              ('3/2  1  -1','1/3  1  -1','half-integer'),
                              ('3/2  1  -1','3/2  3  -1','allowed range')]:
            with self.subTest(new=new): self.bad(self.text.replace(old,new),match)

    def test_unknown_option_and_setting(self):
        self.bad(self.text.replace('link=0 ', 'lnik=0 '),'unknown')
        self.bad(self.text.replace('dpi =', 'dpp ='),'unknown figure setting')

    def test_pairing_and_duplicates(self):
        self.bad(self.text.replace('[levels 3]','[levels 9]'),'matching')
        self.bad(self.text+'\n[figure]\n','duplicate section')
        self.bad(self.text.replace('dpi = 350.0','dpi = 350.0\ndpi = 300'),'duplicate setting')

    def test_quotes_preserve_math(self):
        config = self.parse(self.text.replace('left  None  None','left  "a label"  "$\\Lambda$"',1))
        state = config.datasets[0].levels[0]
        self.assertEqual(state.bottom, 'a label')
        self.assertEqual(state.top, r'$\Lambda$')

    def test_legacy_count(self):
        self.bad((ROOT/'data_legacy.in').read_text().replace('\n4\n','\n5\n',1),'declared 5, found 4')

    def test_column_spacing_removed(self):
        # column_spacing was removed; column_width is the visible control
        self.bad(self.text.replace('dpi = 350.0', 'column_spacing = 2.0\ndpi = 350.0'),
                 'unknown figure setting')

    def test_label_line_option(self):
        anchor = 'link=0  link_color=-1'
        config = self.parse(self.text.replace(anchor, 'label_line=yes  ' + anchor, 1))
        self.assertIs(config.datasets[1].levels[0].options['label_line'], True)
        config = self.parse(self.text.replace(anchor, 'label_line=no  ' + anchor, 1))
        self.assertIs(config.datasets[1].levels[0].options['label_line'], False)
        self.assertNotIn('label_line', config.datasets[0].levels[0].options)

    def test_label_line_invalid(self):
        self.bad(self.text.replace('link=0  link_color=-1', 'label_line=maybe  link=0  link_color=-1', 1), 'yes or no')

    def test_label_dx_option(self):
        anchor = 'link=0  link_color=-1'
        config = self.parse(self.text.replace(anchor, 'label_dx=0.05  ' + anchor, 1))
        self.assertAlmostEqual(config.datasets[1].levels[0].options['label_dx'], 0.05)
        config = self.parse(self.text.replace(anchor, 'label_dx=-0.02  ' + anchor, 1))
        self.assertAlmostEqual(config.datasets[1].levels[0].options['label_dx'], -0.02)
        self.assertNotIn('label_dx', config.datasets[0].levels[0].options)
        self.bad(self.text.replace(anchor, 'label_dx=sideways  ' + anchor, 1), 'finite number')
        # round-trips through write_input
        config = self.parse(self.text.replace(anchor, 'label_dx=0.05  ' + anchor, 1))
        write_input(config, self.path)
        again = read_input(self.path)
        self.assertEqual(again.datasets, config.datasets)
        self.assertIn('label_dx=0.05', self.path.read_text())

    def test_label_line_figure_default(self):
        config = self.parse(self.text.replace('label_line = no', 'label_line = yes'))
        self.assertIs(config.figure['label_line'], True)
        self.assertIs(self.parse(self.text).figure['label_line'], False)
        self.bad(self.text.replace('label_line = no', 'label_line = maybe'), 'yes or no')

    def test_new_options_round_trip(self):
        text = (self.text
                .replace('column_width = 0.7', 'column_width = 0.85')
                .replace('label_line = no', 'label_line = yes')
                .replace('link=0  link_color=-1', 'label_line=no  link=0  link_color=-1', 1))
        config = self.parse(text)
        write_input(config, self.path)
        again = read_input(self.path)
        self.assertEqual(again.figure, config.figure)
        self.assertEqual(again.datasets, config.datasets)
        written = self.path.read_text()
        self.assertIn('column_width = 0.85', written)
        self.assertIn('label_line = yes', written)
        self.assertIn('label_line=no', written)

    def test_check_cli_needs_no_plotting(self):
        self.path.write_text(self.text)
        with patch('EnergyLevels.render', side_effect=AssertionError('should not plot')):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(self.path),'--check']), 0)

    def test_cli_error_exit(self):
        self.path.write_text('')
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(main([str(self.path),'--check']), 2)
        self.assertIn('input is empty',err.getvalue())

    def test_render_ids_width_error_and_degenerate_levels(self):
        import matplotlib
        matplotlib.use('Agg')
        from energydiagram import ED
        self.path.write_text('''[figure]
format = pdf
[dataset 1]
name = Example
[levels 1]
100 0 0.1 0.05 1/2 + -1 left None None
[dataset 2]
[levels 2]
900 0 -1 -1 1/2 + -1 right None None link=100
''')
        output = self.path.with_suffix('.pdf')
        instances = []
        class Capture(ED):
            def __init__(self):
                super().__init__()
                instances.append(self)
        with patch('energydiagram.ED', Capture), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(self.path),'-o',str(output),'--show-ids']),0)
        self.assertGreater(output.stat().st_size,1000)
        fig=instances[0]
        self.assertEqual(fig.links[0][0][0],1)
        self.assertAlmostEqual(fig.widths_boxes[0][1],0)
        self.assertAlmostEqual(fig.errorbars[0][2],.05)
        self.assertGreater(fig.dimension,0)
        self.assertEqual([t.get_text() for t in fig.ax.texts][-2:], ['100','900'])
        # without breaks, links stay plain data-coordinate lines on the panel
        self.assertTrue(any(ln.get_linestyle() == '--' for ln in fig.ax.lines))

    def test_render_label_line(self):
        import matplotlib
        matplotlib.use('Agg')
        from energydiagram import ED
        self.path.write_text('''[figure]
format = pdf
label_line = yes
[dataset 1]
name = Example
[levels 1]
100 0 -1 -1 1/2 + -1 left None None label_line=no
101 1 -1 -1 1/2 + -1 right None None
''')
        output = self.path.with_suffix('.pdf')
        instances = []
        class Capture(ED):
            def __init__(self):
                super().__init__()
                instances.append(self)
        with patch('energydiagram.ED', Capture), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(self.path),'-o',str(output)]),0)
        fig = instances[0]
        # auto pitch from the energy range, split 70/30 by column_width
        space_for_level = 1.0*fig.ratio/len(set(fig.positions))  # energies 0 and 1
        self.assertAlmostEqual(fig.dimension, space_for_level*0.7)
        self.assertAlmostEqual(fig.space, space_for_level*0.3)
        # only level 101 has a side label with label_line enabled (figure default yes)
        leaders = [ln for ln in fig.ax.lines if ln.get_color() == 'k' and ln.get_linewidth() == 0.75]
        self.assertEqual(len(leaders), 1)
        xdata, ydata = leaders[0].get_xdata(), leaders[0].get_ydata()
        start = fig.positions[1]*(fig.dimension+fig.space)
        x_end = start + fig.dimension
        x_anchor = x_end*1.01  # label anchor (label_dx defaults to 0)
        g = min(fig.label_line_gap*fig.dimension, 0.4*abs(x_anchor-x_end))
        # white gap at BOTH ends: the connector touches neither the line nor the label
        self.assertAlmostEqual(xdata[0], x_end + g)
        self.assertGreater(xdata[0], x_end)
        self.assertAlmostEqual(xdata[1], x_anchor - g)
        self.assertLess(xdata[1], x_anchor)
        self.assertLess(xdata[0], xdata[1])  # a visible line remains
        self.assertAlmostEqual(ydata[0], 1)
        self.assertAlmostEqual(ydata[1], 1)  # label_dy defaults to 0

    def test_render_label_dx_and_gap(self):
        import matplotlib
        matplotlib.use('Agg')
        from energydiagram import ED
        self.path.write_text('''[figure]
format = pdf
label_line = yes
[dataset 1]
name = A
[levels 1]
100 0 -1 -1 1/2 + -1 left None None label_dx=0.03  label_dy=0.02
[dataset 2]
name = B
[levels 2]
101 1 -1 -1 1/2 + -1 right None None label_dx=-0.01  label_dy=-0.04
''')
        output = self.path.with_suffix('.pdf')
        instances = []
        class Capture(ED):
            def __init__(self):
                super().__init__()
                instances.append(self)
        with patch('energydiagram.ED', Capture), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(self.path), '-o', str(output)]), 0)
        fig = instances[0]
        pitch = fig.dimension + fig.space
        def inset(x_line_end, x_anchor):
            span = x_anchor - x_line_end
            g = min(fig.label_line_gap*fig.dimension, 0.4*abs(span))
            s = 1 if span >= 0 else -1
            return (x_line_end + s*g, x_anchor - s*g), g
        leaders = [ln for ln in fig.ax.lines if ln.get_color() == 'k' and ln.get_linewidth() == 0.75]
        self.assertEqual(len(leaders), 2)
        by_y0 = {ln.get_ydata()[0]: ln for ln in leaders}
        # level 100 (position 1, jpi=left -> label on the LEFT side of the line)
        start0 = 1*pitch
        anchor0 = start0*0.97 + 0.03
        (x_from, x_to), g0 = inset(start0, anchor0)
        left_line = by_y0[0]
        xdata, ydata = left_line.get_xdata(), left_line.get_ydata()
        self.assertAlmostEqual(xdata[0], x_from)   # inset at the level-line end
        self.assertAlmostEqual(xdata[1], x_to)     # inset at the label end (follows label_dx)
        self.assertNotEqual(xdata[0], start0)      # does not touch the level line
        self.assertNotEqual(xdata[1], anchor0)     # does not touch the label
        self.assertAlmostEqual(ydata[1], 0 + 0.02)  # label_dy
        # level 101 (position 2, jpi=right -> label on the RIGHT side of the line)
        start1 = 2*pitch
        x_end1 = start1 + fig.dimension
        anchor1 = x_end1*1.01 - 0.01
        (x_from, x_to), g1 = inset(x_end1, anchor1)
        right_line = by_y0[1]
        xdata, ydata = right_line.get_xdata(), right_line.get_ydata()
        self.assertAlmostEqual(xdata[0], x_from)
        self.assertAlmostEqual(xdata[1], x_to)
        self.assertNotEqual(xdata[0], x_end1)
        self.assertNotEqual(xdata[1], anchor1)
        self.assertAlmostEqual(ydata[1], 1 - 0.04)  # label_dy
        # the side label texts themselves sit at the shifted anchors
        side_labels = [t for t in fig.ax.texts if t.get_text().startswith('$1/2')]
        self.assertEqual(len(side_labels), 2)
        by_y = {t.get_y(): t for t in side_labels}
        self.assertAlmostEqual(by_y[0.02].get_x(), start0*0.97 + 0.03)
        self.assertAlmostEqual(by_y[0.96].get_x(), x_end1*1.01 - 0.01)
        # label_dx=0 keeps the default anchor (gap only)
        self.assertAlmostEqual(fig.label_dx_offsets, [0.03, -0.01])

    def test_axis_break_setting(self):
        config = self.parse(self.text.replace('axis_break = none', 'axis_break = 1.1, 2.4'))
        self.assertEqual(config.figure['axis_break'], (1.1, 2.4))
        # several breaks: pairs of low, high values
        config = self.parse(self.text.replace('axis_break = none', 'axis_break = 0.1, 0.4, 0.8, 0.95'))
        self.assertEqual(config.figure['axis_break'], (0.1, 0.4, 0.8, 0.95))
        config = self.parse(self.text.replace('axis_break = none', 'axis_break = NONE'))
        self.assertIsNone(config.figure['axis_break'])
        self.assertIsNone(self.parse(self.text).figure['axis_break'])

    def test_axis_break_invalid(self):
        for bad, match in [('0.5', 'pairs of comma-separated'),
                           ('0.2, 0.5, 2.4', 'pairs of comma-separated'),
                           ('2.4, 0.2', 'smaller than high'),
                           ('0.2, 0.5, 0.5, 2.4', 'must not overlap'),
                           ('0.2, 0.5, 0.4, 2.4', 'must not overlap'),
                           ('a, b', 'finite number')]:
            with self.subTest(bad=bad):
                self.bad(self.text.replace('axis_break = none', f'axis_break = {bad}'), match)

    def test_axis_break_rejects_level_inside_gap(self):
        # states at 0.467 and 0.796 lie inside (0.2, 0.9)
        self.bad(self.text.replace('axis_break = none', 'axis_break = 0.2, 0.9'), 'inside the break')

    def test_axis_break_round_trip(self):
        config = self.parse(self.text.replace('axis_break = none', 'axis_break = 1.1, 2.4'))
        write_input(config, self.path)
        again = read_input(self.path)
        self.assertEqual(again.figure, config.figure)
        self.assertEqual(again.datasets, config.datasets)
        self.assertIn('axis_break = 1.1, 2.4', self.path.read_text())
        # multiple breaks round-trip too
        config = self.parse(self.text.replace('axis_break = none', 'axis_break = 0.1, 0.4, 0.8, 0.95'))
        write_input(config, self.path)
        again = read_input(self.path)
        self.assertEqual(again.figure['axis_break'], (0.1, 0.4, 0.8, 0.95))
        self.assertIn('axis_break = 0.1, 0.4, 0.8, 0.95', self.path.read_text())

    def test_column_width_setting(self):
        config = self.parse(self.text.replace('column_width = 0.7', 'column_width = 0.85'))
        self.assertEqual(config.figure['column_width'], 0.85)
        self.assertEqual(self.parse(self.text).figure['column_width'], 0.7)

    def test_column_width_invalid(self):
        for bad, match in [('0', 'greater than 0'), ('1', 'less than 1'), ('1.5', 'less than 1'),
                           ('-0.2', 'greater than 0'), ('banana', 'finite number')]:
            with self.subTest(bad=bad):
                self.bad(self.text.replace('column_width = 0.7', f'column_width = {bad}'), match)

    def test_break_gap_setting(self):
        config = self.parse(self.text.replace('break_gap = 0.04', 'break_gap = 0.15'))
        self.assertEqual(config.figure['break_gap'], 0.15)
        self.assertEqual(self.parse(self.text).figure['break_gap'], 0.04)
        self.bad(self.text.replace('break_gap = 0.04', 'break_gap = -0.1'), 'between 0 and 1')
        self.bad(self.text.replace('break_gap = 0.04', 'break_gap = 1.5'), 'between 0 and 1')

    def test_ylabel_pad_setting(self):
        config = self.parse(self.text.replace('ylabel_pad = 4.0', 'ylabel_pad = 6.5'))
        self.assertEqual(config.figure['ylabel_pad'], 6.5)
        self.assertEqual(self.parse(self.text).figure['ylabel_pad'], 4.0)
        self.bad(self.text.replace('ylabel_pad = 4.0', 'ylabel_pad = -1'), 'zero or greater')
        self.bad(self.text.replace('ylabel_pad = 4.0', 'ylabel_pad = banana'), 'finite number')

    def test_errorbar_head_setting(self):
        config = self.parse(self.text.replace('errorbar_head = 10.0', 'errorbar_head = 2.5'))
        self.assertEqual(config.figure['errorbar_head'], 2.5)
        self.assertEqual(self.parse(self.text).figure['errorbar_head'], 10.0)
        self.bad(self.text.replace('errorbar_head = 10.0', 'errorbar_head = -0.5'), 'zero or greater')
        self.bad(self.text.replace('errorbar_head = 10.0', 'errorbar_head = x'), 'finite number')

    def test_render_column_width(self):
        import matplotlib
        matplotlib.use('Agg')
        from energydiagram import ED
        self.path.write_text('''[figure]
format = pdf
column_width = 0.9
[dataset 1]
name = A
[levels 1]
100 0 -1 -1 1/2 + -1 left None None
[dataset 2]
name = B
[levels 2]
101 1 -1 -1 1/2 + -1 right None None
''')
        output = self.path.with_suffix('.pdf')
        instances = []
        class Capture(ED):
            def __init__(self):
                super().__init__()
                instances.append(self)
        with patch('energydiagram.ED', Capture), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(self.path),'-o',str(output)]),0)
        fig = instances[0]
        self.assertAlmostEqual(fig.dimension/(fig.dimension+fig.space), 0.9)

    def test_render_errorbar_head_column_names_and_ylabel_pad(self):
        import matplotlib
        matplotlib.use('Agg')
        from energydiagram import ED
        self.path.write_text('''[figure]
format = pdf
errorbar_head = 3.0
ylabel_pad = 8.0
[dataset 1]
name = A
[levels 1]
100 0 -1 0.05 1/2 + -1 left None None
[dataset 2]
name = B
[levels 2]
101 1 -1 -1 1/2 + -1 right None None
''')
        output = self.path.with_suffix('.pdf')
        instances = []
        class Capture(ED):
            def __init__(self):
                super().__init__()
                instances.append(self)
        with patch('energydiagram.ED', Capture), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(self.path),'-o',str(output)]),0)
        fig = instances[0]
        # the cap-size factor is stored with the error bar
        self.assertAlmostEqual(fig.errorbars[0][2], 0.05)
        self.assertAlmostEqual(fig.errorbars[0][-1], 3.0)
        # column names are x tick labels at the column centers, not in-plot text
        pitch = fig.dimension + fig.space
        self.assertEqual([l.get_text() for l in fig.ax.get_xticklabels()], ['A', 'B'])
        self.assertAlmostEqual(fig.ax.get_xticks()[0], 1*pitch + fig.dimension/2)
        self.assertAlmostEqual(fig.ax.get_xticks()[1], 2*pitch + fig.dimension/2)
        self.assertNotIn('A', [t.get_text() for t in fig.ax.texts])
        # ... with the x tick marks themselves hidden
        self.assertEqual(fig.ax.xaxis.tick_params.get('size'), 0)
        # the y label hugs the axis with the requested padding
        self.assertEqual(fig.ax.yaxis.get_label().get_text(), 'Energy (MeV)')
        self.assertAlmostEqual(fig.ax.yaxis.labelpad, 8.0)

    def test_render_axis_break(self):
        import matplotlib
        matplotlib.use('Agg')
        from energydiagram import ED
        self.path.write_text('''[figure]
format = pdf
axis_break = 0.5, 2.0
break_gap = 0.12
ylabel_pad = 8.0
[dataset 1]
name = Low
[levels 1]
100 0 -1 -1 1/2 + -1 left None None
[dataset 2]
name = High
[levels 2]
101 3 -1 -1 1/2 + -1 right None None link=100
''')
        output = self.path.with_suffix('.pdf')
        instances = []
        class Capture(ED):
            def __init__(self):
                super().__init__()
                instances.append(self)
        with patch('energydiagram.ED', Capture), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(self.path),'-o',str(output)]),0)
        fig = instances[0]
        self.assertIsNotNone(fig.ax2)
        self.assertEqual(fig.ax.get_ylim()[0], 2.0)      # top panel starts at the break high
        self.assertEqual(fig.ax2.get_ylim()[1], 0.5)     # bottom panel ends at the break low
        # // break marks drawn on both panels (marker lines at the touching edges)
        self.assertTrue(any(ln.get_marker() not in (None, '', 'None') for ln in fig.ax.lines))
        self.assertTrue(any(ln.get_marker() not in (None, '', 'None') for ln in fig.ax2.lines))
        # spines facing the gap are hidden
        self.assertFalse(fig.ax.spines['bottom'].get_visible())
        self.assertFalse(fig.ax2.spines['top'].get_visible())
        # each panel got the full set of artists (clipping does the visual split)
        self.assertEqual(len(fig.ax.texts), len(fig.ax2.texts))
        # ax_for_energy routes to the right panel
        self.assertIs(fig.ax_for_energy(3), fig.ax)
        self.assertIs(fig.ax_for_energy(0), fig.ax2)
        # the gridspec must stay tight_layout-compatible (no locally modified
        # subplot params such as hspace), otherwise fig.tight_layout() warns
        ss = fig.ax.get_subplotspec() if hasattr(fig.ax, 'get_subplotspec') else None
        if ss is not None:
            self.assertEqual(ss.get_gridspec().locally_modified_subplot_params(), [])
        # the white gap between the panels is pinned via break_gap (hspace)
        self.assertAlmostEqual(fig.fig.subplotpars.hspace, 0.12)
        # the figure-level y label exists and, after layout, sits ylabel_pad
        # points left of the y tick labels (not at a fixed figure fraction)
        t = fig.supylabel_text
        self.assertIsNotNone(t)
        self.assertEqual(t.get_text(), 'Energy (MeV)')
        bb = fig.ax.yaxis.get_tightbbox(None)
        tick_left = fig.fig.transFigure.inverted().transform((bb.x0, bb.y0))[0]
        expected = tick_left - 8.0/72.0/fig.fig.get_size_inches()[0]
        self.assertAlmostEqual(t.get_x(), expected)
        # column names are x tick labels, shown on the bottom panel only
        self.assertEqual([l.get_text() for l in fig.ax2.get_xticklabels()], ['Low', 'High'])
        self.assertIs(fig.ax.xaxis.tick_params.get('labelbottom'), False)
        self.assertNotIn('Low', [t2.get_text() for t2 in fig.ax.texts])
        # the link crossing the break is one continuous ConnectionPatch between
        # the two endpoint panels, not per-panel clipped stubs
        from matplotlib.patches import ConnectionPatch
        cons = [p for p in fig.axs[-1].patches if isinstance(p, ConnectionPatch)]
        self.assertEqual(len(cons), 1)
        con = cons[0]
        self.assertEqual(con.coordsA, 'data')
        self.assertEqual(con.coordsB, 'data')
        self.assertEqual(con.xyA[1], 0)   # source level energy 0
        self.assertEqual(con.xyB[1], 3)   # target level energy 3
        self.assertIs(con.axesA, fig.axs[-1])  # energy 0 lives in the bottom panel
        self.assertIs(con.axesB, fig.axs[0])   # energy 3 lives in the top panel
        self.assertFalse(con.kwargs.get('clip_on', True))
        self.assertFalse(any(ln.get_linestyle() == '--' for ax in fig.axs for ln in ax.lines))
        # a level inside the gap is rejected with exit code 2
        self.path.write_text(self.path.read_text().replace('100 0 -1', '100 1.0 -1'))
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(main([str(self.path),'-o',str(output),'--force']),2)
        self.assertIn('inside the break', err.getvalue())

    def test_render_axis_break_multiple(self):
        import matplotlib
        matplotlib.use('Agg')
        from energydiagram import ED
        self.path.write_text('''[figure]
format = pdf
axis_break = 0.5, 1.5, 2.5, 3.5
break_gap = 0.1
[dataset 1]
name = Low
[levels 1]
100 0 -1 -1 1/2 + -1 left None None
[dataset 2]
name = Mid
[levels 2]
101 2.0 -1 -1 1/2 + -1 None None None link=100
[dataset 3]
name = High
[levels 3]
102 4.0 -1 -1 1/2 + -1 right None None link=101
''')
        output = self.path.with_suffix('.pdf')
        instances = []
        class Capture(ED):
            def __init__(self):
                super().__init__()
                instances.append(self)
        with patch('energydiagram.ED', Capture), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(self.path),'-o',str(output)]),0)
        fig = instances[0]
        # two breaks -> three stacked panels sharing the x axis
        self.assertEqual(len(fig.axs), 3)
        self.assertIs(fig.ax, fig.axs[0])
        self.assertIs(fig.ax2, fig.axs[-1])
        self.assertEqual(fig.axs[0].get_ylim()[0], 3.5)      # top panel starts above the highest gap
        self.assertEqual(fig.axs[1].get_ylim(), (1.5, 2.5))   # middle panel between the two gaps
        self.assertEqual(fig.axs[2].get_ylim()[1], 0.5)       # bottom panel ends below the lowest gap
        # spines facing the gaps are hidden, outer spines stay
        self.assertFalse(fig.axs[0].spines['bottom'].get_visible())
        self.assertFalse(fig.axs[1].spines['bottom'].get_visible())
        self.assertFalse(fig.axs[1].spines['top'].get_visible())
        self.assertFalse(fig.axs[2].spines['top'].get_visible())
        self.assertTrue(fig.axs[0].spines['top'].get_visible())
        self.assertTrue(fig.axs[2].spines['bottom'].get_visible())
        # // marks: bottom edge of the top/middle panels, top edge of middle/bottom
        def marks(ax):
            return sum(1 for ln in ax.lines if ln.get_marker() not in (None, '', 'None'))
        self.assertEqual([marks(ax) for ax in fig.axs], [1, 2, 1])
        # every panel got the full set of artists (clipping does the visual split)
        self.assertEqual(len(fig.axs[0].texts), len(fig.axs[1].texts))
        self.assertEqual(len(fig.axs[1].texts), len(fig.axs[2].texts))
        # ax_for_energy routes to the right panel
        self.assertIs(fig.ax_for_energy(4.0), fig.axs[0])
        self.assertIs(fig.ax_for_energy(2.0), fig.axs[1])
        self.assertIs(fig.ax_for_energy(0.0), fig.axs[2])
        # the white gaps are pinned via break_gap (hspace); the gridspec itself
        # stays tight_layout-compatible
        self.assertAlmostEqual(fig.fig.subplotpars.hspace, 0.1)
        ss = fig.axs[0].get_subplotspec()
        self.assertEqual(ss.get_gridspec().locally_modified_subplot_params(), [])
        self.assertEqual(len(ss.get_gridspec().height_ratios), 3)
        # column names on the bottom panel only, x tick marks hidden everywhere
        self.assertEqual([l.get_text() for l in fig.axs[2].get_xticklabels()], ['Low', 'Mid', 'High'])
        self.assertIs(fig.axs[0].xaxis.tick_params.get('labelbottom'), False)
        self.assertIs(fig.axs[1].xaxis.tick_params.get('labelbottom'), False)
        self.assertEqual(fig.axs[0].xaxis.tick_params.get('size'), 0)
        # both links cross a gap: drawn once each as continuous ConnectionPatches
        # routed through the correct endpoint panels
        from matplotlib.patches import ConnectionPatch
        cons = [p for p in fig.axs[-1].patches if isinstance(p, ConnectionPatch)]
        self.assertEqual(len(cons), 2)
        by_y = {c.xyA[1]: c for c in cons}
        self.assertIs(by_y[0.0].axesA, fig.axs[2])   # 0.0 -> bottom panel
        self.assertIs(by_y[0.0].axesB, fig.axs[1])   # 2.0 -> middle panel
        self.assertIs(by_y[2.0].axesA, fig.axs[1])   # 2.0 -> middle panel
        self.assertIs(by_y[2.0].axesB, fig.axs[0])   # 4.0 -> top panel
        self.assertFalse(any(ln.get_linestyle() == '--' for ax in fig.axs for ln in ax.lines))
        # the figure-level y label is repositioned next to the axis
        self.assertIsNotNone(fig.supylabel_text)
        bb = fig.axs[0].yaxis.get_tightbbox(None)
        tick_left = fig.fig.transFigure.inverted().transform((bb.x0, bb.y0))[0]
        self.assertAlmostEqual(fig.supylabel_text.get_x(),
                               tick_left - 4.0/72.0/fig.fig.get_size_inches()[0])
        # a level inside any gap is rejected with exit code 2
        self.path.write_text(self.path.read_text().replace('101 2.0 -1', '101 1.0 -1'))
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(main([str(self.path),'-o',str(output),'--force']),2)
        self.assertIn('inside the break', err.getvalue())

    def test_tight_layout_warning_retries_then_falls_back(self):
        # simulate real matplotlib refusing tight_layout (happens when several
        # break panels are too short for their decorations): the renderer must
        # retry with smaller padding and finally fall back to fixed margins
        import warnings as warnings_mod
        import matplotlib
        matplotlib.use('Agg')
        from matplotlib.figure import Figure
        from energydiagram import ED
        self.path.write_text('''[figure]
format = pdf
axis_break = 0.5, 2.0
break_gap = 0.04
[dataset 1]
name = Low
[levels 1]
100 0 -1 -1 1/2 + -1 left None None
[dataset 2]
name = High
[levels 2]
101 3 -1 -1 1/2 + -1 right None None link=100
''')
        output = self.path.with_suffix('.pdf')
        calls = []
        original = Figure.tight_layout
        def fake_tight_layout(self, *a, **kw):
            calls.append(kw.get('pad', a[0] if a else None))
            warnings_mod.warn('Tight layout not applied. tight_layout cannot make '
                              'Axes height small enough to accommodate all Axes '
                              'decorations.', UserWarning)
        instances = []
        class Capture(ED):
            def __init__(self):
                super().__init__()
                instances.append(self)
        try:
            Figure.tight_layout = fake_tight_layout
            with patch('energydiagram.ED', Capture), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(self.path), '-o', str(output)]), 0)
        finally:
            Figure.tight_layout = original
        fig = instances[0]
        # retried with progressively smaller padding, then gave up
        self.assertEqual(calls, [1.08, 0.5, 0.2, 0.05])
        # fallback fixed margins were applied, with the break gap as hspace
        self.assertAlmostEqual(fig.fig.subplotpars.left, 0.12)
        self.assertAlmostEqual(fig.fig.subplotpars.right, 0.98)
        self.assertAlmostEqual(fig.fig.subplotpars.hspace, 0.04)
        self.assertTrue(output.exists())


if __name__ == '__main__':
    unittest.main()
