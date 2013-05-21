*******************
Drag and drop rules
*******************

.. module:: drag_and_drop_rules

Rules in the answer format
==========================

.. note::
    For specifying answers for targets on draggables please see next section.

There are two correct answer formats: short and long
If short from correct answer is mapping of 'draggable_id' to 'target_id'::

    correct_answer = {'grass':     [[300, 200], 200], 'ant': [[500, 0], 200]}
    correct_answer = {'name4': 't1', '7': 't2'}

In long form correct answer is list of dicts. Every dict has 3 keys:
draggables, targets and rule. For example::

    correct_answer = [
    {
    'draggables':   ['7', '8'],
    'targets':  ['t5_c', 't6_c'],
    'rule': 'anyof'
    },
    {
    'draggables': ['1', '2'],
    'targets': ['t2_h', 't3_h', 't4_h', 't7_h', 't8_h', 't10_h'],
    'rule': 'anyof'
    }]

Draggables is list of draggables id. Target is list of targets id, draggables
must be dragged to with considering rule. Rule is string.

.. note::

    Draggables in dicts inside correct_answer list must not intersect!

.. note::

    If in <draggable> you have internal <target> tags, then you can address to
    these targets using index notation.

    For example, you have next:

        <draggable id="my_draggable" icon="/static/images/images_list/lcao-mo/orbital_single.png" label="s" can_reuse="true" >
            <target id="my_internal_target" x="0" y="0" w="32" h="32"/>
        </draggable>

    'my_internal_target[my_internal_target]' - notation, which you can use in `correct_answer` object.

Wrong (for draggable id 7)::

    correct_answer = [
    {
    'draggables':   ['7', '8'],
    'targets':  ['t5_c', 't6_c'],
    'rule': 'anyof'
    },
    {
    'draggables': ['7', '2'],
    'targets': ['t2_h', 't3_h', 't4_h', 't7_h', 't8_h', 't10_h'],
    'rule': 'anyof'
    }]

Rules are: exact, anyof, unordered_equal, anyof+number, unordered_equal+number


.. such long lines are needed for sphinx to display lists correctly

- Exact rule means that targets for draggable id's in user_answer are the same that targets from correct answer. For example, for draggables 7 and 8 user must drag 7 to target1 and 8 to target2 if correct_answer is::

    correct_answer = [
    {
    'draggables':   ['7', '8'],
    'targets':  ['tartget1', 'target2'],
    'rule': 'exact'
    }]


- unordered_equal rule allows draggables be dragged to targets unordered. If one want to allow for student to drag 7 to target1 or target2 and 8 to target2 or target 1 and 7 and 8 must be in different targets, then correct answer must be::

    correct_answer = [
    {
    'draggables':   ['7', '8'],
    'targets':  ['tartget1', 'target2'],
    'rule': 'unordered_equal'
    }]


- Anyof rule allows draggables to be dragged to any of targets. If one want to allow for student to drag 7 and 8 to target1 or target2, which means that if 7 is on target1 and 8 is on target1 or 7 on target2 and 8 on target2 or 7 on target1 and 8 on target2. Any of theese are correct which anyof rule::

    correct_answer = [
    {
    'draggables':   ['7', '8'],
    'targets':  ['tartget1', 'target2'],
    'rule': 'anyof'
    }]


- If you have can_reuse true, then you, for example, have draggables a,b,c and 10 targets. These will allow you to drag 4 'a' draggables to ['target1',  'target4', 'target7', 'target10'] , you do not need to write 'a' four times. Also this will allow you to drag 'b' draggable to target2 or target5 for target5 and target2 etc..::

    correct_answer = [
        {
            'draggables': ['a'],
            'targets': ['target1',  'target4', 'target7', 'target10'],
            'rule': 'unordered_equal'
        },
        {
            'draggables': ['b'],
            'targets': ['target2', 'target5', 'target8'],
            'rule': 'anyof'
        },
        {
            'draggables': ['c'],
            'targets': ['target3', 'target6', 'target9'],
            'rule': 'unordered_equal'
        }]

- And sometimes you want to allow drag only two 'b' draggables, in these case you should use 'anyof+number' of 'unordered_equal+number' rule::

    correct_answer = [
        {
            'draggables': ['a', 'a', 'a'],
            'targets': ['target1',  'target4', 'target7'],
            'rule': 'unordered_equal+numbers'
        },
        {
            'draggables': ['b', 'b'],
            'targets': ['target2', 'target5', 'target8'],
            'rule': 'anyof+numbers'
        },
        {
            'draggables': ['c'],
            'targets': ['target3', 'target6', 'target9'],
            'rule': 'unordered_equal'
        }]

In case if we have no multiple draggables per targets (one_per_target="true"),
for same number of draggables, anyof is equal to unordered_equal

