""" Construct behavior trees
"""

from __future__ import print_function, absolute_import, division

from .behavior_tree import BehaviorTree
from mousestyles.behavior import metrics


def _get_units(feature):
    """
    Look up units for `feature`.

    Parameters
    ----------
    feature : {'F', 'W', 'L'}
        The feature used. 'F' for food, 'W' for water, 'L' for locomotion.

    Returns
    -------
    units : dict
        Dictionary mapping nodes to units.
    """
    # Food is in grams, water in milligrams,
    # locomotion in meters
    unit_lookup = {'F': 'g', 'W': 'mg', 'L': 'm'}
    unit = unit_lookup[feature]
    units = {'Consumption Rate': '{}/s'.format(unit),
             'AS Prob': '',
             'Intensity': '{}/s'.format(unit),
             'Bout Rate': 'bouts/s'.format(unit),
             'Bout Size': '{}/bout'.format(unit),
             'Bout Duration': 's/bout',
             'Bout Intensity': '{}/s'.format(unit),
             'Bout Event Rate': 'events/s',
             'Event Size': '{}/event'.format(unit)}
    return units


def process_raw_intervals(feature, consumption, intervals, active_time,
                          total_time, epsilon):
    """
    Takes `total_consumption` and the data in `intervals` and
    decomposes it into a tree of behavioral summary statistics.

    Parameters
    ----------
    feature : {'F', 'W', 'L'}
        The feature used. 'F' for food, 'W' for water, 'L' for locomotion.
    consumption: float
        total consumption (food, water, or movement) in the time period
    intervals: Intervals
        Intervals object representing intervals of behavior

    active_time: float
        amount of time the mouse was active in the day

    total_time: float
        total amount of recording time in the day

    epsilon: float
        tolerance for merging events into bouts

    Returns
    -------
    behavior : BehaviorTree
        dictionary-like object representing breakdown of
        consumption into various nodes

    Examples
    --------
    >>> from mousestyles import data, intervals
    >>> ints = intervals.Intervals(data.load_intervals('AS'))
    >>> results = process_raw_intervals(1000, ints, 1)
    """

    units = _get_units(feature)
    tree = BehaviorTree(['Consumption Rate',
                         ['AS Prob',
                          ['Intensity',
                           ['Bout Rate',
                            ['Bout Size',
                             ['Bout Duration',
                              ['Bout Intensity',
                               ['Bout Event Rate',
                                'Event Size']]]]]]]], units=units)
    bout_intervals = metrics.create_collapsed_intervals(intervals, epsilon)
    as_probability = active_time / total_time
    tree['Consumption Rate'] = consumption / total_time
    tree['AS Prob'] = as_probability
    tree['Intensity'] = tree['Consumption Rate'] / as_probability
    num_bouts = bout_intervals.num()
    tree['Bout Rate'] = num_bouts / active_time
    tree['Bout Size'] = tree['Intensity'] / tree['Bout Rate']
    tree['Bout Duration'] = bout_intervals.measure() / num_bouts
    tree['Bout Intensity'] = tree['Bout Size'] / tree['Bout Duration']
    tree['Event Size'] = consumption / intervals.num()
    tree['Bout Event Rate'] = tree['Bout Intensity'] / tree['Event Size']

    return tree


def compute_tree(feature, strain, mouse, day, epsilon=1):
    """
    Compute and return a tree decomposition of a feature for a single mouse-day

    Parameters
    ----------
    feature : {'F', 'W', 'L'}
        The feature used. 'F' for food, 'W' for water, 'L' for locomotion.
    strain : int
        Integer representing the strain of the mouse
    mouse : int
        Integer representing the specific mouse
    day : int
        Integer representing the day to produce the metrics for
    epsilon: float, optional
        tolerance for merging events into bouts

    Returns
    -------
    behavior : BehaviorTree
        dictionary-like object representing breakdown of
        consumption into various nodes
    """
    intervals = metrics.create_intervals(feature, strain, mouse, day)
    active_time = metrics.active_time(strain, mouse, day)
    total_time = metrics.total_time(strain, mouse, day)
    consumption = metrics.total_amount(strain, mouse, day, feature)
    return process_raw_intervals(feature, consumption, intervals, active_time,
                                 total_time, epsilon)
