import numpy as np
from scipy.interpolate import make_interp_spline
from scipy.special import comb

def bezier_curve(points, num=100):
    n = len(points) - 1
    t = np.linspace(0, 1, num)
    curve = np.zeros((num, 2))
    for i in range(n + 1):
        binomial = comb(n, i)
        curve += binomial * ((1 - t) ** (n - i))[:, None] * (t ** i)[:, None] * points[i][None, :]

    return curve

def bspline_curve(points, num=100):
    points = np.array(points)
    x = points[:, 0]
    y = points[:, 1]
    t = np.linspace(0, 1, num)
    try:
        splx = make_interp_spline(np.linspace(0, 1, len(points)), x, k=3)
        sply = make_interp_spline(np.linspace(0, 1, len(points)), y, k=3)
        return np.vstack((splx(t), sply(t))).T
    except Exception:
        return points  # fallback

def lagrange_interpolation(points, num=100):
    points = np.array(points)
    x_vals = np.linspace(points[0, 0], points[-1, 0], num)
    y_vals = np.zeros_like(x_vals)
    for i in range(len(points)):
        xi, yi = points[i]
        Li = np.ones_like(x_vals)
        for j in range(len(points)):
            if i != j:
                xj = points[j][0]
                Li *= (x_vals - xj) / (xi - xj)
        y_vals += yi * Li
    return np.vstack((x_vals, y_vals)).T