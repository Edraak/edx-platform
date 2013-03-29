(function (requirejs, require, define) {
define(function(require) {

  function Label(value, text)
  {
    this.value = value;
    this.text = text;
  }

  return Label;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));