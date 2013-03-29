(function (requirejs, require, define) {
define(function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  var Color = require('color');
  var Font = require('font');

  function Text(left, top) {
    //Call super class
    this.Component(left, top, 10, 10);
    this.text = '';
    this.textColor = Color.white;
    this.xway = 'left';
    this.yway = 'bottom';
    this.alignCrit = null; // see note below specialAlignment

    this.anchorLeft = left; //where the text is actually drawn
    this.anchorTop = top;
  }
  U.copyPrototype(Text, Component);

  Text.prototype.draw = function () {
    this.measure();
    this.clear();

    // this.debug();

    this.ctx.fillStyle = this.textColor;
    var x = 2;
    var y = 2 + Font.subSupSize.height + 5;
    // xway and yway influenced the positioning of the canvas
    U.drawSubSuperScript(this.ctx, this.text,
                         x, y, 'left', 'bottom',
                         Font.normalText, Font.subSupText);
  };

  Text.prototype.measure = function () {
    var bBox = U.findTextbBox(this.ctx, this.anchorLeft, this.anchorTop,
			     this.text, this.xway, this.yway);

    if (this.xway === 'special') {
      this.specialAlignment(bBox);
    }

    // changing the size makes the canvas blank, so avoid it
    if (bBox[0] === this.width && bBox[3] === this.height) {
      this.setPosition(bBox[0], bBox[1]);
    }
    else {
      this.setBounds(bBox[0], bBox[1], bBox[2], bBox[3]);
    }
  };

  // splits the string into two parts, to the left and right of anchor
  // if given a #, splits on the nth character
  // if given a char, splits on the 1st instance of char
  // if given a function, splits on the substring returned (eg one with a regex)
  Text.prototype.specialAlignment = function(bBox) {
    var substr; // the stuff to the left of the anchor
    if (typeof this.alignCrit === 'number') {
      var n = this.alignCrit;
      n ++;
      substr = this.text.substring(0, n);
    }
    else if (typeof this.alignCrit === 'string') {
      var n = this.text.indexOf(this.alignCrit);
      n += this.alignCrit.length;
      substr = this.text.substring(0, n);
    }
    else if (typeof this.alignCrit === 'function') {
      var str = this.alignCrit();
      var n = this.text.indexOf(str);
      n += str.length;
      substr = this.text.substring(0, n);
    }

    var width = U.subSuperScriptLength(this.ctx, substr,
                                       Font.normalText, Font.subSupText);
    bBox[0] -= width;
  };

  return Text;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));