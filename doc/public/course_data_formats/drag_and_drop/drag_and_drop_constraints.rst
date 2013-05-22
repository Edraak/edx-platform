*************************
Drag and drop constraints
*************************

.. module:: drag_and_drop_constraints

Constraints in the answer format
================================

Along with ``draganddrop.grade(submission[0], correct_answer)`` grading you can use some additional type of grading – **constraints**.

After you get all information about objects, with next line of code:

.. code-block:: python

    draggables = draganddrop.get_all_dragabbles(submission[0], xml)

you can use `draggables` in a different ways.

`draggables` support:

    .. glossary::

        getting by key (id)
            ``draggables['draggable_id']`` return all draggables with id equal to 'draggable_id'.
            Return object with type – `DraggableSet`.

`DraggableSet` support next feature:

    .. glossary::

        `getting by index`
            ``draggables['draggable_id'][n]`` – return n-th (n starts from 0) draggables with id equal to 'draggable_id', using order by X and then by Y coordinate. So, the main order by Y-coordinate, and if Y-coordinate the same, first object will be the object with lower X-coordinate. (0,0) – top left corner.
            Return object with type – `Draggable`.

        `count`
            ``draggables['draggable_id'].count`` – return numbers of all draggables with id equal to 'draggable_id'.
            Return object with type – `int`.

        `on`
            ``draggables['draggable_id'].on('draggable_target')`` – return all draggables with id equal to 'draggable_id', which lays on the target 'draggable_target'.
            Return object with type – `DraggableSet`.

`Draggable` support next feature:

    .. glossary::

        `x`
            ``draggables['draggable_id'][0].x`` – return value of X coordinate of first draggables with id == 'draggable_id' (X-coordinate on the base image where the top left corner of the target will be positioned).
            Return object with type – `float`.
        `y`
            ``draggables['draggable_id'][0].y`` – return value of X coordinate of first draggables with id == 'draggable_id' (Y-coordinate on the base image where the top left corner of the target will be positioned).
            Return object with type – `float`.

        `contains`
            ``draggables['draggable_id'][0].contains('draggable_id1', 'draggable_id2', ...)`` – return True if first draggables with id == 'draggable_id' contains some numbers of draggables, which you can define like the arguments. This method support permutation of contained draggables.
            With options `exact` you can define strict contains or not. `exact` equal to `True` means, that current draggable must contains exactly these draggables, and not other. By default `exact` == `True`.
            Return object with type – `bool`.


Simple examples of usage
========================

    ``draggables`` – whole targets object. 
    ``draggables['p']`` – return all draggables with id == 'p'.

    ``draggables['p'].count()`` – return numbers of all draggables with id == 'p'.

    ``draggables['p'][0]`` – return first draggables with id == 'p', using order by Y coordinate (sorting by Y coordinate of draggables). This object have has two properties: `x` (value of X coordinate) and `y` (value of X coordinate).

    ``draggables['p'][0].x`` – return value of X coordinate of first draggables with id == 'p' (X-coordinate on the base image where the top left corner of the target will be positioned).

    ``draggables['p'][0].y`` – return value of Y coordinate of first draggables with id == 'p' (Y-coordinate on the base image where the top left corner of the target will be positioned).

    ``draggables['p'].on('left-side')`` – return all draggables with id == 'p', which lays on the target 'left-side'.

    ``draggables['p'].on('left-side').count()`` – return numbers of all draggables with id == 'p', which lays on the target 'left-side'.
    
    ``draggables['p'].on('left-side')[0]`` – return first draggables with id == 'p', which lays on the target 'left-side', using order by Y coordinate (sorting by Y coordinate of draggables). This object have has two properties: `x` (value of X coordinate) and `y` (value of X coordinate).

    ``draggables['p'].on('left-side')[0].x`` – return value of X coordinate of first draggables with id == 'p', which lays on the target 'left-side' (X-coordinate on the base image where the top left corner of the target will be positioned).

    ``draggables['p'].on('left-side')[0].y`` – return value of Y coordinate of first draggables with id == 'p', which lays on the target 'left-side' (Y-coordinate on the base image where the top left corner of the target will be positioned).

    ``draggables['p'][0].contains('a', 'b', 'b')`` – return True if first draggables with id == 'p' contains three draggables: one 'a' and two 'b'. Current draggables 'p' **can't** contains any other draggables. `Contains` – means that current draggable has target in which lays some draggables object.

    ``draggables['p'][0].contains('a', 'b', 'b', exact=False)`` – return True if first draggables with id == 'p' contains three draggables: one 'a' and two 'b'. Draggables 'p' also **may** contains other draggables.

