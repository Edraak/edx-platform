(function (undefined) {
    'use strict';
    describe('VideoProgressSlider', function () {
        var state, oldOTBD;

        beforeEach(function () {
            oldOTBD = window.onTouchBasedDevice;
            window.onTouchBasedDevice = jasmine.createSpy('onTouchBasedDevice')
                .andReturn(null);
        });

        afterEach(function () {
            $('source').remove();
            window.onTouchBasedDevice = oldOTBD;
            state.storage.clear();
        });

        describe('constructor', function () {
            describe('on a non-touch based device', function () {
                beforeEach(function () {
                    spyOn($.fn, 'slider').andCallThrough();

                    state = jasmine.initializePlayer();
                });

                it('build the slider', function () {
                    expect(state.videoProgressSlider.slider).toBe('.slider');
                    expect($.fn.slider).toHaveBeenCalledWith({
                        range: 'min',
                        slide: jasmine.any(Function),
                        stop: jasmine.any(Function)
                    });
                });

                it('build the seek handle', function () {
                    expect($('.slider .ui-slider-handle')).toExist();
                });
            });

            describe('on a touch-based device', function () {
                it('does not build the slider on iPhone', function () {

                    window.onTouchBasedDevice.andReturn(['iPhone']);

                    state = jasmine.initializePlayer();

                    expect(state.videoProgressSlider).toBeUndefined();

                    // We can't expect $.fn.slider not to have been called,
                    // because sliders are used in other parts of Video.
                });
                $.each(['iPad', 'Android'], function (index, device) {
                    it('build the slider on ' + device, function () {
                        window.onTouchBasedDevice.andReturn([device]);

                        state = jasmine.initializePlayer();

                        expect(state.videoProgressSlider.slider).toBeDefined();
                    });
                });
            });
        });

        describe('updatePlayTime', function () {
            beforeEach(function () {
                state = jasmine.initializePlayer();
            });

            xdescribe('when frozen', function () {
                beforeEach(function () {
                    spyOn($.fn, 'slider').andCallThrough();
                    state.videoProgressSlider.frozen = true;
                    state.videoProgressSlider.updatePlayTime(20, 120);
                });

                it('does not update the slider', function () {
                    expect($.fn.slider).not.toHaveBeenCalled();
                });
            });

            describe('when not frozen', function () {
                beforeEach(function () {
                    spyOn($.fn, 'slider').andCallThrough();
                    state.videoProgressSlider.updatePlayTime(20, 120);
                });

                it('update the max and current values of the slider', function () {
                    expect($.fn.slider).toHaveBeenCalledWith(
                        'option', {
                            'max': 120,
                            'value': 20
                    });
                });
            });
        });

        describe('onSlide', function () {
            beforeEach(function () {
                state = jasmine.initializePlayer();

                spyOn($.fn, 'slider').andCallThrough();
                spyOn(state.videoPlayer, 'onSlideSeek').andCallThrough();
            });

            // Disabled 12/30/13 due to flakiness in master
            xit('freeze the slider', function () {
                state.videoProgressSlider.onSlide(
                    jQuery.Event('slide'), { value: 20 }
                );

                expect(state.videoProgressSlider.frozen).toBeTruthy();
            });

            // Disabled 12/30/13 due to flakiness in master
            xit('trigger seek event', function () {
                state.videoProgressSlider.onSlide(
                    jQuery.Event('slide'), { value: 20 }
                );

                expect(state.videoPlayer.onSlideSeek).toHaveBeenCalled();
            });
        });

        describe('onStop', function () {

            beforeEach(function () {
                jasmine.Clock.useMock();

                state = jasmine.initializePlayer();

                spyOn(state.videoPlayer, 'onSlideSeek').andCallThrough();
            });

            // Disabled 12/30/13 due to flakiness in master
            xit('freeze the slider', function () {
                state.videoProgressSlider.onStop(
                    jQuery.Event('stop'), { value: 20 }
                );

                expect(state.videoProgressSlider.frozen).toBeTruthy();
            });

            // Disabled 12/30/13 due to flakiness in master
            xit('trigger seek event', function () {
                state.videoProgressSlider.onStop(
                    jQuery.Event('stop'), { value: 20 }
                );

                expect(state.videoPlayer.onSlideSeek).toHaveBeenCalled();
            });

            // Disabled 12/30/13 due to flakiness in master
            xit('set timeout to unfreeze the slider', function () {
                state.videoProgressSlider.onStop(
                    jQuery.Event('stop'), { value: 20 }
                );

                jasmine.Clock.tick(200);

                expect(state.videoProgressSlider.frozen).toBeFalsy();
            });
        });

        it('getRangeParams' , function () {
            var testCases = [
                    {
                        startTime: 10,
                        endTime: 20,
                        duration: 150
                    },
                    {
                        startTime: 90,
                        endTime: 100,
                        duration: 100
                    },
                    {
                        startTime: 0,
                        endTime: 200,
                        duration: 200
                    }
                ];

            state = jasmine.initializePlayer();

            $.each(testCases, function (index, testCase) {
                var step = 100/testCase.duration,
                    left = testCase.startTime*step,
                    width = testCase.endTime*step - left,
                    expectedParams = {
                        left: left + '%',
                        width: width + '%'
                    },
                    params = state.videoProgressSlider.getRangeParams(
                        testCase.startTime, testCase.endTime, testCase.duration
                    );

                expect(params).toEqual(expectedParams);
            });
        });

        describe('notifyThroughHandleEnd', function () {
            beforeEach(function () {
                state = jasmine.initializePlayer();
                this.handle = $('.ui-slider-handle');
                this.handle.css({
                    'display': 'block',
                    'height': 10,
                    'width': 10
                });
            });

            it('we see \'Video ended\' if video is ended', function () {
                state.el.trigger('ended', [10]);
                expect(this.handle).toHaveAttr('title', 'Video ended');
                expect(this.handle).toBeFocused();
            });

            it('we see \'Video position\' if video plays', function () {
                state.el.trigger('progress', [10]);
                expect(this.handle).toHaveAttr('title', 'Video position');
                expect(this.handle).not.toBeFocused();
            });
        });

        describe('getTimeDescription', function () {
            beforeEach(function () {
                var el;

                spyOn(_, 'debounce').andCallFake(function (f) { return f; });
                state = jasmine.initializePlayer();
                el = state.videoProgressSlider.el;
                this.slider = el.find('.ui-slider-handle');
            });

            it('0 seconds on initialization', function () {
                var expected = '0 seconds';

                expect(this.slider).toHaveAttr('aria-valuetext', expected);
            });

            it('0 seconds to be 0 seconds', function () {
                var expected = '0 seconds';

                state.videoProgressSlider.rewind(0);
                expect(this.slider).toHaveAttr('aria-valuetext', expected);
            });

            it('1 second to be 1 second', function () {
                var expected = '1 second';

                state.videoProgressSlider.rewind(1);
                expect(this.slider).toHaveAttr('aria-valuetext', expected);
            });

            it('10 seconds to be 10 seconds', function () {
                var expected = '10 seconds';

                state.videoProgressSlider.rewind(10);
                expect(this.slider).toHaveAttr('aria-valuetext', expected);
            });

            it('60 seconds to be 1 minute', function () {
                var expected = '1 minute';

                state.videoProgressSlider.rewind(60);
                expect(this.slider).toHaveAttr('aria-valuetext', expected);
            });

            it('121 seconds to be 2 minutes 1 second', function () {
                var expected = '2 minutes 1 second';

                state.videoProgressSlider.rewind(121);
                expect(this.slider).toHaveAttr('aria-valuetext', expected);
            });

            it('3600 seconds to be 1 hour', function () {
                var expected = '1 hour';

                state.videoProgressSlider.rewind(3600);
                expect(this.slider).toHaveAttr('aria-valuetext', expected);
            });

            it('3610 seconds to be 1 hour 10 seconds', function () {
                var expected = '1 hour 10 seconds';

                state.videoProgressSlider.rewind(3610);
                expect(this.slider).toHaveAttr('aria-valuetext', expected);
            });

            it('3670 seconds to be 1 hour 1 minute 10 seconds', function () {
                var expected = '1 hour 1 minute 10 seconds';

                state.videoProgressSlider.rewind(3670);
                expect(this.slider).toHaveAttr('aria-valuetext', expected);
            });

            it('21541 seconds to be 5 hours 59 minutes 1 second', function () {
                var expected = '5 hours 59 minutes 1 second';

                state.videoProgressSlider.rewind(21541);
                expect(this.slider).toHaveAttr('aria-valuetext', expected);
            });
        });
    });

}).call(this);
