from __future__ import print_function, absolute_import, division

from collections import defaultdict
import copy


class BehaviorTree():
    """
    Object representing a decomposed tree of behavior. Behaves much like
    a dictionary, with an additional representation of the tree structure
    of the data.

    Parameters
    ----------
    structure : list, optional
        Representation of parent-child relationships between nodes
    contents : defaultdict, optional
        Initial  node values
    units : defaultdict, optional
        Mapping of node names to units
    Examples
    --------
    >>> tree = BehaviorTree(['Consumption',
                             ['AS Prob', 'Intensity']])
    >>> tree['Consumption'] = 5
    >>> tree['AS Prob'] = 1
    >>> tree['Intensity'] = 2
    >>> tree.contents
    defaultdict(float, {'AS Prob': 1, 'Consumption': 5, 'Intensity': 2})
    >>> tree.structure
    ['Consumption', ['AS Prob', 'Intensity']]
    >>> print(tree)

    Consumption: 5
         AS Prob: 1
         Intensity: 2
    """

    def __init__(self, structure=None, contents=None, units=None):
        if contents is None:
            contents = defaultdict(float)
        if units is None:
            units = defaultdict(str)
        self.contents = contents
        self.structure = structure
        self.units = units

    def copy(self):
        """
        Return a copy of the tree.
        """
        return BehaviorTree(structure=copy.deepcopy(self.structure),
                            contents=copy.deepcopy(self.contents),
                            units=copy.deepcopy(self.units))

    def __str__(self):
        """
        Return a string representation for printing.
        """
        if self.structure is None:
            return self.contents.__str__()
        else:
            return self._display_tree()

    def __getitem__(self, key):
        """
        Return the value of the node specified by `key`

        Parameters
        ----------
        key : string
            Name of a node in the tree
        """
        return self.contents[key]

    def __setitem__(self, key, value):
        """
        Set the value of `key` to `value`.

        Parameters
        ----------
        key : string
            Name of a node in the tree
        value
            Value to be used for that node
        """
        self.contents[key] = value

    def __iter__(self):
        """
        Return an iterator over the nodes in the tree.
        """
        return iter(self.contents)

    def _display_tree(self, level=0):
        """
        Return a string representation of the tree structure,
        based on relationships in the attribute `structure`.

        Parameters
        ----------
        level : int
            The indentation level for display
        """
        struct = self.structure
        if isinstance(struct, list):
            root = struct[0]
            children = struct[1]
        else:
            root = struct
            children = []

        if isinstance(self[root], list):
            formatted_value = " " .join(
                ["{:.6f}".format(v) for v in self[root]])
        else:
            formatted_value = "{:.6f}".format(self[root])
        result = "\n" + " " * 5 * level + \
            "{}: {} {}".format(root,
                               formatted_value,
                               self.units[root])

        for child in children:
            current_tree = self.copy()
            current_tree.structure = child
            result += current_tree._display_tree(level + 1)

        return result

    @staticmethod
    def merge(*args):
        """
        Merge several trees into one compound tree.

        Parameters
        ----------
        *args : variable-length argument list of BehaviorTree objects
            One or more trees to be merged.

        Returns
        -------
        new_tree : BehaviorTree
            Tree with same structure as input trees, where each node
            is a list containing the node values from the input trees.

        Examples
        --------
        >>> tree = BehaviorTree(contents={'a': 1, 'b': 2})
        >>> tree2 = BehaviorTree(contents={'a': -1.5, 'b': 20})
        >>> BehaviorTree.merge(tree, tree2).contents
        defaultdict(list, {'a': [1, -1.5], 'b': [2, 20]})
        """
        if len(args) == 0:
            raise TypeError("Expected at least one argument")
        new_tree = BehaviorTree(structure=args[0].structure,
                                contents=defaultdict(list))
        for tree in args:
            assert tree.structure == new_tree.structure
            for k in tree:
                new_tree[k].append(tree[k])
        return new_tree

    def summarize(self, f):
        """
        Computes a summary statistic for the nodes in a tree.

        Parameters
        ----------
        f : function
            A function to be applied to the contents in each node. Most
           often, this will take in a list and return a single number.

        Returns
        -------
        A new tree with the same structure, where each node value tree[k]
        is replaced by f(tree[k]).
        """
        results = self.copy()
        for k in results:
            results[k] = f(results[k])
        return results
