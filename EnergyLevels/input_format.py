"""Validated readable and legacy inputs; checking needs only Python itself."""
from dataclasses import dataclass, field
from pathlib import Path
from fractions import Fraction
import math
import re
import shlex

class InputError(ValueError):
    pass

@dataclass
class Source:
    path: Path
    line: int
    text: str
    section: str = ''
    def fail(self, key, message):
        raise InputError(f'{self.path}:{self.line} [{self.section}] {key}: {message}\n  > {self.text}')

@dataclass
class Level:
    id: int
    energy: float
    width: float
    uncertainty: float
    j: str
    parity: int
    label_index: int
    jpi: str
    bottom: str
    top: str
    options: dict
    source: Source = field(compare=False)

@dataclass
class Dataset:
    name: str
    color: int
    linestyle: str
    levels: list

@dataclass
class Config:
    figure: dict
    datasets: list
    legacy: bool = False

DEFAULTS = dict(output='energy_levels', format='pdf', dpi=350., size_px=(1200., 900.),
                ticks=(.02, .2), x_margin=.5, y_margin=.05, width_alpha=.4,
                width_spacing=.1, reference_energy=0., ylabel='Energy (MeV)', font_size=10., title_size=11.,
                label_line=False, axis_break=None, column_width=0.7, break_gap=0.04,
                ylabel_pad=4.0, errorbar_head=10.0)
STYLES = ('-', '--', ':', '-.')
ALIASES = dict(C='color', LS='linestyle', L='link', LC='link_color', LLS='link_style', LLW='link_width')
OPTIONS = ('color', 'linestyle', 'link', 'link_color', 'link_style', 'link_width', 'label_dy', 'label_dx', 'label_line')

def number(value, src, key, integer=False, minimum=None, maximum=None):
    try:
        result = int(value) if integer else float(value)
        if not math.isfinite(result):
            raise ValueError()
    except (ValueError, OverflowError):
        src.fail(key, f'expected a finite {"integer" if integer else "number"}, got {value!r}')
    if (minimum is not None and result < minimum) or (maximum is not None and result > maximum):
        src.fail(key, f'{result} is outside the allowed range [{minimum}, {maximum}]')
    return result

def style(value, src, key):
    if value not in STYLES:
        src.fail(key, f'choose one of {STYLES}, got {value!r}')
    return value

def yes_no(value, src, key):
    low = value.strip().lower()
    if low in ('yes', 'true', '1'):
        return True
    if low in ('no', 'false', '0'):
        return False
    src.fail(key, f'use yes or no, got {value!r}')

def tokens(src):
    lexer = shlex.shlex(src.text, posix=True)
    lexer.whitespace_split = True
    lexer.commenters = ''
    lexer.escape = ''  # Preserve LaTeX backslashes, including inside quotes.
    try:
        return list(lexer)
    except ValueError as exc:
        src.fail('quotes', str(exc))

