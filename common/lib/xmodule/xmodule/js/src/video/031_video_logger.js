(function(define) {
'use strict';
define('video/031_video_logger.js',
    [
        'video/00_loggers/load_video.js', 'video/00_loggers/pause_video.js',
        'video/00_loggers/play_video.js', 'video/00_loggers/watch_video.js',
        'video/00_loggers/transcript_video.js',
        'video/00_loggers/speed_video.js', 'video/00_loggers/seek_video.js'
    ],
function(
    LoadVideoLogger, PauseVideoLogger, PlayVideoLogger, WatchVideoLogger,
    TranscriptVideoLogger, SpeedVideoLogger, SeekVideoLogger
) {
    var VideoLogger = function(state, i18n) {
        if (!(this instanceof VideoLogger)) {
            return new VideoLogger(state, i18n);
        }

        this.initialize(state);

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
        initialize: function(state) {
            this.state = state;
            this.state.VideoLogger = this;
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
        LoadVideoLogger, PauseVideoLogger, PlayVideoLogger, WatchVideoLogger,
        TranscriptVideoLogger, SpeedVideoLogger, SeekVideoLogger
    ]);

    return VideoLogger;
});
}(RequireJS.define));
