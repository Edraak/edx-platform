""" Grader of drag and drop input.

Client side behavior: user can drag and drop images from list on base image.


 Then json returned from client is:
 {
    "draggable": [
        { "image1": "t1"  },
        { "ant": "t2"  },
        { "molecule": "t3"  },
                ]
}
values are target names.

or:
 {
    "draggable": [
        { "image1": "[10, 20]"  },
        { "ant": "[30, 40]"  },
        { "molecule": "[100, 200]"  },
                ]
}
values are (x,y) coordinates of centers of dragged images.
"""

import json
import re
from itertools import groupby


def flat_user_answer(user_answer):
    """
    Convert nested `user_answer` to flat format.

        {'up': {'first': {'p': 'p_l'}}}

        to

        {'up': 'p_l[p][first]'}
    """

    def parse_user_answer(answer):
        key = answer.keys()[0]
        value = answer.values()[0]

        if isinstance(value, dict):
            # Make complex value:
            # Example:
            # Create like 'p_l[p][first]' from {'first': {'p': 'p_l'}
            complex_value_list = []
            v_value = value
            while isinstance(v_value, dict):
                v_key = v_value.keys()[0]
                v_value = v_value.values()[0]
                complex_value_list.append(v_key)

            complex_value = '{0}'.format(v_value)
            for i in reversed(complex_value_list):
                complex_value = '{0}[{1}]'.format(complex_value, i)

            res = {key: complex_value}
            return res
        else:
            return answer

    result = []
    for answer in user_answer:
        parse_answer = parse_user_answer(answer)
        result.append(parse_answer)

    return result


def clean_user_answer(user_answer):
    """
    Clean `user_answer` from {col}{row}, when target use type == "grid",
    cause teacher use target id without additional info about columns
    and rows.

        {'up': 'p_l[p][first{3}{5}]'}

        to

        {'up': 'p_l[p][first]'}
    """

    def parse_user_answer(answer):
        key = answer.keys()[0]
        value = answer.values()[0]

        if isinstance(value, basestring):
            # Remove next sequences - "{any number of digits}"
            p = re.compile(r'\{[0-9]*\}')
            new_value = p.sub('', value)
            return {key: new_value}
        else:
            return answer

    result = []
    for answer in user_answer:
        parse_answer = parse_user_answer(answer)
        result.append(parse_answer)

    return result


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

        if (isinstance(self[0], (list, int, float)) and
            isinstance(other[0], (list, int, float))):
            return self.coordinate_positions_compare(other)

        elif (isinstance(self[0], (unicode, str)) and
              isinstance(other[0], (unicode, str))):
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


