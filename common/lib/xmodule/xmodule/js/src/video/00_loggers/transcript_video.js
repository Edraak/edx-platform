(function (define) {
'use strict';
define('video/00_loggers/transcript_video.js', ['video/00_abstarct_logger.js'],
function (AbstractLogger) {
    var TranscriptVideoLogger = AbstractLogger.extend({
        watch: function (el) {
            el.on(
                'captions:visibilitychange', this.onTranscriptHandler.bind(this)
            );
        },

        onTranscriptHandler: function (options) {
            if (options.sendLogs) {
                var eventName = options.visible ? 'show' : 'hide';

                this.log(eventName + '_transcript', {
                    currentTime: this.getCurrentTime()
                });
            }
        }
    });

    return TranscriptVideoLogger;
});
}(RequireJS.define));
