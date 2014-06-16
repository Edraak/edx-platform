(function (define) {
'use strict';
define('video/loggers/transcript_video.js', ['video/00_abstarct_logger.js'],
function (AbstractLogger) {
    var TranscriptVideoLogger = AbstractLogger.extend({
        watch: function (el) {
            el.on(
                'captions:visibilitychange', this.onTranscriptHandler.bind(this)
            );
        },

        onTranscriptHandler: function () {
            var eventName = (options.visible ? 'show' : 'hide') + '_transcript';

            this.log(eventName, { currentTime: this.getCurrentTime() });
        }
    });

    return TranscriptVideoLogger;
});
}(RequireJS.define));
