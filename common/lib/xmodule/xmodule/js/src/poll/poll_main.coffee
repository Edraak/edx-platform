# Wrapper for RequireJS. It will make the standard requirejs(), require(), and
# define() functions from Require JS available inside the anonymous function.
((requirejs, require, define) ->

  # Even though it is not explicitly in this module, we have to specify
  # 'GeneralMethods' as a dependency. It expands some of the core JS objects
  # with additional useful methods that are used in other modules.
  define "PollMain", ["logme"], (logme) ->
    PollMain = (pollId) ->
      logme pollId
      alert "PollJSConstructor"
      {}
    return PollMain


# End of wrapper for RequireJS. As you can see, we are passing
# namespaced Require JS variables to an anonymous function. Within
# it, you can use the standard requirejs(), require(), and define()
# functions as if they were in the global namespace.
) RequireJS.requirejs, RequireJS.require, RequireJS.define # End-of: (function (requirejs, require, define)