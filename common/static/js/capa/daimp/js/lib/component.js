(function (requirejs, require, define) {
define(function (require) {

  //Imports
  //var $ = require('jquery');
  var U = require('utils');
  var Color = require('color');
  //var Tool = require('tool');

  function Component(left, top, width, height) {
    //Default values
    //Position component at (0,0) with width and height equal to 100
    this.left = (typeof left === 'undefined') ? 0 : left;
    this.top = (typeof top === 'undefined') ? 0 : top;
    this.width = (typeof width === 'undefined') ? 100 : width;
    this.height = (typeof height === 'undefined') ? 100 : height;
    this.right = this.left + this.width - 1;
    this.bottom = this.top + this.height - 1;
    this.background = (typeof background=== 'undefined')
                      ? Color.background : background;
    this.isVisible = true;
    this.eventListeners = {};
    
    //Create a canvas
    this.canvas = document.createElement('canvas');
    //Get a drawing context
    this.ctx = this.canvas.getContext("2d");
    
    this.tool = null; //This will change when component is added to tool
    
    //Size and position the canvas
    this.size();
    this.position();
    
    this.canvas.style.backgroundColor = 'transparent'; //Color.background;
    //For testing purposes
    //this.canvas.style.background = "rgb(25, 25, 25)";
  }

  // an empty default drawing method
  Component.prototype.draw = function () {};

  Component.prototype.debug = function () {
    // draws a border
    this.ctx.strokeStyle = Color.blue;
    U.drawRect(this.ctx, 0, 0, this.width - 1, this.height - 1);

    // draws a crosshair on the anchor
    if ('anchorLeft' in this) {
      this.ctx.strokeStyle = Color.lomidgray;
      var x = this.anchorLeft - this.left;
      var y = this.anchorTop - this.top;
      U.drawLine(this.ctx, x - 5, y, x + 5, y);
      U.drawLine(this.ctx, x, y - 5, x, y + 5);
    }
  };

  Component.prototype.setPosition = function (left, top) {
    this.left = left;
    this.top = top;
    this.right = this.left + this.width - 1;
    this.bottom = this.top + this.height - 1;
    this.position();
  };
  
  Component.prototype.setSize = function (width, height) {
    this.width = width;
    this.height = height;
    this.right = this.left + this.width - 1;
    this.bottom = this.top + this.height - 1;
    this.size();
  };
  
  //A combination of the two previous functions
  Component.prototype.setBounds = function (left, top, width, height) {
    this.left = left;
    this.top = top;
    this.width = width;
    this.height = height;
    this.right = this.left + this.width - 1;
    this.bottom = this.top + this.height - 1;
    this.size();
    this.position();
  };
  
  Component.prototype.size = function () {
    //DO NOT USE: this.canvas.style.width and this.canvas.style.height
    this.canvas.width = parseInt(this.width);
    this.canvas.height = parseInt(this.height);
  };
  
  Component.prototype.position = function () {
    this.canvas.style.position = 'absolute';
    this.canvas.style.left = parseInt(this.left) + 'px';
    this.canvas.style.top = parseInt(this.top) + 'px';
  };
  
  Component.prototype.setzIndex = function (zIndex) {
    this.canvas.style.zIndex = zIndex;
  };

  Component.prototype.clear = function () {
    this.ctx.clearRect(0, 0, this.width, this.height);
  };

  Component.prototype.setVisibility = function(bool) {
    this.isVisible = bool;
    this.canvas.style.visibility = bool ? 'visible' : 'hidden';
  };
  
  Component.prototype.addEventListener = function (type, eventListener) {
    if (!(type in this.eventListeners)) {
      this.eventListeners[type] = eventListener;
    }
  };

  Component.prototype.removeEventListener = function (type) {
    if (type in this.eventListeners) {
      delete this.eventListeners[type];
    }
  };

  Component.prototype.fireEvent = function (event, parameters) {
    if (typeof event === "string") {
      if (this.eventListeners[event] !== undefined) {
        (this.eventListeners[event])(parameters);
      }
    } else {
      throw new Error("Event object missing 'type' property.");
    }
  };
  
  //Slightly modified http://www.javascripter.net/faq/eventpreventdefault.htm
  //The event that gets here is already either an event or window.event
  Component.prototype.cancelDefaultAction = function (event) {
    if (event.preventDefault) { //FF
      event.preventDefault();
    }
    event.returnValue = false; //IE
    return false;
  }

  //This will get the mouse coordinates on the canvas attached to every
  //component. It will be used when the mouse events are captured initially
  //and before the above events are fired.
  Component.prototype.getMousePosition = function (event) {
    var jqElement = $(this.canvas);
    var mouseX = event.pageX -
                 (parseInt(jqElement.offset().left, 10) +
                  parseInt(jqElement.css('paddingLeft'), 10) +
                  parseInt(jqElement.css('borderLeftWidth'), 10));
    var mouseY = event.pageY -
                 (parseInt(jqElement.offset().top, 10) +
                  parseInt(jqElement.css('paddingTop'), 10) +
                  parseInt(jqElement.css('borderTopWidth'), 10));

    //TO DO: figure out why this shift exists and why clicking above the canvas
    //will capture the mouse event!
    mouseX -= 1;
    mouseY -= 1;
    
    return {
      x: mouseX,
      y: mouseY
    };
  };

  return Component;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));

//KEEPING THIS UNTIL I KNOW WHY IT WAS MODIFIED COMPARED TO THE SIMPLER
//VERSION ABOVE
  /*Component.prototype.addEventListener = function (type, eventListener) {
    if (!(type in this.eventListeners)) {
      this.eventListeners[type] = [];
    }

    this.eventListeners[type].push(eventListener);
  };

  Component.prototype.removeEventListener = function (type, eventListener) {
    if (type in this.eventListeners) {
      // go through the list and get rid of them
      var list = this.eventListeners[type];
      for (var i = 0; i < list.length; i ++) {
        if (list[i] === eventListener) {
          list.splice(i, 1);
          i--;
        }
      }
      if (list.length === 0) {
        delete this.eventListeners[type];
      }
    }
  };

  // true or false if any listeners were fired
  Component.prototype.fireEvent = function (event, parameters) {
    if (typeof event === "string") {
      if (event in this.eventListeners) {
        var list = this.eventListeners[event];
        for (var i = 0; i < list.length; i ++) {
          (this.eventListeners[event][i]).call(this, parameters);
        }
        return list.length === 0 ? false : true;
      }
    }

    return false;
  };*/