(function(define) {
'use strict';
define('video/031_video_logger.js',
    [
        'video/00_abstarct_logger.js', 'video/loggers/load_video.js',
        'video/loggers/pause_video.js', 'video/loggers/play_video.js',
        'video/loggers/watch_video.js'
    ],
function(
    AbstractLogger, LoadVideoLogger, PauseVideoLogger, PlayVideoLogger,
    WatchVideoLogger
) {
    var VideoLogger = function(state, i18n) {
        if (!(this instanceof VideoLogger)) {
            return new VideoLogger(state, i18n);
        }

        this.initialize(state, i18n);

        return $.Deferred().resolve().promise();
    };

    VideoLogger.addLogger = function(logger) {
        VideoLogger.loggers = VideoLogger.loggers || [];
        if ($.isFunction(logger)) {
            VideoLogger.loggers.push(logger);
        }
    };

    VideoLogger.addLoggers = function(loggersList) {
        $.each(loggersList, function(index, logger) {
            VideoLogger.addLogger(logger);
        });
    };

    VideoLogger.prototype = {
        initialize: function(state, i18n) {
            this.state = state;
            this.state.VideoLogger = this;
            this.i18n = i18n;
            this.activeLoggers = $.map(this.getLoggers(), function(Logger) {
                return new Logger(state);
            });
        },

        getLoggers: function() {
            return VideoLogger.loggers;
        },

        getActiveLoggers: function() {
            return this.activeLoggers;
        }
    };

    VideoLogger.addLoggers([
        LoadVideoLogger, PauseVideoLogger, PlayVideoLogger, WatchVideoLogger
    ]);

    return VideoLogger;
});
}(RequireJS.define));
