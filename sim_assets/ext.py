
import numpy as np
import operator as op
from functools import reduce

def ncr(n, r):
    """n choose r"""
    r = min(r, n - r)  # This works since it's symmetric
    
    numer = reduce(op.mul, range(n, n - r, -1), 1)
    denom = reduce(op.mul, range(1, r + 1), 1)
    return numer / denom

def bernstein_poly(i, n, t):
    """
     The Bernstein polynomial of n, i as a function of t
    """
    return ncr(n, i) * (t ** (n - i)) * (1 - t)**i
    
def compute_bezier_points(points, n_times=25):
    """
        Returns a list of points that can be used to construct a bezier curve.
    """
    n_points = len(points)
    x_points, y_points = np.array([p[0] for p in points]), np.array([p[1] for p in points])

    t = np.linspace(0.0, 1.0, n_times)
    polynomial_array = np.array([bernstein_poly(i, n_points-1, t) for i in range(0, n_points)])

    x_vals, y_vals = np.dot(x_points, polynomial_array), np.dot(y_points, polynomial_array)

    return [(x, y) for x, y in zip(x_vals, y_vals)]

def colour_linear_interpolation(col_a, col_b, t):
    """
        Linearly interpolates between two colours. 
    """
    col = tuple([a + (b - a) * t for a, b in zip(col_a, col_b)])
    return col

def map_from_to(x, a, b, c, d):
    """
        Maps a value x from a-b to c-d.
    """
    return (x - a) / (b - a) * (d - c) + c