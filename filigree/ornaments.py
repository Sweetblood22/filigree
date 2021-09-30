import numpy as np
from copy import copy

from bokeh.layouts import Column, Row, Spacer
from bokeh.plotting import Figure
from bokeh.models import Circle, HoverTool, ColumnDataSource, Range1d

from filigree.colors import get_colors_hex


def color_plot(colors, width=720, height=180):
    x = np.array([0, 1, 1, 0])
    y = np.array([0, 0, 1, 1])
    f = figure(width=width, height=height)
    src = ColumnDataSource(data={'color': colors,
                                 'x': [x + i for i in range(len(colors))],
                                 'y': [y] * len(colors)})
    
    f.patches('x', 'y', color='color', source=src)
    return f


def scatter_matrix(df, xcols=None, ycols=None, width=None, height=None, margin=0, all_range=None, 
                   source=None, full=False, colors=None, include_hist=False, tooltips=None, **sckwargs):
    
    if xcols is None and ycols is not None:
        ycols = copy(ycols)
        xcols = copy(ycols)
    elif xcols is not None and ycols is None:
        xcols = copy(xcols)
        ycols = copy(xcols)
    elif xcols is None and ycols is None:
        _dt = df.dtypes
        xcols = _dt.index[_dt.apply(lambda t: 'int' in t.name or 'float' in t.name)].to_series().tolist()
        ycols = copy(xcols)
    else:
        xcols = copy(xcols)
        ycols = copy(ycols)
    
    cols = set(xcols).union(set(ycols))
    
    if tooltips is not None and tooltips == 'auto':
        tooltips = [(col, f"@{col}") for col in cols]
    
    colors = dict(zip(cols, random_rgb(len(cols))))
    xcolors = mix_colors({c: colors[c] for c in xcols},
                         {c: colors[c] for c in ycols})
    
    ncols = len(xcols)
    nrows = len(ycols)
    
    # TODO something more to handle sizing
    width = 240 if width is None else width
    height = 180 if height is None else height
    
    if source is None or any([ncols > 2, nrows > 2]):
        fsource = ColumnDataSource(data={c: df[c].values for c in df.columns})

    if colors is None:
        colors = dict(zip(cols, random_rgb(len(cols))))
    elif type(colors) is str:
        color = hex_to_rgb(colors)
        colors = {col: color for col in cols}
        
    sgrey = np.array([234] * 3) / 255
        
    rows = []
    for i, ycol in enumerate(ycols):  # range(nrows):
        row = []
        for j, xcol in enumerate(xcols):  # range(ncols):
            #if i == j:
            #    continue
            if i >= j or full:
                scolor = mix_colors(colors[xcol], colors[ycol])
                light_color = rgb_to_hex(scolor * sgrey) # ** 4 ** md)
                color = rgb_to_hex(scolor)
                g = Figure(width=width, height=height, tools='box_select,wheel_zoom', toolbar_location=None)
                glyph = g.circle(x=xcol, y=ycol, source=fsource, color=color, **sckwargs)
                glyph.selection_glyph = Circle(fill_alpha=np.sqrt(sckwargs.get('alpha', 1)), fill_color=color, line_color=None)
                glyph.nonselection_glyph = Circle(fill_alpha=1, fill_color='#EAEAEA', line_color=light_color,
                                                  line_alpha=0.0) #, line_width=sckwargs.get('size', 8)/4)
                g.add_tools(HoverTool(tooltips=tooltips))

                g.xaxis.visible = False
                g.yaxis.visible = False
                if all_range is not None:
                    g.y_range = Range1d(*all_range)
                    g.x_range = Range1d(*all_range)
                row.append(g)
            else:
                row.append(Spacer(width=width))
        rows.append(Row(*row))

    return Column(*rows)

#TODO # method to plot pairwise feature slice metrics of f(y, yhat) for analyzing ML model performance
# possible default heatmaps r2_score, accuracy_score/f1_score, deviation from fitted normal distribution