def level(src):
    t = tokens(src)
    fields = 'id energy width uncertainty j parity label_index jpi bottom top'.split()
    if len(t) < 10:
        src.fail('columns', f'expected 10 required fields, got {len(t)}; missing {", ".join(fields[len(t):])}')
    ident = number(t[0], src, 'id', True, 0)
    energy = number(t[1], src, 'energy')
    width = number(t[2], src, 'width', minimum=-1)
    uncertainty = number(t[3], src, 'uncertainty', minimum=-1)
    for key, val in [('width', width), ('uncertainty', uncertainty)]:
        if -1 < val < 0:
            src.fail(key, 'use -1 or 0 to disable, or a positive value in MeV')
    try:
        spin = Fraction(t[4])
        if spin < 0 or (2*spin).denominator != 1:
            raise ValueError()
    except (ValueError, ZeroDivisionError):
        if not (t[4] == '-1' and t[7] == 'None'):
            src.fail('j', 'use a nonnegative integer or half-integer (e.g. 3/2); -1 only with jpi=None')
    parity = number({'+':'1', '-':'0'}.get(t[5], t[5]), src, 'parity', True, 0, 1)
    index = number(t[6], src, 'label_index', True, -1)
    if t[7] not in ('left', 'right', 'None'):
        src.fail('jpi', 'choose left, right, or None')
    opts = {}
    for token in t[10:]:
        sep = '=' if '=' in token else '#'
        if sep not in token:
            src.fail('option', f'{token!r}: use key=value, e.g. color=2 or link=4')
        key, value = token.split(sep, 1)
        key = ALIASES.get(key, key)
        if key not in OPTIONS:
            src.fail('option', f'unknown {key!r}; available: {", ".join(OPTIONS)}')
        if key in opts:
            src.fail(key, 'option appears more than once')
        if key in ('color', 'link_color'):
            value = number(value, src, key, True, -1, 9)
        elif key == 'link':
            value = number(value, src, key, True, 0)
        elif key == 'label_dy':
            value = number(value, src, key)
        elif key == 'label_dx':
            value = number(value, src, key)
        elif key == 'label_line':
            value = yes_no(value, src, key)
        elif key == 'link_width':
            value = number(value, src, key, minimum=0)
            if value == 0:
                src.fail(key, 'must be greater than zero')
        else:
            value = style(value, src, key)
        opts[key] = value
    if 'link' not in opts and any(k.startswith('link_') for k in opts):
        src.fail('link', 'link styling requires a link=<state id> destination')
    return Level(ident, energy, width, uncertainty, t[4], parity, index, t[7],
                 '' if t[8] == 'None' else t[8], '' if t[9] == 'None' else t[9], opts, src)

def figure_value(key, value, src):
    if key not in DEFAULTS:
        src.fail(key, f'unknown figure setting; available: {", ".join(DEFAULTS)}')
    if key in ('output', 'ylabel'):
        if not value:
            src.fail(key, 'must not be empty')
        return value
    if key == 'format':
        value = value.lower()
        if value not in ('pdf', 'png', 'jpg', 'jpeg', 'svg', 'eps', 'ps', 'pgf'):
            src.fail(key, 'choose pdf, png, jpg, jpeg, svg, eps, ps, or pgf')
        return value
    if key == 'column_width':
        val = number(value, src, key)
        if not 0 < val < 1:
            src.fail(key, 'must be greater than 0 and less than 1 (fraction of the column pitch)')
        return val
    if key == 'break_gap':
        val = number(value, src, key)
        if not 0 <= val <= 1:
            src.fail(key, 'must be between 0 and 1 (fraction of the average panel height)')
        return val
    if key == 'label_line':
        return yes_no(value, src, key)
    if key == 'axis_break':
        if value.strip().lower() in ('none', 'off', 'no'):
            return None
        parts = value.split(',')
        if len(parts) < 2 or len(parts) % 2:
            src.fail(key, 'use none, or pairs of comma-separated displayed-energy values: '
                          'low1, high1, low2, high2, ... (one pair per break)')
        vals = tuple(number(p.strip(), src, key) for p in parts)
        for k in range(0, len(vals), 2):
            lo, hi = vals[k], vals[k+1]
            if not lo < hi:
                src.fail(key, f'low ({lo}) must be smaller than high ({hi})')
        for k in range(1, len(vals)-1, 2):
            if not vals[k] < vals[k+1]:
                src.fail(key, f'breaks must not overlap and must increase: '
                              f'{vals[k]} must be smaller than {vals[k+1]}')
        return vals
    if key in ('size_px', 'ticks'):
        parts = value.split(',')
        if len(parts) != 2:
            src.fail(key, 'expected two comma-separated positive numbers')
        vals = tuple(number(v.strip(), src, key, minimum=0) for v in parts)
        if min(vals) <= 0:
            src.fail(key, 'both values must be greater than zero')
        if key == 'ticks' and vals[0] > vals[1]:
            src.fail(key, 'minor spacing must not exceed major spacing')
        return vals
    val = number(value, src, key)
    if key in ('dpi', 'font_size', 'title_size') and val <= 0:
        src.fail(key, 'must be greater than zero')
    if key in ('x_margin', 'y_margin', 'width_alpha') and not 0 <= val <= 1:
        src.fail(key, 'must be between 0 and 1')
    if key == 'width_spacing' and not 0 <= val < .5:
        src.fail(key, 'must be at least 0 and less than 0.5')
    if key in ('ylabel_pad', 'errorbar_head') and val < 0:
        src.fail(key, 'must be zero or greater')
    return val

