(function (requirejs, require, define) {
define(function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  var Color = require('color');
  var Font = require('font');

  //The code for this component differs very little from the checkbox.
  //We should consider having one common ancestor
  function RadioButton(left, top, width, height) {
    //Call super class
    this.Component(left, top, width, height);
    this.isChecked = false;
    this.text = "";
    this.circleBackgroundColor = Color.black;
    this.circleBorderColor = Color.himidgray;
    this.textColor = Color.white;
    this.circle = {
      left: 0,
      top: 2,
      right: 11,
      bottom: 13,
      width: 12,
      height: 12
    };

    this.group = null; //This changes if the radio button is added to a group

    //Bind mouseDown to the correct context
    //Otherwise 'this' in mouseDown would refer to the source of the event,
    //the canvas
    this.mouseDown = this.mouseDown.bind(this);
    //Register the click that will check/unckeck the radiobutton
    this.canvas.addEventListener('mousedown', this.mouseDown, false);
  }
  U.copyPrototype(RadioButton, Component);

  RadioButton.prototype.draw = function () {
    this.clear();

    //Recalculate the bounding box based on the text
    var textWidth = U.subSuperScriptLength(this.ctx, this.text,
                                           Font.normalText, Font.subSupText);
    var width = 1 + this.circle.width + 8 + textWidth;
    var height = 1 + Math.max(this.circle.bottom, Font.normalSize.height);
    this.setSize(width, height);

    //Draw the component
    this.ctx.fillStyle = this.circleBackgroundColor;
    U.fillCircle(this.ctx,
                 this.circle.left, this.circle.top,
                 this.circle.right, this.circle.bottom);
    this.ctx.strokeStyle = this.circleBorderColor;
    U.drawCircle(this.ctx,
                 this.circle.left, this.circle.top,
                 this.circle.right, this.circle.bottom);

    this.ctx.fillStyle = this.textColor;
    U.drawSubSuperScript(this.ctx, this.text,
                         this.circle.right + 8, this.circle.bottom,
                         "left", "alphabetic", Font.normalText,
                         Font.subSupText);
    if (this.isChecked) {
      this.ctx.fillStyle = this.textColor;
      this.ctx.strokeStyle = this.textColor;
      U.fillCircle(this.ctx,
                   this.circle.left + 2, this.circle.top + 2,
                   this.circle.right - 2, this.circle.bottom - 2);
    }
  }

  RadioButton.prototype.mouseDown = function (event) {
    var event = event || window.event;
    //Unselect all the other radiobuttons of the group
    if (this.group !== null && !this.isChecked) {
      var rbs = this.group.radioButtons;
      for (var i = 0; i < rbs.length; i++) {
        //Only redraw a checked radio button
        if (rbs[i].isChecked) {
          rbs[i].isChecked = false;
          rbs[i].draw();
        }
      }
      //Now check our radio button and draw
      this.isChecked = !this.isChecked;
      this.draw();
      this.fireEvent("mousedown", this);
    }
    this.cancelDefaultAction(event);
  };

  return RadioButton;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));