(function () {
    var timeout = 1000;

    waitForProtex();

    function waitForProtex() {
        if (typeof(protex) !== "undefined" && protex) {
            protex.onInjectionDone("protex");
        }
        else {
            setTimeout(function() { waitForProtex(); }, timeout);
        }
    }
    
    //NOTE:
    // Protex uses four global functions:
    // protexSetTargetShape (exported from GWT)
    // protexCheckAnswer (exported from GWT)
    // It calls protexIsReady with a deferred command when it has finished 
    // initialization and has drawn itself
    // It calls protexProteinIsFolded when a protein has been folded and is   
    // ready to get checked
    
    protexProteinIsFolded = function() {
        //Get answer from protex and store it into the hidden input field
        //when Fold button is clicked
        var problem = $('#protex_container').parents('.problem');
        var input_field = problem.find('input[type=hidden]');
        var protex_answer = protexCheckAnswer();
        var value = {protex_answer: protex_answer};
        input_field.val(JSON.stringify(value));
    }
        
    protexIsReady = function() {
        //Load target shape
        var target_shape = $('#target_shape').val();
        protexSetTargetShape(target_shape);            
    };
}).call(this);
