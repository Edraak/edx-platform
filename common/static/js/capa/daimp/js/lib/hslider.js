(function (requirejs, require, define) {
define(function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  var Color = require('color');
  var Label = require('label');
  var Font = require('font');

  function HSlider(left, top, width, height) {
    //Call super class
    this.Component(left, top, width, height);
    this.darkTrackColor = Color.black;
    this.lightTrackColor = Color.lomidgray;
    this.knobColor = Color.himidgray;
    this.knobPointerColor = Color.white;
    this.labelColor = Color.himidgray;
    this.textColor = Color.white;

    this.xmin = 0.0;
    this.xmax = 100.0;
    this.xspan = 100.0;
    this.xvalue = 0.0;
    this.shortTickStep = 5.0;
    this.longTickStep = 10.0;
    this.labelStep = 10.0;
    this.wxmin = 50;
    this.wxmax = this.width - 50;
    this.wxspan = this.wxmax - this.wxmin;
    this.wxvalue = this.getxPix(this.xvalue);
    this.wyAxis = 20;
    this.wyTrack = this.wyAxis + 5;
    this.text = "";
    this.valueDecimalDigits = 2;
    this.labelDecimalDigits = 0;

    this.inDrawingZone = false;
    this.mouseIsDragged = false;
    this.isInTickZone = false;
    this.snapToTicks = false;
    this.snapxmin = this.xmin;
    this.snapxmax = this.xmax;
    this.snapwxmin = this.getxPix(this.snapxmin);
    this.snapwxmax = this.getxPix(this.snapxmax);
    this.formatZero = true;
    this.automaticLabels = true;
    this.hasPI = false; //If true, multiplies the value of the slider by PI
    this.hasDegree = false; //If true, a degree sign is appended after the value
    //TO DO: Get rid of this when subsuperscript routine is fixed
    this.hasSubSuperscript = false;
    this.labels = [new Label(this.xmin, 
                             this.xmin.toFixed(this.labelDecimalDigits)),
                   new Label(this.xmax, 
                             this.xmax.toFixed(this.labelDecimalDigits))];
    this.isSelected = false;
    //Bind events to the correct context
    this.mouseDown = this.mouseDown.bind(this);
    this.mouseMove = this.mouseMove.bind(this);
    this.mouseUp = this.mouseUp.bind(this);
    
    //Add the necessary events
    this.canvas.addEventListener('mousedown', this.mouseDown);
    // these are attached later, on the mousedown
    //this.canvas.addEventListener('mousemove', this.mouseMove);
    //this.canvas.addEventListener('mouseup', this.mouseUp);
  }
  U.copyPrototype(HSlider, Component);

  HSlider.prototype.draw = function () {
    this.clear();
    
    this.drawLabels(); //Draw this first otherwise artifacts appear in Safari
    this.drawDarkTrack();
    this.drawLightTrack();
    this.drawAxis();
    this.drawShortTicks();
    this.drawLongTicks();
    this.drawKnob();
    this.drawKnobPointer();
    this.drawText();
    this.drawValue();
  };

  HSlider.prototype.drawDarkTrack = function () {
    this.ctx.strokeStyle = this.darkTrackColor;
    U.drawLine(this.ctx, this.wxmin, this.wyTrack, this.wxmax, this.wyTrack);

  };

  HSlider.prototype.drawLightTrack = function () {
    this.ctx.strokeStyle = this.lightTrackColor;
    U.drawLine(this.ctx,
               this.wxmin, this.wyTrack + 2,
               this.wxmax, this.wyTrack + 2);
  };

  HSlider.prototype.drawAxis = function () {
    this.ctx.strokeStyle = this.labelColor;
    U.drawLine(this.ctx, this.wxmin, this.wyAxis, this.wxmax, this.wyAxis);
  };

  HSlider.prototype.drawShortTicks = function () {
    var x;
    var wx;

    this.ctx.strokeStyle = this.labelColor;

    if (this.shortTickStep > 0) {
      for (x = this.xmin; x <= this.xmax; x += this.shortTickStep) {
        wx = this.getxPix(x);
        U.drawLine(this.ctx, wx, this.wyAxis, wx, this.wyAxis - 2);
      }
    }
  };

  HSlider.prototype.drawLongTicks = function () {
    var x;
    var wx;

    this.ctx.strokeStyle = this.labelColor;

    if (this.longTickStep > 0) {
      for (x = this.xmin; x <= this.xmax; x += this.longTickStep) {
        wx = this.getxPix(x);
        U.drawLine(this.ctx, wx, this.wyAxis, wx, this.wyAxis - 4);
      }
    }
  };

  HSlider.prototype.drawKnob = function () {
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

  HSlider.prototype.drawKnobPointer = function () {
    this.ctx.strokeStyle = this.knobPointerColor;

    U.drawLine(this.ctx,
               this.wxvalue, this.wyTrack - 3, this.wxvalue, this.wyTrack + 4);
  };

  HSlider.prototype.drawLabels = function () {
    var x;
    var wx, wy;
    var str;

    wy = this.wyAxis - 5;

    this.ctx.font = Font.labelText;
    this.ctx.fillStyle = this.labelColor;
    this.ctx.textAlign = "center";
    this.ctx.textBaseline = "bottom";

    if (this.automaticLabels) {
      if (this.labelStep > 0) {
        for (x = this.xmin; x <= this.xmax; x += this.labelStep) {
          wx = this.getxPix(x);
          if (Math.abs(x) < 0.00001 && this.formatZero) {
            str = "0";
          }  
          else {
            str = x.toFixed(this.labelDecimalDigits);
          }
          this.ctx.fillText(str, wx, wy);
        }
      }
    }
    else {
      for (var i = 0, l = this.labels.length; i < l; i++) {
        wx = this.getxPix(this.labels[i].value);
        str = this.labels[i].text;
        this.ctx.fillText(str, wx, wy);
      }
    }
  };

  HSlider.prototype.drawValue = function () {
    var wx = this.wxmax + 10;
    var wy = this.wyTrack + 5;
    var val;
    if (this.hasPI) {
      val = Math.PI * this.xvalue;
    }
    else {
      val = this.xvalue;
    }  
    var str = val.toFixed(this.valueDecimalDigits);
    
    if (this.hasDegree) {
      str += '\u00B0';
    }  

    this.ctx.font = Font.normalText;
    this.ctx.fillStyle = this.textColor;
    this.ctx.textAlign = "left";
    this.ctx.textBaseline = "bottom";

    this.ctx.fillText(str, wx, wy);
  };

  HSlider.prototype.drawText = function () {
    var wx = this.wxmin - 10;
    var wy = this.wyTrack + 5;

    this.ctx.font = Font.normalText;
    this.ctx.fillStyle = this.textColor;
    this.ctx.textAlign = "right";
    this.ctx.textBaseline = "bottom";

    if (!this.hasSubSuperscript) {
      this.ctx.fillText(this.text, wx, wy);
    }
    else {
      U.drawSubSuperScript(this.ctx, this.text,
                           wx, wy,
                           "right", "bottom", Font.normalText, Font.subSupText);
    }                       
  };

  HSlider.prototype.getClickZone = function (pt) {
    if (pt.y <= this.wyAxis) {
      this.isInTickZone = true;
    }
    else {
      this.isInTickZone = false;
    }  
  };

  HSlider.prototype.getValue = function (pt) {
    if (this.isInTickZone) {
      this.wxvalue = this.findNearestTick(pt);
      if (this.wxvalue > this.wxmax) {
        this.wxvalue = this.wxmax;
      }
      else if (this.wxvalue < this.wxmin) {
        this.wxvalue = this.wxmin;
      }  
      this.xvalue = this.getxFromPix(this.wxvalue);
    }
    else {
      if (this.snapToTicks) {
        this.snapwxmin = this.getxPix(this.snapxmin);
        this.snapwxmax = this.getxPix(this.snapxmax);
        this.wxvalue = this.findNearestTick(pt);
        if (this.wxvalue < this.snapwxmin) {
          this.wxvalue = this.snapwxmin;
        }  
        if (this.wxvalue > this.snapwxmax) { 
          this.wxvalue = this.snapwxmax;
        }  
      }
      else {
        this.wxvalue = pt.x;
        if (this.wxvalue > this.wxmax) {
          this.wxvalue = this.wxmax;
        }
        else if (this.wxvalue < this.wxmin) {
          this.wxvalue = this.wxmin;
        }  
      }
    this.xvalue = this.getxFromPix(this.wxvalue);
    }
  };

  HSlider.prototype.setValue = function (x) {
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

  HSlider.prototype.findNearestTick = function (pt) {
    var x;
    var wx;
    var wxc = pt.x;
    //Distance between wxc (mouse click position) and wx (tick position)
    var currentDist; 
    var minDist = Number.MAX_VALUE; //Min value between wxc and wx
    var step; // Step between small or large ticks
    var result;

    if (this.longTickStep > 0) {//Long ticks are visible
      step = this.longTickStep;
    }  
    if (this.shortTickStep > 0) { //Short ticks are visible
      step = this.shortTickStep;
    }  

    //Small or large ticks visible
    if (this.shortTickStep > 0 || this.longTickStep > 0) {
      var i = 0;
      for (x = this.xmin; x <= this.xmax; x += step) {
        wx = this.getxPix(x);
        currentDist = Math.abs(wxc - wx);
        if (currentDist < minDist) {
          minDist = currentDist;
          result = wx;
        }
      }
    }
    else { //No ticks are visible, return wxc
      result = wxc;
    }  

    return result;
  };

  HSlider.prototype.getxPix = function (x) {
    return Math.round(this.wxmin + this.wxspan * (x - this.xmin) / this.xspan);
  };

  HSlider.prototype.getxFromPix = function (wx) {
    return (this.xmin + this.xspan * (wx - this.wxmin) / this.wxspan);
  };

  HSlider.prototype.mouseDown = function (event) {
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

  HSlider.prototype.mouseMove = function (event) {
    var event = event || window.event;
    if (this.isSelected) {
      var mpos = this.getMousePosition(event);
      this.getValue(mpos);
      this.draw();
      this.fireEvent("mousedrag");
    }
    this.cancelDefaultAction(event);  
  };

  HSlider.prototype.mouseUp = function (event) {
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

  return HSlider;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));