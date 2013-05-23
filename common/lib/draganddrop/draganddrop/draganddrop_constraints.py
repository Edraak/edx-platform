# -*- coding: utf-8 -*-

import json
from collections import Counter
from itertools import groupby

from .draganddrop_helpers import clean_user_answer, flatten_user_answer
from .draganddrop_helpers import re_col_row


class Draggable(object):
    """Class which describe draggables objects."""
    def __init__(self, name, x, y, target, children):
        """Initialize `Draggable`:

        :param name: name of draggable object.
        :type name: str or unicode.
        :param x: X-coordinate.
        :type x: int.
        :param y: Y-coordinate.
        :type y: int.
        :param target: target in which lays current draggable.
        :type target: str or unicode.
        :param children: list of first level children.
        :type children: list.
        """
        self.name = name
        self.x = x
        self.y = y
        self.target = target
        self.children = children

    def contains(self, *args, **kwargs):
        """Check if current `Draggable` object contains some draggables.

        :param exact: name of draggable object. If you set option
        `exact` to `False`, then you have not strict conditional and
        check only, that `args` in `self.children`. Default value = `True`.
        :type exact: bool.

        Example:
        ...contains('obj1', 'obj2', 'obj1')
        return `True` if `self.children` equal to permutation of
        ['obj1', 'obj1', 'obj2']

        So, the order doesn't matter.
        """

        exact = kwargs.get('exact', True)

        if isinstance(self.children, BadProperty):
            return BadProperty()

        if exact:
            return sorted(self.children) == sorted(args)
        else:
            return not bool(Counter(args) - Counter(self.children))


class BadProperty(object):
    """Property for non-existent object.
    This class help managing some case, when we have for example:
        dragabbles.sun.on_target('base_target')[0].y > 100

    and dragabbles.sun object doesn't exist.

    Any operations (==, !=, <, >, <=, >=) with this object
    return False.
    """
    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return False

    def __le__(self, other):
        return False

    def __ge__(self, other):
        return False

    def __nonzero__(self):
        return False


class DraggableSet(list):
    """This class use to unite many Draggable objects to one
    structure, which has some helpful filters and properties.
    """
    def __getitem__(self, key):
        try:
            return super(DraggableSet, self).__getitem__(key)
        except IndexError:
            return Draggable(*([BadProperty()] * 5))

    @property
    def count(self):
        """Return total counts for draggable set."""
        return len(self)

    def on(self, target):
        """Filter draggables by target.

        :param target: name of target.
        :type target: str or unicode.
        :returns: `DraggableSet`.
        """
        return DraggableSet(i for i in self if i.target == target)


class AllDragabbles(dict):
    """Class which manage all dragabbles by classes attributes."""

    def __getitem__(self, key):
        return self.get(key, DraggableSet([]))


def prepare_first_target_level(item):
    """Get first target level.

    :param item: item of user_input.
    :type item: dict.
    :returns: dict.

    Example:
    {'baby': {'1': {'house': 'base_target'}}}
    to
    {u'baby': {u'house': u'base_target'}}.
    """
    if isinstance(item.values()[0], dict):
        return {item.keys()[0]: item.values()[0].values()[0]}
    return item


def prepare_targets(user_info):
    """Convert `user_info` to helpful structure:

    [(draggable_id, [target1, target2, ...]), ...],

    where target - is parent - nearest higher level `<target>` or `<draggable>`.
    This actually revert user_unput to be more readable.

    :param user_info: raw user_info (without any cleaning and modifying).
    :type user_info: list.
    :returns: list.

    Example::

    user_info = [
        {'house': 'base_target{5}{10}'},
        {'baby': {'house': 'base_target'}},
        {'baby': {'house': 'base_target'}}
    ]

    `prepare_targets` returns
    [
        ('baby', ['base_target[house]', 'base_target[house]']),
        ('house', ['base_target{5}{10}'])
    ]
    """
    # get rid of unnecessary information for this step
    user_info = flatten_user_answer(user_info)

    # sort for group
    sorted_user_info = sorted(user_info, key=lambda obj: obj.keys()[0])

    # group same draggables per children
    groups = groupby(sorted_user_info, key=lambda obj: obj.keys()[0])

    return [
        (draggable, [j.values()[0] for j in group])
        for draggable, group in groups
    ]


def prepare_children(user_info):
    """Convert `user_info` to helpful structure:

    {target: [draggable1_id, draggable2_id, ...]},

    where target - is parent - nearest higher level `<target>` or `<draggable>`.
    This actually revert user_unput to be more readable.

    :param user_info: raw user_info (without any cleaning and modifying).
    :type user_info: list.
    :returns: dict.

    Example::

    user_info = [
        {'house': 'base_target{5}{10}'},
        {'baby': {'house': 'base_target'}},
        {'baby': {'house': 'base_target'}}
    ]

    `prepare_children` returns
    {
        'base_target': ['house'],
        'base_target[house]': ['baby', 'baby']
    }
    """
    # get rid of unnecessary information for this step
    user_info = clean_user_answer(flatten_user_answer(user_info))

    # sort for group
    sorted_user_info = sorted(user_info, key=lambda obj: obj.values()[0])

    # group same draggables per target
    groups = groupby(sorted_user_info, key=lambda obj: obj.values()[0])

    # create reverted data structure
    return dict([
        (target, [j.keys()[0] for j in group])
        for target, group in groups
    ])


def get_all_dragabbles(raw_user_input, xml):
    """Return all draggables objects."""

    user_input = json.loads(raw_user_input)

    # Container for all `Draggable` instances.
    all_dragabbles = AllDragabbles()

    all_children = prepare_children(
        map(prepare_first_target_level, user_input)
    )
    all_targets = prepare_targets(
        map(prepare_first_target_level, user_input)
    )

    for draggable, targets in all_targets:
        dragabbles = []

        for target in targets:
            item_col = 0
            item_row = 0

            item_col, item_row = map(int, re_col_row.findall(target)) \
                or [0, 0]
            target = re_col_row.sub('', target)

            # For dragabbles on draggables we support minor features.
            # For that objects we don't support x,y properties.

            # `target_object` is None if it complex, like a[b].
            target_object = xml.find(
                'drag_and_drop_input'
            ).find("target[@id='{0}']".format(target))

            # Ignore support x,y properties for nested draggables.
            x = BadProperty()
            y = BadProperty()

            if target_object is not None:
                # Get data from xml.
                target_x = float(target_object.attrib.get('x'))
                target_y = float(target_object.attrib.get('y'))
                target_width = float(target_object.attrib.get('w'))
                target_height = float(target_object.attrib.get('h'))
                target_col = float(target_object.attrib.get('col', 1))
                target_row = float(target_object.attrib.get('row', 1))

                cell_width = target_width / target_col
                cell_height = target_height / target_row

                # Calculate x,y coordinates of item.
                x = cell_width * (item_col + 0.5) + target_x
                y = cell_height * (item_row + 0.5) + target_y

            # Try to find children.
            children = all_children.get('{0}[{1}]'.format(
                target, draggable), [])
            dragabbles.append(
                Draggable(draggable, x, y, target, children)
            )

            # Sort by X and then by Y-coordinate.
            dragabbles.sort(key=lambda obj: (obj.y, obj.x))

        all_dragabbles[draggable] = DraggableSet(dragabbles)

    return all_dragabbles
