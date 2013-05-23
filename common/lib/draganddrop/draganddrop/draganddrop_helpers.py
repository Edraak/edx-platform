# -*- coding: utf-8 -*-

import re

re_col_row = re.compile(r'\{([0-9]*)\}')


def flatten_user_answer(user_answer):
    """
    Convert each item of `user_answer` to flat format.

    Convert each item like:
    {'up': {'first': {'p': 'p_l'}}}
    to
    {'up': 'p_l[p][first]'}

    :param user_answer: list of dicts where dict value is nested dict
    -- information about draggables.
    :type user_answer: list.
    :returns: list of dicts where dict value is string
    -- flattened list of information about draggables.
    """

    def parse_user_answer(info):
        draggable, target = info.items()[0]

        if isinstance(target, dict):
            # Make complex target. Examples:
            # Create like 'p_l[p][first]' from {'first': {'p': 'p_l'}
            nested_draggables = []

            while isinstance(target, dict):
                nested_draggable, target = target.items()[0]
                nested_draggables.append(nested_draggable)

            joined_targets = ''.join(
                ['[{0}]'.format(i) for i in reversed(nested_draggables)]
            )

            return {draggable: '{0}{1}'.format(target, joined_targets)}
        else:
            return info

    return [parse_user_answer(info) for info in user_answer]


def clean_user_answer(user_answer):
    """
    Clean `user_answer` from {col}{row}, when target use type == "grid",
    cause teacher use target id without additional info about columns
    and rows. Support only targets, which already was flatted.

    Convert each item like:
    {'up': 'p_l[p][first{3}{5}]'}
    to
    {'up': 'p_l[p][first]'}

    :param user_answer: list of dicts -- information about draggables.
    :type user_answer: list.
    :returns: list of dicts -- clean list of information about draggables.
    """

    def parse_user_answer(answer):
        draggable, target = answer.items()[0]

        # Possible `target` type: `basestring` or
        # `list` (coordinates of centers of dragged images).
        if isinstance(target, basestring):
            # Remove next sequences - "{any number of digits}"
            return {draggable: re_col_row.sub('', target)}
        else:
            return answer

    return [parse_user_answer(answer) for answer in user_answer]


class PositionsCompare(list):
    """ Class for comparing positions.

        Args:
                list or string::
                    "abc" - target
                    [10, 20] - list of integers
                    [[10,20], 200] list of list and integer

    """
    def __eq__(self, other):
        """ Compares two arguments.

        Default lists behavior is conversion of string "abc" to  list
        ["a", "b", "c"]. We will use that.

        If self or other is empty - returns False.

        Args:
                self, other: str, unicode, list, int, float

        Returns: bool
        """
        # checks if self or other is not empty list (empty lists  = false)
        if not self or not other:
            return False

        if (
            isinstance(self[0], (list, int, float)) and
            isinstance(other[0], (list, int, float))
        ):
            return self.coordinate_positions_compare(other)
        elif (
            isinstance(self[0], (unicode, str)) and
            isinstance(other[0], (unicode, str))
        ):
            return ''.join(self) == ''.join(other)
        else:  # improper argument types: no (float / int or lists of list
            #and float / int pair) or two string / unicode lists pair
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def coordinate_positions_compare(self, other, r=10):
        """ Checks if self is equal to other inside radius of forgiveness
            (default 10 px).

            Args:
                self, other: [x, y] or [[x, y], r], where r is radius of
                             forgiveness;
                             x, y, r: int

            Returns: bool.
        """
        # get max radius of forgiveness
        if isinstance(self[0], list):  # [(x, y), r] case
            r = max(self[1], r)
            x1, y1 = self[0]
        else:
            x1, y1 = self

        if isinstance(other[0], list):  # [(x, y), r] case
            r = max(other[1], r)
            x2, y2 = other[0]
        else:
            x2, y2 = other

        if (x2 - x1) ** 2 + (y2 - y1) ** 2 > r * r:
            return False

        return True
