from __future__ import (absolute_import, division,
                        print_function, unicode_literals)


import numpy as np
import pandas as pd
from mousestyles.path_diversity.path_features import angle_between


def compute_advanced(path_obj):
    r"""
    Returns dictionary containing several advanced features of path.

    The features are the radius, center angles, area covered by the path,
    area of the rectangle spanned by the path, and
    absolute distance between start and end points.

    Parameters
    ----------
    path_obj : pandas.DataFrame
        CX and CY must be contained.
        The length must be greater than 2.

    Returns
    -------
    radius : list
        each element is the distance between center point and
        each point in the path. The length equals to the length
        of the path_obj.

    center_angles : list
        each element is the center angle generated by 2 adjacent
        radius. The length equals to the length of the radius minus 1.

    area_cov : numpy float object
        area covered by the path.
        Computed by radius and center angles.

    area_rec : numpy float object
        area of the rectangle spanned by the path.

    abs_distance : numpy float object
        the distance between the start and end points in a path.

    Examples
    --------
    >>> movement = data.load_movement(1,2,1)
    >>> adv_features = compute_advanced(movement[5:10])
    """
    if not isinstance(path_obj, pd.core.frame.DataFrame):
        raise TypeError("path_obj must be pandas DataFrame")

    if not set(path_obj.keys()).issuperset(['x', 'y']):
        raise ValueError("the keys of path_obj must contain 'x', 'y'")

    if len(path_obj) <= 2:
        raise ValueError("path_obj must contain at least 3 rows")

    # Computes edge points
    edge_points = {'xmin': np.min(path_obj.x), 'xmax': np.max(path_obj.x),
                   'ymin': np.min(path_obj.y), 'ymax': np.max(path_obj.y)}

    # Computes area of rectangle
    area_rec = (edge_points['xmax'] - edge_points['xmin']) * \
               (edge_points['ymax'] - edge_points['ymin'])

    # Computes center point
    center = {'x': (edge_points['xmin'] + edge_points['xmax']) / 2,
              'y': (edge_points['ymin'] + edge_points['ymax']) / 2}

    # Computes radius
    indices = path_obj.index
    vectors = [path_obj.loc[i, 'x':'y'] -
               [center['x'], center['y']] for i in indices]
    radius = [np.linalg.norm(v) for v in vectors]

    # Computes center angles
    center_angles = [angle_between(list(v1), list(v2)) for
                     v1, v2 in zip(vectors[1:], vectors[:-1])]

    # Computes area covered
    zipped = zip(radius[1:], radius[:-1], center_angles)
    areas = [v1 * v2 * np.sin(theta) / 2 for v1, v2, theta in zipped]
    area_cov = sum(areas)

    # Computes distance between start and end points
    initial = path_obj.loc[path_obj.index[0], 'x':'y']
    end = path_obj.loc[path_obj.index[-1], 'x':'y']
    abs_distance = np.sqrt((end['x'] - initial['x']) ** 2 +
                           (end['y'] - initial['y']) ** 2)

    return({'radius': radius, 'center_angles': center_angles,
            'area_cov': area_cov, 'area_rec': area_rec,
            'abs_distance': abs_distance})
