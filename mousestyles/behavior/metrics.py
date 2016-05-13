"""Metrics for behavior"""

from __future__ import print_function, absolute_import, division

from mousestyles import data
from mousestyles import intervals


def _select_strain_mouse_day_in_data_frame(df, strain, mouse, day):
    """Returns a subsetted data frame selecting
    rows with a specified strain, mouse, and day.

    Parameters
    ----------
    df : pandas.DataFrame
        A dataframe with columns named 'strain', 'mouse', and 'day'
    strain : int
    mouse : int
    day : int

    Returns
    -------
    selected_rows : pandas.DataFrame
        A dataframe with rows of the strain, mouse, and day
        given.
    """
    return df[(df['strain'] == strain) & (df['mouse'] == mouse) &
              (df['day'] == day)]


def total_time(strain, mouse, day):
    """Returns the total amount of time recorded for a certain mouse-day.

    Parameters
    ----------
    strain : int
    mouse : int
    day : int

    Returns
    -------
    The total amount of time in seconds of the specified mouse-day.
    """
    start_seconds, end_seconds = data.load_start_time_end_time(
        strain, mouse, day)
    return end_seconds - start_seconds


def active_time(strain, mouse, day):
    """Returns the total amount of active time recorded for a certain mouse-day.

    Parameters
    ----------
    strain : int
    mouse : int
    day : int

    Returns
    -------
    The total amount of active time in seconds for the specified mouse-day.
    """
    return create_intervals('AS', strain, mouse, day).measure()


def total_amount(strain, mouse, day, feature):
    """Returns the total amount consumed/moved for one of the following features:
     food ("F"), water ("W"), and locomotion ("L").

    Parameters
    ----------
    strain : int
    mouse : int
    day : int
    feature : {'F', 'W', 'L'}
        The feature used. 'F' for food, 'W' for water, 'L' for locomotion.

    Returns
    -------
    The total amount consumed/moved for the given feature in the mouse-day.
    """
    df = data.load_all_features()

    df = _select_strain_mouse_day_in_data_frame(df, strain, mouse, day)

    if df.shape[0] == 0:
        raise ValueError(
            "No consumption data available for specified mouse-day.")

    feature_names = {'W': 'Water', 'F': 'Food', 'L': 'Distance'}
    if feature not in feature_names.keys():
        raise ValueError("Feature must be one of :" + str(set(feature_names
                                                              .keys())))

    return df[feature_names[feature]].sum()


def create_intervals(activity_type, strain, mouse, day):
    r"""Returns an interval object on a certain mouse-strain-day
    for a given activity type.

    Parameters
    ----------
    activity_type : str
        String specifying activity type {"AS", "F", "IS", "M_AS", "M_IS", "W"}
    strain : int
        Integer representing the strain of the mouse
    mouse : int
        Integer representing the specific mouse
    day : int
        Integer representing the day to produce the metrics for
    bout_threshold: : float
        Float representing the time threshold to use for collapsing separate
        events into bouts

    Returns
    -------
    An intervals object `intervals` for the given activity type and
    mouse-strain-day within a bout threshold

    Examples
    --------

    >>> ints=behavior.create_intervals(activity_type = 'F', strain = 0
                                       , mouse = 0, day = 0
                                       , bout_threshold = 0.001)
    >>> print(sum(ints))

    """

    # Load intervals by activity type
    l_ints = data.load_intervals(activity_type)

    # Subset to M*2 array of  (start, stop) intervals based on
    # specific mouse, strain and day
    l_ints = _select_strain_mouse_day_in_data_frame(l_ints, strain, mouse, day)
    l_ints = l_ints[['start', 'stop']]

    # Create and return the intervals object
    return intervals.Intervals(l_ints)


def create_collapsed_intervals(intervals, bout_threshold):
    r"""Returns a collapsed interval object (within a
    given threshold) on a certain mouse-strain-day for a given activity type.

    Parameters
    ----------
    intervals : interval object on a certain mouse-strain-day
    for a given activity type
    bout_threshold: : float
        Float representing the time threshold to use for collapsing separate
        events into bouts

    Returns
    -------
    An intervals object `intervals` for the given activity type and
    mouse-strain-day within a bout threshold

    Examples
    --------
    >>> ints=behavior.create_intervals('F', strain = 0
                                       , mouse = 0, day = 0
                                       , bout_threshold = 0.001)
    >>> collapsed_ints=behavior.create_collapsed_intervals(intervals = ints
                                                    , bout_threshold = 0.001)
    >>> print(collapsed_ints)

    """

    # Create and return the collapsed intervals object.
    # Need to copy the original intervals object first else the collapse method
    # will overwrite it as a collapsed interval object
    return intervals.copy().connect_gaps(eps=bout_threshold)
