# Addendum to the EnergyLevels input guide (updated 11 November 2026)

New input options, available in the readable `[figure]` / `[levels N]` format.
Legacy `OUTPUT FILE` inputs keep the previous behavior (all new settings take
their defaults there). Note: the earlier experimental `column_spacing` setting
has been **removed** — `column_width` below is the effective control.

## 1 / Column width — `[figure]` setting `column_width`

| Setting | Default | Meaning / allowed values |
| --- | --- | --- |
|  column_width | 0.7 | Length of each level line as a fraction of the column pitch (the center-to-center distance between columns, auto-sized from the energy range). Must satisfy 0 < value < 1; the rest of the pitch is the gap between columns. This is the setting that visibly changes how long the state lines look: 0.9 gives long lines with narrow gaps, 0.3 gives short lines with wide gaps. |

```ini
[figure]
column_width = 0.7    # default: 70% line, 30% gap
# column_width = 0.45 # shorter lines, wider gaps between columns
```

Invalid values (0, 1, negatives, >= 1, non-numbers) are rejected with a
diagnostic.

## 2 / Column names — `[dataset N]` setting `name`

The column title under each column is simply the dataset name:

```ini
[dataset 1]
name = Exp-$^{39}$Ca-
[dataset 2]
name = GSM
```

The names are drawn as x-axis tick labels centered under each column, below
the bottom panel (also with axis breaks), at `title_size` points. Because
they are real tick labels, `tight_layout` reserves room for them, so they are
always fully visible — they can no longer be clipped at the figure edge. The
x tick marks themselves are hidden; only the labels are shown.

## 3 / Label connector line — `label_line` yes/no

Draws a thin black line from the end of a level line to its side spin-parity
label. Useful together with `label_dy` for close doublets, where the shifted
label could otherwise be ambiguous.

| Where | Default | Meaning |
| --- | --- | --- |
|  `[figure]` `label_line` | no | Default for every state in the file. |
|  per state row, `label_line=yes/no` | figure value | Overrides the figure default for that state only. |

```ini
[levels 3]
# id energy width uncertainty j parity label_index jpi bottom top [options]
8  0.0    -1.0  -1.0  1  1  1  right  None  None  link=4  label_dy=-0.045  label_line=yes
9  0.029  -1.0  -1.0  2  1  1  right  None  None  link=4  label_dy=0.035   label_line=yes
```

The connector runs from the end of the level line nearest the label to the
label anchor, so it follows `label_dy`. It is drawn only when the state has a
side label (`jpi` left or right). Values `yes/no/true/false/1/0` are accepted,
case-insensitive. `--convert` writes the option back as `label_line=yes/no`.

The connector does not touch the level line: it starts a tiny white gap past
the end of the line (1% of the level-line length, the `ED.label_line_gap`
code constant), so the black line is visually separate from the level line.

## 3b / Horizontal label shift — per-state option `label_dx`

`label_dx=<number>` shifts only the side spin-parity label horizontally, in x
data units, on top of its default position just past the end of the level
line. Positive values move the label to the right (away from a right-side
label, toward a left-side one); negative values move it left. Like
`label_dy`, it is a per-state option only (default 0), and the `label_line`
connector follows it: the connector still runs from just past the end of the
level line to the shifted label anchor.

```ini
[levels 3]
# id energy width uncertainty j parity label_index jpi bottom top [options]
8  0.0    -1.0  -1.0  1  1  1  right  None  None  link=4  label_dy=-0.045  label_dx=0.02  label_line=yes
```

`--convert` writes it back as `label_dx=<number>`.

## 4 / Broken energy axis — `[figure]` setting `axis_break`

| Setting | Default | Meaning / allowed values |
| --- | --- | --- |
|  axis_break | none | `none`, or pairs of comma-separated displayed-energy values `low1, high1, low2, high2, ...`. The y axis jumps inside every `(low, high)` gap, drawn as one stacked panel per energy range, all sharing the x axis, with the spines facing each gap hidden and `//` break marks drawn, as in a classic broken-axis plot. A single pair `low, high` gives the usual two-panel break; more pairs give more breaks. |

