(function (requirejs, require, define) {
define(function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  var Color = require('color');
  var Font = require('font');

  function Button(left, top, width, height) {
    //Call super class
    this.Component(left, top, width, height);
    this.isPressed = false;
    this.text = '';
    this.backgroundColor = Color.darkgray;
    this.darkBorderColor = Color.black;
    this.lightBorderColor = Color.himidgray;
    this.textColor = Color.white;
    this.canvas.style.backgroundColor = this.backgroundColor;
    //Bind the events to the correct context
    this.mouseDown = this.mouseDown.bind(this);
    this.mouseUp = this.mouseUp.bind(this);
    this.canvas.addEventListener('mousedown', this.mouseDown, false);
    // mouseup is attached later, on the mousedown
    //this.canvas.addEventListener('mouseup', this.mouseUp, false);
  }
  U.copyPrototype(Button, Component);

  Button.prototype.draw = function () {
    var topColor, bottomColor, xTextOffset, yTextOffset;
    var xmid, ymid;
    var right = this.width - 1, bottom = this.height - 1;

    if (this.isPressed) {
      topColor = this.darkBorderColor;
      bottomColor = this.lightBorderColor;
      xTextOffset = 1;
      yTextOffset = 1;
    }
    else {
      topColor = this.lightBorderColor;
      bottomColor = this.darkBorderColor;
      xTextOffset = 0;
      yTextOffset = 0;
    }

    this.clear();

    this.ctx.strokeStyle = topColor;
    U.drawLine(this.ctx, 0, 0, 0, bottom);
    U.drawLine(this.ctx, 0, 0, right, 0);

    this.ctx.strokeStyle = bottomColor;
    U.drawLine(this.ctx, 0, bottom, right, bottom);
    U.drawLine(this.ctx, right, bottom, right, 0);

    //this.ctx.font = Font.normalText;
    //this.ctx.fillStyle = this.textColor;
    //this.ctx.textAlign = "center";
    //this.ctx.textBaseline = "middle";

    xmid = this.width/2 + xTextOffset;
    ymid = this.height/2 + yTextOffset;
    //this.ctx.fillText(this.text, xmid, ymid + 1);
    this.ctx.fillStyle = this.textColor;
    U.drawSubSuperScript(this.ctx, this.text,
                         xmid, ymid,
                         'center', 'middle',
                         Font.normalText, Font.subSupText);
  };
  
  Button.prototype.mouseDown = function (event) {
    var event = event || window.event;
    this.isPressed = true;
    this.draw();
    this.fireEvent("mousedown", this);
    //Attach an event listener to the document used if mouse up occurs outside
    //of the button
    document.addEventListener('mouseup', this.mouseUp, true);
    this.cancelDefaultAction(event);
  };
  
  Button.prototype.mouseUp = function (event) {
    var event = event || window.event;
    this.isPressed = false;
    this.draw();
    this.fireEvent("mouseup", this);
    //Remove the previous event listener, as it is no longer useful
    document.removeEventListener('mouseup', this.mouseUp, true);
    this.cancelDefaultAction(event);
  };

  return Button;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));