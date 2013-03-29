(function (requirejs, require, define) {
define(function (require) {

  //Imports
  var $ = require('jquery');
  var U = require('utils');
  var Component = require('component');

  function RichText(left, top) {
    //Call super class
    this.Component(left, top, 10, 10);
    this.baseLine = false; // to use, set it to a y-value

    this.node = document.createElement('div');
    this.node.setAttribute("class", "richtext-default");

    var $node = $(this.node);
    $node.css({
      'position': 'absolute',
      'left': this.left,
      'top': this.top
    });

    // add to the DOM at the right time
    this.canvas = this.node;
  }
  U.copyPrototype(RichText, Component);

  RichText.prototype.draw = function () {
    // // default value is false
    // if (typeof this.baseLine === "number") {
    //   var span = $('<span>Hg</span>');
    //   $node.append(span);
    //   var textPos = span[0].offsetTop;
    //   span.remove();
    //   var h = U.measureFont($node.css('font'));
    //   this.top = this.baseLine - h.ascent - textPos;
    // }

    // set bbox using $node.width(), $node.height()
  };

  return RichText;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));