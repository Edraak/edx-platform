(function (define) {
'use strict';
define('video/loggers/load_video.js', ['video/00_abstarct_logger.js'],
function (AbstractLogger) {
    var LoadVideoLogger = AbstractLogger.extend({
        watch: function (element) {
            element.on('ready', this.onLoadVideoHandler.bind(this));
        },

        onLoadVideoHandler: function () {
            this.log('load_video');
        }
    });

    return LoadVideoLogger;
});
}(RequireJS.define));
