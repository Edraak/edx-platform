(function (requirejs, require, define) {
define(['logme', 'draggable_events', 'draggable_logic', 'targets'], function (logme, draggableEvents, draggableLogic, Targets) {
    // REFACTOR: No init() method. Just return function.
    return {
        'init': init
    };

    function init(state) {
        state.config.draggables.every(function (draggable) {
            processDraggable(state, draggable);

            return true;
        });
    }

    // REFACTOR: Rename to 'callback'.
    function makeDraggableCopy(callbackFunc) {
        var draggableObj, property;

        // Make a full proper copy of the draggable object, with some modifications.
        draggableObj = {};
        for (property in this) {
            // REFACTOR: Use shorthand if.
            if (this.hasOwnProperty(property) === true) {
                draggableObj[property] = this[property];
            }
        }
        // The modifications to the draggable copy.
        draggableObj.isOriginal = false; // This new draggable is a copy.
        draggableObj.uniqueId = draggableObj.state.getUniqueId(); // Is newly set.
        draggableObj.stateDraggablesIndex = null; // Will be set.
        draggableObj.containerEl = null; // Not needed, since a copy will never return to a container element.
        draggableObj.iconEl = null; // Will be created.
        draggableObj.iconImgEl = null; // Will be created.
        draggableObj.labelEl = null; // Will be created.
        draggableObj.targetField = []; // Will be populated.

        // Create DOM elements and attach events.
        // REFACTOR: Use shorthand.
        if (draggableObj.originalConfigObj.icon.length > 0) {

            // REFACTOR: create iconEl object only once (currrently it is created in both if cases).
            draggableObj.iconEl = $('<div />');

            // REFACTOR: Use chaining.
            draggableObj.iconImgEl = $('<img />');
            draggableObj.iconImgEl.attr('src', draggableObj.originalConfigObj.icon);

            // REFACTOR: Pass callback. Not inlined function.
            // REFACTOR: chain iconImgEl.
            // REFACTOR: Move styling to CSS.
            draggableObj.iconImgEl.load(function () {

                draggableObj.iconEl.css({
                    'position': 'absolute',
                    'width': draggableObj.iconWidthSmall,
                    'height': draggableObj.iconHeightSmall,
                    'left': 50 - draggableObj.iconWidthSmall * 0.5,
                    // REFACTOR: Shorthand.
                    'top': ((draggableObj.originalConfigObj.label.length > 0) ? 5 : 50 - draggableObj.iconHeightSmall * 0.5)
                });
                draggableObj.iconImgEl.css({
                    'position': 'absolute',
                    'width': draggableObj.iconWidthSmall,
                    'height': draggableObj.iconHeightSmall,
                    'left': 0,
                    'top': 0
                });
                draggableObj.iconImgEl.appendTo(draggableObj.iconEl);

                // REFACTOR: Shorthand.
                if (draggableObj.originalConfigObj.label.length > 0) {
                    // REFACTOR: Use chainig.
                    draggableObj.labelEl = $(
                        '<div ' +
                            'style=" ' +
                                'position: absolute; ' +
                                'color: black; ' +
                                'font-size: 0.95em; ' +
                            '" ' +
                        '>' +
                            draggableObj.originalConfigObj.label +
                        '</div>'
                    );
                    draggableObj.labelEl.css({
                        'left': 50 - draggableObj.labelWidth * 0.5,
                        'top': 5 + draggableObj.iconHeightSmall + 5,
                        'min-width': draggableObj.labelWidth
                    });

                    draggableObj.attachMouseEventsTo('labelEl');
                }

                // REFACTOR: Move to separate function. The same code repeats in the below else condition.
                draggableObj.attachMouseEventsTo('iconEl');

                draggableObj.stateDraggablesIndex = draggableObj.state.draggables.push(draggableObj) - 1;

                // REFACTOR: Document why this is necessary.
                setTimeout(function () {
                    callbackFunc(draggableObj);
                }, 0);
            });
         } else { // REFACTOR: Use else if with condition from below.
            // REFACTOR: Shorthand.
            if (draggableObj.originalConfigObj.label.length > 0) {
            // REFACTOR: Move styling to CSS.
            // REFACTOR: Use chainig.
                draggableObj.iconEl = $(
                    '<div ' +
                        'style=" ' +
                            'position: absolute; ' +
                            'color: black; ' +
                            'font-size: 0.95em; ' +
                        '" ' +
                    '>' +
                        draggableObj.originalConfigObj.label +
                    '</div>'
                );
                draggableObj.iconEl.css({
                    'left': 50 - draggableObj.iconWidthSmall * 0.5,
                    'top': 50 - draggableObj.iconHeightSmall * 0.5
                });

                draggableObj.attachMouseEventsTo('iconEl');

                draggableObj.stateDraggablesIndex = draggableObj.state.draggables.push(draggableObj) - 1;

                // REFACTOR: Document why this is necessary.
                setTimeout(function () {
                    callbackFunc(draggableObj);
                }, 0);
            }
        }
    }

    function processDraggable(state, obj) {
        var draggableObj = {
            'uniqueId': state.getUniqueId(),
            'originalConfigObj': obj,
            'stateDraggablesIndex': null,
            'id': obj.id,
            'isReusable': obj.can_reuse,
            'isOriginal': true,
            'x': -1,
            'y': -1,
            'zIndex': 1,
            'containerEl': null,
            'iconEl': null,
            'iconImgEl': null,
            'iconElBGColor': null,
            'iconElPadding': null,
            'iconElBorder': null,
            'iconElLeftOffset': null,
            'iconWidth': null,
            'iconHeight': null,
            'iconWidthSmall': null,
            'iconHeightSmall': null,
            'labelEl': null,
            'labelWidth': null,
            'labelWidthSmall': null,
            'hasLoaded': false,
            'inContainer': true,
            'mousePressed': false,
            'onTarget': null,
            'onTargetIndex': null,
            'state': state,

            'mouseDown': draggableEvents.mouseDown,
            'mouseUp': draggableEvents.mouseUp,
            'mouseMove': draggableEvents.mouseMove,

            'checkLandingElement': draggableLogic.checkLandingElement,
            'checkIfOnTarget': draggableLogic.checkIfOnTarget,
            'snapToTarget': draggableLogic.snapToTarget,
            'correctZIndexes': draggableLogic.correctZIndexes,
            'moveBackToSlider': draggableLogic.moveBackToSlider,
            'moveDraggableTo': draggableLogic.moveDraggableTo,

            'makeDraggableCopy': makeDraggableCopy,

            'attachMouseEventsTo': draggableEvents.attachMouseEventsTo,

            'targetField': [],
            'numDraggablesOnMe': 0
        };
        // REFACTOR: Move styling to CSS.
        // REFACTOR: Use chainig.
        draggableObj.containerEl = $(
            '<div ' +
                'style=" ' +
                    'width: 100px; ' +
                    'height: 100px; ' +
                    'display: inline; ' +
                    'float: left; ' +
                    'overflow: hidden; ' +
                    'border-left: 1px solid #CCC; ' +
                    'border-right: 1px solid #CCC; ' +
                    'text-align: center; ' +
                    'position: relative; ' +
                '" ' +
                '></div>'
        );

        draggableObj.containerEl.appendTo(state.sliderEl);
        // REFACTOR: Shorthand.
        if (obj.icon.length > 0) {
            draggableObj.iconElBGColor = 'transparent';
            draggableObj.iconElPadding = 0;
            draggableObj.iconElBorder = 'none';
            draggableObj.iconElLeftOffset = 0;

            draggableObj.iconEl = $('<div />').css({
                'overflow': 'hidden'
            });
            // REFACTOR: Use chainig.
            draggableObj.iconImgEl = $('<img />');
            draggableObj.iconImgEl.attr('src', obj.icon);
            // REFACTOR: Pass callback. Not inlined function.
            draggableObj.iconImgEl.load(function () {
                draggableObj.iconWidth = this.width;
                draggableObj.iconHeight = this.height;
                
                if(draggableObj.state.config.autoResize){
                    if (draggableObj.iconWidth >= draggableObj.iconHeight) {
                        draggableObj.iconWidthSmall = 60;
                        draggableObj.iconHeightSmall = draggableObj.iconWidthSmall * (draggableObj.iconHeight / draggableObj.iconWidth);
                    } else {
                        draggableObj.iconHeightSmall = 60;
                        draggableObj.iconWidthSmall = draggableObj.iconHeightSmall * (draggableObj.iconWidth / draggableObj.iconHeight);
                    }
                } else {
                    draggableObj.iconHeightSmall = 30;
                    draggableObj.iconWidthSmall = draggableObj.iconHeightSmall * (draggableObj.iconWidth / draggableObj.iconHeight);
                }
                // REFACTOR: Move styling to CSS.
                draggableObj.iconEl.css({
                    'position': 'absolute',
                    'width': draggableObj.iconWidthSmall,
                    'height': draggableObj.iconHeightSmall,
                    'left': 50 - draggableObj.iconWidthSmall * 0.5,

                    // REFACTOR: Shorthand.
                     'top': ((obj.label.length > 0 || !draggableObj.state.config.autoResize) ? 37.5 : 50.0) - 0.5 * draggableObj.iconHeightSmall
                });
                
                draggableObj.iconImgEl.css({
                    'position': 'absolute',
                    'width': draggableObj.iconWidthSmall,
                    'height': draggableObj.iconHeightSmall,
                    'left': 0,
                    'top': 0
                });
                draggableObj.iconImgEl.appendTo(draggableObj.iconEl);
                draggableObj.iconEl.appendTo(draggableObj.containerEl);

                // Initially, when a draggable is created from the config JSON, it is placed in the slider.
                // At this time we must draw temporary targets.
                Targets.drawDummyTargets(draggableObj);
                // REFACTOR: Shorthand.
                if (obj.label.length > 0) {
                    // REFACTOR: Move styling to CSS.
                    // REFACTOR: Use chainig.
                    draggableObj.labelEl = $(
                        '<div ' +
                            'style=" ' +
                                'position: absolute; ' +
                                'color: black; ' +
                                'font-size: 0.95em; ' +

                                // This is really important. If we don't set this, then sometimes
                                // the text wraps when a draggable is moved beyong the right side of
                                // the entire DnD instance.
                                'white-space: nowrap; ' +
                            '" ' +
                        '>' +
                            obj.label +
                        '</div>'
                    );

                    draggableObj.labelEl.appendTo(draggableObj.containerEl);

                    // REFACTOR: Check why this must be done here, and not when you are creating labelEl.
                    draggableObj.labelEl.html(obj.shortLabel);



                    // REFACTOR: These are set to the same value. Why? a = b = c.width()
                    draggableObj.labelWidth = draggableObj.labelEl.width();
                    draggableObj.labelWidthSmall = draggableObj.labelEl.width();
                    
                    // If element has MathJax we hide it before processing
                    if (obj.isMathJax) {
                        draggableObj.labelEl.css({
                            'top': (!draggableObj.state.config.separateLabels) ? 42.5 + 0.5 * draggableObj.iconHeightSmall : 70,
                            'opacity': 0
                        });
                    } else {
                        draggableObj.labelEl.css({
                            'left': 50 - draggableObj.labelWidthSmall * 0.5,
                            'top': (!draggableObj.state.config.separateLabels) ? 42.5 + 0.5 * draggableObj.iconHeightSmall : 70,
                            'min-width': draggableObj.labelWidthSmall
                        });
                    }
                    
                    draggableObj.attachMouseEventsTo('labelEl');
                    
                    if (obj.isMathJax) {
                        MathJax.Hub.Queue(
                            ['Typeset', MathJax.Hub, draggableObj.labelEl[0]],
                            [function(){
                                // REFACTOR: Maybe this can be removed?
                                draggableObj.labelWidth = draggableObj.labelEl.width();
                                draggableObj.labelWidthSmall = draggableObj.labelEl.width();
                                
                                // REFACTOR: Maybe CSS classes can be used instead of .css()
                                draggableObj.labelEl
                                    .css({
                                        'left': 50 - draggableObj.labelWidthSmall * 0.5,
                                        'opacity': 1,
                                        'min-width': draggableObj.labelWidthSmall
                                    })
                                .children()
                                .filter('span, div')
                                    .css({
                                        'margin-top': '3px',
                                        'margin-bottom': '0',
                                        'text-align': 'center'
                                    })
                                .children()
                                    .css({
                                        'display': 'inline'
                                    })
                                .find('.math > span')
                                    .css({
                                        'font-size': '100%'
                                    })
                                .find('.mrow > span')
                                    .css({
                                        'color': '#000'
                                    });
                            }]
                        );
                    }    
                }

                draggableObj.hasLoaded = true;             
            });
        } else {
            // To make life easier, if there is no icon, but there is a
            // label, we will create a label and store it as if it was an
            // icon. All the existing code will work, and the user will
            // see a label instead of an icon.

            // REFACTOR: Shorthand.
            if (obj.label.length > 0) {
                draggableObj.iconElBGColor = state.config.labelBgColor;
                draggableObj.iconElPadding = 8;
                draggableObj.iconElBorder = '1px solid black';
                draggableObj.iconElLeftOffset = 9;

                // REFACTOR: Use chaining.
                draggableObj.iconEl = $(
                    '<div ' +
                        'style=" ' +
                            'position: absolute; ' +
                            'color: black; ' +
                            'font-size: 0.95em; ' +

                            // This is really important. If we don't set this, then sometimes
                            // the text wraps when a draggable is moved beyong the right side of
                            // the entire DnD instance.
                            'white-space: nowrap; ' +
                        '" ' +
                    '>' +
                        obj.label +
                    '</div>'
                );

                // The first time we append, we get the width of the label with the original text.
                draggableObj.iconEl.appendTo(draggableObj.containerEl);

                // If element has MathJax we hide it before processing
                if (obj.isMathJax) {
                    draggableObj.iconEl.css({
                        'opacity': 0,
                        'min-width': 60
                    });
                } 

                draggableObj.iconWidth = draggableObj.iconEl.width();
                draggableObj.iconHeight = draggableObj.iconEl.height();

                // Now we will change the label text to the short version, and record
                // the width of the resulting element.
                draggableObj.iconEl.html(obj.shortLabel);
                draggableObj.iconWidthSmall = draggableObj.iconEl.width();
                draggableObj.iconHeightSmall = draggableObj.iconEl.height();

                draggableObj.iconEl.css({
                    'left': 50 - draggableObj.iconWidthSmall * 0.5,
                    'top': (!draggableObj.state.config.separateLabels) ? 50 - draggableObj.iconHeightSmall * 0.5 : 70
                });

                draggableObj.hasLoaded = true;

                // REFACTOR: Below block is already used somewhere above. Move to separate function with parameters.
                if (obj.isMathJax) {
                    MathJax.Hub.Queue(
                        ["Typeset", MathJax.Hub, draggableObj.iconEl[0]],
                        [function(){
                            draggableObj.iconWidth = draggableObj.iconEl.width();
                            draggableObj.iconWidthSmall = draggableObj.iconEl.width();
                            
                            // REFACTOR: Try to move styles to CSS.
                            draggableObj.iconEl
                                .css({
                                    'left': 50 - draggableObj.iconWidthSmall * 0.5,
                                    'opacity': 1
                                })
                            .children()
                            .filter('span, div')
                                .css({
                                    'margin-top': '3px',
                                    'margin-bottom': '0',
                                    'text-align': 'center'
                                })
                            .children()
                                .css({
                                    'display': 'inline'
                                })
                            .find('.math > span')
                                .css({
                                    'font-size': '100%'
                                })
                            .find('.mrow > span')
                                .css({
                                    'color': '#000'
                                });
                        }]
                    );
                }
            
            } else {
                // If no icon and no label, don't create a draggable.
                return;
            }
        }

        draggableObj.attachMouseEventsTo('iconEl');
        draggableObj.attachMouseEventsTo('containerEl');

        state.numDraggablesInSlider += 1;
        draggableObj.stateDraggablesIndex = state.draggables.push(draggableObj) - 1;            
    }
}); // End-of: define(['logme', 'draggable_events', 'draggable_logic'], function (logme, draggableEvents, draggableLogic) {
}(RequireJS.requirejs, RequireJS.require, RequireJS.define)); // End-of: (function (requirejs, require, define) {
