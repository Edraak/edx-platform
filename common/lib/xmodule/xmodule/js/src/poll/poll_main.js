// Wrapper for RequireJS. It will make the standard requirejs(), require(), and
// define() functions from Require JS available inside the anonymous function.
(function(requirejs, require, define) {

  // Even though it is not explicitly in this module, we have to specify
  // 'GeneralMethods' as a dependency. It expands some of the core JS objects
  // with additional useful methods that are used in other modules.
  define("PollMain", ["logme"], function(logme) {

    function PollMain(element) {
      logme(element);
      // alert("PollJSConstructor");

      this.reinitialize(element);
    }

    PollMain.prototype.submit_answer = function (event, _this) {
      // alert('answer');
      _this.status_item = $(event.target).parent().parent();
      // _this.status_number = status_item.data("status-number");
      _this.data = {
        task_number: "1"
      };
      logme( "" + _this.ajax_url + "/submit_answer");
      $.postWithPrefix(
        "" + _this.ajax_url + "/submit_answer",
        _this.data,
        function(response) {
          if (response.success) {
            return alert("Success");
          } else {
            return alert("No success");
          }
        }
      );
    };

    PollMain.prototype.reinitialize = function (element) {
      var _this = this;
      // alert('Reinit');
      this.id = element.data("id");
      this.ajax_url = element.data("ajax-url");
      this.state = element.data("state");
      this.answer_button = element.find(".submit-button");
      this.answer_button.click(function (event) {
        // logme('123');
        _this.submit_answer(event, _this);
      });
    };
    return PollMain;
  });
// End of wrapper for RequireJS. As you can see, we are passing
// namespaced Require JS variables to an anonymous function. Within
// it, you can use the standard requirejs(), require(), and define()
// functions as if they were in the global namespace.
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));

