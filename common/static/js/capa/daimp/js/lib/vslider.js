(function (requirejs, require, define) {
define(function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  var Color = require('color');
  var Label = require('label');
  var Font = require('font');

  function VSlider(left, top, width, height) {
    //Call super class
    this.Component(left, top, width, height);
    this.darkTrackColor = Color.black;
    this.lightTrackColor = Color.lomidgray;
    this.knobColor = Color.himidgray;
    this.knobPointerColor = Color.white;
    this.labelColor = Color.himidgray;
    this.textColor = Color.white;

    this.ymin = 0.0;
    this.ymax = 100.0;
    this.yspan = 100.0;
    this.yvalue = 0.0;
    this.shortTickStep = 5.0;
    this.longTickStep = 10.0;
    this.labelStep = 10.0;
    this.wymin = this.height - 1 - 40;
    this.wymax = 40;
    this.wyspan = this.wymin - this.wymax;
    this.wyvalue = this.getyPix(this.yvalue);
    this.wxAxis = 40;
    this.wxTrack = this.wxAxis + 5;
    this.text = "";
    this.valueDecimalDigits = 2;
    this.labelDecimalDigits = 0;

    this.inDrawingZone = false;
    this.mouseIsDragged = false;
    this.isInTickZone = false;
    this.snapToTicks = false;
    this.snapymin = this.ymin;
    this.snapymax = this.ymax;
    this.snapwymin = this.getyPix(this.snapymin);
    this.snapwymax = this.getyPix(this.snapymax);
    this.formatZero = true;
    //TO DO, labels like in HSlider

    this.isSelected = false;
    //Bind events to the correct context
    this.mouseDown = this.mouseDown.bind(this);
    this.mouseMove = this.mouseMove.bind(this);
    this.mouseUp = this.mouseUp.bind(this);
    
    //Add the necessary events
    this.canvas.addEventListener('mousedown', this.mouseDown);
    // these are added on the mousedown
    //this.canvas.addEventListener('mousemove', this.mouseMove);
    //this.canvas.addEventListener('mouseup', this.mouseUp);

  }
  U.copyPrototype(VSlider, Component);

  VSlider.prototype.draw = function () {
    this.clear();

    this.drawDarkTrack();
    this.drawLightTrack();
    this.drawAxis();
    this.drawShortTicks();
    this.drawLongTicks();
    this.drawKnob();
    this.drawKnobPointer();
    this.drawLabels();
    this.drawText();
    this.drawValue();
  };

  VSlider.prototype.drawDarkTrack = function () {
    this.ctx.strokeStyle = this.darkTrackColor;
    U.drawLine(this.ctx, this.wxTrack, this.wymin, this.wxTrack, this.wymax);

  };

  VSlider.prototype.drawLightTrack = function () {
    this.ctx.strokeStyle = this.lightTrackColor;
    U.drawLine(this.ctx,
               this.wxTrack + 2, this.wymin,
               this.wxTrack + 2, this.wymax);
  };

  VSlider.prototype.drawAxis = function () {
    this.ctx.strokeStyle = this.labelColor;
    U.drawLine(this.ctx, this.wxAxis, this.wymin, this.wxAxis, this.wymax);
  };

  VSlider.prototype.drawShortTicks = function () {
    var y;
    var wy;

    this.ctx.strokeStyle = this.labelColor;

    if (this.shortTickStep > 0) {
      for (y = this.ymin; y <= this.ymax; y += this.shortTickStep) {
        wy = this.getyPix(y);
        U.drawLine(this.ctx, this.wxAxis, wy, this.wxAxis - 2, wy);
      }
    }
  };

  VSlider.prototype.drawLongTicks = function () {
    var y;
    var wy;

    this.ctx.strokeStyle = this.labelColor;

    if (this.longTickStep > 0) {
      for (y = this.ymin; y <= this.ymax; y += this.longTickStep) {
        wy = this.getyPix(y);
        U.drawLine(this.ctx, this.wxAxis, wy, this.wxAxis - 4, wy);
      }
    }
  };

  VSlider.prototype.drawKnob = function () {
    this.ctx.strokeStyle = this.knobColor;

    U.drawLine(this.ctx,
               this.wxTrack - 1, this.wyvalue + 1,
               this.wxTrack + 4, this.wyvalue + 1);
    U.drawLine(this.ctx,
               this.wxTrack - 1, this.wyvalue - 1,
               this.wxTrack + 4, this.wyvalue - 1);
    U.drawLine(this.ctx,
               this.wxTrack - 1, this.wyvalue,
               this.wxTrack + 4, this.wyvalue);
    U.drawLine(this.ctx,
               this.wxTrack, this.wyvalue + 2,
               this.wxTrack + 3, this.wyvalue + 2);
    U.drawLine(this.ctx,
               this.wxTrack, this.wyvalue - 2,
               this.wxTrack + 3, this.wyvalue - 2);
  };

  VSlider.prototype.drawKnobPointer = function () {
    this.ctx.strokeStyle = this.knobPointerColor;

    U.drawLine(this.ctx,
               this.wxTrack - 3, this.wyvalue,
               this.wxTrack + 4, this.wyvalue);
  };

  VSlider.prototype.drawLabels = function () {
    var y;
    var wx, wy;
    var str;

    wx = this.wxAxis - 10;

    this.ctx.font = Font.labelText;
    this.ctx.fillStyle = this.labelColor;
    this.ctx.textAlign = "right";
    this.ctx.textBaseline = "middle";

    if (this.labelStep > 0) {
      for (y = this.ymin; y <= this.ymax; y += this.labelStep) {
        wy = this.getyPix(y);
        if (Math.abs(y) < 0.00001 && this.formatZero) {
          str = "0";
        }  
        else {
          str = y.toFixed(this.labelDecimalDigits);
        }  
        this.ctx.fillText(str, wx, wy);
      }
    }
  };

  VSlider.prototype.drawValue = function () {
    var wx = this.wxTrack;
    var wy = this.wymax - 10;
    var str = this.yvalue.toFixed(this.valueDecimalDigits);

    this.ctx.font = Font.normalText;
    this.ctx.fillStyle = this.textColor;
    this.ctx.textAlign = "center";
    this.ctx.textBaseline = "bottom";

    this.ctx.fillText(str, wx, wy);
  };

  VSlider.prototype.drawText = function () {
    var wx = this.wxTrack;
    var wy = this.wymin + 5;

    this.ctx.font = Font.normalText;
    this.ctx.fillStyle = this.textColor;
    this.ctx.textAlign = "right";
    this.ctx.textBaseline = "top";

    this.ctx.fillText(this.text, wx, wy);
  };

  VSlider.prototype.getClickZone = function (pt) {
    if (pt.x <= this.wxAxis) {
      this.isInTickZone = true;
    }  
    else {
      this.isInTickZone = false;
    }  
  };

  VSlider.prototype.getValue = function (pt) {
    if (this.isInTickZone) {
      this.wyvalue = this.findNearestTick(pt);
      if (this.wyvalue < this.wymax) {
        this.wyvalue = this.wymax;
      }  
      else if (this.wyvalue > this.wymin) {
        this.wyvalue = this.wymin;
      }  
      this.yvalue = this.getyFromPix(this.wyvalue);
    }
    else {
      if (this.snapToTicks) {
        this.snapwymin = this.getyPix(this.snapymin);
        this.snapwymax = this.getyPix(this.snapymax);
        this.wyvalue = this.findNearestTick(pt);
        if (this.wyvalue > this.snapwxmin) {
          this.wyvalue = this.snapwymin;
        }  
        if (this.wyvalue < this.snapwymax) {
          this.wyvalue = this.snapwymax;
        }  
      }
      else {
        this.wyvalue = pt.y;
        if (this.wyvalue < this.wymax) {
          this.wyvalue = this.wymax;
        }  
        else if (this.wyvalue > this.wymin) {
          this.wyvalue = this.wymin;
        }  
      }

      this.yvalue = this.getyFromPix(this.wyvalue);
    }
  };

  VSlider.prototype.setValue = function (y) {
    if (y < this.ymin) {
      this.yvalue = this.ymin;
    }  
    else if (y > this.ymax) {
      this.yvalue = this.ymax;
    }  
    else {
      this.yvalue = y;
    }  
    this.wyvalue = this.getyPix(this.yvalue);
  };

  VSlider.prototype.findNearestTick = function (pt) {
    var y;
    var wy;
    var wyc = pt.y;
     //Distance between wyc (mouse click position) and wy (tick position)
    var currentDist;
    var minDist = Number.MAX_VALUE; //Min value between wyc and wy
    var step; // Step between small or large ticks
    var result;

    if (this.longTickStep > 0) { //Long ticks are visible
      step = this.longTickStep;
    }  
    if (this.shortTickStep > 0) {//Short ticks are visible
      step = this.shortTickStep;
    }  
    //Small or large ticks visible
    if (this.shortTickStep > 0 || this.longTickStep > 0) {
      var i = 0;
      for (y = this.ymin; y <= this.ymax; y += step) {
        wy = this.getyPix(y);
        currentDist = Math.abs(wyc - wy);
        if (currentDist < minDist) {
          minDist = currentDist;
          result = wy;
        }
      }
    } 
    else {//No ticks are visible, return wxc
      result = wyc;
    }  

    return result;
  };

  VSlider.prototype.getyPix = function (y) {
    return Math.round(this.wymin - this.wyspan * (y - this.ymin) / this.yspan);
  };

  VSlider.prototype.getyFromPix = function (wy) {
    return (this.ymin + this.yspan * (this.wymin - wy) / this.wyspan);
  };

  VSlider.prototype.mouseDown = function (event) {
    var event = event || window.event;
    var mpos = this.getMousePosition(event);
    this.isSelected = true;
    this.getClickZone(mpos);
    this.getValue(mpos);
    this.draw();
    this.fireEvent('mousedown');
    //Track the mouse movement outside of the component
    document.addEventListener('mousemove', this.mouseMove, true);
    //Track if a mouse up occurs outside of the component
    document.addEventListener('mouseup', this.mouseUp, true);
    this.cancelDefaultAction(event);
  };

  VSlider.prototype.mouseMove = function (event) {
    var event = event || window.event;
    if (this.isSelected) {
      var mpos = this.getMousePosition(event);
      this.getValue(mpos);
      this.draw();
      this.fireEvent("mousedrag");
    }
    this.cancelDefaultAction(event);
  };

  VSlider.prototype.mouseUp = function (event) {
    var event = event || window.event;
    var mpos = this.getMousePosition(event);
    //To avoid mouse up when mouse down happened on another component
    if (this.isSelected) {
      this.getValue(mpos);
      this.draw();
      this.fireEvent("mouseup");
      //Remove the previous event listeners, as they are no longer useful
      document.removeEventListener('mousemove', this.mouseMove, true);
      document.removeEventListener('mouseup', this.mouseUp, true);
    }  
    this.isSelected = false;
    this.cancelDefaultAction(event);  
  };

  return VSlider;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));