(function (define) {
'use strict';
define('video/00_loggers/pause_video.js', ['video/00_abstarct_logger.js'],
function (AbstractLogger) {
    var PauseVideoLogger = AbstractLogger.extend({
        watch: function (el) {
            el.on('pause', this.onPauseHandler.bind(this));
        },

        onPauseHandler: function (event, options) {
            this.log('pause_video', { currentTime: options.time });
        }
    });

    return PauseVideoLogger;
});
}(RequireJS.define));
