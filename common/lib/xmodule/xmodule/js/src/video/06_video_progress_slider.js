(function(define) {
'use strict';
// VideoProgressSlider module.
define(
'video/06_video_progress_slider.js', [],
function() {
    /**
     * Video progress slider module.
     * @exports video/06_video_progress_slider.js
     * @constructor
     * @param {Object} state The object containing the state of the video
     * @param {Object} i18n The object containing strings with translations.
     * @return {jquery Promise}
     */
    var ProgressSlider = function(state, i18n) {
        if (!(this instanceof ProgressSlider)) {
            return new ProgressSlider(state, i18n);
        }

        this.state = state;
        this.state.videoProgressSlider = this;
        this.i18n = i18n;
        this.initialize();

        return $.Deferred().resolve().promise();
    };

    ProgressSlider.prototype = {
        /** Step to increase/decrease volume level via keyboard. */
        step: 20,

        /** Initializes the module. */
        initialize: function() {
            this.el = this.state.el.find('.video-controls .slider');
            this.render();
            this.a11y = new Accessibility(this.el, this.slider, this.i18n);
            this.bindHandlers();
        },

        /**
         * Creates any necessary DOM elements, attach them, and set their,
         * initial configuration.
         */
        render: function() {
            this.slider = this.el.slider({
                range: 'min',
                slide: this.onSlide.bind(this),
                stop: this.onStop.bind(this)
            });

            this.sliderProgress = this.slider
                .find('.ui-slider-range.ui-widget-header.ui-slider-range-min');
        },

        /** Bind any necessary function callbacks to DOM events. */
        bindHandlers: function() { },


        // Rebuild the slider start-end range (if it doesn't take up the
        // whole slider). Remember that endTime === null means the end-time
        // is set to the end of video by default.
        updateStartEndTimeRegion: function (params) {
            var start, end, duration, rangeParams;

            // We must have a duration in order to determine the area of range.
            // It also must be non-zero.
            if (!params.duration) {
                return;
            } else {
                duration = params.duration;
            }

            start = this.state.config.startTime;
            end = this.state.config.endTime;

            if (start > duration) {
                start = 0;
            } else if (this.state.isFlashMode()) {
                start /= Number(this.state.speed);
            }

            // If end is set to null, or it is greater than the duration of the
            // video, then we set it to the end of the video.
            if (end === null || end > duration) {
                end = duration;
            } else if (this.state.isFlashMode()) {
                end /= Number(this.state.speed);
            }

            // Don't build a range if it takes up the whole slider.
            if (start === 0 && end === duration) {
                return;
            }

            // Because JavaScript has weird rounding rules when a series of
            // mathematical operations are performed in a single statement, we
            // will split everything up into smaller statements.
            //
            // This will ensure that visually, the start-end range aligns nicely
            // with actual starting and ending point of the video.

            rangeParams = this.getRangeParams(start, end, duration);

            if (!this.sliderRange) {
                this.sliderRange = $('<div />', {
                    'class': 'ui-slider-range ' +
                             'ui-widget-header ' +
                             'ui-corner-all ' +
                             'slider-range'
                })
                .css({
                    left: rangeParams.left,
                    width: rangeParams.width
                });

                this.sliderProgress.after(this.sliderRange);
            } else {
                this.sliderRange.css(rangeParams);
            }
        },

        getRangeParams: function (startTime, endTime, duration) {
            var step = 100 / duration,
                left = startTime * step,
                width = endTime * step - left;

            return {
                left: left + '%',
                width: width + '%'
            };
        },

        onSlide: function (event, ui) {
            console.log('onSlide');
            var time = ui.value,
                duration = this.state.videoPlayer.duration();

            this.state.trigger(
                'videoControl.updateVcrVidTime',
                {
                    time: time,
                    duration: duration
                }
            );

            this.state.trigger(
                'videoPlayer.onSlideSeek',
                {'type': 'onSlideSeek', 'time': time}
            );

            this.a11y.update(this.state.videoPlayer.currentTime);

            event.stopPropagation();
        },

        updatePlayTime: function (params) {
            var time = Math.floor(params.time),
                duration = Math.floor(params.duration);

            if (this.slider) {
                this.slider.slider('option', {
                    'max': duration,
                    'value': time
                });
            }
        }
    };

    /**
     * Module responsible for the accessibility of volume controls.
     * @constructor
     * @private
     * @param {jquery $} button The volume button.
     * @param {Number} min Minimum value for the volume slider.
     * @param {Number} max Maximum value for the volume slider.
     * @param {Object} i18n The object containing strings with translations.
     */
    var Accessibility = function (el, slider, i18n) {
        this.el = el;
        this.slider = slider;
        this.handle = slider.find('.ui-slider-handle');
        this.i18n = i18n;

        this.initialize();
    };

    Accessibility.prototype = {
        /** Initializes the module. */
        initialize: function() {
            // ARIA
            // We just want the knob to be selectable with keyboard
            this.el.attr('tabindex', -1);
            this.handle.attr({
                'role': 'slider',
                'title': this.i18n['Video position'],
                'aria-disabled': false,
                'aria-valuetext': this.getTimeDescription(
                    this.slider.slider('option', 'value')
                )
            });
        },

        update: function (value) {
            this.handle.attr('aria-valuetext', this.getTimeDescription(value));
        },

        // When the video stops playing (either because the end was reached, or
        // because endTime was reached), the screen reader must be notified that
        // the video is no longer playing. We do this by a little trick. Setting
        // the title attribute of the slider know to "video ended", and focusing
        // on it. The screen reader will read the attr text.
        //
        // The user can then tab his way forward, landing on the next control
        // element, the Play button.
        //
        // @param params  -  object with property `end`. If set to true, the
        // function must set the title attribute to `video ended`;
        // if set to false, the function must reset the attr to it's original
        // state.
        // This function will be triggered from VideoPlayer methods onEnded(),
        // onPlay(), and update() (update method handles endTime).
        notifyThroughHandleEnd: function (params) {
            if (params.end) {
                this.handle.attr('title', this.i18n['Video ended']).focus();
            } else {
                this.handle.attr('title', this.i18n['Video position']);
            }
        },

        // Returns a string describing the current time of video in
        // `%d hours %d minutes %d seconds` format.
        getTimeDescription: function (time) {
            var seconds = Math.floor(time),
                minutes = Math.floor(seconds / 60),
                hours = Math.floor(minutes / 60),
                i18n = function (value, word) {
                    var msg;

                    switch(word) {
                        case 'hour':
                        // @TODO i18n
                            msg = ngettext(
                                '%(value)s hour', '%(value)s hours', value
                            );
                            break;
                        case 'minute':
                        // @TODO i18n
                            msg = ngettext(
                                '%(value)s minute', '%(value)s minutes', value
                            );
                            break;
                        case 'second':
                        // @TODO i18n
                            msg = ngettext(
                                '%(value)s second', '%(value)s seconds', value
                            );
                            break;
                    }
                    return interpolate(msg, {'value': value}, true);
                };

            seconds = seconds % 60;
            minutes = minutes % 60;

            if (hours) {
                return  i18n(hours, 'hour') + ' ' +
                        i18n(minutes, 'minute') + ' ' +
                        i18n(seconds, 'second');
            } else if (minutes) {
                return  i18n(minutes, 'minute') + ' ' +
                        i18n(seconds, 'second');
            }

            return i18n(seconds, 'second');
        }
    };

    return ProgressSlider;
});
}(RequireJS.define));

