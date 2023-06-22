import numpy as np
from scipy.optimize import curve_fit


def gauss(x, *p):
    A, mu, sigma = p
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))


def mean(x):
    return np.mean(x)


def median(x):
    return np.median(x)


def vmax(x):
    return np.max(x)


def vmin(x):
    return np.min(x)


def prepareGauss(x, p0 = [1., 0., 1.]):
    hist, edges = np.histogram(x, density=True)
    centres = (edges[:-1] + edges[1:]) / 2

    cfs, variation = curve_fit(gauss, centres, hist, p0=p0)
    errs = np.sqrt(np.diag(variation))

    #hist_fit = gauss(centres, *cfs)

    return (cfs, errs, )


def polyFit(x, y, order=3):
    return np.polyfit(x, y, order)


def preparePolyFit(x, y, order=3):
    z = polyFit(x, y, order)
    return np.poly1d(z)