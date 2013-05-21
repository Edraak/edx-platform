**********************************************
XML format of drag and drop input [inputtypes]
**********************************************

.. module:: drag_and_drop_input

Format description
==================

The main tag of Drag and Drop (DnD) input is::

    <drag_and_drop_input> ... </drag_and_drop_input>

``drag_and_drop_input`` can include any number of the following 2 tags:
``draggable`` and ``target``.

drag_and_drop_input tag
-----------------------

The main container for a single instance of DnD. The following attributes can
be specified for this tag::

    img - Relative path to an image that will be the base image. All draggables
        can be dragged onto it.
    [target_outline | false] - Specify whether an outline (gray dashed line) should be
        drawn around targets (if they are specified). It can be either
        'true' or 'false'.
    [auto_resize | true] - Specify whether we must auto resize image on draggables.
    [separate_labels|false] - Specify whether labels should be separated from
        the image on draggables.
    [one_per_target | true] - Specify whether to allow more than one draggable to be
        placed onto a single target. It can be either 'true' or 'false'.
    [no_labels | false] - in default behaviour if label is not set, label
        is obtained from id. If no_labels is true, labels are not automatically
        populated from id, and one can not set labels and obtain only icons.

draggable tag
-------------

Draggable tag specifies a single draggable object which has the following
attributes::

    id - Unique identifier of the draggable object.
    label - Human readable label that will be shown to the user.
    icon - Relative path to an image that will be shown to the user.
    can_reuse - true or false, default is false. If true, same draggable can be
    used multiple times.

A draggable is what the user must drag out of the slider and place onto the
base image. After a drag operation, if the center of the draggable ends up
outside the rectangular dimensions of the image, it will be returned back
to the slider.

In order for the grader to work, it is essential that a unique ID
is provided. Otherwise, there will be no way to tell which draggable is at what
coordinate, or over what target. Label and icon attributes are optional. If
they are provided they will be used, otherwise, you can have an empty
draggable. The path is relative to 'course_folder' folder, for example,
/static/images/img1.png.

target tag
----------

Target tag specifies a single target object which has the following required
attributes::

    id – Unique identifier of the target object.
    x – X-coordinate on the base image where the top left corner of the target
        will be positioned.
    y – Y-coordinate on the base image where the top left corner of the target
        will be positioned.
    w – Width of the target.
    h – Height of the target.
    [type | normal] – Define type of target (value = "normal"/"grid"):
        "normal" – usual behaviour
        "grid" – target will be divided into a grid cells
    [row | 1] – number of rows (only using, when type = "grid")
    [col | 1] – number of columns (only using, when type = "grid")

A target specifies a place on the base image where a draggable can be
positioned. By design, if the center of a draggable lies within the target
(i.e. in the rectangle defined by [[x, y], [x + w, y + h]], then it is within
the target. Otherwise, it is outside.

If at lest one target is provided, the behavior of the client side logic
changes. If a draggable is not dragged on to a target, it is returned back to
the slider.

If no targets are provided, then a draggable can be dragged and placed anywhere
on the base image.

Targets on draggables
---------------------

Sometimes it is not enough to have targets only on the base image, and all of the
draggables on these targets. If a complex problem exists where a draggable must
become itself a target (or many targets), then the following extended syntax
can be used: ::

    <draggable {attribute list}>
        <target {attribute list} />
        <target {attribute list} />
        <target {attribute list} />
        ...
    </draggable>

The attribute list in the tags above ('draggable' and 'target') is the same as for
normal 'draggable' and 'target' tags. The only difference is when you will be
specifying inner target position coordinates. Using the 'x' and 'y' attributes you
are setting the offset of the inner target from the upper-left corner of the
parent draggable (that contains the inner target).

Limitations of targets on draggables
------------------------------------

1.) Currently there is a limitation to the level of nesting of targets.

Even though you can pile up a large number of draggables on targets that themselves
are on draggables, the Drag and Drop instance will be graded only in the case if
there is a maximum of two levels of targets. The first level are the "base" targets.
They are attached to the base image. The second level are the targets defined on
draggables.

2.) Another limitation is that the target bounds are not checked against
other targets.

For now, it is the responsibility of the person who is constructing the course
material to make sure that there is no overlapping of targets. It is also preferable
that targets on draggables are smaller than the actual parent draggable. Technically
this is not necessary, but from the usability perspective it is desirable.

3.) You can have targets on draggables only in the case when there are base targets
defined (base targets are attached to the base image).

If you do not have base targets, then you can only have a single level of nesting
(draggables on the base image). In this case the client side will be reporting (x,y)
positions of each draggables on the base image.


Logic flow
==========

(Click on image to see full size version.)

.. image:: draganddrop_logic_flow.png
    :width: 100%
    :target: _images/draganddrop_logic_flow.png


Rules and constraints
=====================

We have two type of conditions, which you can define for DnD objects: rules and constraints.

.. note::
    Please, use **constraints** – it's a new way of DnD conditions.

.. toctree::
   :maxdepth: 2

   drag_and_drop_rules.rst
   drag_and_drop_constraints.rst


Examples
========

Here yo can find many examples of <drag_and_drop_input> and rules/constraints.

.. toctree::
   :maxdepth: 2

   drag_and_drop_examples.rst
