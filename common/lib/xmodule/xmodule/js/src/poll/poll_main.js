// Wrapper for RequireJS. It will make the standard requirejs(), require(), and
// define() functions from Require JS available inside the anonymous function.
(function (requirejs, require, define) {

define(
    'PollMain',

    // Even though it is not explicitly in this module, we have to specify
    // 'GeneralMethods' as a dependency. It expands some of the core JS objects
    // with additional useful methods that are used in other modules.
    ['logme'],
    function (logme) {

    return PollMain;

    function PollMain(pollId) {
        logme(pollId);
        alert('PollJSConstructor')
        return {};
    }
});

// End of wrapper for RequireJS. As you can see, we are passing
// namespaced Require JS variables to an anonymous function. Within
// it, you can use the standard requirejs(), require(), and define()
// functions as if they were in the global namespace.
}(RequireJS.requirejs, RequireJS.require, RequireJS.define)); // End-of: (function (requirejs, require, define)
