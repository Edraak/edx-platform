(function (define) {
'use strict';
define('video/loggers/pause_video.js', ['video/00_abstarct_logger.js'],
function (AbstractLogger) {
    var PauseVideoLogger = AbstractLogger.extend({
        watch: function (el) {
            el.on('pause', this.onPauseHandler.bind(this));
        },

        onPauseHandler: function (event, time) {
            this.log('pause_video', { currentTime: time });
        }
    });

    return PauseVideoLogger;
});
}(RequireJS.define));
