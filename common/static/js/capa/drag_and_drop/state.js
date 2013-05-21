(function (requirejs, require, define) {
define([], function () {
    return State;

    function State(problemId) {

        // REFACTOR: Style - one line defs.
        var state;

        // REFACTOR: Style - names without quotes.
        state = {
            'config': null,

            'baseImageEl': null,
            'baseImageLoaded': false,

            'containerEl': null,

            'sliderEl': null,

            'problemId': problemId,

            'draggables': [],
            'numDraggablesInSlider': 0,
            'currentMovingDraggable': null,

            'targets': [],

            'updateArrowOpacity': null,

            'uniqueId': 0,
            'salt': makeSalt(),

            'getUniqueId': getUniqueId,

            'normalizeEvent': normalizeEvent
        };

        // REFACTOR: Use .on()
        $(document).mousemove(function (event) {
            documentMouseMove(state, event);
        });

        return state;
    }

    // REFACTOR: Move utility code to separate file. Later put on wiki.
    function getUniqueId() {
        this.uniqueId += 1;

        return this.salt + '_' + this.uniqueId.toFixed(0);
    }

    function makeSalt() {
        var text, possible, i;

        text = '';
        possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

        for(i = 0; i < 5; i += 1) {
            text += possible.charAt(Math.floor(Math.random() * possible.length));
        }

        return text;
    }

    function documentMouseMove(state, event) {
        // REFACTOR: ate.currentMovingDraggable should be cached.

        if (state.currentMovingDraggable !== null) {
            // We need to make sure that event.pageX, and event.pageY behave in the same way
            // across diffrent browsers. This 'fix' was applied after it was discovered that
            // in IE10 you could not drag properly if the page was scrolled down or right.
            state.normalizeEvent(event);

            state.currentMovingDraggable.iconEl.css(
                'left',
                event.pageX -
                    state.baseImageEl.offset().left -
                    state.currentMovingDraggable.iconWidth * 0.5
                    - state.currentMovingDraggable.iconElLeftOffset
            );
            state.currentMovingDraggable.iconEl.css(
                'top',
                event.pageY -
                    state.baseImageEl.offset().top -
                    state.currentMovingDraggable.iconHeight * 0.5
            );

            if (state.currentMovingDraggable.labelEl !== null) {
                state.currentMovingDraggable.labelEl.css({
                    'left':
                        event.pageX -
                            state.baseImageEl.offset().left -
                            state.currentMovingDraggable.labelWidth * 0.5
                            - 9, // Account for padding, border.
                    'top':
                        event.pageY -
                            state.baseImageEl.offset().top +
                            state.currentMovingDraggable.iconHeight * 0.5 +
                            5,
                    'min-width': state.currentMovingDraggable.labelWidth
                });
            }
        }
    }

    function normalizeEvent(event) {
        event.pageX = event.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
        event.pageY = event.clientY + document.body.scrollTop + document.documentElement.scrollTop;
    }
}); // End-of: define([], function () {
}(RequireJS.requirejs, RequireJS.require, RequireJS.define)); // End-of: (function (requirejs, require, define) {
