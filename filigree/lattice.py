import numpy as np
from tools import frequency, calculate_quantiles

def box_plots(df, by, col, outlier_r=1.5, width=None, center_map=None, jitter=True):
    
    sf = calculate_boxes(df, by, col, outlier_r=outlier_r)
    
    width = 0.8 if width is None else width
    
    if center_map is None:
        if 'int' not in df[by].dtype.name:
            center_map = {g: i for i, g in enumerate(sorted(list(set(df[by]))))}
        else:
            center_map = {g: g for g in set(df[by])}
    
    
    
    df_ = is_outlier(df, by, col, outlier_r=outlier_r, sf=sf)
    
    bxs = []
    bys = []
    nlo = []
    nho = []
    plo = []
    pho = []
    nrs = []
    
    lx = np.array([-.5, 0.5])
    ly = np.array([0, 0])
    mxs = []
    mys = []
    
    groups = []
    for g, dat in sf.iterrows():
        _x, _y = _draw_box_plot(center=center_map[g], width=width, **dat.to_dict())
        bxs.append(_x)
        bys.append(_y)
        mxs.append(lx * width + center_map[g])
        mys.append(ly + dat['mu'])
        nlo.append(df_.is_low.sum())
        nho.append(df_.is_high.sum())
        plo.append(df_.is_low.mean())
        pho.append(df_.is_high.mean())
        nrs.append(dat['n_records'])
        groups.append(g)
    
    oxs = df_.loc[df_.is_outlier, by].apply(lambda g: center_map[g]).values + width * (np.random.uniform(size=df_.is_outlier.sum()) * 0.8 - 0.4)
    ogs = df_.loc[df_.is_outlier, by].values
    oys = df_.loc[df_.is_outlier, col].values

    center_map = {v: k for k, v in center_map.items()}
    
    return {'boxes': {'x': bxs, 'y': bys, 'group': groups,
                      'nlo': nlo, 'nho': nho, 'plo': plo, 'pho': pho, 'n': nrs},
            'outliers': {'x': oxs, 'y': oys, 'group': ogs},
            'means': {'x': mxs, 'y': mys, 'group': groups}}

def qhistograms(df, by, col, quantiles=np.arange(0.25, .8, .05), centered=True, 
                absolute=False, center_map=None, width=.8, transform=None):
    """Create multiple quantile histograms by groups of a column from a pandas.DataFrame

        Args:
            df, pandas.DataFrame: must contain columns passed in arguments `by` and `col`
            by, str: column of `df` which to group data from creating histograms
            col, str: column of data in `df` to create histograms
            quantiles, iterable(float): quantiles marking bin edges for histogram must satisfy 0 < q < 1
            centered, bool: default, True, boxes start from [-.5, .5] rather than [0, 1]
                     making the histogram symmetric around it's origin
            absolute, bool: default False, histogram plots density, True will plot frequency
            center_map, dict: Keys with values of group labels in column `by` and numeric 
                     values of where to center histogram on x_axis
            width, numeric: how wide to scale histogram
            transform: method to scale height (sqrt to see detail of distribution 
                     tails when plotting small multiples)

        Return:
            dict with structure to plot histograms using ColumnDataSource
    """
    assert len(quantiles) > 2
    quantiles = np.sort(quantiles)
    
    qt = calculate_quantiles(df, by, col, quantiles=quantiles)
    tot_records = qt.n_records.sum()
    
    qcols = sorted([_ for _ in qt.columns if _.startswith('q_0')])
    
    
    if center_map is None:
        if 'int' not in df[by].dtype.name:
            center_map = {g: i for i, g in enumerate(sorted(list(set(df[by]))))}
        else:
            center_map = {g: g for g in set(df[by])}
    
    mx = (np.array([0, 1]) - (0.5 * centered)) * width
    my = np.array([0, 0])
    
    hxs = []
    hys = []
    nrs = []
    lows = []
    upps = []
    group = []
    names = []
    mxs = []
    mys = []
    qp = []
    
    for g, dat in qt.iterrows():
        # rotates hx  & hy to make verticle graphs
        hy, hx = qhist(dat, centered=centered)
        hxs += [_ + center_map[g] for _ in hx]
        hys += hy
        lows += [min(_) for _ in hy]
        upps += [max(_) for _ in hy]
        group += [g] * len(hy)
        names += [f"{l * 100:4.1f}-{u * 100:4.1f}" for l, u in zip(quantiles[:-1], quantiles[1:])]
        nrs += ((quantiles[1:] - quantiles[:-1]) * dat['n_records']).astype(int).tolist()
        
        mxs.append(mx + center_map[g])
        mys.append(my + dat['qmedian'])
        
    return {'histograms': {'x': hxs,
                           'y': hys,
                           'lower': lows,
                           'upper': upps,
                           'g': group,
                           'n': nrs,
                           'name': names
                          },
            'medians': {'x': mxs,
                        'y': mys}
           }

def histogram(s, bins=None):
    """output (freq, bins, cts, width)
    """
    freq, bins = np.histogram(s, bins=bins)
    cts = (bins[1:] + bins[:-1]) / 2
    width = bins[1] - bins[2]
    
    return {'histogram': {'freq': freq,
                          'bin_edges': bins, 
                          'centers': cts,
                          'width': width
                          }
           }


def histogram2d(x, y, bins, group_largest=False, colors=Cividis256):
    """Create plot data structure of 2d histogram

        Args:
            x,
            y,
            bins, tuple(iterable),
            group_largest bool,

    """
    H, xedges, yedges = np.histogram2d(df.hour_of_day, df.residuals, bins=bins)
    
    
    Hn = H / H.max()
    Hp = H / len(df)
    Hci = (Hn * 255).astype(int)
    
    freq = frequency(Hci.ravel())
    mode = max(freq, key=lambda s: freq[s])
    mode_p = freq[mode] / Hci.size
    xw = xedges[1] - xedges[0]
    yw = yedges[1] - yedges[0]
    patx = np.array([0, 1, 1, 0]) * xw
    paty = np.array([0, 0, 1, 1]) * yw
    
    if group_largest:

        xs = [np.array([0, 1, 1, 0]) * (xedges[-1] - xedges[0]) + xedges[0]]
        ys = [np.array([0, 0, 1, 1]) * (yedges[-1] - yedges[0]) + yedges[0]]
        cs = [colors[mode]]
        ns = [mode]
        ps = [mode / len(df)]
        alps = [mode / H.max()]
    else:

        xs = []
        ys = []
        cs = []
        ns = []
        ps = []
        alps = []
        
    for i in range(Hci.shape[0]):
        for j in range(Hci.shape[1]):
            if group_largest and Hci[i, j] == mode:
                continue
            xs.append(patx + xedges[i])
            ys.append(paty + yedges[j])
            cs.append(colors[Hci[i, j]])
            ns.append(H[i, j])
            ps.append(Hp[i, j])
            alps.append(Hn[i, j])
            
    return {'histogram2d': {'x': xs,
                            'y': ys,
                            'color': cs,
                            'frequency': ns,
                            'density': ps,
                            'alpha': alps
                           }
           }

