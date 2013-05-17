# -*- coding: utf-8 -*-

import re
import json
from collections import Counter
from itertools import groupby

from .draganddrop_helpers import clean_user_answer, flat_user_answer


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
        return `True` if `self.children` equal to
        ['obj1', 'obj1', 'obj2']
        or
        ['obj1', 'obj2', 'obj1']
        or
        ['obj2', 'obj1', 'obj1'].

        So, the order doesn't matter.
        """

        exact = kwargs.get('exact', True)

        if exact:
            return sorted(self.children) == sorted(args)
        else:
            return not bool(Counter(args) - Counter(self.children))


class BadProperty(object):
    """Property for non-existent object.
    This class help managing some case, when we have for example:
        dragabbles.sun.on_target('base_target')[0].y > 100

    and dragabbles.sun object doesn't exist.

    Any operations (>, <, >=, <=, !=, ==) with this object
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


class DraggableSet(object):
    """This class use to unite many Draggable objects to one
    structure, which has some helpful filters and properties.
    """
    def __init__(self, items):
        self.items = items

    def __getitem__(self, key):
        try:
            return self.items[key]
        except IndexError:
            bad_property = BadProperty()
            return Draggable(
                bad_property,
                bad_property,
                bad_property,
                bad_property,
                bad_property
            )

    @property
    def count(self):
        """Return total counts for draggable set."""
        return len(self.items)

    def on(self, target):
        """Filter draggables by target.

        :param target: name of target.
        :type target: str or unicode.
        :returns: `DraggableSet`.
        """
        new_items = [i for i in self.items if i.target == target]
        return DraggableSet(new_items)


class AllDragabbles(dict):
    """Class which manage all dragabbles by classes attributes."""

    def __getitem__(self, key):
        return self.get(key, DraggableSet([]))


def prepare_targets(user_input):
    """Convert `user_input` from client to helpful structure:

    [(draggable_id, [target1, target2, ...]), ...],

    where target - first level `<target>` or nearest `<draggable>`.

    :param user_input: raw user_input (without any cleaning and modifying).
    :type user_input: list.
    :returns: list.

    Example:
    user_input = [
        {'house': 'base_target{5}{10}'},
        {'baby': {'1': {'house': 'base_target'}}},
        {'baby': {'2': {'house': 'base_target'}}}
    ]

    `prepare_targets` return
    [
        ('baby', ['base_target[house]', 'base_target[house]']),
        ('house', ['base_target{5}{10}'])
    ]
    """
    result = []

    for item in user_input:
        if isinstance(item.values()[0], dict):
            result.append({item.keys()[0]: item.values()[0].values()[0]})
        else:
            result.append(item)

    result = flat_user_answer(result)
    sorted_result = sorted(result, key=lambda obj: obj.keys()[0])
    groups = groupby(sorted_result, key=lambda obj: obj.keys()[0])

    return [(i[0], [j.values()[0] for j in i[1]]) for i in groups]


def prepare_children(user_input):
    """Convert `user_input` from client to helpful structure:

    {target: [draggable1_id, draggable2_id, ...]},

    where target - first level `<target>` or nearest `<draggable>`.

    :param user_input: raw user_input (without any cleaning and modifying).
    :type user_input: list.
    :returns: dict.

    Example:
    user_input = [
        {'house': 'base_target{5}{10}'},
        {'baby': {'1': {'house': 'base_target'}}},
        {'baby': {'2': {'house': 'base_target'}}}
    ]

    `prepare_children` return
    {
        'base_target': ['house'],
        'base_target[house]': ['baby', 'baby']
    }
    """
    result = []

    for item in user_input:
        if isinstance(item.values()[0], dict):
            result.append({item.keys()[0]: item.values()[0].values()[0]})
        else:
            result.append(item)

    result = clean_user_answer(flat_user_answer(result))
    sorted_result = sorted(result, key=lambda obj: obj.values()[0])
    groups = groupby(sorted_result, key=lambda obj: obj.values()[0])

    return dict([(i[0], [j.keys()[0] for j in i[1]]) for i in groups])


def get_all_dragabbles(raw_user_input, xml):
    """Return all draggables objects."""

    user_input = json.loads(raw_user_input)

    # Container for all `Draggable` instances.
    all_dragabbles = AllDragabbles()

    all_children = prepare_children(user_input)
    all_targets = prepare_targets(user_input)

    for draggable, targets in all_targets:
        dragabbles = []

        for target in targets:
            cell_positions = re.findall(r'\{([0-9]*)\}', target)
            if cell_positions:
                p = re.compile(r'\{[0-9]*\}')
                clean_target = p.sub('', target)
                item_col, item_row = [int(i) for i in cell_positions]
            else:
                clean_target = target
                item_col = 0
                item_row = 0

            # For dragabbles on draggables we support minor features.
            # For that objects we don't support x,y properties.
            # TODO: add support x,y properties for nested draggables.
            target_object = xml.find(
                'drag_and_drop_input'
            ).find("target[@id='{0}']".format(clean_target))

            if target_object is not None:
                # Get data from xml.
                target_x = int(target_object.attrib.get('x'))
                target_y = int(target_object.attrib.get('y'))
                target_width = int(target_object.attrib.get('w'))
                target_height = int(target_object.attrib.get('h'))
                target_col = int(target_object.attrib.get('col', 1))
                target_row = int(target_object.attrib.get('row', 1))

                cell_width = target_width / target_col
                cell_height = target_height / target_row

                # Calculate x,y coordinates of item.
                x = int(target_x + (item_col + 0.5) * cell_width)
                y = int(target_y + (item_row + 0.5) * cell_height)
            else:
                x = BadProperty()
                y = BadProperty()

            # Try to find children.
            children = all_children.get('{0}[{1}]'.format(
                clean_target, draggable),
                []
            )
            dragabbles.append(
                Draggable(draggable, x, y, clean_target, children)
            )

            # Sort by Y-coordinate.
            dragabbles.sort(key=lambda obj: obj.y)

        all_dragabbles[draggable] = DraggableSet(dragabbles)

    return all_dragabbles
