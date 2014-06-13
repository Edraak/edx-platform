(function (define) {
'use strict';
define('video/loggers/watch_video.js', ['video/00_abstarct_logger.js'],
function (AbstractLogger) {
    var WatchVideoLogger = AbstractLogger.extend({
        size: 100,
        watch: function (element) {
            this.coef = 1;
            element.on('play', _.once(this.onPlayHandler.bind(this)));
        },

        getWatchedProgress: function () {
            var timeline = this.getTimeline();

            return _.compact(timeline).length * this.coef;
        },

        createTimeline: function () {
            return [];
        },

        getTimeline: function () {
            return this.timeline || this.createTimeline();
        },

        isPositionWatched: function (position) {
            var timeline = this.getTimeline();

            return timeline[position];
        },

        markPositionAsWatched: function (position) {
            var timeline = this.getTimeline();

            timeline[position] = 1;
        },

        getData: function () {
            return {
                id: this.id,
                code: this.getCode(),
                percent: this.getWatchedProgress()
            };
        },

        bindOnProgressHandler: function () {
            this.element.on('progress.watched_logger', _.throttle(
                this.onProgressHandler.bind(this), this.waitTime,
                { leading: true, trailing: true }
            ));
        },

        unBindOnProgressHandler: function () {
            this.element.off('progress.watched_logger');
        },

        onPlayHandler: function () {
            setTimeout(function () {
                var interval;

                this.range = this.getStartEndTimes();
                interval = 1000 * this.range.size;
                // event `progress` triggers with interval 200 ms.
                this.waitTime = Math.max(interval/this.size, 200);

                // We're going to receive 1-2 events `progress` for each
                // timeline position for the small videos to be more precise and
                // to avoid some issues with invoking of timers.
                if (this.waitTime <= 1000) {
                    this.size = interval / 1000;
                    this.coef = 100 / this.size;
                }

                this.timeline = this.getTimeline();
                this.bindOnProgressHandler();
                this.bindLoggerOnUnload();
            }.bind(this), 0);
        },

        onProgressHandler: function (event, time) {
            var seconds = Math.floor(time);

            if (this.range.start <= seconds && seconds <= this.range.end) {
                var position = Math.floor(
                    (time - this.range.start) * this.size / this.range.size
                );

                if (!this.isPositionWatched(position)) {
                    this.markPositionAsWatched(position);
                }
            }
        },

        bindLoggerOnUnload: function () {
            this.bind('edx.video.watched', this.getData.bind(this));
        }
    });

    return WatchVideoLogger;
});
}(RequireJS.define));
