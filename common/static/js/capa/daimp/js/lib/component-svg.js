define(function (require) {

  //Imports
  var U = require('utils');
  
  var SVG_NS = 'http://www.w3.org/2000/svg';
  
  function Component(x, y, width, height) {
    //Default values
    //Position component at (0,0) with width and height equal to 100
    this.x = (typeof x === 'undefined') ? 0 : x;
    this.y = (typeof y === 'undefined') ? 0 : y;
    this.width = (typeof width === 'undefined') ? 100 : width;
    this.height = (typeof height === 'undefined') ? 100 : height;
    
    this.node = document.createElementNS('http://www.w3.org/2000/svg', 'g'); 
    this.node.setAttribute('class', 'daimp-component');
    this.node.setAttribute('pointer-events', 'all');
    this.setPosition(x, y);
    this.eventListeners = {};
  }

  Component.prototype.setPosition = function (x, y) {
    this.x = x;
    this.y = y;
    this.node.setAttribute('transform',
                           'translate(' +
                           parseInt(this.x) + ',' +
                           parseInt(this.y) + ')');
  };
  
  //Change this later on
  Component.prototype.setPosRot = function (trans) {
    this.node.setAttribute('transform', trans);
  };
  
  Component.prototype.setSize = function (width, height) {
    this.width = width;
    this.height = height;
  };
  
  //A combination of the two previous functions
  Component.prototype.setBounds = function (x, y, width, height) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
    this.setSize();
    this.setPosition();
  };
  
  Component.prototype.calculateBBox = function () {
    var bb = this.node.getBBox();
    this.bBox = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    this.bBox.setAttribute('class', 'daimp-bBox');
    this.bBox.setAttribute('x', bb.x);
    this.bBox.setAttribute('y', bb.y);
    this.bBox.setAttribute('width', bb.width);
    this.bBox.setAttribute('height', bb.height);
    this.node.appendChild(this.bBox);
  }
  
  Component.prototype.toBack = function () {
  };
  
  Component.prototype.toFront = function () {
  };

  Component.prototype.setVisibility = function(bool) {
    this.isVisible = bool;
    
    if (this.isVisible) {
      this.node.setAttribute('visibility', 'visible');
    }
    else {
      this.node.setAttribute('visibility', 'hidden');
    }  
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

  //This will get the mouse coordinates on the bounding box attached to every
  //component. It will be used when the mouse events are captured initially
  //and before the above events are fired.
  Component.prototype.getMousePosition = function (event) {
    var event = event || window.event;
    
    var paddingLeft = window.getComputedStyle(this.bBox, null).getPropertyValue('padding-left');
    
    var borderLeftWidth =  window.getComputedStyle(this.bBox, null).getPropertyValue('border-left-width');
    
    var paddingTop = window.getComputedStyle(this.bBox, null).getPropertyValue('padding-top');
    
    var borderTopWidth =  window.getComputedStyle(this.bBox, null).getPropertyValue('border-top-width');
    
    
    var m = this.bBox.getScreenCTM();
    var p = tool.createSVGPoint();
    p.x = event.pageX; //clientX?
    p.y = event.pageY; //clientY?
    p = p.matrixTransform(m.inverse());
    
    return {
      x: p.x,
      y: p.y
    };
  };

  return Component;
});