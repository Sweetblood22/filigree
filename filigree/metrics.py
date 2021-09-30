import numpy as np
import re

class ABCMetric(object):
    def __init__(self, *params, **kwargs):
        self._acronym = ''.join(c.lower() for c in self.__class__.__name__ if 65 <= ord(c) and ord(c) <= 90)
        self.params = params
        # TODO name override
        #self.set_name(kwargs.pop('name': None))

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        assert len(params) < 3
        if len(params) > 1:
            self._tmplt = "{name}({p0}to{p1})"
        else:
            self._tmplt = "{name}({p0})"

        self._params = params
        self._fmtd = {f"p{i}": p for i, p in enumerate(self.params)}

    def __str__(self):
        return self._tmplt.format(name=self.__class__.__name__, **self._fmtd).replace('to', ', ')

    def __repr__(self):
        return self.__str__()
    
    @property
    def __name__(self):
        name = self._tmplt.format(name=self._acronym, **self._fmtd)

        return re.sub('[()]', '', re.sub('[.-]', '_', name))


class SigmaOffset(ABCMetric):
    def __init__(self, sigma, name=None):
        assert np.abs(sigma) < 4
        super().__init__(sigma, name=name)
       
    @property
    def sigma(self):
        return self.params[0]

    def __call__(self, s):
        return np.mean(s) + self.sigma * np.std(s)
    
class SigmaRadius(ABCMetric):
    def __init__(self, sigmar, name=None):
        assert 0 < sigmar and sigmar < 4
        super().__init__(sigmar, name=name)
        
        self.get_low_offset = SigmaOffset(-self.sigmar)
        self.get_high_offset = SigmaOffset(self.sigmar)
        
    @property
    def sigmar(self):
        return self.params[0]
    
    def __call__(self, s):
        return self.get_high_offset(s) - self.get_low_offset(s)
    
    
class Quantile(ABCMetric):
    def __init__(self, q, name=None):
        assert 0.0 < q and q < 1.0
        super().__init__(q, name=name)
        
    @property
    def q(self):
        return self.params[0]
    
    def __call__(self, s):
        return np.quantile(s, self.q)
    
class QuantileRange(ABCMetric):
    def __init__(self, qlow, qhigh, name=None):
        assert qlow < qhigh
        assert 0.0 < qlow
        assert qhigh < 1.0
        super().__init__(qlow, qhigh, name=name)
        
        self.get_low_quantile = Quantile(self.params[0])
        self.get_high_quantile = Quantile(self.params[1])
        
    @property
    def qlow(self):
        return self.params[0]
        
    @property
    def qhigh(self):
        return self.params[1]
    
    def __call__(self, s):
        return self.get_high_quantile(s) - self.get_low_quantile(s)
    
class PortionInBounds(ABCMetric):
    def __init__(self, low, high, name=None):
        assert low < high
        super().__init__(low, high, name=name)
        
    @property
    def low(self):
        return self.params[0]
    
    @property
    def high(self):
        return self.params[1]
    
    def __call__(self, s):
        s = np.array(s)
        return ((self.low <= s) & (s <= self.high)).sum() / len(s)
    
class PortionInRadius(ABCMetric):
    def __init__(self, r, name=None):
        assert 0 < r
        super().__init__(r)
        
    @property
    def r(self):
        return self.params[0]
    
    def __call__(self, s):
        s = np.array(s)
        return (np.abs(s) <= self.r).sum() / len(s)
