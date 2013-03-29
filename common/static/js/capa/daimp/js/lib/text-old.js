define(function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  var Color = require('color');
  var Font = require('font');

  function Text(left, top, right, bottom) {
    //Call super class
    this.Component(left, top, right, bottom);
    this.isChecked = false;
    this.text = "";
    this.textColor = Color.white;
    this.textAlign = "left";
    this.anchorLeft = left; //where the text is actually drawn
    this.anchorTop = top;
    this.hasSubSuperscripts = false;
  }
  U.copyPrototype(Text, Component);

  Text.prototype.clear = function () {
    this.getBB();
    // super.clear()
    Component.prototype.clear.call(this);
  };

  Text.prototype.draw = function () {
    this.clear();
    this.ctx.font = Font.normalText;
    this.ctx.textAlign = this.textAlign;
    this.ctx.textBaseline = "bottom";
    this.ctx.fillStyle = this.textColor;
    if (!this.hasSubSuperscript) {
      this.ctx.fillText(this.text, this.anchorLeft, this.anchorTop);
    }  
    else {
      U.drawSubSuperScript(this.ctx, this.text,
                           this.bBox.left, this.bBox.top,
                           this.textAlign, "bottom",
                           Font.normalText, Font.subSupText);
    }

    // DEBUG
    // this.ctx.strokeStyle = "red";
    // U.drawRect(this.ctx, this.bBox.left, this.bBox.top, this.bBox.right, this.bBox.bottom);
  };

  Text.prototype.getBB = function () {
    this.ctx.font = Font.normalText;
    var width = this.ctx.measureText(this.text).width;
    var height = U.measureFont(Font.normalText).height;

    var x = this.anchorLeft;
    var y = this.anchorTop;

    this.bBox.left = x - width / 2;
    this.bBox.right = x + width / 2;
    this.bBox.top = y - height;
    this.bBox.bottom = y;
    this.bBox.width = width;
    this.bBox.height = height;

    if (this.textAlign === "left") {
      this.bBox.left = x;
      this.bBox.right = x + width;
    }
    else if (this.textAlign === "right") {
      this.bBox.left = x - width;
      this.bBox.right = x;
    }

    return this.bBox;
  };

  return Text;
});