class DragAndDrop(object):
    """ Grader class for drag and drop inputtype.
    """

    def grade(self):
        ''' Grader user answer.

        Checks if every draggable isplaced on proper target or  on proper
        coordinates within radius of forgiveness (default is 10).

        Returns: bool.
        '''
        for draggable in self.excess_draggables:
            if self.excess_draggables[draggable]:
                return False  # user answer has more draggables than correct answer

        # Number of draggables in user_groups may be differ that in
        # correct_groups, that is incorrect, except special case with 'number'
        for index, draggable_ids in enumerate(self.correct_groups):
            # 'number' rule special case
            # for reusable draggables we may get in self.user_groups
            # {'1': [u'2', u'2', u'2'], '0': [u'1', u'1'], '2': [u'3']}
            # if '+number' is in rule - do not remove duplicates and strip
            # '+number' from rule
            current_rule = self.correct_positions[index].keys()[0]
            if 'number' in current_rule:
                rule_values = self.correct_positions[index][current_rule]
                # clean rule, do not do clean duplicate items
                self.correct_positions[index].pop(current_rule, None)
                parsed_rule = current_rule.replace('+', '').replace('number', '')
                self.correct_positions[index][parsed_rule] = rule_values
            else:  # remove dublicates
                self.user_groups[index] = list(set(self.user_groups[index]))

            if sorted(draggable_ids) != sorted(self.user_groups[index]):
                return False

        # Check that in every group, for rule of that group, user positions of
        # every element are equal with correct positions
        for index, _ in enumerate(self.correct_groups):
            rules_executed = 0
            for rule in ('exact', 'anyof', 'unordered_equal'):
                # every group has only one rule
                if self.correct_positions[index].get(rule, None):
                    rules_executed += 1
                    if not self.compare_positions(
                            self.correct_positions[index][rule],
                            self.user_positions[index]['user'], flag=rule):
                        return False
            if not rules_executed:  # no correct rules for current group
            # probably xml content mistake - wrong rules names
                return False

        return True

    def compare_positions(self, correct, user, flag):
        """ Compares two lists of positions with flag rules. Order of
        correct/user arguments is matter only in 'anyof' flag.

        Rules description:

            'exact' means 1-1 ordered relationship::

                [el1, el2, el3] is 'exact' equal to [el5, el6, el7] when
                el1 == el5, el2 == el6, el3 == el7.
                Equality function is custom, see below.


            'anyof' means subset relationship::

                user = [el1, el2] is 'anyof' equal to correct = [el1, el2, el3]
                when
                        set(user) <= set(correct).

                'anyof' is ordered relationship. It always checks if user
                is subset of correct

                Equality function is custom, see below.

                Examples:

                     - many draggables per position:
                    user ['1','2','2','2'] is 'anyof' equal to ['1', '2', '3']

                     - draggables can be placed in any order:
                    user ['1','2','3','4'] is 'anyof' equal to ['4', '2', '1', 3']

            'unordered_equal' is same as 'exact' but disregards on order

        Equality functions:

        Equality functon depends on type of element. They declared in
        PositionsCompare class. For position like targets
        ids ("t1", "t2", etc..) it is string equality function. For coordinate
        positions ([1,2] or [[1,2], 15]) it is coordinate_positions_compare
        function (see docstrings in PositionsCompare class)

        Args:
            correst, user: lists of positions

        Returns: True if within rule lists are equal, otherwise False.
        """
        if flag == 'exact':
            if len(correct) != len(user):
                return False
            for el1, el2 in zip(correct, user):
                if PositionsCompare(el1) != PositionsCompare(el2):
                    return False

        if flag == 'anyof':
            for u_el in user:
                for c_el in correct:
                    if PositionsCompare(u_el) == PositionsCompare(c_el):
                        break
                else:
                    # General: the else is executed after the for,
                    # only if the for terminates normally (not by a break)

                    # In this case, 'for' is terminated normally if every element
                    # from 'correct' list isn't equal to concrete element from
                    # 'user' list. So as we found one element from 'user' list,
                    # that not in 'correct' list - we return False
                    return False

        if flag == 'unordered_equal':
            if len(correct) != len(user):
                return False
            temp = correct[:]
            for u_el in user:
                for c_el in temp:
                    if PositionsCompare(u_el) == PositionsCompare(c_el):
                        temp.remove(c_el)
                        break
                else:
                    # same as upper -  if we found element from 'user' list,
                    # that not in 'correct' list - we return False.
                    return False

        return True

    def __init__(self, correct_answer, user_answer):
        """ Populates DragAndDrop variables from user_answer and correct_answer.
        If correct_answer is dict, converts it to list.
        Correct answer in dict form is simpe structure for fast and simple
        grading. Example of correct answer dict example::

            correct_answer = {'name4': 't1',
                            'name_with_icon': 't1',
                            '5': 't2',
                            '7': 't2'}

            It is draggable_name: dragable_position mapping.

            Advanced form converted from simple form uses 'exact' rule
            for matching.

        Correct answer in list form is designed for advanced cases::

        correct_answers = [
        {
        'draggables': ['1', '2', '3', '4', '5', '6'],
        'targets': [
           's_left', 's_right', 's_sigma', 's_sigma_star', 'p_pi_1',  'p_pi_2'],
        'rule': 'anyof'},
        {
        'draggables': ['7', '8', '9', '10'],
        'targets': ['p_left_1', 'p_left_2', 'p_right_1', 'p_right_2'],
        'rule': 'anyof'
        }
                        ]

        Advanced answer in list form is list of dicts, and every dict must have
        3 keys: 'draggables', 'targets' and 'rule'. 'Draggables' value is
        list of draggables ids, 'targes' values are list of targets ids, 'rule'
        value one of 'exact', 'anyof', 'unordered_equal', 'anyof+number',
        'unordered_equal+number'

        Advanced form uses "all dicts must match with their rule" logic.

        Same draggable cannot appears more that in one dict.

        Behavior is more widely explained in sphinx documentation.

        Args:
            user_answer: json
            correct_answer: dict or list
        """

        self.correct_groups = []  # Correct groups from xml.
        self.correct_positions = []  # Correct positions for comparing.
        self.user_groups = []  # Will be populated from user answer.
        self.user_positions = []  # Will be populated from user answer.

        # Convert from dict answer format to list format.
        if isinstance(correct_answer, dict):
            tmp = []
            for key, value in correct_answer.items():
                tmp.append({
                    'draggables': [key],
                    'targets': [value],
                    'rule': 'exact'})
            correct_answer = tmp

        # Convert string `user_answer` to object.
        user_answer = json.loads(user_answer)

        # This dictionary will hold a key for each draggable the user placed on
        # the image.  The value is True if that draggable is not mentioned in any
        # correct_answer entries.  If the draggable is mentioned in at least one
        # correct_answer entry, the value is False.
        # default to consider every user answer excess until proven otherwise.
        self.excess_draggables = dict((users_draggable.keys()[0],True)
            for users_draggable in user_answer)

        # Convert nested `user_answer` to flat format.
        user_answer = flat_user_answer(user_answer)

        # Clean `user_answer`.
        user_answer = clean_user_answer(user_answer)

        # Create identical data structures from user answer and correct answer.
        for answer in correct_answer:
            user_groups_data = []
            user_positions_data = []
            for draggable_dict in user_answer:
                # Draggable_dict is 1-to-1 {draggable_name: position}.
                draggable_name = draggable_dict.keys()[0]
                if draggable_name in answer['draggables']:
                    user_groups_data.append(draggable_name)
                    user_positions_data.append(
                                            draggable_dict[draggable_name])
                    # proved that this is not excess
                    self.excess_draggables[draggable_name] = False

            self.correct_groups.append(answer['draggables'])
            self.correct_positions.append({answer['rule']: answer['targets']})
            self.user_groups.append(user_groups_data)
            self.user_positions.append({'user': user_positions_data})