```ini
[figure]
axis_break = none                  # default
# axis_break = 0.2, 2.4            # one break between 0.2 and 2.4 MeV
# axis_break = 0.2, 0.5, 2.4, 3.0  # two breaks: (0.2, 0.5) and (2.4, 3.0)
```

Values are in displayed units, i.e. after `reference_energy` is subtracted,
and must strictly increase (each `low` smaller than its `high`, gaps must not
overlap). Panel heights are proportional to each range's energy span. Levels,
width boxes, error bars and labels are clipped at each gap; links are the
exception — each link is drawn as one continuous straight line across the
gap(s) (a `ConnectionPatch` between the two endpoint panels), so a link
crossing a break never shows a discontinuity. No state may lie strictly
inside any gap — such inputs are rejected with an error naming the offending
line. Ticks use the usual `ticks` spacing on each panel; the gaps themselves
get no ticks. Not available in the legacy `OUTPUT FILE` format (it stays
`none`). The panels are created through a plain gridspec with height ratios
only, so `fig.tight_layout()` in `EnergyLevels.py` stays fully compatible and
does not emit the "Axes that are not compatible with tight_layout" warning.

With many breaks the individual panels can become shorter than their own
decorations (tick labels, `//` marks); real matplotlib then prints
`UserWarning: Tight layout not applied. tight_layout cannot make Axes height
small enough to accommodate all Axes decorations.` and skips the layout.
`EnergyLevels.py` handles this automatically: it retries `tight_layout` with
progressively smaller padding (1.08, 0.5, 0.2, 0.05) and, if every attempt is
refused, falls back to fixed figure margins — so the figure is always laid
out, and `break_gap` is applied afterwards either way. No input change is
needed; if you ever see that warning, the fallback has already kicked in.

## 5 / Break gap size — `[figure]` setting `break_gap`

| Setting | Default | Meaning / allowed values |
| --- | --- | --- |
|  break_gap | 0.04 | White gap between the two panels of an axis break, as a fraction of the average panel height. Must satisfy 0 <= value <= 1. Only used when `axis_break` is set. The gap is applied with `fig.subplots_adjust(hspace=...)` after `tight_layout()`, so it can be pinned small (e.g. 0.02) without triggering the tight_layout incompatibility warning. |

```ini
[figure]
axis_break = 0.2, 2.4
break_gap = 0.04    # default
# break_gap = 0.015 # tighter break, less white space between the panels
```

## 6 / Y-axis label distance — `[figure]` setting `ylabel_pad`

| Setting | Default | Meaning / allowed values |
| --- | --- | --- |
|  ylabel_pad | 4.0 | Padding between the energy-axis label and the axis (tick labels), in points. Must be >= 0. Smaller values pull `Energy (MeV)` closer to the axis; larger values push it outward. In single-panel figures it is the usual `labelpad` of `set_ylabel`; with an axis break the figure-level label is repositioned after `tight_layout()` so it hugs the axis by exactly this amount. |

```ini
[figure]
ylabel_pad = 4.0    # default (matplotlib's default labelpad)
# ylabel_pad = 1.0  # label nearly touching the tick labels
```

## 7 / Error-bar cap size — `[figure]` setting `errorbar_head`

| Setting | Default | Meaning / allowed values |
| --- | --- | --- |
|  errorbar_head | 10.0 | Size of the error-bar end caps, as a multiple of the level-line length (the same scale `width_spacing` uses for width boxes). Must be >= 0; `0` draws a plain vertical line without caps. Default 10 reproduces the previous hardcoded size. |

```ini
[figure]
errorbar_head = 10.0   # default
# errorbar_head = 4.0  # smaller caps, like in the reference figures
# errorbar_head = 0    # no caps at all
```
