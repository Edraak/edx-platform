(function (define) {
'use strict';
define('video/00_loggers/seek_video.js', ['video/00_abstarct_logger.js'],
function (AbstractLogger) {
    var SeekVideoLogger = AbstractLogger.extend({
        watch: function (el) {
            el.on('seek', this.onSeekHandler.bind(this));
        },

        onSeekHandler: function (event, options) {
            if (options.sendLogs) {
                this.log('seek_video', {
                    old_time: options.time,
                    new_time: options.suggestedTime,
                    type: options.type
                });
            }
        }
    });

    return SeekVideoLogger;
});
}(RequireJS.define));
