define(function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  
  var SVG_NS = 'http://www.w3.org/2000/svg';
  
  function Checkbox(x, y, width, height) {
    //Call super class
    this.Component(x, y, width, height);
    this.isChecked = false;
    this.text = 'A checkbox';
    
    this.backSquare = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    this.backSquare.setAttribute('x', 0);
    this.backSquare.setAttribute('y', 0);
    this.backSquare.setAttribute('width', 12);
    this.backSquare.setAttribute('height', 12);
    this.backSquare.setAttribute('class', 'daimp-checkbox-back-square');
    this.node.appendChild(this.backSquare);
    
    this.frontSquare = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    this.frontSquare.setAttribute('x', 2);
    this.frontSquare.setAttribute('y', 2);
    this.frontSquare.setAttribute('width', 8);
    this.frontSquare.setAttribute('height', 8);
    this.frontSquare.setAttribute('class', 'daimp-checkbox-front-square');
    if (this.isChecked) {
      this.frontSquare.setAttribute('visibility', 'visible');
    }
    else {
      this.frontSquare.setAttribute('visibility', 'hidden');
    }  
    this.node.appendChild(this.frontSquare);
    
    this.label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    this.label.setAttribute('x', 20);
    this.label.setAttribute('y', 12);
    this.label.setAttribute('class', 'daimp-checkbox-label');
    this.label.textContent = this.text;
    this.node.appendChild(this.label);
  }
  U.copyPrototype(Checkbox, Component);
  
  Checkbox.prototype.bindEvents = function() {
    //Bind mouseDown to the correct context
    //Otherwise 'this' in mouseDown would refer to the source of the event,
    //the canvas
    this.mouseDown = this.mouseDown.bind(this);
    //Register the click that will check/unckeck the checkbox
    this.bBox.addEventListener('mousedown', this.mouseDown, false);
  }
  
  Checkbox.prototype.mouseDown = function (event) {
    this.isChecked = !this.isChecked;
    
    if (this.isChecked) {
      this.frontSquare.setAttribute('visibility', 'visible');
    }
    else {
      this.frontSquare.setAttribute('visibility', 'hidden');
    }
    
    this.fireEvent('mousedown', this);
    this.cancelDefaultAction(event);
  };

  return Checkbox;
});