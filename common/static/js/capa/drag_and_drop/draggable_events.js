(function (requirejs, require, define) {
define(['logme', 'targets'], function (logme, Targets) {
return {
    'attachMouseEventsTo': function (element) {
        var self;

        self = this;

        this[element].mousedown(function (event) {
            self.mouseDown(event);
        });
        this[element].mouseup(function (event) {
            self.mouseUp(event);
        });
        this[element].mousemove(function (event) {
            self.mouseMove(event);
        });
    },

    'mouseDown': function (event) {
        if (this.mousePressed === false) {
            // So that the browser does not perform a default drag.
            // If we don't do this, each drag operation will
            // potentially cause the highlghting of the dragged element.
            event.preventDefault();
            event.stopPropagation();

            if (this.numDraggablesOnMe > 0) {
                return;
            }

            // If this draggable is just being dragged out of the
            // container, we must perform some additional tasks.
            if (this.inContainer === true) {
                if ((this.isReusable === true) && (this.isOriginal === true)) {
                    this.makeDraggableCopy(function (draggableCopy) {
                        draggableCopy.mouseDown(event);
                    });

                    return;
                }

                if (this.isOriginal === true) {
                    this.containerEl.hide();
                    this.iconEl.detach();
                }

                if (this.iconImgEl !== null) {
                    this.iconImgEl.css({
                        'width': this.iconWidth,
                        'height': this.iconHeight
                    });
                }

                // We need to make sure that event.pageX, and event.pageY behave in the same way
                // across diffrent browsers. This 'fix' was applied after it was discovered that
                // in IE10 you could not drag properly if the page was scrolled down or right.
                this.state.normalizeEvent(event);

                this.iconEl.css({
                    'background-color': this.iconElBGColor,
                    'padding-left': this.iconElPadding,
                    'padding-right': this.iconElPadding,
                    'border': this.iconElBorder,
                    'width': this.iconWidth,
                    'height': this.iconHeight,
                    'left': event.pageX - this.state.baseImageEl.offset().left - this.iconWidth * 0.5 - this.iconElLeftOffset,
                    'top': event.pageY - this.state.baseImageEl.offset().top - this.iconHeight * 0.5
                });
                this.iconEl.appendTo(this.state.baseImageEl.parent());

                if (this.labelEl !== null) {
                    if (this.isOriginal === true) {
                        this.labelEl.detach();
                    }
                    this.labelEl.css({
                        'background-color': this.state.config.labelBgColor,
                        'padding-left': 8,
                        'padding-right': 8,
                        'border': '1px solid black',
                        'left': event.pageX - this.state.baseImageEl.offset().left - this.labelWidth * 0.5 - 9, // Account for padding, border.
                        'top': event.pageY - this.state.baseImageEl.offset().top + this.iconHeight * 0.5 + 5,
                        'min-width': this.labelWidth
                    });
                    this.labelEl.appendTo(this.state.baseImageEl.parent());
                }

                // When a draggable is being removed from the slider, the temporary targets that were drawn on it
                // must be cleared (because they were drawn using the small dimensions), and new temporary targets
                // must be drawn using the full dimensions.
                Targets.clearDummyTargets(this);
                Targets.drawDummyTargets(this, true);

                // When removing a draggable from the slider, we must change the label to the origian,
                // unshortened version.
                if (this.originalConfigObj.label.length > 0) {
                    // Depending on whether we have only a lable, or it is an image with a label,
                    // the text must be updated in different objects.
                    if (this.originalConfigObj.icon.length > 0) {
                        this.labelEl.html(this.originalConfigObj.label);
                    } else {
                        this.iconEl.html(this.originalConfigObj.label);
                    }
                }

                this.inContainer = false;
                if (this.isOriginal === true) {
                    this.state.numDraggablesInSlider -= 1;
                }
            }

            this.zIndex = 1000;
            this.iconEl.css('z-index', '1000');
            if (this.labelEl !== null) {
                this.labelEl.css('z-index', '1000');
            }

            this.mousePressed = true;
            this.state.currentMovingDraggable = this;
        }
    },

    'mouseUp': function () {
        if (this.mousePressed === true) {
            this.state.currentMovingDraggable = null;

            this.checkLandingElement();
        }
    },

    'mouseMove': function (event) {
        if (this.mousePressed === true) {
            // Because we have also attached a 'mousemove' event to the
            // 'document' (that will do the same thing), let's tell the
            // browser not to bubble up this event. The attached event
            // on the 'document' will only be triggered when the mouse
            // pointer leaves the draggable while it is in the middle
            // of a drag operation (user moves the mouse very quickly).
            event.stopPropagation();

            // We need to make sure that event.pageX, and event.pageY behave in the same way
            // across diffrent browsers. This 'fix' was applied after it was discovered that
            // in IE10 you could not drag properly if the page was scrolled down or right.
            this.state.normalizeEvent(event);

            this.iconEl.css({
                'left': event.pageX - this.state.baseImageEl.offset().left - this.iconWidth * 0.5 - this.iconElLeftOffset,
                'top': event.pageY - this.state.baseImageEl.offset().top - this.iconHeight * 0.5
            });

            if (this.labelEl !== null) {
                this.labelEl.css({
                    'left': event.pageX - this.state.baseImageEl.offset().left - this.labelWidth * 0.5 - 9, // Acoount for padding, border.
                    'top': event.pageY - this.state.baseImageEl.offset().top + this.iconHeight * 0.5 + 5,
                    'min-width': this.labelWidth
                });
            }
        }
    }
}; // End-of: return {
}); // End-of: define(['logme'], function (logme) {
}(RequireJS.requirejs, RequireJS.require, RequireJS.define)); // End-of: (function (requirejs, require, define) {
