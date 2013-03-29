(function (requirejs, require, define) {
define(function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  var Color = require('color');
  var Font = require('font');

  function DrawingZone(left, top, right, bottom) {
    this.left = left;
    this.top = top;
    this.right = right;
    this.bottom = bottom;
  }

  function Graph(left, top, width, height) {
    //Call super class
    this.Component(left, top, width, height);

    this.dZone = new DrawingZone(40, 40,
                                 this.width - 1 - 40, this.height - 1 - 40);
    this.drawingZoneColor = Color.black;
    this.drawingZoneBorderColor = Color.lomidgray;

    this.xGridColor = Color.darkgray;
    this.xAxisColor = Color.himidgray;
    this.xLabelColor = Color.himidgray;
    this.xTextColor = Color.litegray;

    this.yGridColor = Color.darkgray;
    this.yAxisColor = Color.himidgray;
    this.yLabelColor = Color.himidgray;
    this.yTextColor = Color.litegray;

    this.xText = "x";
    this.yText = "y";

    this.xmin = -1.0;
    this.xmax = 1.0;
    this.xspan = 2.0;
    this.ymin = -10.0;
    this.ymax = 10.0;
    this.yspan = 20.0;

    this.x0 = 0.0;
    this.y0 = 0.0;
    this.wx0 = 0;
    this.wy0 = 0;
    this.xShortTickStep = 0.1;
    this.xShortTickMin = this.xmin;
    this.xShortTickMax = this.xmax;

    this.xLongTickStep = 0.2;
    this.xLongTickMin = this.xmin;
    this.xLongTickMax = this.xmax;

    this.xLabelStep = 0.2;
    this.xLabelMin = this.xmin;
    this.xLabelMax = this.xmax;

    this.xGridStep = 0.2;
    this.xGridMin = this.xmin;
    this.xGridMax = this.xmax;

    this.formatxzero = true;
    this.formatyzero = true;

    this.yShortTickStep = 1;
    this.yShortTickMin = this.ymin;
    this.yShortTickMax = this.ymax;

    this.yLongTickStep = 2;
    this.yLongTickMin = this.ymin;
    this.yLongTickMax = this.ymax;

    this.yLabelStep = 2;
    this.yLabelMin = this.ymin;
    this.yLabelMax = this.ymax;

    this.yGridStep = 2;
    this.yGridMin = this.ymin;
    this.yGridMax = this.ymax;

    this.automaticxLabels = true;
    this.xLabelyOffset = 7;
    this.automaticyLabels = true;
    this.yLabelxOffset = -7;

    this.xTextxOffset = 9;
    this.yTextyOffset = -9;

    this.hasxLog = false;
    this.hasyLog = false;
    this.xPowerMin = 1;
    this.xPowerMax = 5;
    this.yPowerMin = 1;
    this.yPowerMax = 5;
    this.xLabelDecimalDigits = 1;
    this.yLabelDecimalDigits = 1;

    this.showxGrid = true;
    this.showyGrid = true;
    this.showBorder = true;
    this.showxShortTicks = true;
    this.showxLongTicks = true;
    this.showxLabels = true;
    this.showyShortTicks = true;
    this.showyLongTicks = true;
    this.showyLabels = true;
    this.showxAxis = true;
    this.showxText = true;
    this.showyAxis = true;
    this.showyText = true;

    //Readouts
    this.hasHReadout = false;
    this.hasVReadout = false;
    this.hasReadout = false;
    this.crosshairColor = Color.litegray;
    this.mousePosx = 0;
    this.mousePosy = 0;
    this.showHCrosshair = false;
    this.showVCrosshair = false;
    this.mouseInside = false;
    
    this.isDragging = false;
    //Bind events to the correct context
    this.mouseDown = this.mouseDown.bind(this);
    this.mouseMove = this.mouseMove.bind(this);
    this.mouseUp = this.mouseUp.bind(this);
    this.mouseOver = this.mouseOver.bind(this);
    this.mouseOut = this.mouseOut.bind(this);
    
    //Add the necessary events
    this.canvas.addEventListener('mousedown', this.mouseDown);
    this.canvas.addEventListener('mouseover', this.mouseOver);
      
    //These are attached later, on mousedown
    //this.canvas.addEventListener('mousemove', this.mouseMove);
    //this.canvas.addEventListener('mouseup', this.mouseUp);
    //This is attached later, on mouseover, is there is a readout
    //this.canvas.addEventListener('mouseout', this.mouseOut);
  }
  U.copyPrototype(Graph, Component);

  Graph.prototype.drawBorder = function () {
    this.ctx.strokeStyle = this.drawingZoneBorderColor;
    U.drawRect(this.ctx,
               this.dZone.left, this.dZone.top,
               this.dZone.right, this.dZone.bottom);
  };

  Graph.prototype.drawxAxis = function () {
    this.wy0 = this.getyPix(this.y0);
    this.ctx.strokeStyle = this.xAxisColor;
    U.drawLine(this.ctx,
               this.dZone.left, this.wy0,
               this.dZone.right + 6, this.wy0);
    U.drawLine(this.ctx,
               this.dZone.right + 3, this.wy0 - 3,
               this.dZone.right + 3, this.wy0 + 3);
    U.drawLine(this.ctx,
               this.dZone.right + 4, this.wy0 - 2,
               this.dZone.right + 4, this.wy0 + 2);
    U.drawLine(this.ctx,
               this.dZone.right + 5, this.wy0 - 1,
               this.dZone.right + 5, this.wy0 + 1);
  };

  Graph.prototype.drawxLog = function () {
    var power;
    var x;
    var wx;
    var wy = this.dZone.bottom + 12;
    var str;

    //Don't draw grid line when on border of graph
    for (var p = this.xPowerMin; p <= this.xPowerMax; p++) {
      wx = this.getxPix(p);
      if (wx > this.dZone.right) {
        wx = this.dZone.right;
      }  
      //Labeled grid line
       //Don't draw line on left or right border of graph
      if (p !== this.xPowerMin && p !== this.xPowerMax) {
        this.ctx.strokeStyle = this.xGridColor;
        U.drawLine(this.ctx, wx, this.dZone.bottom, wx, this.dZone.top);
      }
      //Long ticks
      this.ctx.strokeStyle = this.xLabelColor;
      U.drawLine(this.ctx, wx, this.dZone.bottom, wx, this.dZone.bottom + 4);
      //Now the labels
      this.ctx.fillStyle = this.xLabelColor;
      this.ctx.strokeStyle = this.xLabelColor;
      str = "10^{" + p.toFixed(0) + "}";
      U.drawSubSuperScript(this.ctx, str, wx, wy, "center", "top");

      if (p !== this.xPowerMax) {
        for (var i = 2; i < 10; i++) {
          x = p + U.log10(i);
          wx = this.getxPix(x);
          //Grid
          this.ctx.strokeStyle = this.xGridColor;
          U.drawLine(this.ctx, wx, this.dZone.bottom, wx, this.dZone.top);
          //Short ticks
          this.ctx.strokeStyle = this.xLabelColor;
          U.drawLine(this.ctx,
                     wx, this.dZone.bottom,
                     wx, this.dZone.bottom + 2);
        }
      }
    }
  };

  Graph.prototype.drawyLog = function () {
    var power;
    var y;
    var wy;
    var wx = this.dZone.left - 7;
    var str;

    //Don't draw grid line when on border of graph
    for (var p = this.yPowerMin; p <= this.yPowerMax; p++) {
      wy = this.getyPix(p);
      if (wy < this.dZone.top) {
        wy = this.dZone.top;
      }  
      //Labeled grid line
      //Don't draw line on left or right border of graph
      if (p !== this.yPowerMin && p !== this.yPowerMax) {
        this.ctx.strokeStyle = this.yGridColor;
        U.drawLine(this.ctx, this.dZone.left, wy, this.dZone.right, wy);
      }
      //Long ticks
      this.ctx.strokeStyle = this.yLabelColor;
      U.drawLine(this.ctx, this.dZone.left, wy, this.dZone.left - 4, wy);
      //Now the labels
      this.ctx.fillStyle = this.yLabelColor;
      this.ctx.strokeStyle = this.yLabelColor;
      str = "10^{" + p.toFixed(0) + "}";
      U.drawSubSuperScript(this.ctx, str, wx, wy, "right", "middle");

      if (p !== this.xPowerMax) {
        for (var i = 2; i < 10; i++) {
          y = p + U.log10(i);
          wy = this.getyPix(y);
          //Grid
          this.ctx.strokeStyle = this.yGridColor;
          U.drawLine(this.ctx, this.dZone.left, wy, this.dZone.right, wy);
          //Short ticks
          this.ctx.strokeStyle = this.xLabelColor;
          U.drawLine(this.ctx, this.dZone.left, wy, this.dZone.left - 2, wy);
        }
      }
    }
  };

  Graph.prototype.drawxGrid = function () {
    var x;
    var wx;

    this.ctx.strokeStyle = this.xGridColor;

    if (this.xGridStep > 0) {
      for (x = this.xGridMin; x <= this.xGridMax; x += this.xGridStep) {
        wx = this.getxPix(x);
        if (wx > this.dZone.right) {
          wx = this.dZone.right;
        }  
        U.drawLine(this.ctx, wx, this.dZone.bottom, wx, this.dZone.top);
      }
    }
  };

  Graph.prototype.drawxLongTicks = function () {
    var x;
    var wx;

    this.ctx.strokeStyle = this.xLabelColor;

    if (this.xLongTickStep > 0) {
      for (x = this.xLongTickMin; x <= this.xLongTickMax;
           x += this.xLongTickStep) {
        wx = this.getxPix(x);
        if (wx > this.dZone.right) {
          wx = this.dZone.right;
        }  
        U.drawLine(this.ctx, wx, this.dZone.bottom, wx, this.dZone.bottom + 4);
      }
    }
  };

  Graph.prototype.drawxShortTicks = function () {
    var x;
    var wx;

    this.ctx.strokeStyle = this.xLabelColor;

    if (this.xShortTickStep > 0) {
      for (x = this.xShortTickMin; x <= this.xShortTickMax;
           x += this.xShortTickStep) {
        wx = this.getxPix(x);
        if (wx > this.dZone.right) {
          wx = this.dZone.right;
        }  
        U.drawLine(this.ctx, wx, this.dZone.bottom, wx, this.dZone.bottom + 2);
      }
    }
  };

  Graph.prototype.drawyAxis = function () {
    this.wx0 = this.getxPix(this.x0);

    this.ctx.strokeStyle = this.yAxisColor;
    U.drawLine(this.ctx,
               this.wx0, this.dZone.bottom,
               this.wx0, this.dZone.top - 6);
    U.drawLine(this.ctx,
               this.wx0 - 3, this.dZone.top - 3,
               this.wx0 + 3, this.dZone.top - 3);
    U.drawLine(this.ctx,
               this.wx0 - 2, this.dZone.top - 4,
               this.wx0 + 2, this.dZone.top - 4);
    U.drawLine(this.ctx,
               this.wx0 - 1, this.dZone.top - 5,
               this.wx0 + 1, this.dZone.top - 5);
  };

  Graph.prototype.drawyLongTicks = function () {
    var y;
    var wy;

    this.ctx.strokeStyle = this.yLabelColor;

    if (this.yLongTickStep > 0) {
      for (y = this.yLongTickMin; y <= this.yLongTickMax; y += 
           this.yLongTickStep) {
        wy = this.getyPix(y);
        if (wy < this.dZone.top) {
          wy = this.dZone.top;
        }  
        U.drawLine(this.ctx, this.dZone.left, wy, this.dZone.left - 4, wy);
      }
    }
  };

  Graph.prototype.drawyShortTicks = function () {
    var y;
    var wy;

    this.ctx.strokeStyle = this.yLabelColor;

    if (this.yShortTickStep > 0) {
      for (y = this.yShortTickMin; y <= this.yShortTickMax;
           y += this.yShortTickStep) {
        wy = this.getyPix(y);
        if (wy < this.dZone.top) {
          wy = this.dZone.top;
        }  
        U.drawLine(this.ctx, this.dZone.left, wy, this.dZone.left - 2, wy);
      }
    }
  };

  Graph.prototype.drawyGrid = function () {
    var y;
    var wy;

    this.ctx.strokeStyle = this.yGridColor;

    if (this.yGridStep > 0) {
      for (y = this.yGridMin; y <= this.yGridMax; y += this.yGridStep) {
        wy = this.getyPix(y);
        if (wy < this.dZone.top) {
          wy = this.dZone.top;
        }  
        U.drawLine(this.ctx, this.dZone.left, wy, this.dZone.right, wy);
      }
    }
  };

  Graph.prototype.drawxLabels = function () {
    var x;
    var wx = 0;
    var wy = this.dZone.bottom + this.xLabelyOffset;
    //y coordinate of all labels
    var str;

    this.ctx.font = Font.labelText;
    this.ctx.fillStyle = this.xLabelColor;
    this.ctx.textAlign = "center";
    this.ctx.textBaseline = "top";

    if (this.xLabelStep > 0.0) {
      if (this.automaticxLabels) {
        for (x = this.xLabelMin; x <= this.xLabelMax; x += this.xLabelStep) {
          wx = this.getxPix(x);

          if (Math.abs(x) < 0.00001 && this.formatxzero) {
            str = "0";
          }  
          else {
            str = x.toFixed(this.xLabelDecimalDigits);
          }  

          this.ctx.fillText(str, wx, wy);
        }
      }
    }
  };

  Graph.prototype.drawxText = function () {
    var x;
    var wx = this.dZone.right + this.xTextxOffset;
    var wy = this.getyPix(this.y0);

    this.ctx.fillStyle = this.xTextColor;
    U.drawSubSuperScript(this.ctx,
                         this.xText, wx, wy, "left", "middle",
                         Font.normalText, Font.subSupText);
  };

  Graph.prototype.drawyLabels = function () {
    var y;
    var wy = 0;
    var wx = this.dZone.left + this.yLabelxOffset;
    var str;

    this.ctx.font = Font.labelText;
    this.ctx.fillStyle = this.yLabelColor;
    this.ctx.textAlign = "right";
    this.ctx.textBaseline = "middle";

    if (this.yLabelStep > 0.0) {
      if (this.automaticyLabels) {
        for (y = this.yLabelMin; y <= this.yLabelMax; y += this.yLabelStep) {
          wy = this.getyPix(y);

          if (Math.abs(y) < 0.00001 && this.formatyzero) {
            str = "0";
          }  
          else {
            str = y.toFixed(this.yLabelDecimalDigits);
          }  

          this.ctx.fillText(str, wx, wy);
        }
      }
    }
  };

  Graph.prototype.drawyText = function () {
    var x;
    var wx = this.getxPix(this.x0);
    var wy = this.dZone.top + this.yTextyOffset;

    this.ctx.fillStyle = this.yTextColor;
    U.drawSubSuperScript(this.ctx, this.yText, wx, wy,
                         "center", "bottom", Font.normalText, Font.subSupText);
  };

  Graph.prototype.setReadouts = function (hasHReadout, hasVReadout) {
      this.hasHReadout = hasHReadout;
      this.hasVReadout = hasVReadout;
      
      this.hasReadout = this.hasHReadout || this.hasVReadout ;
  };
  
  Graph.prototype.drawCrosshairs = function () {
    if (this.showHCrosshair) {
      this.drawHCrosshair();
    }
    if (this.showVCrosshair) {
      this.drawVCrosshair();
    }  
  };  
  
  Graph.prototype.drawHCrosshair = function () {
      this.ctx.strokeStyle = this.crosshairColor;
      U.drawLine(this.ctx,
                 this.dZone.left, this.mousePosy,
                 this.dZone.right, this.mousePosy);
  };

  Graph.prototype.drawVCrosshair = function () {
      this.ctx.strokeStyle = this.crosshairColor;
      U.drawLine(this.ctx,
                this.mousePosx, this.dZone.bottom,
                this.mousePosx, this.dZone.top);
  };

  Graph.prototype.setClip = function () {
    this.ctx.beginPath();
    this.ctx.rect(this.dZone.left, this.dZone.top,
                  this.dZone.right - this.dZone.left + 1,
                  this.dZone.bottom - this.dZone.top + 1);
    this.ctx.clip();
  };

  Graph.prototype.updateDrawingZone = function () {
    //Clear drawing zone
    this.ctx.fillStyle = this.drawingZoneColor;
    U.fillRect(this.ctx,
               this.dZone.left, this.dZone.top,
               this.dZone.right, this.dZone.bottom);

    if (!this.hasxLog && this.showxGrid) {
      this.drawxGrid();
    }

    if (!this.hasyLog && this.showyGrid) {
      this.drawyGrid();
    }

    if (this.showBorder) {
      this.drawBorder();
    }  

    if (this.showxAxis) {
      this.drawxAxis();
    }  

    if (this.showyAxis) {
      this.drawyAxis();
    }  
  };

  Graph.prototype.draw = function () {
    this.clear();
    
    //Clear drawing zone
    this.ctx.fillStyle = this.drawingZoneColor;
    U.fillRect(this.ctx,
               this.dZone.left, this.dZone.top,
               this.dZone.right, this.dZone.bottom);

    if (!this.hasxLog && this.showxGrid) {
      this.drawxGrid();
    }

    if (!this.hasyLog && this.showyGrid) {
      this.drawyGrid();
    }

    if (this.showBorder) {
      this.drawBorder();
    }  

    if (!this.hasxLog) {
      if (this.showxShortTicks) {
        this.drawxShortTicks();
      }  
      if (this.showxLongTicks) {
        this.drawxLongTicks();
      }  
      if (this.showxLabels) {
        this.drawxLabels();
      }  
    }

    if (!this.hasyLog) {
      if (this.showyShortTicks) {
        this.drawyShortTicks();
      }  
      if (this.showyLongTicks) {
        this.drawyLongTicks();
      }  
      if (this.showyLabels) {
        this.drawyLabels();
      }  
    }

    if (this.hasxLog) {
      this.drawxLog();
    }  

    if (this.hasyLog) {
      this.drawyLog();
    }  

    if (this.showxAxis) {
      this.drawxAxis();
    }  
    if (this.showxText) {
      this.drawxText();
    }  

    if (this.showyAxis) {
      this.drawyAxis();
    }  
    if (this.showyText) {
      this.drawyText();
    }  
  };

  //Functions f, with any number of arguments, drawn from x = left to x = right
  Graph.prototype.drawCurve = function (f, xlow, xhigh, color) {
    this.ctx.save();
    this.setClip();
    var wx, wy, wxlow, wxhigh;
    var x, y;

    this.ctx.strokeStyle = color;

    //Get the left and right pixel bounds
    wxlow = this.getxPix(xlow);
    wxhigh = this.getxPix(xhigh);

    //Now start iteration, pixel by pixel
    x = xlow;
    wx = this.getxPix(x);
    y = f(x);
    wy = this.getyPix(y);

    this.ctx.beginPath();
    this.ctx.moveTo(wx + 0.5, wy + 0.5);

    while (wx < wxhigh) {
      wx++;
      x = this.getxFromPix(wx);
      y = f(x);
      wy = this.getyPix(y);
      this.ctx.lineTo(wx + 0.5, wy + 0.5);
    }
    this.ctx.lineTo(wx, wy);

    this.ctx.stroke();
    this.ctx.restore();
  };

  Graph.prototype.fillCurve = function (f, xlow, xhigh, color) {
    this.ctx.save();
    this.ctx.globalAlpha = 0.5;
    this.setClip();
    var wx, wy, wxlow, wxhigh;
    var x, y;

    this.ctx.fillStyle = color;
    //Get the left and right pixel bounds
    wxlow = this.getxPix(xlow);
    wxhigh = this.getxPix(xhigh);

    //Now start iteration, pixel by pixel
    wx = wxlow;
    y = f(x);
    wy = this.getyPix(y);

    this.ctx.beginPath();
    this.ctx.moveTo(wx + 0.5, wy + 0.5);

    while (wx < wxhigh) {
      wx++;
      x = this.getxFromPix(wx);
      y = f(x);
      wy = this.getyPix(y);
      this.ctx.lineTo(wx + 0.5, wy + 0.5);
    }
    this.ctx.lineTo(wx, wy);
    wy = this.getyPix(0.0);
    this.ctx.lineTo(wxhigh, wy);
    this.ctx.lineTo(wxlow, wy);

    this.ctx.fill();
    this.ctx.restore();
  };

  //Not used for the moment. TO DO: correct its behavior
  Graph.prototype.drawArray = function (tt, ff, color) {
    this.ctx.save();
    this.setClip();
    var wx, wy;
    var x, y;
    var l = tt.length;
    this.ctx.beginPath();
    this.ctx.rect(this.dZone.left, this.dZone.top,
                  this.dZone.width, this.dZone.height);
    this.ctx.clip();
    this.ctx.strokeStyle = color;

    wx = this.getxPix(tt[0]);
    wy = this.getyPix(ff[0]);
    this.ctx.beginPath();
    this.ctx.moveTo(wx + 0.5, wy + 0.5);

    for (var i = 0; i < l; i++) {
      wx = this.getxPix(tt[i]);
      wy = this.getyPix(ff[i]);
      this.ctx.lineTo(wx, wy);
    }

    this.ctx.stroke();
    this.ctx.restore();
  };

  Graph.prototype.drawPoint = function (x, y, color) {
    this.ctx.save();
    this.setClip();
    this.ctx.fillStyle = color;
    U.drawPoint(this.ctx, this.getxPix(x), this.getyPix(y), 2);
    this.ctx.restore();
  };

  Graph.prototype.drawHollowPoint = function (x, y, color) {
    this.ctx.save();
    this.setClip();
    this.ctx.strokeStyle = color;
    U.drawHollowPoint(this.ctx, this.getxPix(x), this.getyPix(y), 4);
    this.ctx.restore();
  };

  Graph.prototype.drawDiamond = function (x, y, color) {
    this.ctx.save();
    this.setClip();
    this.ctx.fillStyle = color;
    U.drawDiamond(this.ctx, this.getxPix(x), this.getyPix(y), 4);
    this.ctx.restore();
  };

  Graph.prototype.drawX = function (x, y, color) {
    this.ctx.save();
    this.setClip();
    this.ctx.strokeStyle = color;
    U.drawX(this.ctx, this.getxPix(x), this.getyPix(y), 4);
    this.ctx.restore();
  };

  Graph.prototype.drawLine = function (x1, y1, x2, y2, color) {
    this.ctx.save();
    this.setClip();
    this.ctx.strokeStyle = color;
    U.drawLine(this.ctx,
               this.getxPix(x1), this.getyPix(y1),
               this.getxPix(x2), this.getyPix(y2));
    this.ctx.restore();
  };

  Graph.prototype.drawArrow = function (x1, y1, x2, y2, color) {
    this.ctx.save();
    this.setClip();
    this.ctx.strokeStyle = color;
    this.ctx.fillStyle = color;
    U.drawArrow(this.ctx,
                this.getxPix(x1), this.getyPix(y1),
                this.getxPix(x2), this.getyPix(y2), 5, 10);
    this.ctx.restore();
  };

  //Draws a rectangle, bottom left (x, y), width, height
  Graph.prototype.drawRectangle = function (x, y, width, height, fillColor, borderColor) {
    this.ctx.save();
    this.setClip();
    this.ctx.globalAlpha = 0.5;
    this.ctx.fillStyle = fillColor;
    U.fillRect(this.ctx,
               this.getxPix(x), this.getyPix(y + height),
               this.getxPix(x + width), this.getyPix(y));
    this.ctx.globalAlpha = 1.0;
    this.ctx.strokeStyle = borderColor;
    U.drawRect(this.ctx,
               this.getxPix(x), this.getyPix(y + height),
               this.getxPix(x + width), this.getyPix(y));
    this.ctx.restore();
  };

  Graph.prototype.drawArc = function (x, y, radius, start, end, 
                                      counterclockwise, radiusInPixels, color) {
    var wx = this.getxPix(x);
    var wy = this.getyPix(y);
    var wx0, wy0, wx1, wy1, xy, wxd, wyd, wradius;
     
    this.ctx.save();
    this.setClip();
    this.ctx.strokeStyle = color;
    if (radiusInPixels) {
      U.drawArc(this.ctx, wx, wy, radius, start, end, counterclockwise);
    }
    else { 
      wx0 = this.getxPix(0.0);
      wy0 = this.getyPix(0.0);
      //Now take a point at a distance of 1 from the origin
      //For example set x*x = 0.5, x = Math.sqrt(0.5) then y = x
      xy = Math.sqrt(0.5);
      wx1 = this.getxPix(xy);
      wy1 = this.getyPix(xy);
      
      wxd = wx1 - wx0;
      wyd = wy1 - wy0;
      wradius = Math.round(Math.sqrt(wxd*wxd + wyd*wyd));//# pixels for 1.0
      wradius *= radius;
      U.drawArc(this.ctx, wx, wy, wradius, start, end, counterclockwise);
    }
      
    this.ctx.restore();
  };

  Graph.prototype.drawShape = function (x, y, color) {
    var xpix = [], ypix = []; //Array of pixels
    this.ctx.save();
    this.setClip();
    this.ctx.strokeStyle = color;
    //Convert to an array of pixels
    for (var i = 0, l = x.length; i < l; i++) {
      xpix[i] = this.getxPix(x[i]);
      ypix[i] = this.getyPix(y[i]);
    }
    U.drawShape(this.ctx, xpix, ypix);
    this.ctx.restore();
  };

  Graph.prototype.fillShape = function (x, y, color) {
    var xpix = [],
      ypix = []; //Array of pixels
    this.ctx.save();
    this.setClip();
    this.ctx.fillStyle = color;
    //Convert to an array of pixels
    for (var i = 0, l = x.length; i < l; i++) {
      xpix[i] = this.getxPix(x[i]);
      ypix[i] = this.getyPix(y[i]);
    }
    U.fillShape(this.ctx, xpix, ypix);
    this.ctx.restore();
  };

  Graph.prototype.getxPix = function (x) {
    return Math.round(this.dZone.left +
    (this.dZone.right - this.dZone.left) * (x - this.xmin) / this.xspan);
  };

  Graph.prototype.getyPix = function (y) {
    return Math.round(this.dZone.bottom -
    (this.dZone.bottom - this.dZone.top) * (y - this.ymin) / this.yspan);
  };

  Graph.prototype.getxFromPix = function (wx) {
    return (this.xmin + 
    this.xspan * (wx - this.dZone.left) / (this.dZone.right - this.dZone.left));
  };

  Graph.prototype.getyFromPix = function (wy) {
    return (this.ymin +
    this.yspan * (this.dZone.bottom - wy) / (this.dZone.bottom - this.dZone.top));
  };

  Graph.prototype.inBounds = function (pt) {
    if ((this.dZone.left <= pt.x) && (pt.x <= this.dZone.right) && 
        (this.dZone.top <= pt.y) && (pt.y <= this.dZone.bottom)) {
      return true;
    }
    else {
      return false;
    }  
  };
  
  Graph.prototype.clipToBounds = function (pt) {
    if (pt.x < this.dZone.left) {
      pt.x = this.dZone.left;
    }
    else if (pt.x > this.dZone.right) {
      pt.x = this.dZone.right;
    }
    if (pt.y < this.dZone.top) {
      pt.y = this.dZone.top;
    }
    else if (pt.y > this.dZone.bottom) {
      pt.y = this.dZone.bottom;
    }  
  };
  
  Graph.prototype.mouseDown = function (event) {
    var event = event || window.event;
    var mpos = this.getMousePosition(event);
    if (this.inBounds(mpos)) {
      if (this.hasReadout) {
        //First remove the mousemove listener that has been added
        this.canvas.removeEventListener('mousemove', this.mouseMove, true);
        if (this.hasHReadout) {
          this.showHCrosshair = false;
        }
        if (this.hasVReadout) {
          this.showVCrosshair = false;
        }
      }  
           
      this.isDragging = true;
      var xm = this.getxFromPix(mpos.x);
      var ym = this.getyFromPix(mpos.y);
      this.fireEvent("mousedown", {
        x: xm,
        y: ym,
        wx: mpos.x,
        wy: mpos.y
      });
      //Track the mouse movement outside of the component
      document.addEventListener('mousemove', this.mouseMove, true);
      //Track if a mouse up occurs outside of the component
      document.addEventListener('mouseup', this.mouseUp, true);
      this.cancelDefaultAction(event);
    }  
  };
  
  Graph.prototype.mouseOver = function (event) {
    var event = event || window.event;
    if (!this.isDragging && this.hasReadout) {
      this.canvas.addEventListener('mousemove', this.mouseMove, false);
    }  
  };

  Graph.prototype.mouseMove = function (event) {
    var event = event || window.event;
    var mpos, xm, ym;
    if (this.isDragging) {
      mpos = this.getMousePosition(event);
      this.clipToBounds(mpos);
      xm = this.getxFromPix(mpos.x);
      ym = this.getyFromPix(mpos.y);
      this.fireEvent('mousedrag', {
        x: xm,
        y: ym,
        wx: mpos.x,
        wy: mpos.y
      });
    }
    //We are in readout mode
    else {
      mpos = this.getMousePosition(event);
      if (this.inBounds(mpos)) {
        this.mousePosx = mpos.x;
        this.mousePosy = mpos.y;
        xm = this.getxFromPix(mpos.x);
        ym = this.getyFromPix(mpos.y);
        if (this.mouseInside === false) {
          if (this.hasHReadout) {
            this.showHCrosshair = true;
          }
          if (this.hasVReadout) {
            this.showVCrosshair = true;
          } 
          this.fireEvent('mouseover', {
            x: xm,
            y: ym,
            wx: mpos.x,
            wy: mpos.y
          });
          this.mouseInside = true;   
        }
        else {
          this.fireEvent('mousemove', {
            x: xm,
            y: ym,
            wx: mpos.x,
            wy: mpos.y
          });
        }     
      }
      else {
        if (this.mouseInside === true) {
          if (this.hasHReadout) {
            this.showHCrosshair = false;
          }
          if (this.hasVReadout) {
            this.showVCrosshair = false;
          }
          this.fireEvent('mouseout');
          this.mouseInside = false;
        }
      }        
    }  
    this.cancelDefaultAction(event);  
  };

  Graph.prototype.mouseUp = function (event) {
    var event = event || window.event;
    var mposini = this.getMousePosition(event);
    var mpos = this.getMousePosition(event);
    //To avoid mouse up when mouse down happened on another component
    if (this.isDragging) {
      this.clipToBounds(mpos);
      var xm = this.getxFromPix(mpos.x);
      var ym = this.getyFromPix(mpos.y);
      this.fireEvent("mouseup", {
        x: xm,
        y: ym,
        wx: mpos.x,
        wy: mpos.y
      });
      //Remove the previous event listeners, as they are no longer useful
      document.removeEventListener('mousemove', this.mouseMove, true);
      document.removeEventListener('mouseup', this.mouseUp, true);
    }  
    this.isDragging = false;
    if (this.inBounds(mposini) && this.hasReadout) {
      this.canvas.addEventListener('mousemove', this.mouseMove, false);
      this.mousePosx = mpos.x;
      this.mousePosy = mpos.y;
      xm = this.getxFromPix(mpos.x);
      ym = this.getyFromPix(mpos.y);
      if (this.hasHReadout) {
        this.showHCrosshair = true;
      }
      if (this.hasVReadout) {
        this.showVCrosshair = true;
      } 
      this.fireEvent('mousemove', {
        x: xm,
        y: ym,
        wx: mpos.x,
        wy: mpos.y
      });
      this.mouseInside = true;
    }  
    this.cancelDefaultAction(event);
  };
  
  Graph.prototype.mouseOut = function (event) {
    var event = event || window.event;
    if (this.hasReadout) {
      this.canvas.removeEventListener('mousemove', this.mouseMove, true);
    }
  };

  return Graph;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));