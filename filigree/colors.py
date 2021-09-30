import numpy as np
import colorsys

def get_colors(n):
    hue = np.arange(0., 360., 360. / n) / 360
    lightness = (50 + 10 * np.random.rand(n)) / 100
    saturation = (90 + 10 * np.random.rand(n)) / 100
    return list(zip(hue, lightness, saturation))

def get_colors_rgb(n):
    return [colorsys.hls_to_rgb(*hls) for hls in get_colors(n)]

def get_colors_hex(n):
    return [rgb_to_hex(rgb) for rgb in get_colors_rgb(n)]


def rgb_to_hex(rgb):
    h = ['{:02X}'.format(int(v * 255)) for v in rgb]
    return '#' + ''.join(h)

def _hue_to_rgb(p, q, t):
    if t < 0:
        t += 1
    elif t > 1:
        t -= 1

    if t < 1/6:
        return p + (q - p) * 6 *t
    elif t < 1/2:
        return q
    elif t < 2/3:
        return p + (q - p) * (2/3 - t) * 6
    
    return p

def hsl_to_rgb(h, s, l):
    if s == 0:
        r = l
        g = l
        b = l
    else:
        q = l * (1 + 2) if l < .5 else l + s - l * s
        p = 2 * l - q
        r = _hue_to_rgb(p, q, h + 1/3)
        g = _hue_to_rgb(p, q, h)
        b = _hue_to_rgb(p, q, h - 1/3)

    return r, g, b