One of the real example, how can you use this feature::

    correct_answer = [
        {'draggables': ['p'], 'targets': ['left-side', 'right-side'], 'rule': 'unordered_equal'},
        {'draggables': ['s'], 'targets': ['left-side', 'right-side'], 'rule': 'unordered_equal'},
        {'draggables': ['s-sigma'], 'targets': ['center-side'], 'rule': 'exact'},
        {'draggables': ['s-sigma*'], 'targets': ['center-side'], 'rule': 'exact'},
        {'draggables': ['p-pi'], 'targets': ['center-side'], 'rule': 'exact'},
        {'draggables': ['p-sigma'], 'targets': ['center-side'], 'rule': 'exact'},
        {'draggables': ['p-pi*'], 'targets': ['center-side'], 'rule': 'exact'},
        {'draggables': ['p-sigma*'], 'targets': ['center-side'], 'rule': 'exact'},
        {
            'draggables': ['up_and_down'],
            'targets': ['left-side[s][1]', 'right-side[s][1]', 'center-side[s-sigma][1]', 'center-side[s-sigma*][1]', 'center-side[p-pi][1]', 'center-side[p-pi][2]'],
            'rule': 'unordered_equal'
        },
        {
            'draggables': ['up'],
            'targets': ['left-side[p][1]', 'left-side[p][2]', 'right-side[p][2]', 'right-side[p][3]',],
            'rule': 'unordered_equal'
        }
    ]

    # Do not remove this!
    orbitals = draganddrop.get_all_dragabbles(submission[0], xml) 

    constraints = [
        orbitals['p'].on('left-side').count == 1,
        orbitals['s'].on('left-side').count == 1,
        orbitals['p'].on('right-side').count == 1,
        orbitals['s'].on('right-side').count == 1,
        orbitals['s-sigma'].on('center-side').count == 1,
        orbitals['s-sigma*'].on('center-side').count == 1,
        orbitals['p-pi'].on('center-side').count == 1,
        orbitals['p-sigma'].on('center-side').count == 1,
        orbitals['p-pi*'].on('center-side').count == 1,
        orbitals['p-sigma*'].on('center-side').count == 1,

        orbitals['p'].on('left-side')[0].y < orbitals['s'].on('left-side')[0].y,
        orbitals['p'].on('right-side')[0].y < orbitals['s'].on('right-side')[0].y,

        orbitals['s-sigma'].on('center-side')[0].y > orbitals['s-sigma*'].on('center-side')[0].y,
        orbitals['s-sigma*'].on('center-side')[0].y > orbitals['p-pi'].on('center-side')[0].y,
        orbitals['p-pi'].on('center-side')[0].y > orbitals['p-sigma'].on('center-side')[0].y,
        orbitals['p-sigma'].on('center-side')[0].y > orbitals['p-pi*'].on('center-side')[0].y,
        orbitals['p-pi*'].on('center-side')[0].y > orbitals['p-sigma*'].on('center-side')[0].y,

        orbitals['s'].on('left-side')[0].y == orbitals['s'].on('right-side')[0].y,
        orbitals['s'].on('left-side')[0].y > orbitals['s-sigma*'].on('center-side')[0].y,
        orbitals['s'].on('left-side')[0].y < orbitals['s-sigma'].on('center-side')[0].y,

        orbitals['p'].on('left-side')[0].y == orbitals['p'].on('right-side')[0].y,
        orbitals['p'].on('left-side')[0].y > orbitals['p-pi*'].on('center-side')[0].y,
        orbitals['p'].on('left-side')[0].y < orbitals['p-sigma'].on('center-side')[0].y
    ]

    if draganddrop.grade(submission[0], correct_answer) and all(constraints):
        correct = ['correct']
    else:
        correct = ['incorrect']

.. note::

    You can use any mathematical operations and python functions to deal with your goals.

.. note::

    ``on()`` and ``contains()`` expect, that some draggable have place, where this draggable lays. And place – it's a base target or any other draggables. For example: 'base_target', 'base_target[draggable]', 'base_target[draggable1][internal_target][draggable2]', etc. So, we do not support base_target[draggable][internal_target] !

.. warning::

    If analyzer has some trouble with conditions, for example: ``draggables['NONEXISTENT_ID'][0].x > 10``, then for applying any operation to this property ``draggables['NONEXISTENT_ID'][0].x`` return ``False``. So, ``draggables['NONEXISTENT_ID'][0].x > 10`` or ``draggables['NONEXISTENT_ID'][0].x < 10`` or ``draggables['NONEXISTENT_ID'][0].x == 10`` return ``False``. But, ``not draggables['NONEXISTENT_ID'][0].x > 10`` obviously return ``True``, and this is not, that we expect. According to this, you should use inversed operation ``draggables['NONEXISTENT_ID'][0].x <= 10``, and keep in mind about that behaviour.
