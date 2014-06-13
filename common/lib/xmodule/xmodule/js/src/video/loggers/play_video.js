(function (define) {
'use strict';
define('video/loggers/play_video.js', ['video/00_abstarct_logger.js'],
function (AbstractLogger) {
    var PlayVideoLogger = AbstractLogger.extend({
        watch: function (el) {
            el.on('play', this.onPlayHandler.bind(this));
        },

        onPlayHandler: function (event, time) {
            this.log('play_video', { currentTime: time });
        }
    });

    return PlayVideoLogger;
});
}(RequireJS.define));
