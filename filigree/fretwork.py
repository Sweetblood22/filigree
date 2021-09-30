import numpy as np
from tools import calculate_quantiles, plural_multi_agg


def qhist(data, centered=True, width=.8, transform=None):
    """Create a histogram with bins located as specific quantiles in data

        Args:
            data, pandas.DataFrame: output of tools.calculate_quantiles method; must have
                     multiple quantile columns labeled starting with 'q_0'
            centered bool: default True. boxes start from [-.5, .5] rather than [0, 1]
                     making the histogram symmetric around it's origin 
            width numeric: greater than 0, how wide to scale histogram
            transform: method to scale height (sqrt to see detail of distribution 
                     tails when plotting small multiples)

        return: 
            tuple of list of arrays (xs, ys), sub elements are array of len 4 plotting
                 corners of rectagles for each bin of histogram (use bokeh.figure.patches(xs, ys))
    """
    assert width > 0
    hx = np.array([0.0, 0.0, 1.0, 1.0]) # patches don't need to be closed
    hy = np.array([0.0, 1.0, 1.0, 0.0]) - (0.5 * centered)
    qcols = sorted([_ for _ in data.keys() if _.startswith('q_0')])
    qs = [int(_[-4:]) / 1000 for _ in qcols]
    
    hxs = []
    hys = []
    scls = []
    for i, (s, e) in enumerate(zip(qcols[:-1], qcols[1:])):
        qd = qs[i + 1] - qs[i]
        p = (data[e] - data[s])
        scls.append(qd / p)
        hxs.append(hx * p + data[s])
        hys.append(hy * scls[-1])
        
    return hxs, [_ / max(scls) * width for _ in hys]


def _draw_box_plot(center=0, width=1, qmin=-2, q1=-0.5, q2=0.0, q3=0.5, qmax=2, mu=0.0, n_records=1337, iqr=1.0, lower=-2, upper=2):
    """Draw a box plot with input measurements (draw using bokeh.figure.line or many in a list with multi_line)

        Args:
            center, numeric: where on x_axis to cetner boxplot
            width, numeric: positive, how wide to scale boxplot
            qmin, numeric: lower edge of whisker if more than lower
            q1, numeric: 1st quartile
            q2, numeric: the median, unused
            q3, numeric: 3rd quartile
            qmax, numeric: upper edge of whisker if less than upper
            mu, numeric: the mean, unused
            n_records, int: unused
            iqr, numeric: inner quartile range, unused
            lower, numeric: lower edge of whisker
            upper, numeric: upper edge of whisker

        return: tuple (np.array(xcoordinates), np.array(ycoordinates))
    """
    q0 = max(lower, qmin)
    q4 = min(upper, qmax)
    y = np.array([q1, q1, q3, q3, q1, np.nan, q2, q2, np.nan, q0, q1, np.nan, q3, q4, np.nan, q0, q0, np.nan, q4, q4]) 
    x = np.array([0, 1, 1, 0, 0, np.nan, 0, 1, np.nan, 0.5, 0.5, np.nan, 0.5, 0.5, np.nan, 0, 1, np.nan, 0, 1]) - 0.5
    
    return x * width + center, y

def calculate_boxes(df, by, col, outlier_r=1.5):
    
    return (plural_multi_agg(df.groupby(by),
                                qmin=lambda x: x[col].min(),
                                q1=lambda x: x[col].quantile(.25),
                                q2=lambda x: x[col].quantile(.5),
                                q3=lambda x: x[col].quantile(.75),
                                qmax=lambda x: x[col].max(),
                                mu=lambda x: x[col].mean(),
                                n_records=lambda x: len(x))
                .assign(iqr=lambda x: x.q3 - x.q1,
                        lower=lambda x: x.q1 - x.iqr * outlier_r,
                        upper=lambda x: x.q3 + x.iqr * outlier_r
                       )
             )

def is_outlier(df, by, col, outlier_r=1.5, sf=None):
    if sf is None:
        sf = calculate_boxes(df, by, col, outlier_r=outlier_r)
    return (df[[by, col]]
              .join(sf[['lower', 'upper']], on=by)
              .assign(is_low=lambda x: (x[col] < x.lower),
                      is_high=lambda x: (x.upper < x[col]),
                      is_outlier=lambda x: x.is_low | x.is_high)
              .drop(columns=['lower', 'upper'])
           )
    

def create_square_patches(x, y, z, width=1, palette=Cividis256):
    px = np.array([[0, 1, 1, 0]])
    py = np.array([[0, 0, 1, 1]])
    
    cc = np.array(palette)[((z * len(palette) - 1) // max(z)).astype(int)]
    
    return np.array(x).reshape(-1, 1) + px * width, np.array(y).reshape(-1, 1) + py * width, cc
