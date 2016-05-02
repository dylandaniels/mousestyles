"""Test behavior functions
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pytest

from mousestyles import behavior
from mousestyles import data
from mousestyles import intervals

from collections import defaultdict
import numpy as np


def test_create_intervals1():

    # Checking intervals are being correctly loaded for a particular
    # activity type and mouse-day

    # More specifically this is testing 'Food' Consumption
    # for strain=0, mouse=0, day=0
    load_ints1 = behavior.create_intervals(
        'F', strain=0, mouse=0, day=0)

    # Calculate the sum of the loaded intervals
    ints1_sum = sum(load_ints1)

    # We now do the above calculations using a manual query
    l_ints_manual = data.load_intervals('F')
    l_ints_manual = l_ints_manual.query('strain == 0 and mouse == 0 and \
                                         day == 0')[['start', 'stop']]
    ints_manual = intervals.Intervals(l_ints_manual)
    ints_manual_sum = sum(ints_manual)

    # Check that the sum of total values from manual query and
    # function output match for every value
    assert (ints1_sum == ints_manual_sum).all()


def test_create_intervals2():

    # Checking intervals are being correctly loaded for a particular
    # activity type and mouse-day

    # More specifically this is testing 'Water' Consumption
    # for strain=0, mouse=1, day=1
    load_ints1 = behavior.create_intervals(
        'W', strain=0, mouse=1, day=1)

    # Calculate the sum of the loaded intervals
    ints1_sum = sum(load_ints1)

    # We now do the above calculations using a manual query
    l_ints_manual = data.load_intervals('W')
    l_ints_manual = l_ints_manual.query('strain == 0 and mouse == 1 and \
                                         day == 1')[['start', 'stop']]
    ints_manual = intervals.Intervals(l_ints_manual)
    ints_manual_sum = sum(ints_manual)

    # Check that the sum of total values from manual query and
    # function output match for every value
    assert (ints1_sum == ints_manual_sum).all()


def test_create_collapse_intervals1():

    # Checking intervals are being correctly loaded for a particular
    # activity type and mouse-day

    # More specifically this is testing 'Food' Consumption
    # for strain=0, mouse=0, day=0
    load_ints1 = behavior.create_intervals(
        'F', strain=0, mouse=0, day=0)

    # Collapse the intervals within a given threshold
    cp = behavior.create_collapsed_intervals(load_ints1, bout_threshold=0.001)

    # Calculate the sum of the loaded intervals
    ints1_sum_collapsed = sum(cp)

    # We now do the above calculations using a manual query
    l_ints_manual = data.load_intervals('F')
    l_ints_manual = l_ints_manual.query('strain == 0 and mouse == 0 and \
                                         day == 0')[['start', 'stop']]

    ints_manual = intervals.Intervals(l_ints_manual)

    # Collapse the intervals within a given threshold
    ints_man_collapsed = ints_manual.copy().connect_gaps(eps=0.001)
    ints_man_sum_collapsed = sum(ints_man_collapsed)

    # Check that the sum of total values from manual query and
    # function output match for every value
    assert (ints1_sum_collapsed == ints_man_sum_collapsed).all()


def dicts_equal(d1, d2):
    return set(d1.items()) == set(d2.items())


def test_init_tree():
    tree = behavior.BehaviorTree(['Consumption',
                                  ['AS Prob', 'Intensity']])
    tree['Consumption'] = 5
    tree['AS Prob'] = 1
    tree['Intensity'] = 2
    assert dicts_equal(tree.contents,
                       defaultdict(float, {'AS Prob': 1,
                                           'Consumption': 5,
                                           'Intensity': 2}))
    assert tree.structure == ['Consumption', ['AS Prob', 'Intensity']]


def test_copy_tree():
    tree = behavior.BehaviorTree(['Consumption'], {'Consumption': 100})
    tree2 = tree.copy()
    assert tree.structure == tree2.structure
    assert dicts_equal(tree.contents, tree2.contents)


def test_create_intervals():

    # Checking intervals are being correctly loaded for a particular
    # activity type and mouse-day
    load_ints1 = behavior.create_intervals(
        'F', strain=0, mouse=0, day=0, bout_threshold=0.001)

    # Calculate the sum of the loaded intervals
    ints1_sum = sum(load_ints1)

    # We now do the above calculations using a manual query
    l_ints_manual = data.load_intervals('F')
    l_ints_manual = l_ints_manual.query('strain == 0 and mouse == 0 and \
                                         day == 0')[['start', 'stop']]
    ints_manual = intervals.Intervals(l_ints_manual)
    ints_manual_sum = sum(ints_manual)

    assert ints1_sum.all() == ints_manual_sum.all()


def test_print_tree():
    tree_no_structure = behavior.BehaviorTree(contents={'Consumption': 100})
    assert str(tree_no_structure) == str({'Consumption': 100})
    tree = behavior.BehaviorTree(['Consumption', ['AS Prob']],
                                 {'Consumption': 100,
                                  'AS Prob': 50.0})
    assert str(tree) == '\nConsumption: 100.000000 \n     AS Prob: 50.000000 '


def test_tree_getitem():
    tree_empty = behavior.BehaviorTree()
    assert tree_empty['a'] == 0.0
    tree2 = behavior.BehaviorTree(contents={'a': 5})
    with pytest.raises(KeyError) as excinfo:
        tree2['b']
    assert excinfo.value.args[0] == 'b'
    tree_list = behavior.BehaviorTree(contents=defaultdict(list))
    assert tree_list['a'] == []


def test_tree_setitem():
    tree_empty = behavior.BehaviorTree()
    tree_empty['a'] = 10
    assert tree_empty['a'] == 10
    tree_empty['b'] += 5
    assert tree_empty['b'] == 5
    tree_list = behavior.BehaviorTree(contents=defaultdict(list))
    tree_list['a'].append(5)
    assert tree_list['a'] == [5]


def test_tree_iter():
    tree = behavior.BehaviorTree(contents={'Consumption': 100})
    # should give back same set of keys
    assert set(iter(tree)) == set(iter(tree.contents))


def test_display_tree():
    tree = behavior.BehaviorTree('Consumption')
    assert tree._display_tree() == "\nConsumption: 0.000000 "
    assert tree._display_tree(1) == "\n     Consumption: 0.000000 "
    tree = behavior.BehaviorTree('Consumption', units={'Consumption': 'g'})
    assert tree._display_tree() == "\nConsumption: 0.000000 g"
    assert tree._display_tree(1) == "\n     Consumption: 0.000000 g"


def test_tree_merge():
    structure = ['Consumption',
                 ['AS Prob', 'Intensity']]
    tree1 = behavior.BehaviorTree(structure,
                                  {'AS Prob': 1,
                                   'Consumption': 5,
                                   'Intensity': 2})
    tree2 = behavior.BehaviorTree(structure,
                                  {'AS Prob': 1,
                                   'Consumption': -5,
                                   'Intensity': 1.0})
    merged = behavior.BehaviorTree.merge(tree1, tree2)
    assert merged.structure == structure
    # convert to tuple (hashable) so dicts_equal doesn't error out
    for k in merged:
        merged[k] = tuple(merged[k])
    assert dicts_equal(merged.contents,
                       {'AS Prob': (1, 1),
                        'Consumption': (5, -5),
                        'Intensity': (2, 1.0)})
    with pytest.raises(TypeError) as excinfo:
        behavior.BehaviorTree.merge()
    assert excinfo.value.args[0] == 'Expected at least one argument'


def test_tree_summarize():
    structure = ['Consumption',
                 ['AS Prob', 'Intensity']]
    tree1 = behavior.BehaviorTree(structure,
                                  {'AS Prob': 1,
                                   'Consumption': 5,
                                   'Intensity': 2})
    tree2 = behavior.BehaviorTree(structure,
                                  {'AS Prob': 1,
                                   'Consumption': -5,
                                   'Intensity': 1.0})
    merged = behavior.BehaviorTree.merge(tree1, tree2)
    summarized = merged.summarize(sum)
    assert summarized.structure == structure
    assert dicts_equal(summarized.contents,
                       {'AS Prob': 2,
                        'Consumption': 0,
                        'Intensity': 3.0})


def test_get_units():
    units = behavior.construct_trees._get_units('F')
    reference = {'Consumption Rate': 'g/s',
                 'AS Prob': '',
                 'Intensity': 'g/s',
                 'Bout Rate': 'bouts/s',
                 'Bout Size': 'g/bout',
                 'Bout Duration': 's/bout',
                 'Bout Intensity': 'g/s',
                 'Bout Event Rate': 'events/s',
                 'Event Size': 'g/event'}
    assert dicts_equal(units, reference)


def test_process_raw_intervals():
    ints_raw = np.array([[1, 2], [2.5, 3]])
    ints = intervals.Intervals(ints_raw)
    consump = 100
    active_time = 4
    total_time = 5
    eps = 1
    tree = behavior.process_raw_intervals('F', consump, ints,
                                          active_time,
                                          total_time, eps)
    assert len(tree.contents) == 9
    assert tree['Consumption Rate'] == consump / total_time
    assert tree['AS Prob'] == active_time / total_time


def test_active_time():
    time_active = behavior.metrics.active_time(0, 0, 0)
    assert time_active > 0
    assert time_active < 86400  # Number of seconds in a day


def test_total_time():
    total_time = behavior.metrics.total_time(0, 0, 0)
    assert total_time > 0
    assert total_time < 86400  # Number of seconds in a day


def test_total_amount():
    for feature in ['W', 'L', 'F']:
        total_amount = behavior.metrics.total_amount(0, 0, 5, feature)
        assert total_amount > 0

    # Bad feature
    with pytest.raises(ValueError):
        behavior.metrics.total_amount(5, 5, 5, 'G')

    # Bad strain/mouse/day
    with pytest.raises(ValueError):
        behavior.metrics.total_amount(1000, 0, 0, 'W')
