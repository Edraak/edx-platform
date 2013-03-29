(function (requirejs, require, define) {
define(function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  var Color = require('color');
  var Font = require('font');

  function RowArrow(ax, ay, w, h2) { // optional w/h
    // ax and ay are the anchor point, the tip of the arrow

    this.width = (w === undefined) ? 5 : w;
    this.halfHeight = (h2 === undefined) ? 5 : h2;
    this.padding = 5; // easier to click

    this.Component(ax, ay, ax, ay); // will be reset soon
    this.setAnchor(ax, ay);
    this.arrowColor = Color.yellow;
  }
  U.copyPrototype(RowArrow, Component);

  RowArrow.prototype.setAnchor = function(x, y) {
    this.anchorLeft = x;
    this.anchorTop = y;
    this.setBounds(x - this.width - this.padding,
                   y - this.halfHeight - this.padding,
                   x + this.padding,
                   y + this.halfHeight + this.padding);
  };

  RowArrow.prototype.draw = function(alreadyCleared) {
    if (!alreadyCleared) {
      this.clear();
    }  

    this.ctx.fillStyle = this.arrowColor;
    U.fillTriangle(this.ctx, 
                   this.anchorLeft, this.anchorTop, 
                   this.anchorLeft - this.width, this.anchorTop + this.halfHeight,   
                   this.anchorLeft - this.width, this.anchorTop - this.halfHeight);
  };

  return RowArrow;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));