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

if __name__ == '__main__':
    unittest.main()
