define(function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  
  var SVG_NS = 'http://www.w3.org/2000/svg';

  function Tool(container, width, height) {
    //Container is the name of the div (or other element)
    //containing the svg element
    this.container = container;
    //Default values
    //The max available width when integrated in edX is 818 px
    this.width = (typeof width === 'undefined') ? 818 : width;
    this.height = (typeof height === 'undefined') ? 575 : height;
    this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    this.svg.setAttribute('version', '1.2');
    this.svg.setAttribute('baseProfile', 'tiny');
    this.svg.setAttribute('width', this.width);
    this.svg.setAttribute('height', this.height);
    this.container.appendChild(this.svg);
    
    this.eventListeners = {};
    //Disable text selection when clicking on div
    this.onselectstart = function () {
      return false;
    };
  }

  Tool.prototype.addEventListener = function (type, eventListener) {
    if (!(type in this.eventListeners)) {
      this.eventListeners[type] = eventListener;
    }  
  };

  Tool.prototype.removeEventListener = function (type) {
    if (type in this.eventListeners) {
      delete this.eventListeners[type];
    }
  };

  Tool.prototype.fireEvent = function (event, parameters) {
    if (typeof event === "string") {
      (this.eventListeners[event])(parameters);
    }  
    else {
      throw new Error("Event object missing 'type' property.");
    }  
  };

  //If we end up having names for components, use a dictionary instead
  //of an array
  /*Tool.prototype.add = function (comp) {
    comp.tool = this;
    this.container.appendChild(comp.canvas);
    this.components.push(comp);
  }
  
  Tool.prototype.remove = function (comp) {
    comp.tool = null;
    this.container.removeChild(comp.canvas);
    for (var i = 0; i < this.components.length; i++) {
      if (this.components[i] === comp) {
        this.components.splice(i, 1);
      }
    }  
  };;*/
  
  return Tool;
});