(function (define) {
'use strict';
define('video/00_loggers/watch_video.js', ['video/00_abstarct_logger.js'],
function (AbstractLogger) {
    var WatchVideoLogger = AbstractLogger.extend({
        watch: function (element) {
            this.createSegmentsList();
            element.on({
                'play': this.onPlayHandler.bind(this),
                'pause': this.onPauseHandler.bind(this),
                'ended': this.onEndedHandler.bind(this),
                'seek': this.onSeekHandler.bind(this),
                'progress': this.onProgressHandler.bind(this)
            });
            this.bindLoggerOnUnload();
        },

        createSegmentsList: function () {
            this.segmentsList = new SegmentsList();
            return this.segmentsList;
        },

        getSegmentsList: function () {
            return this.segmentsList || this.createSegmentsList();
        },

        createSegment: function (time) {
            var segment = this.getSegmentsList().getLast();

            if (!segment || segment.isDone()) {
                this.getSegmentsList().add(new Segment(time || 0));
            }

            return this;
        },

        finishSegment: function (value) {
            var segment = this.getSegmentsList().getLast();

            return segment ? segment.end(value) : null;
        },

        extraData: function () {
            this.finishSegment(this.getCurrentTime());
            return {
                percent: this.getSegmentsList().toArray()
            };
        },

        onPlayHandler: function (event, options) {
            this.createSegment(options.time);
        },

        onProgressHandler: function (event, time) {
            // do nothing right now
        },

        onSeekHandler: function (event, options) {
            if (options.sendLogs) {
                this.finishSegment(options.oldTime);
                this.createSegment(options.time);
            }
        },

        onPauseHandler: function (event, options) {
            this.finishSegment(options.time);
        },

        onEndedHandler: function (event, options) {
            this.finishSegment(options.time);
        },

        bindLoggerOnUnload: function () {
            this.state.el.on('play', _.once(function () {
                this.bind('edx.video.watched', this.getData.bind(this));
            }.bind(this)));
        }
    });


    var SegmentsList = function () {
        this.list = [];
    };

    SegmentsList.prototype = {
        add: function (segment) {
            if (segment instanceof Segment) {
                this.list.push(segment);
            }

            return this;
        },

        getLast: function () {
            return _.last(this.list);
        },

        toArray: function () {
            return $.map(this.list, function (segment) {
                return segment.toArray();
            });
        }
    };


    var Segment = function (start, end) {
        this.segment = [];

        if (start) {
            this.start(start);
        }
        if (end) {
            this.end(end);
        }
    };

    Segment.prototype = {
        isDone: function () {
            return _.isNumber(this.segment[0]) && _.isNumber(this.segment[1]);
        },

        updatePosition: function (index, value) {
            if (!_.isNumber(this.segment[index])) {
                this.segment[index] = value;
            }

            return this;
        },

        start: function (value) {
            return this.updatePosition(0, value);
        },

        end: function (value) {
            return this.updatePosition(1, value);
        },

        toArray: function () {
            return [this.segment];
        }
    };

    return WatchVideoLogger;
});
}(RequireJS.define));
