(function (requirejs, require, define) {

define(
'video/055_sign_language_control.js',
['video/00_sign_language_state.js'],
function (SignLanguageState) {
    // SignLanguageControl() function - what this module "exports".
    return function (state) {
        var dfd = $.Deferred();

        // Changing sign-language for now only works for YouTube videos.
        if (state.videoType !== 'youtube') {
            state.el.find('a.sign-language').remove();
            return;
        }

        state.signLanguageControl = {};

        _makeFunctionsPublic(state);
        _renderElements(state);
        _bindHandlers(state);

        dfd.resolve();
        return dfd.promise();
    };

    // ***************************************************************
    // Private functions start here.
    // ***************************************************************

    // function _makeFunctionsPublic(state)
    //
    //     Functions which will be accessible via 'state' object. When called, these functions will
    //     get the 'state' object as a context.
    function _makeFunctionsPublic(state) {
        var methodsDict = {
            toggleSignLanguage: toggleSignLanguage,
            disableTooltip: disableTooltip,
            showTooltip: showTooltip
        };

        state.bindTo(methodsDict, state.signLanguageControl, state);
    }

    // function _renderElements(state)
    //
    //     Create any necessary DOM elements, attach them, and set their initial configuration. Also
    //     make the created DOM elements available via the 'state' object. Much easier to work this
    //     way - you don't have to do repeated jQuery element selects.
    function _renderElements(state) {
        state.signLanguageControl.el = state.el.find('a.sign-language');
        state.signLanguageControl.popoverEl = state.el.find('.sign-language-popover-container .popover');
        state.signLanguageControl.popoverCloseEl = state.el.find('.sign-language-popover-container .close');

        if (!state.config.nonSignLanguageVideoId) {
            // Non-sign language the video
            return;
        }

        state.signLanguageControl.el.show();
    }

    // function _bindHandlers(state)
    //
    //     Bind any necessary function callbacks to DOM events (click, mousemove, etc.).
    function _bindHandlers(state) {
        state.signLanguageControl.el.on('click',
            state.signLanguageControl.toggleSignLanguage
        );

        state.signLanguageControl.popoverCloseEl.on('click',
            state.signLanguageControl.disableTooltip
        );
    }

    // ***************************************************************
    // Public functions start here.
    // These are available via the 'state' object. Their context ('this' keyword) is the 'state' object.
    // The magic private function that makes them available and sets up their context is makeFunctionsPublic().
    // ***************************************************************

    // This function toggles the sign-language video
    function toggleSignLanguage(event) {
        var newIsActive = !SignLanguageState.getIsActive();
        event.preventDefault();

        SignLanguageState.setIsActive(newIsActive);
        this.trigger('videoPlayer.handleSignLanguageChange', newIsActive);

        if (!newIsActive) {
            // As a student, I would like to hide the tooltip when I disable the sign-language.
            this.signLanguageControl.disableTooltip();
        }
    }

    // Show the tooltip
    function showTooltip() {
        if (!this.config.nonSignLanguageVideoId ||
            this.signLanguageControl.isTooltipShown ||
            !SignLanguageState.shouldShowTooltip()) {
            return;
        }

        // To run this only once
        this.signLanguageControl.isTooltipShown = true;

        var popoverEl = this.signLanguageControl.popoverEl,
            buttonHeight = this.signLanguageControl.el.height(),
            offset = -32,
            popoverMarginTop = -(buttonHeight + offset);

        // Let the browser calculate the height, to position it correctly
        popoverEl.css({
            opacity: '0.01',
            display: 'block',
            visibility: 'hidden'
        });

        this.signLanguageControl.el.addClass('attention-grabbing');

        setTimeout(function () {
            popoverEl.css('visibility', 'visible');
            popoverMarginTop -= popoverEl.height();

            popoverEl.css('margin-top', popoverMarginTop + 'px');
            popoverEl.fadeTo(400, 1);
        }, 0);
    }

    // Disable the tooltip
    function disableTooltip(event) {
        if (event) {
            event.preventDefault();
        }

        SignLanguageState.disableTooltip();
        this.signLanguageControl.popoverEl.fadeOut();
        this.signLanguageControl.el.removeClass('attention-grabbing');
    }

});

}(RequireJS.requirejs, RequireJS.require, RequireJS.define));
