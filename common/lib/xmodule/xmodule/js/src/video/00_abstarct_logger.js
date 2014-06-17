(function (define) {
'use strict';
define('video/00_abstarct_logger.js', ['video/00_component.js'],
function (Component) {
    var AbstractLogger = Component.extend({
        debugMode: true,
        initialize: function (state) {
            this.state = state;
            this.element = this.state.el;
            this.id = this.state.id;
            this.watch(this.state.el, this.state);
            this.logger = window.Logger;
        },

        getData: function (data) {
            var extra = _.isFunction(this.extraData) ? this.extraData() : null;

            return $.extend(true, {}, data, {
                id: this.id,
                code: this.getCode()
            }, extra);
        },

        getCurrentTime: function () {
            return this.state.videoPlayer.currentTime;
        },

        log: function (eventName, data) {
            data = this.getData(data);
            this.logger.log(eventName, data);
            this.debug(eventName, data);
        },

        bind: function (eventName, data) {
            this.logger.bind(eventName, data);
            this.logger.listen(eventName, this.element, this.debug.bind(this));
        },

        debug: function () {
            if (this.debugMode) { console.log.apply(console, arguments); }
        },

        getCode: function () {
            return this.state.isYoutubeType() ?
                this.state.youtubeId() :
                'html5';
        },

        watch: function (el, state) {
            throw new Error('Please implement `watch` method.');
        },

        getStartEndTimes: function () {
            var startTime = this.state.config.startTime,
                endTime = this.state.config.endTime,
                duration = this.state.videoPlayer.duration();

            if (this.range && duration === this.range.duration) {
                return this.range;
            }

            if (startTime >= duration) {
                startTime = 0;
            }

            if (endTime <= startTime || endTime >= duration) {
                endTime = duration;
            }

            if (this.state.isFlashMode()) {
                startTime /= Number(this.state.speed);
                endTime /= Number(this.state.speed);
            }

            this.range = {
                start: startTime,
                end: endTime,
                size: endTime - startTime,
                duration: duration
            };

            return this.range;
        }
    });

    return AbstractLogger;
});
}(RequireJS.define));
