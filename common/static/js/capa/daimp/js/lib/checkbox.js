(function (requirejs, require, define) {
define(function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  var Color = require('color');
  var Font = require('font');

  function Checkbox(left, top, width, height) {
    //Call super class
    this.Component(left, top, width, height);
    this.isChecked = false;
    this.text = '';
    this.squareBackgroundColor = Color.black;
    this.squareBorderColor = Color.himidgray;
    this.textColor = Color.white;
    this.square = {
      left: 0,
      top: 2,
      right: 11,
      bottom: 13,
      width: 12,
      height: 12
    };
    //Bind mouseDown to the correct context
    //Otherwise 'this' in mouseDown would refer to the source of the event,
    //the canvas
    this.mouseDown = this.mouseDown.bind(this);
    //Register the click that will check/unckeck the checkbox
    this.canvas.addEventListener('mousedown', this.mouseDown, false);
  }
  U.copyPrototype(Checkbox, Component);

  Checkbox.prototype.draw = function () {
    this.clear();

    //Recalculate the bounding box based on the text
    var textWidth = U.subSuperScriptLength(this.ctx, this.text,
                                           Font.normalText, Font.subSupText);
    var width = 1 + this.square.width + 8 + textWidth;
    var height = 1 + Math.max(this.square.bottom, Font.normalSize.height);
    this.setSize(width, height);

    //Draw the component
    this.ctx.fillStyle = this.squareBackgroundColor;
    U.fillRect(this.ctx,
               this.square.left, this.square.top,
               this.square.right, this.square.bottom);
    this.ctx.strokeStyle = this.squareBorderColor;
    U.drawRect(this.ctx,
               this.square.left, this.square.top,
               this.square.right, this.square.bottom);

    this.ctx.fillStyle = this.textColor;
    U.drawSubSuperScript(this.ctx, this.text,
                         this.square.right + 8, this.square.bottom,
                         'left', 'alphabetic', Font.normalText,
                         Font.subSupText);
    if (this.isChecked) {
      this.ctx.fillStyle = this.textColor;
      this.ctx.strokeStyle = this.textColor;
      U.fillRect(this.ctx,
                 this.square.left + 2, this.square.top + 2,
                 this.square.right - 2, this.square.bottom - 2);
    }
  };

  Checkbox.prototype.mouseDown = function (event) {
    var event = event || window.event;
    this.isChecked = !this.isChecked;
    this.draw();
    this.fireEvent("mousedown", this);
    this.cancelDefaultAction(event);
  };

  return Checkbox;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));