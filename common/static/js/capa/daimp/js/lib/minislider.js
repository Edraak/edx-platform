(function (requirejs, require, define) {
define(function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  var Color = require('color');

  function MiniSlider(x, y, width, height) // optional w/h
  {
    //Call super class
    this.Component(x, y, 10, 10); // set for real soon
    this.canvas.style.background = 'transparent';

    this.borderColor = Color.white;
    this.backgroundColor = Color.background;
    this.darkTrackColor = Color.black;
    this.lightTrackColor = Color.lomidgray;
    this.knobColor = Color.himidgray;
    this.knobPointerColor = Color.white;

    this.xmin = 0.0;
    this.xmax = 100.0;
    this.xspan = 100.0;
    this.xvalue = 0.0;

    // (x,y) is the anchor point.
    this.anchorTriangleHeight = 5; // px
    this.setAnchor(x, y, width, height);

    // behavior
    this.shy = true; // hides if there is a click outside
//    this.setVisibility(false);

    //Bind events to the correct context
    this.mouseDown = this.mouseDown.bind(this);
    this.mouseMove = this.mouseMove.bind(this);
    this.mouseUp = this.mouseUp.bind(this);
    this.hideEvent = this.hideEvent.bind(this);

    //Add the necessary events
    this.canvas.addEventListener('mousedown', this.mouseDown);
  }
  U.copyPrototype(MiniSlider, Component);

  // override
  MiniSlider.prototype.setVisibility = function(bool) {
    // super.setVisibility(bool)
    Component.prototype.setVisibility.call(this, bool);

    // if (this.isVisible) {
    //   document.addEventListener('mousedown', this.hideEvent);
    // }
    // else {
    //   document.removeEventListener('mousedown', this.hideEvent);
    // }
  }

  MiniSlider.prototype.setAnchor = function (x, y, width, height) {
    width = (width === undefined) ? 50 : width;
    height = (height === undefined) ? 20 : height;

    height += this.anchorTriangleHeight;
    x -= Math.floor(width / 2);
    y -= height - 1;

    this.setBounds(x, y, width, height);

    this.wxmin = 5;
    this.wxmax = this.width - 1 - 5;
    this.wxspan = this.wxmax - this.wxmin;
    this.wyAxis = 5;
    this.wyTrack = this.wyAxis + 5;
    this.wxvalue = this.getxPix(this.xvalue);

    // outline
    var anchorX = Math.floor(width / 2);
    var bottom = this.height - 1;
    var right = this.width - 1;
    var boxBottom = bottom - this.anchorTriangleHeight;

    this.outlineX = [0,
		     0,
		     anchorX - this.anchorTriangleHeight,
		     anchorX,
		     anchorX + this.anchorTriangleHeight,
		     right,
		     right];
    this.outlineY = [0,
		     boxBottom,
		     boxBottom,
		     bottom,
		     boxBottom,
		     boxBottom,
		     0];
  };

  MiniSlider.prototype.draw = function () {
    if (!this.isVisible) {
	return;
    }

    this.clear();

    this.makeOutline();
    this.drawDarkTrack();
    this.drawLightTrack();
    this.drawAxis();
    this.drawKnob();
    this.drawKnobPointer();
  };

  MiniSlider.prototype.makeOutline = function () {
    this.ctx.fillStyle = this.backgroundColor;
    U.fillShape(this.ctx, this.outlineX, this.outlineY);

    this.ctx.strokeStyle = this.borderColor;
    U.drawShape(this.ctx, this.outlineX, this.outlineY);
  };

  MiniSlider.prototype.drawDarkTrack = function () {
    this.ctx.strokeStyle = this.darkTrackColor;
    U.drawLine(this.ctx, this.wxmin, this.wyTrack, this.wxmax, this.wyTrack);

  };

  MiniSlider.prototype.drawLightTrack = function () {
    this.ctx.strokeStyle = this.lightTrackColor;
    U.drawLine(this.ctx,
               this.wxmin, this.wyTrack + 2,
               this.wxmax, this.wyTrack + 2);
  };

  MiniSlider.prototype.drawAxis = function () {
    this.ctx.strokeStyle = this.labelColor;
    U.drawLine(this.ctx, this.wxmin, this.wyAxis, this.wxmax, this.wyAxis);
  };

  MiniSlider.prototype.drawKnob = function () {
    this.ctx.strokeStyle = this.knobColor;

    U.drawLine(this.ctx,
               this.wxvalue + 1, this.wyTrack - 1,
               this.wxvalue + 1, this.wyTrack + 4);
    U.drawLine(this.ctx,
               this.wxvalue - 1, this.wyTrack - 1,
               this.wxvalue - 1, this.wyTrack + 4);
    U.drawLine(this.ctx,
               this.wxvalue, this.wyTrack - 1,
               this.wxvalue, this.wyTrack + 4);
    U.drawLine(this.ctx,
               this.wxvalue + 2, this.wyTrack,
               this.wxvalue + 2, this.wyTrack + 3);
    U.drawLine(this.ctx,
               this.wxvalue - 2, this.wyTrack,
               this.wxvalue - 2, this.wyTrack + 3);
  };

  MiniSlider.prototype.drawKnobPointer = function () {
    this.ctx.strokeStyle = this.knobPointerColor;

    U.drawLine(this.ctx,
               this.wxvalue, this.wyTrack - 3,
               this.wxvalue, this.wyTrack + 4);
  };

  MiniSlider.prototype.getValue = function (pt) {
    this.wxvalue = pt.x;
    if (this.wxvalue > this.wxmax) {
      this.wxvalue = this.wxmax;
    }
    else if (this.wxvalue < this.wxmin) {
      this.wxvalue = this.wxmin;
    }

    this.xvalue = this.getxFromPix(this.wxvalue);
  };

  MiniSlider.prototype.setValue = function (x) {
    if (x < this.xmin) {
      this.xvalue = this.xmin;
    }
    else if (x > this.xmax) {
      this.xvalue = this.xmax;
    }
    else {
      this.xvalue = x;
    }
    this.wxvalue = this.getxPix(this.xvalue);
  };

  MiniSlider.prototype.getxPix = function (x) {
    return Math.round(this.wxmin + this.wxspan * (x - this.xmin) / this.xspan);
  };

  MiniSlider.prototype.getxFromPix = function (wx) {
    return (this.xmin + this.xspan * (wx - this.wxmin) / this.wxspan);
  };

  MiniSlider.prototype.mouseDown = function (event) {
    var event = event || window.event;
    var mpos = this.getMousePosition(event);

    var boxBottom = this.height - 1 - this.anchorTriangleHeight;
    if (mpos.y > boxBottom) {
      this.hideEvent();
      return;
    }

    this.mouseMove(event);

    document.addEventListener('mousemove', this.mouseMove, true);
    document.addEventListener('mouseup', this.mouseUp, true);
  };

  MiniSlider.prototype.mouseMove = function (event) {
    var oldval = this.xvalue;

    var event = event || window.event;
    var mpos = this.getMousePosition(event);
    this.getValue(mpos);
    this.draw();

    if (this.xvalue !== oldval) {
      this.fireEvent('change', this);
    }
    this.cancelDefaultAction(event);  
  };

  MiniSlider.prototype.mouseUp = function (event) {
    this.mouseMove(event);

    //Remove the previous event listeners, as they are no longer useful
    document.removeEventListener('mousemove', this.mouseMove, true);
    document.removeEventListener('mouseup', this.mouseUp, true);
  };

  // mousedown outside the canvas, or on the transparent part
  MiniSlider.prototype.hideEvent = function () {
    if (this.shy) {
      this.setVisibility(false);
    }
  };

  return MiniSlider;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));