def grade(user_input, correct_answer):
    """ Creates DragAndDrop instance from user_input and correct_answer and
        calls DragAndDrop.grade for grading.

        Supports two interfaces for correct_answer: dict and list.

        Args:
            user_input: json. Format::

                { "draggables":
                [{"1": [10, 10]}, {"name_with_icon": [20, 20]}]}'

                or

                {"draggables": [{"1": "t1"}, \
                {"name_with_icon": "t2"}]}

            correct_answer: dict or list.

                Dict form::

                        {'1': 't1',  'name_with_icon': 't2'}

                        or

                        {'1': '[10, 10]',  'name_with_icon': '[[10, 10], 20]'}

                List form::

                    correct_answer = [
                    {
                        'draggables':  ['l3_o', 'l10_o'],
                        'targets':  ['t1_o', 't9_o'],
                        'rule': 'anyof'
                    },
                    {
                        'draggables': ['l1_c','l8_c'],
                        'targets': ['t5_c','t6_c'],
                        'rule': 'anyof'
                    }
                    ]

        Returns: bool
    """
    return DragAndDrop(correct_answer=correct_answer,
                       user_answer=user_input).grade()


def get_all_dragabbles(raw_user_input, xml):
    """Return all draggables objects."""

    def singleton(cls):
        """Signleton decorator."""
        return cls()

    class Draggable(object):
        """Class which describe draggables objects."""
        def __init__(self, x, y, target):
            self.x = x
            self.y = y
            self.target = target

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
                return Draggable(bad_property, bad_property, bad_property)

        @property
        def count(self):
            """Return total counts for draggable set."""
            return len(self.items)

        def on(self, target):
            """Filter draggables by target."""
            new_items = [i for i in self.items if i.target == target]
            return DraggableSet(new_items)

    @singleton
    class AllDragabbles(object):
        """Class which manage all dragabbles by classes attributes."""

        items = {}

        def __setitem__(self, key, value):
            self.items[key] = value

        def __getitem__(self, key):
            return self.items.get(key) or DraggableSet([])

    user_input = json.loads(raw_user_input)
    sorted_user_input = sorted(user_input, key=lambda obj: obj.keys()[0])

    all_dragabbles = AllDragabbles

    for key, value in groupby(sorted_user_input, key=lambda obj: obj.keys()[0]):
        dragabbles = []

        # We ignore dragabbles on draggables. Support only first level
        # target.
        targets = [i[key] for i in value if isinstance(i[key], basestring)]
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

            # We ignore dragabbles on draggables. Support only first
            # level target.
            target_object = xml.find('drag_and_drop_input'
                ).find("target[@id='{0}']".format(clean_target))

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

            dragabbles.append(Draggable(x, y, clean_target))

            # Sort by Y-coordinate.
            dragabbles.sort(key=lambda obj: obj.y)

        all_dragabbles[key] = DraggableSet(dragabbles)

    return all_dragabbles