If we have can_reuse=true, than one must use only long form of correct answer.

Answer format for targets on draggables
=======================================

As with the cases described above, an answer must provide precise positioning for
each draggable (on which targets it must reside). In the case when a draggable must
be placed on a target that itself is on a draggable, then the answer must contain
the chain of target-draggable-target. It is best to understand this on an example.

Suppose we have three draggables - 'up', 's', and 'p'. Draggables 's', and 'p' have targets
on themselves. More specifically, 'p' has three targets - '1', '2', and '3'. The first
requirement is that 's', and 'p' are positioned on specific targets on the base image.
The second requirement is that draggable 'up' is positioned on specific targets of
draggable 'p'. Below is an excerpt from a problem.::

    <draggable id="up" icon="/static/images/images_list/lcao-mo/up.png" can_reuse="true" />

    <draggable id="s" icon="/static/images/images_list/lcao-mo/orbital_single.png" label="s orbital" can_reuse="true" >
        <target id="1" x="0" y="0" w="32" h="32"/>
    </draggable>

    <draggable id="p" icon="/static/images/images_list/lcao-mo/orbital_triple.png" can_reuse="true" label="p orbital" >
        <target id="1" x="0" y="0" w="32" h="32"/>
        <target id="2" x="34" y="0" w="32" h="32"/>
        <target id="3" x="68" y="0" w="32" h="32"/>
    </draggable>

    ...

    correct_answer = [
        {
            'draggables': ['p'],
            'targets': ['p-left-target', 'p-right-target'],
            'rule': 'unordered_equal'
        },
        {
            'draggables': ['s'],
            'targets': ['s-left-target', 's-right-target'],
            'rule': 'unordered_equal'
        },
        {
            'draggables': ['up'],
            'targets': ['p-left-target[p][1]', 'p-left-target[p][2]', 'p-right-target[p][2]', 'p-right-target[p][3]',],
            'rule': 'unordered_equal'
        }
    ]

Note that it is a requirement to specify rules for all draggables, even if some draggable gets included
in more than one chain.


Grading logic
=============

1. User answer (that comes from browser) and correct answer (from xml) are parsed to the same format::

    group_id: group_draggables, group_targets, group_rule


Group_id is ordinal number, for every dict in correct answer incremental
group_id is assigned: 0, 1, 2, ...

Draggables from user answer are added to same group_id where identical draggables
from correct answer are, for example::

    If correct_draggables[group_0] = [t1, t2] then
    user_draggables[group_0] are all draggables t1 and t2 from user answer:
    [t1] or [t1, t2] or [t1, t2, t2] etc..

2. For every group from user answer, for that group draggables, if 'number' is in  group rule, set() is applied,
if 'number' is not in rule, set is not applied::

    set() : [t1, t2, t3, t3] -> [t1, t2, ,t3]

For every group, at this step, draggables lists are equal.


3. For every group, lists of targets are compared using rule for that group.


Set and '+number' cases
.......................

Set() and '+number' are needed only for case of reusable draggables,
for other cases there are no equal draggables in list, so set() does nothing.

.. such long lines needed for sphinx to display nicely

* Usage of set() operation allows easily create rule for case of "any number of same draggable can be dragged to some targets"::

        {
                'draggables': ['draggable_1'],
                'targets': ['target3', 'target6', 'target9'],
                'rule': 'anyof'
        }




* 'number' rule is used for the case of reusable draggables, when one want to fix number of draggable to drag. In this example only two instances of draggables_1 are allowed to be dragged::

    {
            'draggables': ['draggable_1', 'draggable_1'],
            'targets': ['target3', 'target6', 'target9'],
            'rule': 'anyof+number'
    }


* Note, that in using rule 'exact', one does not need 'number', because you can't recognize from user interface which reusable draggable is on which target. Absurd example::

    {
            'draggables': ['draggable_1', 'draggable_1', 'draggable_2'],
            'targets': ['target3', 'target6', 'target9'],
            'rule': 'exact'
    }


    Correct handling of this example is to create different rules for draggable_1 and
    draggable_2

* For 'unordered_equal' (or 'exact' too) we don't need 'number' if you have only same draggable in group, as targets length will provide constraint for the number of draggables::

    {
            'draggables': ['draggable_1'],
            'targets': ['target3', 'target6', 'target9'],
            'rule': 'unordered_equal'
    }


    This means that only three draggaggables 'draggable_1' can be dragged.

* But if you have more that one different reusable draggable in list, you may use 'number' rule::

    {
            'draggables': ['draggable_1', 'draggable_1', 'draggable_2'],
            'targets': ['target3', 'target6', 'target9'],
            'rule': 'unordered_equal+number'
    }


    If not use number, draggables list will be setted to  ['draggable_1', 'draggable_2']
