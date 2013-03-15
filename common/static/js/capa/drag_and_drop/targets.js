(function (requirejs, require, define) {
define(['logme'], function (logme) {
    return {
        'initializeBaseTargets': initializeBaseTargets,
        'initializeTargetField': initializeTargetField,
        'destroyTargetField': destroyTargetField,
        'drawDummyTargets': drawDummyTargets,
        'clearDummyTargets': clearDummyTargets
    };

    function initializeBaseTargets(state) {
        (function (c1) {
            while (c1 < state.config.targets.length) {
                processTarget(state, state.config.targets[c1]);

                c1 += 1;
            }
        }(0));
    }

    function initializeTargetField(draggableObj) {
        var iconElOffset;

        // TODO: Remove dummy targets.
        clearDummyTargets(draggableObj);

        if (draggableObj.targetField.length === 0) {
            draggableObj.originalConfigObj.target_fields.every(function (targetObj) {
                processTarget(draggableObj.state, targetObj, true, draggableObj);

                return true;
            });
        } else {
            iconElOffset = draggableObj.iconEl.position();

            draggableObj.targetField.every(function (targetObj) {
                targetObj.offset.top = iconElOffset.top + targetObj.y;
                targetObj.offset.left = iconElOffset.left + targetObj.x;

                return true;
            });
        }
    }

    function destroyTargetField(draggableObj) {
        var indexOffset, lowestRemovedIndex;

        indexOffset = 0;
        lowestRemovedIndex = draggableObj.state.targets.length + 1;

        draggableObj.targetField.every(function (target) {
            target.el.remove();

            if (lowestRemovedIndex > target.indexInStateArray) {
                lowestRemovedIndex = target.indexInStateArray;
            }

            draggableObj.state.targets.splice(target.indexInStateArray - indexOffset, 1);
            indexOffset += 1;

            return true;
        });

        draggableObj.state.targets.every(function (target) {
            if (target.indexInStateArray > lowestRemovedIndex) {
                target.indexInStateArray -= indexOffset;
            }

            return true;
        });

        draggableObj.targetField = [];
    }

    function drawDummyTargets(draggableObj, dontResize) {
        var borderCss, scaleFactor;

        // TODO.

        if (draggableObj.originalConfigObj.icon.length === 0) {
            return;
        }

        borderCss = '';
        if (draggableObj.state.config.targetOutline === true) {
            borderCss = 'border: 1px dashed gray; ';
        }

        if (dontResize !== true) {
            scaleFactor = draggableObj.iconWidthSmall / draggableObj.iconWidth;
        } else {
            scaleFactor = 1;
        }

        draggableObj.originalConfigObj.target_fields.every(function (obj) {
            draggableObj.iconEl.append(
                '<div ' +
                    'style=" ' +
                        'display: block; ' +
                        'position: absolute; ' +
                        'width: ' + (scaleFactor * obj.w) + 'px; ' +
                        'height: ' + (scaleFactor * obj.h) + 'px; ' +
                        'top: ' + (scaleFactor * obj.y) + 'px; ' +
                        'left: ' + (scaleFactor * obj.x) + 'px; ' +
                        borderCss +
                    '" ' +
                    'class="dummy_target" ' +
                '></div>'
            );

            return true;
        });
    }

    function clearDummyTargets(draggableObj) {
        // TODO.
        draggableObj.iconEl.find('.dummy_target').remove();
    }

    // When a target (it's config object) is of type grid, this method will create multiple
    // targets for it, laying them out in a grid.
    function processGridTarget(state, obj) {
        // We will create normal standard targets, and pass them back to processTarget()
        // method. However, each such targets will have an ID with a common prefix. This
        // ID will be formed like so:
        //
        //     gridId\{col\}\{row\}
        //
        // So, an example is:
        //
        //     targetX{0}{3}
        //
        // "targetX" is the ID (common prefix)
        // 0 is the col
        // 3 is the row

        var i, j, width, height;

        // Calculate the dimensions of each cell.
        width = Math.round(obj.w / obj.col);
        height = Math.round(obj.h / obj.row);

        // For each cell, create a normal target.
        for (i = 0; i < obj.col; i += 1) {
            for (j = 0; j < obj.row; j += 1) {
                processTarget(
                    state,
                    {
                        'id': obj.id + '{' + i + '}{' + j + '}',
                        'w': width,
                        'h': height,
                        'x': obj.x + i * width,
                        'y': obj.y + j * height
                    }
                );
            }
        }
    }

    // All targets will be the same. A target that is a grid in JSON config will
    // be split into multiple normal targets. So, in reality, there will not be
    // a need for a 'isGrid' property.

    function processTarget(state, obj, fromTargetField, draggableObj) {
        var targetEl, borderCss, numTextEl, targetObj;

        // If this is a "complex" grid case, pass it on to a dedicated handler.
        if (obj.type === 'grid') {
            processGridTarget(state, obj);

            return;
        }

        borderCss = '';
        if (state.config.targetOutline === true) {
            borderCss = 'border: 1px dashed gray; ';
        }

        targetEl = $(
            '<div ' +
                'style=" ' +
                    'display: block; ' +
                    'position: absolute; ' +
                    'width: ' + obj.w + 'px; ' +
                    'height: ' + obj.h + 'px; ' +
                    'top: ' + obj.y + 'px; ' +
                    'left: ' + obj.x + 'px; ' +
                    borderCss +
                '" ' +
            '></div>'
        );

        if (fromTargetField === true) {
            targetEl.appendTo(draggableObj.iconEl);
        } else {
            targetEl.appendTo(state.baseImageEl.parent());
        }

        targetEl.mousedown(function (event) {
            event.preventDefault();
        });

        if (state.config.onePerTarget === false) {
            numTextEl = $(
                '<div ' +
                    'style=" ' +
                        'display: block; ' +
                        'position: absolute; ' +
                        'width: 24px; ' +
                        'height: 24px; ' +
                        'top: ' + obj.y + 'px; ' +
                        'left: ' + (obj.x + obj.w - 24) + 'px; ' +
                        'border: 1px solid black; ' +
                        'text-align: center; ' +
                        'z-index: 500; ' +
                        'background-color: white; ' +
                        'font-size: 0.95em; ' +
                        'color: #009fe2; ' +
                        'cursor: pointer; ' +
                    '" ' +
                '>0</div>'
            );
        } else {
            numTextEl = null;
        }

        targetObj = {
            'uniqueId': state.getUniqueId(),

            'id': obj.id,

            'x': obj.x,
            'y': obj.y,

            'w': obj.w,
            'h': obj.h,

            'el': targetEl,
            'offset': targetEl.position(),

            'draggableList': [],

            'state': state,

            'targetEl': targetEl,

            'numTextEl': numTextEl,
            'updateNumTextEl': updateNumTextEl,

            'removeDraggable': removeDraggable,
            'addDraggable': addDraggable,

            'type': 'base',
            'draggableObj': null,

            'zIndex': null
        };

        if (fromTargetField === true) {
            targetObj.offset = draggableObj.iconEl.position();
            targetObj.offset.top += obj.y;
            targetObj.offset.left += obj.x;

            targetObj.type = 'on_drag';
            targetObj.draggableObj = draggableObj;

            targetObj.zIndex = draggableObj.zIndex;
        } else {
            // This is a normal target that sits on the base image. It is the lowest of all
            // possible targets. It gets the lowest z-index possible - zero (0).
            targetObj.zIndex = 0;
        }

        if (state.config.onePerTarget === false) {
            numTextEl.appendTo(state.baseImageEl.parent());
            numTextEl.mousedown(function (event) {
                event.preventDefault();
            });
            numTextEl.mouseup(function () {
                cycleDraggableOrder.call(targetObj)
            });
        }

        targetObj.indexInStateArray = state.targets.push(targetObj) - 1;

        if (fromTargetField === true) {
            draggableObj.targetField.push(targetObj);
        }
    }

    function removeDraggable(draggable) {
        var c1;

        this.draggableList.splice(draggable.onTargetIndex, 1);

        // An item from the array was removed. We need to updated all indexes accordingly.
        // Shift all indexes down by one if they are higher than the index of the removed item.
        c1 = 0;
        while (c1 < this.draggableList.length) {
            if (this.draggableList[c1].onTargetIndex > draggable.onTargetIndex) {
                this.draggableList[c1].onTargetIndex -= 1;
            }

            c1 += 1;
        }

        draggable.onTarget = null;
        draggable.onTargetIndex = null;

        if (this.type === 'on_drag') {
            this.draggableObj.numDraggablesOnMe -= 1;
        }

        this.updateNumTextEl();
    }

    function addDraggable(draggable) {
        draggable.onTarget = this;
        draggable.onTargetIndex = this.draggableList.push(draggable) - 1;

        if (this.type === 'on_drag') {
            this.draggableObj.numDraggablesOnMe += 1;
        }

        this.updateNumTextEl();
    }

    /*
     * function cycleDraggableOrder
     *
     * Parameters:
     *     none - This function does not expect any parameters.
     *
     * Returns:
     *     undefined - The return value of this function is not used.
     *
     * Description:
     *     Go through all draggables that are on the current target, and decrease their
     *     z-index by 1, making sure that the bottom-most draggable ends up on the top.
     */
    function cycleDraggableOrder() {
        var c1, lowestZIndex, highestZIndex;

        if (this.draggableList.length < 2) {
            return;
        }

        highestZIndex = -10000;
        lowestZIndex = 10000;

        for (c1 = 0; c1 < this.draggableList.length; c1 += 1) {
            if (this.draggableList[c1].zIndex < lowestZIndex) {
                lowestZIndex = this.draggableList[c1].zIndex;
            }

            if (this.draggableList[c1].zIndex > highestZIndex) {
                highestZIndex = this.draggableList[c1].zIndex;
            }
        }

        for (c1 = 0; c1 < this.draggableList.length; c1 += 1) {
            if (this.draggableList[c1].zIndex === lowestZIndex) {
                this.draggableList[c1].zIndex = highestZIndex;
            } else {
                this.draggableList[c1].zIndex -= 1;
            }

            this.draggableList[c1].iconEl.css('z-index', this.draggableList[c1].zIndex);
            if (this.draggableList[c1].labelEl !== null) {
                this.draggableList[c1].labelEl.css('z-index', this.draggableList[c1].zIndex);
            }
        }
    }

    function updateNumTextEl() {
        if (this.numTextEl !== null) {
            this.numTextEl.html(this.draggableList.length);
        }
    }
}); // End-of: define(['logme'], function (logme) {
}(RequireJS.requirejs, RequireJS.require, RequireJS.define)); // End-of: (function (requirejs, require, define) {
