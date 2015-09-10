(function (define) {
'use strict';
define('video/04_sign_language_control.js', ['video/00_sign_language_state.js'], function (SignLanguageState) {
    /**
     * Sign language control module.
     * @exports video/04_sign_language_control.js
     * @constructor
     * @param {Object} state The object containing the state of the video
     * @param {Object} i18n The object containing strings with translations
     * @return {jquery Promise}
     */
    var SignLanguageControl = function (state, i18n) {
        if ('youtube' !== state.videoType) {
            // Changing sign-language for now only works for YouTube videos.
            return;
        }

        if (!(this instanceof SignLanguageControl)) {
            return new SignLanguageControl(state, i18n);
        }

        _.bindAll(this, 'toggleSignLanguage', 'disableTooltip', 'showTooltip', 'destroy');

        this.state = state;
        this.state.videoSignLanguageControl = this;
        this.i18n = i18n;
        this.initialize();

        return $.Deferred().resolve().promise();
    };

    SignLanguageControl.prototype = {
        template: [
            '<a href="#" title="',
                // Translators: Edraak-specific
                gettext('Toggle Sign Language'),
                '" class="sign-language is-hidden" role="button" aria-disabled="true">',
                    // This isn't really useful for blind people anyway, right?',
                    // Translators: Edraak-specific
                    gettext('Toggle Sign Language'),
            '</a>'
        ].join(''),
        popoverContainerTemplate: [
            '<div class="sign-language-popover-container">',
                '<div class="popover top">',
                    '<div class="arrow"></div>',
                    '<div class="popover-content">',
                        '<div class="close">',
                            '<span>&times;</span>',
                        '</div>',
                        '<div class="icon"></div>',
                        '<p>',
                            // Translators: Edraak-specific'
                            gettext('Click on the sign language button to disable and enable the sign language subtitling.'),
                        '</p>',
                    '</div>',
                '</div>',
            '</div>'
        ].join(''),
        initialize: function () {
            this.el = $(this.template);
            this.popoverContainerEl = $(this.popoverContainerTemplate);
            this.popoverEl = this.popoverContainerEl.find('.popover');
            this.popoverCloseEl = this.popoverEl.find('.close');

            this.render();
            this.bindHandlers();

        },
        render: function () {
            this.state.el.find('.secondary-controls').prepend(this.el);
            this.el.after(this.popoverContainerEl);

            if (!this.state.config.nonSignLanguageVideoId) {
                // Non-sign language the video
                return;
            }

            this.el.show();
        },
        bindHandlers: function () {
            this.el.on('click', this.toggleSignLanguage);
            this.popoverCloseEl.on('click', this.disableTooltip);

            this.state.el.on({
                'destroy': this.destroy
            });
        },
        destroy: function () {
            delete this.popoverCloseEl;

            this.el.remove();
            this.popoverContainerEl.remove();

            this.state.el.off('destroy', this.destroy);

            delete this.state.videoSignLanguageControl;
        },
        /** This function toggles the sign-language video */
        toggleSignLanguage: function (event) {
            var newIsActive = !SignLanguageState.getIsActive();
            event.preventDefault();

            SignLanguageState.setIsActive(newIsActive);
            this.state.trigger('videoPlayer.handleSignLanguageChange', newIsActive);

            if (!newIsActive) {
                // As a student, I would like to hide the tooltip when I disable the sign-language.
                this.disableTooltip();
            }
        },
        /** Show the sign-language help tooltip */
        showTooltip: function () {
            if (!this.state.config.nonSignLanguageVideoId ||
                this.isTooltipShown || !SignLanguageState.shouldShowTooltip()) {
                return;
            }

            // To run this only once
            this.isTooltipShown = true;

            var buttonHeight = this.el.height(),
                offset = -32,
                popoverMarginTop = -(buttonHeight + offset),
                self = this;

            // Let the browser calculate the height, to position it correctly
            this.popoverEl.css({
                opacity: '0.01',
                display: 'block',
                visibility: 'hidden'
            });

            this.el.addClass('attention-grabbing');

            setTimeout(function () {
                self.popoverEl.css('visibility', 'visible');
                popoverMarginTop -= self.popoverEl.height();

                self.popoverEl.css('margin-top', popoverMarginTop + 'px');
                self.popoverEl.fadeTo(400, 1);
            }, 0);
        },
        /** Hide and disable the sign-language help tooltip */
        disableTooltip: function () {
            if (event) {
                event.preventDefault();
            }

            SignLanguageState.disableTooltip();
            this.popoverEl.fadeOut();
            this.el.removeClass('attention-grabbing');
        }
    };

    return SignLanguageControl;
});
}(RequireJS.define));