def read_input(path):
    path = Path(path)
    lines = path.read_text(encoding='utf-8-sig').splitlines()
    significant = [(i, s.strip()) for i, s in enumerate(lines, 1) if s.strip() and not s.lstrip().startswith('#')]
    if not significant:
        raise InputError(f'{path}: input is empty')
    if not significant[0][1].startswith('['):
        config = read_legacy(path, significant)
    else:
        sections = {}
        current = None
        for lineno, text in significant:
            src = Source(path, lineno, text, current or '')
            match = re.fullmatch(r'\[([^\]]+)\]', text)
            if match:
                current = match[1].strip()
                src.section = current
                if current != 'figure' and not re.fullmatch(r'(dataset|levels) [1-9]\d*', current):
                    src.fail('section', 'expected [figure], [dataset N], or [levels N]')
                if current in sections:
                    src.fail('section', 'duplicate section')
                sections[current] = (src, [])
            elif current is None:
                src.fail('section', 'put settings below a section header')
            else:
                sections[current][1].append(src)
        if 'figure' not in sections:
            raise InputError(f'{path}: missing [figure] section')
        fig = DEFAULTS.copy()
        metadata, tables = {}, {}
        for section, (head, rows) in sections.items():
            if section.startswith('levels '):
                tables[section.split()[1]] = [level(s) for s in rows]
                if not rows:
                    head.fail('levels', 'provide at least one state row')
                continue
            values = {}
            for src in rows:
                if '=' not in src.text:
                    src.fail('setting', 'expected key = value')
                key, val = (v.strip() for v in src.text.split('=', 1))
                if key in values:
                    src.fail(key, 'duplicate setting')
                values[key] = val
                if section == 'figure':
                    fig[key] = figure_value(key, val, src)
                elif key not in ('name', 'color', 'linestyle'):
                    src.fail(key, 'dataset settings are name, color, and linestyle')
                elif key == 'color':
                    number(val, src, key, True, -1, 9)
                elif key == 'linestyle':
                    style(val, src, key)
            if section != 'figure':
                metadata[section.split()[1]] = (head, values)
        if set(metadata) != set(tables):
            raise InputError(f'{path}: every [dataset N] must have a matching [levels N]; '
                             f'dataset IDs={sorted(metadata)}, levels IDs={sorted(tables)}')
        datasets = []
        for ident in sorted(metadata, key=int):
            head, values = metadata[ident]
            datasets.append(Dataset(values.get('name', ''), int(values.get('color', '-1')),
                                    values.get('linestyle', '-'), tables[ident]))
        config = Config(fig, datasets)
    validate(config, path)
    return config

