(function (requirejs, require, define) {
define(function (require) {

  //Imports
  var $ = require('jquery');
  var U = require('utils');
  var Component = require('component');
  var Color = require('color');
  var Font = require('font');
  var Tool = require('tool');

  function TextBox(left, top, width, height) {
    width = (width === undefined) ? 102 : width;
    height = (height === undefined) ? 24 : height;

    //Call super class
    this.Component(left, top, width, height);

    // create node
    this.node = document.createElement('input');
    //We can also use button, checkbox, radio, textarea
    this.node.setAttribute('type', 'text');

    var $node = $(this.node);
    $node.css({
      'position': 'absolute',
      'font': Font.normalText,
      'left': this.left,
      'top': this.top,
      'color': Color.blue,
      'background-color': Color.white,
      'text-indent': 3, // px
      'border': '1px solid ' + Color.black // which is really just a string
    });

    var paddingLR = parseInt($node.css('paddingLeft'), 10) +
                    parseInt($node.css('paddingRight'), 10);
    var paddingTB = parseInt($node.css('paddingTop'), 10) +
                    parseInt($node.css('paddingBottom'), 10);
    var borderLR = parseInt($node.css('borderLeftWidth'), 10) +
                   parseInt($node.css('borderRightWidth'), 10);
    var borderTB = parseInt($node.css('borderTopWidth'), 10) +
                   parseInt($node.css('borderBottomWidth'), 10);
    // if there was a outerWidth setter, this would be easier
    $node.width(this.width - paddingLR - borderLR);
    $node.height(this.height - paddingTB - borderTB);

    // attach to the DOM at the right time by tricking tool.js
    this.canvas = this.node;
  }
  U.copyPrototype(TextBox, Component);

  TextBox.prototype.getFloat = function() {
    var str = this.node.value || '';
    str = str.replace(/[^\d\.\-]/g,''); // all but 0-9, decimal, negative
    return parseFloat(str);
  };

  return TextBox;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));