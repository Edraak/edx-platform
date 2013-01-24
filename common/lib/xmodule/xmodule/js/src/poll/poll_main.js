(function (requirejs, require, define) { define('PollMain', ['logme'], function (logme) { return {

'submitAnswer': function (event, pollObj) {
    // Create data that is going to be sent to the server.
    pollObj.data = {
        'answer': pollObj.element.find('input:checked').val()
    };

    logme('We are sending the following data: ' + JSON.stringify(pollObj.data));

    // Send the data to the server as an AJAX request. Attach a callback that will
    // be fired on server's response.
    $.postWithPrefix(
        pollObj.ajax_url + '/submit_answer',
        pollObj.data,
        function (response) {
            var color;

            logme('The following response was received: ' + JSON.stringify(response));

            // Parse the answer from server.
            if (response.hasOwnProperty('success') === true) {
                color = 'green';
            } else {
                color = 'red';
            }

            // Show the answer from server.
            pollObj.graph_answer.css({
                'width': 400,
                'height': 400,
                'margin-left': 'auto',
                'margin-right': 'auto',
                'margin-bottom': 15
            });
            pollObj.graph_answer.show();

            // Show the next poll in series, and disable the current poll's submit and radio buttons.
            if (pollObj.nextPollObj !== null) {
                pollObj.nextPollObj.element.show();
            }
            pollObj.answer_button.children('input').each(function (index, value) {
                $(value).prop('disabled', true);
            });
            pollObj.vote_blocks.find('input').each(function (index, value) {
                $(value).prop('disabled', true);
            });

            jQuery.plot(
                pollObj.graph_answer,
                [
                    [[1, 57]],
                    [[2, 32]]
                ],
                {
                    'xaxis': {
                        'min': 0,
                        'max': 3,
                        'tickFormatter': function formatter(val, axis) {
                            var valStr;

                            valStr = val.toFixed(axis.tickDecimals);

                            if (valStr === '1.0') {
                                return 'Yes'
                            } else if (valStr === '2.0') {
                                return 'No';
                            } else {
                                return '';
                            }
                        }
                    },
                    'yaxis': {
                        'min': 0,
                        'max': 100,
                        'tickFormatter': function formatter(val, axis) {
                            return val.toFixed(axis.tickDecimals) + ' %';
                        }
                    },
                    'lines': {
                        'show': false
                    },
                    'points': {
                        'show': false
                    },
                    'bars': {
                        'show': true,
                        'align': 'center',
                        'barWidth': 0.5
                    }
                }
            );
        }
    );
},

'initialize': function (element) {
    var _this, prevPollObj;

    if (element.attr('poll_main_processed') === 'true') {
        // This element was already processed once.

        return;
    }

    // Make sure that next time we will not process this element a second time.
    element.attr('poll_main_processed', 'true');

    // Access PollMain instance inside inner functions created by $.each() iterator.
    _this = this;

    // Helper object which will help create a chain of poll objects.
    // Initially there is no previous poll object, so we initialize this reference to null.
    prevPollObj = null;

    element.children('.polls').each(function (index, value) {
        var pollObj;

        // Poll object with poll configuration and properties.
        pollObj = {
            'element': $(value), // Current poll DOM element (jQuery object).
            'id': $(value).prop('id'), // ID of DOM element with current poll.
            'pollId': element.prop('id'), // ID of DOM element which contains all polls.
            'ajax_url': element.data('ajax-url'),
            'answer_button': $(value).find('.submit-button'),
            'vote_blocks': $(value).find('.vote_blocks'),
            'graph_answer': $(value).find('.graph_answer')
        };

        // Set up a reference to current poll object in previous poll object.
        // Reference to next poll object is initialized to null.
        if (prevPollObj !== null) {
            prevPollObj.nextPollObj = pollObj;
        }
        prevPollObj = pollObj;
        pollObj.nextPollObj = null;

        // Attach a handler to the submit button, which will pass the current poll object.
        pollObj.answer_button.click(function (event) {
            _this.submitAnswer(event, pollObj);
        });
    });
}

}; }); }(RequireJS.requirejs, RequireJS.require, RequireJS.define));
