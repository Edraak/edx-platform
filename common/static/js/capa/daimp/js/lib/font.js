(function (requirejs, require, define) {
define(function () {
  //Order that has to be respected in font shorthand:
  //font-style font-variant font-weight font-size line-height font-family
  var Font = {
    normalText: "700 14px Open Sans",
    labelText: "700 11px Open Sans",
    subSupText: "700 11px Open Sans",

    // so they don't have to be constantly recalculated
    // these are temporary values, recalculated in utils.js
    normalSize: { ascent: 14, descent: 5, height: 19 },
    labelSize: { ascent: 11, descent: 5, height: 16 },
    subSupSize: { ascent: 11, descent: 5, height: 16 }
  };

  return Font;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));