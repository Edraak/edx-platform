define(function (require) {
  //Imports
  var U = require('utils'),
    Tool = require('tool'),
    Component = require('component'),
    Checkbox = require('checkbox'),
    WebFonts = require('webfonts');

  var tool, cb;

  //Loads webfonts from Google's website then initializes the tool
  //WebFonts.load(initializeTool);
  initializeTool(); 

  function initializeTool() {
    //The try catch block checks if certain features are present.
    //If not, we exit and alert the user.
    try {
      U.testForFeatures(false, false, false, true); //Test for SVG only
    }
    catch (err) {
      window.alert(err.toString() + ' The tool is disabled.');
    }
    initTool();
  }

  function initTool() {
    var svgContainer = document.getElementById('svgContainer');
    tool = new Tool(svgContainer); //Default size of 818x575
    
    //Test checkbox
    cb = new Checkbox(50, 50, 100, 100);
    cb.setPosRot('translate(100, 100) rotate(-45)');
    tool.svg.appendChild(cb.node); //tool.add(cb);
    cb.calculateBBox();
    cb.bindEvents();
    cb.addEventListener('mousedown',
                        function() { alert('Checkbox was clicked.');});
  } 
});