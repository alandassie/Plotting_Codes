#!/usr/bin/env python3
"""Plot validated nuclear energy levels. Run with --help for diagnostic shortcuts."""
import argparse
from pathlib import Path
import shutil
import sys
import warnings
from input_format import InputError, read_input, write_input

def apply_tight_layout(fig, hspace=None):
    """Call fig.tight_layout, tolerating the 'Axes height small enough' warning.

    With several axis-break panels the per-panel decorations (ticks, labels,
    // marks) can be taller than the panels themselves; matplotlib then emits
    'UserWarning: Tight layout not applied...' and skips the layout entirely.
    Retry with progressively smaller padding, and if every attempt fails fall
    back to fixed margins so the figure is still laid out sensibly.
    """
    for pad in (1.08, 0.5, 0.2, 0.05):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            fig.tight_layout(pad=pad)
        if not any('Tight layout not applied' in str(w.message) for w in caught):
            return
    kwargs = {'left': 0.12, 'right': 0.98, 'top': 0.98, 'bottom': 0.1}
    if hspace is not None:
        kwargs['hspace'] = hspace
    fig.subplots_adjust(**kwargs)


def render(config, args):
    try:
        import matplotlib
        if not args.show:
            matplotlib.use('Agg')
        from matplotlib import pyplot as plt
        from energydiagram import ED
    except ImportError as exc:
        raise InputError(f'Missing plotting dependency: {exc}. Install matplotlib with python3 -m pip install matplotlib') from exc
    f = config.figure.copy()
    if args.format:
        f['format'] = args.format
    tex = args.tex == 'yes'
    if tex or f['format'] == 'pgf':
        executable = 'xelatex' if f['format'] == 'pgf' else 'latex'
        if not shutil.which(executable):
            raise InputError(f'{executable} was not found. Install a TeX distribution, or use --format pdf --tex no.')
    plt.rcParams.update({'pgf.texsystem': 'xelatex', 'pgf.rcfonts': False})
    figure = ED()
    figure.use_tex = tex
    figure.font_size = f['font_size']
    figure.title_size = f['title_size']
    figure.fig_yaxis_label = f['ylabel']
    figure.fig_parameters(f['x_margin'], f['y_margin'], f['dpi'], *f['size_px'], *f['ticks'])
    figure.column_width = f['column_width']
    figure.axis_break = f['axis_break']
    figure.ylabel_pad = f['ylabel_pad']
    figure.errorbar_head = f['errorbar_head']
    states = [s for ds in config.datasets for s in ds.levels]
    mapping = {s.id: i for i, s in enumerate(states)}
    for ds in config.datasets:
        for i, s in enumerate(ds.levels):
            label = f'${s.j}^{{{"+" if s.parity else "-"}}}'
            if s.label_index >= 0:
                label += f'_{{{s.label_index}}}'
            label += '$'
            # Original ED calls text on the physical left right_text, and vice versa.
            kwargs = {('right_text' if s.jpi == 'left' else 'left_text'): label} if s.jpi != 'None' else {}
            figure.add_level(s.energy-f['reference_energy'], bottom_text=s.bottom,
                             top_text=s.top, position=None if i == 0 else 'last',
                             set_title=ds.name if i == 0 else '',
                             color=s.options.get('color', ds.color),
                             linestyle=s.options.get('linestyle', ds.linestyle),
                             label_dy=s.options.get('label_dy', 0),
                             label_dx=s.options.get('label_dx', 0),
                             label_line=s.options.get('label_line', f['label_line']), **kwargs)
    for s in states:
        index = mapping[s.id]
        if s.width > 0:
            figure.add_widthbox(index, s.width, f['width_spacing'], f['width_alpha'])
        if s.uncertainty > 0:
            figure.add_errorbar(index, s.uncertainty)
        if 'link' in s.options:
            dest = mapping[s.options['link']]
            start, end = sorted((dest, index), key=lambda k: figure.positions[k])
            figure.add_link(start, end, color=s.options.get('link_color', -1),
                            ls=s.options.get('link_style', '--'),
                            linewidth=s.options.get('link_width', .75))
    output = Path(args.output) if args.output else Path(f['output'] + '.' + f['format'])
    if output.resolve() == Path(args.input).resolve():
        raise InputError('Output path is the input file; choose another path with -o.')
    if output.exists() and not args.force:
        raise InputError(f'Output already exists: {output}. Use --force to replace it or -o to choose another path.')
    if not output.parent.is_dir():
        raise InputError(f'Output directory does not exist: {output.parent}. Create it or choose another -o path.')
    try:
        figure.plot()
        if args.show_ids:
            for i, s in enumerate(states):
                x = figure.positions[i]*(figure.dimension+figure.space)
                figure.ax_for_energy(figure.energies[i]).text(x, figure.energies[i]+figure.offset*2,
                                                              str(s.id), color='red', fontsize=9)
        apply_tight_layout(figure.fig, f['break_gap'] if figure.ax2 is not None else None)
        if figure.ax2 is not None:
            # pin the white gap between the two break panels (hspace fraction);
            # the gridspec itself stays untouched so tight_layout stays happy
            figure.fig.subplots_adjust(hspace=f['break_gap'])
            # now that the layout is final, place the figure-level y label
            # ylabel_pad points away from the axis
            figure.adjust_figure_ylabel()
        figure.fig.savefig(output, format=f['format'], dpi=f['dpi'])
        if args.show:
            plt.show()
    except Exception as exc:
        raise InputError(f'Rendering/export failed for {output}: {exc}\n'
                         'Check LaTeX/math labels; try --format pdf --tex no. Use --debug for the traceback.') from exc
    finally:
        plt.close('all')
    return output

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', nargs='?', default='data.in', help='input path (default: data.in)')
    p.add_argument('-c', '--check', action='store_true', help='validate without importing Matplotlib or creating a figure')
    p.add_argument('--convert', metavar='FILE', help='write readable input without plotting')
    p.add_argument('-o', '--output', help='exact output path; format is controlled separately')
    p.add_argument('-f', '--format', choices=['pdf','png','jpg','jpeg','svg','eps','ps','pgf'], help='override input format')
    p.add_argument('--tex', choices=['yes','no'], default='no', help='external LaTeX labels (default: no; PGF always needs xelatex)')
    p.add_argument('--show-ids', action='store_true', help='print input state IDs in red')
    p.add_argument('--show', action='store_true', help='show an interactive window after saving')
    p.add_argument('--debug', action='store_true', help='include a traceback on error')
    p.add_argument('--force', action='store_true', help='replace an existing output or converted input')
    args = p.parse_args(argv)
    try:
        config = read_input(args.input)
        print(f'Input OK: {len(config.datasets)} datasets, {sum(len(d.levels) for d in config.datasets)} states'
              f' ({"legacy" if config.legacy else "readable"} format).')
        if args.convert:
            if Path(args.convert).resolve() == Path(args.input).resolve():
                raise InputError('Conversion must use a different path from the source input.')
            if Path(args.convert).exists() and not args.force:
                raise InputError(f'{args.convert} already exists; use --force to replace it.')
            write_input(config, args.convert)
            print(f'Converted input: {args.convert}')
        elif not args.check:
            print(f'Saved: {render(config, args)}')
        return 0
    except (InputError, OSError, UnicodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        return 2

if __name__ == '__main__':
    sys.exit(main())
