(function (requirejs, require, define) {
define(function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  var Color = require('color');

  function Shape(left, top, width, height) {
    //Call super class
    this.Component(left, top, width, height);
    this.canvas.style.backgroundColor = 'transparent';
  }
  U.copyPrototype(Shape, Component);

  Shape.prototype.draw = function () {
    this.clear();
  };

  Shape.prototype.drawLine = function (x1, y1, x2, y2, color) {
    this.ctx.save();
    this.ctx.strokeStyle = color;
    U.drawLine(this.ctx, x1, y1, x2, y2);
    this.ctx.restore();
  };
  
  Shape.prototype.drawLeftBracket = function (x, y, height, color) {
    this.ctx.save();
    this.ctx.strokeStyle = color;
    U.drawLine(this.ctx, x, y, x, y + height);
    U.drawLine(this.ctx, x, y, x + 6, y);
    U.drawLine(this.ctx, x, y + height, x + 6, y + height);
    this.ctx.restore();
  };

  Shape.prototype.drawRightBracket = function (x, y, height, color) {
    this.ctx.save();
    this.ctx.strokeStyle = color;
    U.drawLine(this.ctx, x, y, x, y + height);
    U.drawLine(this.ctx, x - 6, y, x, y);
    U.drawLine(this.ctx, x - 6, y + height, x, y + height);
    this.ctx.restore();
  };

  return Shape;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));