def read_legacy(path, lines):
    sections = {}
    current = None
    for lineno, text in lines:
        name = text.split('#', 1)[0].strip()
        if name in ('OUTPUT FILE', 'EXP BINDING ENERGY', 'NUM DATA') or re.fullmatch(r'DATA-\d+', name):
            if name in sections:
                Source(path, lineno, text, name).fail('section', 'duplicate header')
            current = name
            sections[name] = []
        elif current is None:
            Source(path, lineno, text).fail('section', 'expected OUTPUT FILE')
        else:
            sections[current].append(Source(path, lineno, text, current))
    def block(name, count=None):
        if name not in sections:
            raise InputError(f'{path}: missing {name} section')
        rows = sections[name]
        if count is not None and len(rows) != count:
            raise InputError(f'{path}: [{name}] expected {count} values, found {len(rows)}')
        return rows
    keys = ['output', 'format', 'dpi', 'size_px', 'ticks', 'x_margin', 'y_margin', 'width_alpha', 'width_spacing']
    fig = DEFAULTS.copy()
    for key, src in zip(keys, block('OUTPUT FILE', 9)):
        fig[key] = figure_value(key, src.text, src)
    src = block('EXP BINDING ENERGY', 1)[0]
    fig['reference_energy'] = figure_value('reference_energy', src.text, src)
    src = block('NUM DATA', 1)[0]
    count = number(src.text, src, 'dataset count', True, 1)
    expected = {'OUTPUT FILE', 'EXP BINDING ENERGY', 'NUM DATA'} | {f'DATA-{i}' for i in range(1, count+1)}
    if set(sections) != expected:
        raise InputError(f'{path}: NUM DATA does not match the DATA-N section headers')
    datasets = []
    for i in range(1, count+1):
        rows = block(f'DATA-{i}')
        if len(rows) < 4:
            raise InputError(f'{path}: [DATA-{i}] needs count, title, color, and linestyle')
        n = number(rows[0].text, rows[0], 'state count', True, 1)
        if len(rows[4:]) != n:
            rows[0].fail('state count', f'declared {n}, found {len(rows[4:])} state rows')
        datasets.append(Dataset('' if rows[1].text == 'None' else rows[1].text,
                        number(rows[2].text, rows[2], 'color', True, -1, 9),
                        style(rows[3].text, rows[3], 'linestyle'), [level(s) for s in rows[4:]]))
    # Legacy ED used left/right opposite to their physical position.
    for ds in datasets:
        for s in ds.levels:
            s.jpi = {'left': 'right', 'right': 'left', 'None': 'None'}[s.jpi]
    return Config(fig, datasets, True)

def validate(config, path):
    if not config.datasets:
        raise InputError(f'{path}: provide at least one dataset and one level')
    ids = {}
    for ds in config.datasets:
        for state in ds.levels:
            if state.id in ids:
                state.source.fail('id', f'duplicate state ID {state.id}; first used on line {ids[state.id].source.line}')
            ids[state.id] = state
    for state in ids.values():
        dest = state.options.get('link')
        if dest is not None and dest not in ids:
            state.source.fail('link', f'unknown destination {dest}; available state IDs: {sorted(ids)}')
        if dest == state.id:
            state.source.fail('link', 'a state cannot link to itself')
    brk = config.figure.get('axis_break')
    if brk:
        ref = config.figure['reference_energy']
        for k in range(0, len(brk), 2):
            lo, hi = brk[k], brk[k+1]
            for state in ids.values():
                disp = state.energy - ref
                if lo < disp < hi:
                    state.source.fail('axis_break',
                                      f'displayed energy {disp} lies inside the break ({lo}, {hi}); '
                                      'move the break or the level')

def write_input(config, path):
    def fmt(value):
        if value is None:
            return 'none'
        if isinstance(value, bool):
            return 'yes' if value else 'no'
        if isinstance(value, tuple):
            return ', '.join(map(str, value))
        return value
    out = ['# Energies, widths and uncertainties: MeV. Full-line # comments only.',
           '# Quote level labels containing spaces. Scalar settings need no quotes.', '[figure]']
    for key, value in config.figure.items():
        out.append(f'{key} = {fmt(value)}')
    for i, ds in enumerate(config.datasets, 1):
        out += ['', f'[dataset {i}]', f'name = {ds.name}', f'color = {ds.color}',
                f'linestyle = {ds.linestyle}', '', f'[levels {i}]',
                '# id energy width uncertainty j parity label_index jpi bottom top [options]']
        for s in ds.levels:
            def label(text):
                text = text or 'None'
                if '"' not in text:
                    return '"' + text + '"' if any(c.isspace() for c in text) or "'" in text else text
                if "'" not in text:
                    return "'" + text + "'"
                raise InputError('Labels containing both quote types cannot be converted automatically.')
            parts = [s.id, s.energy, s.width, s.uncertainty, s.j, s.parity,
                     s.label_index, s.jpi, label(s.bottom), label(s.top)]
            out.append('  '.join(map(str, parts)) + ''.join(f'  {k}={fmt(v)}' for k, v in s.options.items()))
    Path(path).write_text('\n'.join(out)+'\n', encoding='utf-8')
