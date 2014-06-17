(function (define) {
'use strict';
define('video/00_loggers/play_video.js', ['video/00_abstarct_logger.js'],
function (AbstractLogger) {
    var PlayVideoLogger = AbstractLogger.extend({
        watch: function (el) {
            el.on('play', this.onPlayHandler.bind(this));
        },

        onPlayHandler: function (event, options) {
            this.log('play_video', { currentTime: options.time });
        }
    });

    return PlayVideoLogger;
});
}(RequireJS.define));
