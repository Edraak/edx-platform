(function (define) {
'use strict';
define('video/loggers/speed_video.js', ['video/00_abstarct_logger.js'],
function (AbstractLogger) {
    var SpeedVideoLogger = AbstractLogger.extend({
        watch: function (el) {
            el.on(
                'speedchange', this.onSpeedHandler.bind(this)
            );
        },

        onSpeedHandler: function (event, speed) {
            var time = this.getCurrentTime();

            if (this.state.isFlashMode()) {
                time = Time.convert(
                    time,
                    parseFloat(this.state.speed),
                    speed
                );
            }

            speed = parseFloat(speed).toFixed(2).replace(/\.00$/, '.0');

            this.log('speed_change_video', {
                current_time: time,
                old_speed: this.state.speed,
                new_speed: speed
            });


            this.log(eventName, { currentTime: options.time });
        }
    });

    return SpeedVideoLogger;
});
}(RequireJS.define));
