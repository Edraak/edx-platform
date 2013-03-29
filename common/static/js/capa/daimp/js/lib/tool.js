(function (requirejs, require, define) {
define(function (require) {

  //var $ = require('jquery');
  var U = require('utils');
  var Color = require('color');
  var Component = require('component');

  //////////TOOL//////////
  function Tool(container, width, height, backgroundColor) {
    //Container is the name of the div containing all the components
    this.container = container;
    
    //Default values
    //The max available width when integrated in edX is 818 px
    this.width = (typeof width === 'undefined') ? 818 : width;
    this.height = (typeof height === 'undefined') ? 575 : height;
    this.backgroundColor = (typeof backgroundColor === 'undefined')
                           ? Color.background : backgroundColor;
    
    //Color and give a size to the div 
    this.container.style.position = 'relative';
    this.container.style.marginLeft = 'auto';
    this.container.style.marginRight = 'auto';
    this.container.style.backgroundColor = this.backgroundColor;
    this.container.style.width = parseInt(this.width) + 'px';
    this.container.style.height = parseInt(this.height) + 'px';

    this.components = [];
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
  Tool.prototype.add = function (comp) {
    comp.tool = this;
    this.container.appendChild(comp.canvas);
    this.components.push(comp);
  };
  
  Tool.prototype.remove = function (comp) {
    comp.tool = null;
    this.container.removeChild(comp.canvas);
    for (var i = 0; i < this.components.length; i++) {
      if (this.components[i] === comp) {
        this.components.splice(i, 1);
      }
    }  
  };
  
  Tool.prototype.draw = function () {
    for (var i = 0; i < this.components.length; i++) {
      this.components[i].draw();
    }  
  };
  
  //Do we need to handle events at the tool div level?
  
  return Tool;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));