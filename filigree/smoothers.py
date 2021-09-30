import numpy as np
from scipy.stats import distributions
#from filigree.metrics import SigmaOffset, Quantile

def QuantileSmoother(x, y, q, window=None):
    return MetricSmoother(x, y, Quantile(q), window=window)


class ABCSmoother(object):
    def __init__(self, x, y, window=None):
        self._x = x
        self._y = y
        self.window = window
        
    @property
    def window(self):
        return self._window
    
    @window.setter
    def window(self, window):
        if window is None:
            _x = np.sort(self._x)
            max_d = max(_x[1:] - _x[:-1])
            x_range = _x[-1] - _x[0]
            self._window = max(x_range / 20, 1.05 * max_d)
        else:
            self._window = window

class MetricSmoother(ABCSmoother):
    def __init__(self, x, y, metric, window=None):
        super().__init__(x, y, window=window)
        self._metric = metric
            
    def __call__(self, x):
        y = x * 0
        for i, x_ in enumerate(x):
            msk = np.abs(x_ - self._x) < self.window
            y[i] = self._metric(self._y[msk])
        
        return y

    
class NormalSmoother(ABCSmoother):
    def __init__(self, x, y, z_score=0, window=None):
        super().__init__(x, y, window=window)
    
    def __call__(self, x):
        _w = distributions.norm.pdf((x.reshape(1, -1) - self._x.reshape(-1, 1)) / self.window)
        _w = _w / _w.sum(axis=0, keepdims=True)
        
        
        return np.dot(self._y.reshape(1, -1), _w).ravel() #, _coun
