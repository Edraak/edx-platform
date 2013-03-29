(function (requirejs, require, define) {
define(function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  var Color = require('color');
  var Font = require('font');

  function DropDown(left, top, width, height) {
    //Call super class
    this.Component(left, top, width, height);
    this.textOptions = [];
    this.which = -1; // index of selection displayed when !isDropped

    this.arrowBackgroundColor = Color.darkgray;
    this.arrowBorderColor = Color.yellow;
    this.arrowColor = Color.litegray;
    this.arrow = {
      left: 0,
      top: 2,
      right: 16,
      bottom: 18,
      width: 17,
      height: 17,
      triangle: [
        4, 9,
        12, 9,
        8, 13
      ]
    };

    this.textColor = Color.litegray;

    this.dropBackgroundColor = Color.darkgray;
    this.dropBorderColor = Color.yellow;
    this.dropTextColor = Color.himidgray;
    this.dropSelectedColor = Color.litegray;
    this.dropHoverColor = Color.white;
    this.dropStaysOverTool = false;

    //// private fields ////
    // padding on top, words, then padding, then a line
    this.dropEntryHeight = 2 + Font.normalSize.height + 2;
    this.isDropped = false;
    this.hoverIndex = -1;

    // create a new component canvas and use its methods
    this.dropComp = new Component(left, top, width, height);
    this.dropComp.canvas.style.backgroundColor = this.dropBackgroundColor;
    this.dropComp.setVisibility(this.isDropped);

    //Bind events to the correct context
    this.openEvent = this.openEvent.bind(this);
    this.closeEvent = this.closeEvent.bind(this);
    this.dropMouseMove = this.dropMouseMove.bind(this);
    this.dropMouseOut = this.dropMouseOut.bind(this);

    //Add the necessary events
    this.canvas.addEventListener('mousedown', this.openEvent, false);
    this.dropComp.canvas.addEventListener('mouseup', this.closeEvent, false);
    this.dropComp.canvas.addEventListener('mousemove', this.dropMouseMove, false);
    this.dropComp.canvas.addEventListener('mouseout', this.dropMouseOut, false);
  }
  U.copyPrototype(DropDown, Component);

  DropDown.prototype.draw = function () {
    // attach
    if (!this.dropComp.canvas.parentNode && this.canvas.parentNode) {
      this.canvas.parentNode.appendChild(this.dropComp.canvas);
    }

    this.calcComponentSize();
    this.clear();
    this.drawArrow();
    this.drawText();
  };

  DropDown.prototype.calcComponentSize = function () {
    var text = (this.which >= 0) ? this.textOptions[this.which] : '--';
    var textWidth = U.subSuperScriptLength(this.ctx, text,
                                           Font.normalText, Font.subSupText);
    var fontSize = Font.normalSize.height;

    var width = 1 + this.arrow.right + 8 + textWidth;
    var height = 1 + Math.max(this.arrow.bottom, fontSize);
    this.setSize(width, height);
  };

  DropDown.prototype.drawArrow = function () {
    // draw the border on a rectangle with 0,0 and 16,16 as corners
    // fill the background
    this.ctx.fillStyle = this.arrowBackgroundColor;
    U.fillRect(this.ctx,
               this.arrow.left, this.arrow.top,
               this.arrow.right, this.arrow.bottom);
    this.ctx.strokeStyle = this.arrowBorderColor;
    U.drawRect(this.ctx,
               this.arrow.left, this.arrow.top,
               this.arrow.right, this.arrow.bottom);

    // fill a triangle with corners (4, 7), (12,7), 8,11)
    var t = this.arrow.triangle;
    this.ctx.fillStyle = this.arrowColor;
    U.fillTriangle(this.ctx, t[0], t[1], t[2], t[3], t[4], t[5]);
    U.fillTriangle(this.ctx, t[0], t[1], t[2], t[3], t[4], t[5]);
  };

  DropDown.prototype.drawText = function () {
    var text = '--';
    if (this.which >=0) {
      text = this.textOptions[this.which];
    }

    // paint the text
    this.ctx.fillStyle = this.textColor;
    var x = this.arrow.right + 8,
      y = this.arrow.top + Math.floor(this.arrow.height / 2);
    U.drawSubSuperScript(this.ctx, text, x, y,
                         'left', 'middle', Font.normalText, Font.subSupText);
  };

  DropDown.prototype.calcDropSize = function () {
    // find the size
    var numOpt = this.textOptions.length;
    var height = 1 + numOpt * this.dropEntryHeight;

    var width = 0;
    for (var i = 0; i < numOpt; i++) {
      var len = U.subSuperScriptLength(this.dropComp.ctx, this.textOptions[i],
                                       Font.normalText, Font.subSupText);
      width = Math.max(width, len);
    }
    width += 1 + 8 + 8; // padding

    // position it, centered if possible
    var x = this.left + this.arrow.right,
      y = this.top + this.arrow.top +
          Math.floor((this.arrow.height - height) / 2);

    if (this.dropStaysOverTool) {
      // check to see it doesn't go off the main tool
      var padding = 5;
      var globalHeight = this.tool.height - padding;

      var diff = (y + height - 1) - globalHeight;
      if (diff > 0) {
        y -= diff;
      }

      diff = padding - y;
      if (diff > 0) {
        y += diff;
      }
    }

    // do the positioning
    this.dropComp.setBounds(x, y, width, height);
  }

  DropDown.prototype.drawDrop = function () {
    var ctx = this.dropComp.ctx;
    var right = this.dropComp.width - 1;
    var bottom = this.dropComp.height- 1;
    ctx.fillStyle = this.dropBorderColor;
    U.fillRect(ctx, 0,0,right,bottom);

    for (var i = 0; i < this.textOptions.length; i++) {
      ctx.fillStyle = (this.which === i) ? 
        this.dropSelectedColor :
        this.dropTextColor;
      this.drawDropOption(i);
    }
  };

  DropDown.prototype.openEvent = function () {
    // this happens on a mousedown on the main canvas
    this.hoverIndex = -1;
    this.isDropped = true;

    // draw the drop
    this.calcDropSize();
    this.drawDrop();
    this.dropComp.setVisibility(this.isDropped);

    // listen on the whole document instead
    this.canvas.removeEventListener('mousedown', this.openEvent, false);
    document.addEventListener('mousedown', this.closeEvent, true);

    // prevent text selection if there is a drag
    document.addEventListener('mousemove', document.cancelDefaultAction, false);
  };

  DropDown.prototype.closeEvent = function () {
    // this happens either on a mousedown when the drop is open
    // or after a mouse drag started on the dropdown
    this.isDropped = false;
    this.dropComp.setVisibility(this.isDropped);

    // stop listening on the whole document
    this.canvas.addEventListener('mousedown', this.openEvent, false);
    document.removeEventListener('mousemove', document.cancelDefaultAction, false);
    document.removeEventListener('mousedown', this.closeEvent, true);

    // change the value of the dropdown
    var newInd = this.hoverIndex;
    var oldInd = this.which;

    if (newInd >=0) {
      // close up shop
      this.which = newInd;
      this.draw(); // the main component
      this.fireEvent("change", {
        src: this,
        oldInd: oldInd,
        newInd: newInd
      });
    }
  };

  // find which number was clicked
  DropDown.prototype.findOptionIndex = function (mpos) {
    var which = Math.floor(mpos.y / this.dropEntryHeight);
    if (which >= this.textOptions.length) {
      which = this.textOptions.length - 1;
    }
    return which;
  };

  DropDown.prototype.drawDropOption = function (i) {
    var ctx = this.dropComp.ctx;
    if (i === -1) {
      return;
    }

    // first clear the box
    var top = i * this.dropEntryHeight;
    var bot = (i + 1) * this.dropEntryHeight;
    var right = this.dropComp.width - 1;

    U.clearRect(ctx, 1, top + 1, right - 1, bot - 1);

    // redraw the text
    var newText = this.textOptions[i];
    var x = 8;
    var y = top + this.dropEntryHeight / 2;
    U.drawSubSuperScript(ctx, newText, x, y,
                         "left", "middle", Font.normalText, Font.subSupText);
  };

  // to minimize the use of fillText, only repaint the old hovered text and the new one 
  //when it changes
  DropDown.prototype.dropMouseMove = function (event) {
    var event = event || window.event;
    var mpos = this.dropComp.getMousePosition(event);
    var newInd = this.findOptionIndex(mpos);
    var oldInd = this.hoverIndex;

    if (oldInd === newInd) {
      return;
    }

    // set the value
    this.hoverIndex = newInd;
    var ctx = this.dropComp.ctx;

    // clear the old box
    ctx.fillStyle = (this.which === oldInd) ? 
      this.dropSelectedColor :
      this.dropTextColor;
    this.drawDropOption(oldInd);

    // then do the new box
    ctx.fillStyle = this.dropHoverColor;
    this.drawDropOption(newInd);
  };

  DropDown.prototype.dropMouseOut = function () {
    var oldInd = this.hoverIndex;
    
    // set the value
    this.hoverIndex = -1;
    var ctx = this.dropComp.ctx;

    // clear the old box
    ctx.fillStyle = (this.which === oldInd) ? 
      this.dropSelectedColor :
      this.dropTextColor;
    this.drawDropOption(oldInd);
  };

  return DropDown;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));