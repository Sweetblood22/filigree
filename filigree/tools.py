import numpy as np
from filigree.metrics import Quantile

qmedian = Quantile(0.5, 'qmedian')

def frequency(x):
    freq = {}
    
    for _ in x:
        freq[_] = freq[_] + 1 if _ in freq else 1
        
    return freq

def calculate_quantiles(df, by, col, quantiles=(.25, .5, .75)):
    quants = {f'q_{q * 1000:04.0f}': (col, Quantile(q)) for q in quantiles}
    #return quants
    return (df.groupby(by).agg(qmin=(col, min),
                               qmax=(col, max),
                               qmedian=(col, qmedian),
                               mu=(col, np.mean),
                               n_records=(col, len),
                               **quants
                              )
           )

def plural_multi_agg(dg, **kwargs):
    """
    
        Args:
            dg, pd.Grouped DataFrame object
            kwargs: <new_col_name>=method(accesses columns in group dg) 
                   similar to the .assign method on DataFrame objects
    """
    for i, (new_col, method) in enumerate(kwargs.items()):
        if i == 0:
            df = dg.apply(method).to_frame()
            df.columns = [new_col]
        df[new_col] = dg.apply(method)
        
    return df
