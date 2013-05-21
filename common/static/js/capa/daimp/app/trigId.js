(function(requirejs, require, define) {
define('app/trigId',['require','webfonts','utils','tool','graph','hslider','checkbox','text','curve','line','diamond','arc'],function (require) {
  //Imports
  var WebFonts = require('webfonts'),
    U = require('utils'),
    Tool = require('tool'),
    Graph = require('graph'),
    HSlider = require('hslider'),
    Checkbox = require('checkbox'),
    Text = require('text'),
    Curve = require('curve'),
    Line = require('line'),
    Diamond = require('diamond'),
    Arc = require('arc');
  //UI
  var tool,
    sumGraph, entryGraph, abGraph,
    ampSlider, phiSlider, aSlider, bSlider, wSlider,
    abCb, ampPhiCb,
    redText, greenText, yellowText, cyanText,
    redCurve, greenCurve, yellowCurve, cyanCurve,
    redLine, yellowLine, cyanLine,
    greenDiamond, redDiamond,
    redArc;
  //x,y bounds of various graphs
  //They are the same for sum graph and entry graph
  var xmin = -4.0, xmax = 4.0, ymin = -3.0, ymax = 3.0;
  var xmin1 = -3.0, xmax1 = 3.0; 
  //States variables
  var amp = 2.0,
    phi = 90.0,
    a = 1.0,
    b = -1.0,
    w = 1.5;
  var x, y;
  var inEdx = false;

  //For the time being, we test if we are running inside edX by testing for
  //JQuery --> Change that later on
  //In that case webfonts are available
  if (U.testForJQuery()) {
    inEdx = true;
    //Load related CSS file dynamically
    U.loadCSS('/static/css/capa/daimp/trig-id.css');
    initializeTool();
  }
  else {
    //Loads webfonts from Google's website then initializes the tool
    WebFonts.load(initializeTool); 
  }
  
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

  //For use in edX
  function  getInputField() { //--> TODO
    var problem = $('#daimp-tool-container').parents('.problem');
    return problem.find('input[type="hidden"][name!="tool_name"][name!="tool_initial_state"]');
  }     
  
  //For use in edX: updates the hidden input field
  function updateState() {
    if (inEdx) {
      var input_field = getInputField();
      var value = {'amp': parseFloat(amp), 'phi': parseFloat(U.radToDeg(phi)),
                   'a': parseFloat(a),'b': parseFloat(b),
                   'w': parseFloat(w)};
      input_field.val(JSON.stringify(value));
    }  
  }

  function initTool() {
    if (inEdx) {
      var initial_state = $('input#tool_initial_state').val();
      var saved_state = getInputField().val();
    
      //Initial state from xml file 
      if (saved_state === '') {
        initial_state = JSON.parse(initial_state);
        amp = initial_state[0];
        phi = initial_state[1];
        a = initial_state[2];
        b = initial_state[3];
        w = initial_state[4];
        //Add checkboxes state?
      }
      //Saved state
      else {
        saved_state = JSON.parse(saved_state);
        amp = saved_state.amp;
        phi = saved_state.phi;
        a = saved_state.a;
        b = saved_state.b;
        w = saved_state.w;
        //Add checkboxes state?
      }
    }

    var toolContainer = document.getElementById('daimp-tool-container');
    tool = new Tool(toolContainer); //Default size of 818x575
    
    //Sum graph
    sumGraph = new Graph(40, 40, 280, 210);
    sumGraph.setPlottingBounds(xmin, xmax, ymin, ymax);
    sumGraph.setXLongTicks(1.0);
    sumGraph.setAutomaticXLabels(1.0, 0, false); 
    sumGraph.setXAxis(0.0);
    sumGraph.setXText('t');
    sumGraph.setYLongTicks(1.0);
    sumGraph.setAutomaticYLabels(1.0, 0, false); 
    sumGraph.setYAxis(0.0);
    sumGraph.setYText('x');
    tool.add(sumGraph);
    sumGraph.calculateBBox();
    sumGraph.resizeBBox();
    sumGraph.bindEvents();
    
    //Entry graph
    entryGraph = new Graph(40, 317, 280, 210);
    entryGraph.setPlottingBounds(xmin, xmax, ymin, ymax);
    entryGraph.setXLongTicks(1.0);
    entryGraph.setAutomaticXLabels(1.0, 0, false); 
    entryGraph.setXAxis(0.0);
    entryGraph.setXText('t');
    entryGraph.setYLongTicks(1.0);
    entryGraph.setAutomaticYLabels(1.0, 0, false); 
    entryGraph.setYAxis(0.0);
    entryGraph.setYText('x');
    tool.add(entryGraph);
    entryGraph.calculateBBox();
    entryGraph.resizeBBox();
    entryGraph.bindEvents();
    
    //ab graph
    abGraph = new Graph(620, 205, 150, 150);
    abGraph.setPlottingBounds(xmin1, xmax1, ymin, ymax);
    abGraph.setXLongTicks(1.0);
    abGraph.setAutomaticXLabels(1.0, 0, false); 
    abGraph.setXAxis(0.0);
    abGraph.setXText('a');
    abGraph.setYLongTicks(1.0);
    abGraph.setAutomaticYLabels(1.0, 0, false); 
    abGraph.setYAxis(0.0);
    abGraph.setYText('b');
    tool.add(abGraph);
    abGraph.calculateBBox();
    abGraph.resizeBBox();
    abGraph.bindEvents();
    
    //amp slider
    ampSlider = new HSlider(sumGraph.x + sumGraph.width + 80, sumGraph.y + 101, 120, 50);
    ampSlider.setPlottingBounds(0.0, 3.0);
    ampSlider.setText('A', 'amp-slider-text');
    ampSlider.setShortTicks(0.5);
    ampSlider.setLongTicks(1.0);
    ampSlider.setValue(amp, 2, 'amp-slider-value-text');
    ampSlider.setAutomaticLabels(1.0, 0, false);
    tool.add(ampSlider);
    ampSlider.calculateBBox();
    ampSlider.resizeBBox();
    ampSlider.bindEvents();
    ampSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(ampSlider);});
    ampSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(ampSlider);});
    ampSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(ampSlider);});                         
    
    //phi slider
    phiSlider = new HSlider(ampSlider.x, ampSlider.y + 50, 120, 50);
    phiSlider.setPlottingBounds(-180.0, 180.0);
    phiSlider.setText(U.STR.phisymbol, 'phi-slider-text');
    phiSlider.setShortTicks(45.0);
    phiSlider.setLongTicks(90.0);
    phiSlider.setValue(phi, 0, 'phi-slider-value-text', true);
    phiSlider.setLabels([
                         {x: -180.0, str: '-' + U.STR.pi},
                         {x: 0.0, str: '0'},
                         {x: 180.0, str: U.STR.pi}
                        ]);
    tool.add(phiSlider);
    phiSlider.calculateBBox();
    phiSlider.resizeBBox();
    phiSlider.bindEvents();
    phiSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(phiSlider);});
    phiSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(phiSlider);});
    phiSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(phiSlider);});       
    
    //a slider
    aSlider = new HSlider(entryGraph.x + entryGraph.width + 80, entryGraph.y + 101, 120, 50);
    aSlider.setPlottingBounds(-2.0, 2.0);
    aSlider.setText('a', 'a-slider-text');
    aSlider.setShortTicks(0.5);
    aSlider.setLongTicks(1.0);
    aSlider.setValue(a, 2, 'a-slider-value-text');
    aSlider.setAutomaticLabels(1.0, 0, false);
    tool.add(aSlider);
    aSlider.calculateBBox();
    aSlider.resizeBBox();
    aSlider.bindEvents();
    aSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(aSlider);});
    aSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(aSlider);});
    aSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(aSlider);});
    
    //b slider
    bSlider = new HSlider(aSlider.x, aSlider.y + 50, 120, 50);
    bSlider.setPlottingBounds(-2.0, 2.0);
    bSlider.setText('b', 'b-slider-text');
    bSlider.setShortTicks(0.5);
    bSlider.setLongTicks(1.0);
    bSlider.setValue(b, 2, 'b-slider-value-text');
    bSlider.setAutomaticLabels(1.0, 0, false);
    tool.add(bSlider);
    bSlider.calculateBBox();
    bSlider.resizeBBox();
    bSlider.bindEvents();
    bSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(bSlider);});
    bSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(bSlider);});
    bSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(bSlider);});

    
    //w slider
    wSlider = new HSlider(abGraph.x, entryGraph.y + entryGraph.height, 75, 50);
    wSlider.setPlottingBounds(0.0, 3.0);
    wSlider.setText(U.STR.omega); //Default style
    wSlider.setShortTicks(0.5);
    wSlider.setLongTicks(1.0);
    wSlider.setValue(w, 2); //Default style
    wSlider.setAutomaticLabels(1.0, 0, false);
    tool.add(wSlider);
    wSlider.calculateBBox();
    wSlider.resizeBBox();
    wSlider.bindEvents();
    wSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(wSlider);});
    wSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(wSlider);});
    wSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(wSlider);});
    
    //Checkboxes
    abCb = new Checkbox(abGraph.x + 75, abGraph.y + abGraph.height + 59, 50, 50);
    abCb.setFrontSquareClass('ab-checkbox-front-square');
    abCb.addText('a,', 'ab-checkbox-label-first');
    abCb.addText('b', 'ab-checkbox-label-last');
    tool.add(abCb);
    abCb.calculateBBox();
    abCb.bindEvents();
    abCb.addEventListener('mousedown',  function() {
                          checkboxMouseDown(abCb);});

    ampPhiCb = new Checkbox(abCb.x, abCb.y + 25, 50, 50);
    ampPhiCb.setFrontSquareClass('amp-phi-checkbox-front-square');
    ampPhiCb.addText('A,' + U.STR.phisymbol, 'amp-phi-checkbox-label');
    tool.add(ampPhiCb);
    ampPhiCb.calculateBBox();
    ampPhiCb.bindEvents();
    ampPhiCb.addEventListener('mousedown',  function() {
                              checkboxMouseDown(ampPhiCb);});

    //Text to the right of top graph
    redText = new Text(sumGraph.x + sumGraph.width + 80, sumGraph.y + 15);
    redText.addText('A cos(' + U.STR.omega + 't - ' + U.STR.phisymbol + ')', 
                    'text-red');
    tool.add(redText);

    greenText = new Text(redText.x, redText.y + 25);
    greenText.addText('a cos(' + U.STR.omega + 't) + ' + 
                      'b sin(' + U.STR.omega + 't)', 
                     'text-green');
    tool.add(greenText);

    //Text to the right of bottom graph
    yellowText = new Text(entryGraph.x + entryGraph.width + 80, entryGraph.y + 15);
    yellowText.addText('a cos(' + U.STR.omega + 't)', 
                       'text-yellow');
    tool.add(yellowText);

    cyanText = new Text(yellowText.x, yellowText.y + 25);
    cyanText.addText('b sin(' + U.STR.omega + 't)', 
                     'text-cyan');
    tool.add(cyanText);
    
    //Convert phi to radians
    phi = U.degToRad(phi);

    //Add the two curves to sum graph
    redCurve = new Curve(sumGraph, fAmpPhi, xmin, xmax, 'curve-red');
    greenCurve = new Curve(sumGraph, fSum, xmin, xmax, 'curve-green');
    //Add the two curves to entry graph
    yellowCurve = new Curve(entryGraph, fEntryCos, xmin, xmax, 'curve-yellow');
    cyanCurve = new Curve(entryGraph, fEntrySin, xmin, xmax, 'curve-cyan');
    //Add three lines and two diamonds to ab graph
    yellowLine = new Line (abGraph, 0.0, 0.0, 0.0, 0.0, 'curve-yellow');
    cyanLine = new Line (abGraph, 0.0, 0.0, 0.0, 0.0, 'curve-cyan');
    greenDiamond = new Diamond(abGraph, 0.0, 0.0, 4, 'diamond-green');
    //Red elements drawn on top of the others
    redLine = new Line (abGraph, 0.0, 0.0, 0.0, 0.0, 'curve-red');
    redDiamond = new Diamond(abGraph, 0.0, 0.0, 4, 'diamond-red');
    //Add arc to ab graph
    redArc = new Arc(abGraph, 0.0, 0.0, 0, 0.0, 0.0, false, false, 'curve-red'); 
    //Now set them
    drawabGraph();
      
    updateState();
  }
  
  function checkboxMouseDown(checkbox) {
    drawabGraph();
  }
  
  function sliderMouseDown(slider) {
    if (slider === ampSlider) {
      amp = ampSlider.value;
    }
    else if (slider === phiSlider) {
      phi = U.degToRad(phiSlider.value);
    }
    else if (slider === aSlider) {
      a = aSlider.value;
      drawEntryGraph();
    }
    else if (slider === bSlider) {
      b = bSlider.value;
      drawEntryGraph();
    }
    else { //wSlider
      w = wSlider.value;
    }
    drawSumGraph();
    drawabGraph();
    updateState();  
  }
   
  function sliderMouseDrag(slider) {
    sliderMouseDown(slider);
  } 
   
  function sliderMouseUp(slider) {
     sliderMouseDown(slider);
  }
  
  function fAmpPhi(t) {
    return amp*Math.cos(w*t-phi);
  }
  
  function fSum(t) {
    return a*Math.cos(w*t) + b*Math.sin(w*t);
  }
  
  function fEntryCos(t) {
    return a*Math.cos(w*t);
  }
  
  function fEntrySin(t) {
    return b*Math.sin(w*t);
  }    
  
  function drawSumGraph() {
    redCurve.setPoints(fAmpPhi, xmin, xmax);
    greenCurve.setPoints(fSum, xmin, xmax);
  }  
  
  function drawEntryGraph() {  
    yellowCurve.setPoints(fEntryCos, xmin, xmax);
    cyanCurve.setPoints(fEntrySin, xmin, xmax);
  }
  
  function drawabGraph() {  
    var x, y, arcRadius, arcAngle;
   
    if (abCb.isChecked) {
      yellowLine.setXY(0.0, 0.0, a, 0.0);
      cyanLine.setXY(a, 0.0, a, b);
      greenDiamond.setXY(a, b);
      yellowLine.setVisibility(true);
      cyanLine.setVisibility(true);
      greenDiamond.setVisibility(true);
    }
    else {
      yellowLine.setVisibility(false);
      cyanLine.setVisibility(false);
      greenDiamond.setVisibility(false);
    }
    if (ampPhiCb.isChecked) {
      x = amp*Math.cos(phi);
      y = amp*Math.sin(phi);
      arcRadius = abGraph.getxPix(amp/2.0) - abGraph.getxPix(0.0);
      redLine.setXY(0.0, 0.0, x, y);
      redDiamond.setXY(x, y);
      if (phi >= 0.0) {
        arcAngle = phi;
        redArc.setAngles(0.0, arcAngle, false); //Counter-clockwise
      }
      else {
        arcAngle = 2.0*Math.PI + phi; 
        redArc.setAngles(0.0, arcAngle, true); //Clockwise
      }
      
      redArc.setRadius(arcRadius);
      redLine.setVisibility(true);
      redDiamond.setVisibility(true);
      redArc.setVisibility(true);
    }
    else {
      redLine.setVisibility(false);
      redDiamond.setVisibility(false);
      redArc.setVisibility(false);
    }                
  }
});}(RequireJS.requirejs, RequireJS.require, RequireJS.define));