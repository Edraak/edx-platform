(function(requirejs, require, define) {
define('app/graphFeatures',['require','webfonts','utils','tool','graph','radiobutton','radiobuttongroup','hslider','text','curve','line','diamond'],function (require) {
  //Imports
  var WebFonts = require('webfonts'),
    U = require('utils'),
    Tool = require('tool'),
    Graph = require('graph'),
    RadioButton = require('radiobutton'),
    RadioButtonGroup = require('radiobuttongroup'),
    HSlider = require('hslider'),
    Text = require('text'),
    Curve = require('curve'),
    Line = require('line'),
    Diamond = require('diamond');
  //UI
  var tool,
    graph,
    aSlider, bSlider, cSlider, dSlider, xSlider,
    risingRb, fallingRb, concaveRb, convexRb, rbg,
    fText, posText, xReadoutText, yReadoutText;

  //State variables are a, b, c, d, x
  var xReadout, yReadout;
  //x,y bounds of graph
  var xmin = -6.0, xmax = 6.0, ymin = -6.0, ymax = 6.0;
  //Coefficients of our function
  var a = 1.0, b = -2.0, c = 0.5, d = 1.0;
  //Position of x slider
  var x = -0.5, y = f(x);
  //Roots of first and second derivatives
  var dfr1, dfr2, df2r;
  //The different zones of the graph each having its own color.
  //They are set in calculateZones
  var zone1Curve,
    zone2Curve,
    zone3Curve,
    zone4Curve,
    dfr1Diamond,
    dfr2Diamond,
    df2rDiamond,
    posLine,
    posDiamond,
    zone1 = 'curve-litegray',
    zone2 = 'curve-litegray',
    zone3 = 'curve-litegray',
    zone4 = 'curve-litegray',
    dfr1Class = 'diamond-purple',
    dfr2Class = 'diamond-purple',
    df2rClass = 'diamond-cyan';

  //Mouse x and y readouts
  var xposStr = '', yposStr = '';
  var inEdx = false; 

  //For the time being, we test if we are running inside edX by testing for
  //JQuery --> Change that later on
  //In that case webfonts are available
  if (U.testForJQuery()) {
    inEdx = true;
    //Load related CSS file dynamically
    U.loadCSS('/static/css/capa/daimp/graph-features.css');
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
  function  getInputField() {
    var problem = $('#daimp-tool-container').parents('.problem');
    return problem.find('input[type="hidden"][name!="tool_name"][name!="tool_initial_state"]');
  }     
  
  //For use in edX: updates the hidden input field
  function updateState() {
    if (inEdx) {
      var input_field = getInputField();
      var value = {'a': parseFloat(a), 'b': parseFloat(b),
                   'c': parseFloat(c),'d': parseFloat(d),
                   'x': parseFloat(x)};
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
        a = initial_state[0];
        b = initial_state[1];
        c = initial_state[2];
        d = initial_state[3];
        x = initial_state[4];
        //Add checkboxes state?
      }
      //Saved state
      else {
        saved_state = JSON.parse(saved_state);
        a = saved_state.a;
        b = saved_state.b;
        c = saved_state.c;
        d = saved_state.d;
        x = saved_state.x;
        //Add checkboxes state?
      }
    }

    var toolContainer = document.getElementById('daimp-tool-container');
    tool = new Tool(toolContainer); //Default size of 818x575
    
    //Graph
    graph = new Graph(90, 90, 360, 360);
    graph.setPlottingBounds(xmin, xmax, ymin, ymax);
    graph.setXShortTicks(1.0);
    graph.setXLongTicks(2.0);
    //No labels for x-axis, they are drawn by the x slider
    //graph.setAutomaticXLabels(2.0, 1, false); 
    graph.setXAxis(0.0);
    graph.setXText('x');
    graph.setXShortTicks(1.0);
    graph.setYLongTicks(2.0);
    graph.setAutomaticYLabels(2.0, 0, false); 
    graph.setYAxis(0.0);
    graph.setYText('y');
    tool.add(graph);
    
    //Drag related
    graph.addEventListener('mousedown', function(mpos) {
                          graphHideReadouts(mpos);});
    graph.addEventListener('mousedrag', function(mpos) {
                          graphHideReadouts(mpos);});
    graph.addEventListener('mouseup', function(mpos) {
                          graphShowReadouts(mpos);});  
    //Crosshair related                      
    graph.addEventListener('mouseover', function(mpos) {
                          graphShowReadouts(mpos);});                                           
    graph.addEventListener('mousemove', function(mpos) {
                          graphShowReadouts(mpos);}); 
    graph.addEventListener('mouseout', function() {
                          graphHideReadouts();});                                            
    
    tool.add(graph);
    
    //Sliders
    //a slider
    aSlider = new HSlider(graph.x + graph.width + 80,
                          graph.y + 20, 200, 50);
    aSlider.setPlottingBounds(-2.0, 2.0);
    aSlider.setText('a');
    aSlider.setShortTicks(0.5);
    aSlider.setLongTicks(1.0);
    aSlider.setValue(a, 2);
    aSlider.setAutomaticLabels(1.0, 1, false);
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
    bSlider = new HSlider(aSlider.x, aSlider.y + 50, 200, 50);
    bSlider.setPlottingBounds(-2.0, 2.0);
    bSlider.setText('b');
    bSlider.setShortTicks(0.5);
    bSlider.setLongTicks(1.0);
    bSlider.setValue(b, 2);
    bSlider.setAutomaticLabels(1.0, 1, false);
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
    
    //c slider
    cSlider = new HSlider(bSlider.x, bSlider.y + 50, 200, 50);
    cSlider.setPlottingBounds(-2.0, 2.0);
    cSlider.setText('c');
    cSlider.setShortTicks(0.5);
    cSlider.setLongTicks(1.0);
    cSlider.setValue(c, 2);
    cSlider.setAutomaticLabels(1.0, 1, false);
    tool.add(cSlider);
    cSlider.calculateBBox();
    cSlider.resizeBBox();
    cSlider.bindEvents();
    cSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(cSlider);});
    cSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(cSlider);});
    cSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(cSlider);});
    
    //d slider --> Color.litegray;
    dSlider = new HSlider(cSlider.x, cSlider.y + 50, 200, 50);
    dSlider.setPlottingBounds(-2.0, 2.0);
    dSlider.setText('d');
    dSlider.setShortTicks(0.5);
    dSlider.setLongTicks(1.0);
    dSlider.setValue(d, 2);
    dSlider.setAutomaticLabels(1.0, 1, false);
    tool.add(dSlider);
    dSlider.calculateBBox();
    dSlider.resizeBBox();
    dSlider.bindEvents();
    dSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(dSlider);});
    dSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(dSlider);});
    dSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(dSlider);});
    
    //x slider under the graph --> Color.litegray;
    xSlider = new HSlider(graph.x, graph.y + graph.height + 27,
                          graph.width, 50);
    xSlider.setPlottingBounds(-6.0, 6.0);
    xSlider.setShortTicks(1.0);
    xSlider.setLongTicks(2.0);
    xSlider.setValue(x, 2);
    xSlider.setAutomaticLabels(2.0, 1, false);
    tool.add(xSlider);
    xSlider.calculateBBox();
    xSlider.resizeBBox();
    xSlider.bindEvents();
    xSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(xSlider);});
    xSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(xSlider);});
    xSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(xSlider);});
    
    //Radio buttons 
    risingRb = new RadioButton(aSlider.x + 6, dSlider.y + 50, 50, 50);
    risingRb.setFrontCircleClass('rising-radiobutton-front-circle');
    risingRb.addText('Rising', 'rising-radiobutton-label');
    risingRb.setChecked(true);
    tool.add(risingRb);
    risingRb.calculateBBox();
    risingRb.bindEvents();
    risingRb.addEventListener('mousedown',  function() {
                              radioButtonMouseDown(risingRb);});

    fallingRb = new RadioButton(risingRb.x, risingRb.y + 25, 50, 50);
    fallingRb.setFrontCircleClass('falling-radiobutton-front-circle');
    fallingRb.addText('Falling', 'falling-radiobutton-label');
    tool.add(fallingRb);
    fallingRb.calculateBBox();
    fallingRb.bindEvents();
    fallingRb.addEventListener('mousedown',  function() {
                              radioButtonMouseDown(fallingRb);});

    concaveRb = new RadioButton(fallingRb.x, fallingRb.y + 25, 50, 50);
    concaveRb.setFrontCircleClass('concave-radiobutton-front-circle');
    concaveRb.addText('Concave', 'concave-radiobutton-label');
    tool.add(concaveRb);
    concaveRb.calculateBBox();
    concaveRb.bindEvents();
    concaveRb.addEventListener('mousedown',  function() {
                              radioButtonMouseDown(concaveRb);});

    convexRb = new RadioButton(concaveRb.x, concaveRb.y + 25, 50, 50);
    convexRb.setFrontCircleClass('convex-radiobutton-front-circle');
    convexRb.addText('Convex', 'convex-radiobutton-label');
    tool.add(convexRb);
    convexRb.calculateBBox();
    convexRb.bindEvents();
    convexRb.addEventListener('mousedown',  function() {
                              radioButtonMouseDown(convexRb);});
    //Radio button group
    rbg = new RadioButtonGroup(risingRb, fallingRb, concaveRb, convexRb);
    
    //Text for f(x) = ax^3 + bx^2 + cx + d
    fText = new Text(aSlider.x, convexRb.y + 40);
    fText.addText('', 'normal-text'); //f(x) = ax
    fText.addSuperScript('3', 'small-text'); //^3
    fText.addText('', 'normal-text'); //+ bx
    fText.addSuperScript('2', 'small-text'); //^2
    fText.addText('', 'normal-text'); //+ cx + d
    setFunctionString();
    tool.add(fText);

    //Text for position of x, f(x)
    posText = new Text(fText.x, fText.y + 25);
    posText.addText(calculatePosString(),'normal-text');
    tool.add(posText);

    //Text for mouse readout
    xReadoutText = new Text(posText.x, posText.y + 60);
    xReadoutText.addText('x = ', 'normal-text');
    tool.add(xReadoutText);
    yReadoutText = new Text(xReadoutText.x, xReadoutText.y + 25);
    yReadoutText.addText('y = ', 'normal-text');
    tool.add(yReadoutText);

    //Add four curves to graph, initially all the same
    zone1Curve = new Curve(graph, f, xmin, xmin, zone1);
    zone2Curve = new Curve(graph, f, xmin, xmin, zone2);
    zone3Curve = new Curve(graph, f, xmin, xmin, zone3);
    zone4Curve = new Curve(graph, f, xmin, xmin, zone4);

    //Add three points to the graph, representing the roots of the the first
    //derivative (dfr1, dfr2) and second derivative (df2r). Initially, they are
    //all the same.
    dfr1Diamond = new Diamond(graph, 0.0, 0.0, 4, dfr1Class);
    dfr2Diamond = new Diamond(graph, 0.0, 0.0, 4, dfr2Class);
    df2rDiamond = new Diamond(graph, 0.0, 0.0, 4, df2rClass);

    //Add the position tracking line and point that follow the x slider
    y = f(x); //Recalculate as x can come from edX xml file
    posLine = new Line (graph, x, ymin, x, y, 'line-darkgray');
    posDiamond = new Diamond(graph, x, y, 4, 'diamond-white');

    graph.setCrosshairs(true, true);
    graph.calculateBBox();
    graph.resizeBBox();
    graph.bindEvents();
    
    //Now set the curves and diamonds
    drawGraph();

    updateState();
  }
  
  //Function is ax^3 + bx^2 + cx + d
  function f(x) {
    return a*x*x*x + b*x*x + c*x + d;
  }
  
  //Derivative is 3ax^2 + 2bx + c
  function df(x) {
    return 3.0*a*x*x + 2.0*b*x + c;
  }
        
  //Derivative is zero for the following points
  //Delta = b*b-3ac
  //r1,2 = (-b +- sqrt(b^2-3ac)) / 3a
  function dfRoots() {
    var delta = b*b - 3.0*a*c;
    var tmp1, tmp2;

    if (a !== 0.0) {
      if (delta >= 0.0) {	
        tmp1 = (-b - Math.sqrt(delta)) / (3.0*a);
        tmp2 = (-b + Math.sqrt(delta)) / (3.0*a);
	
        dfr1 = Math.min(tmp1, tmp2);
        dfr2 = Math.max(tmp1, tmp2);
        return true;
      }
      else {
        return false;
      }	
    }
    //a = 0: function becomes bx^2 + cx + d, derivative 2bx + c, root at -c/2bx
    else if (b !== 0.0) {
      dfr1 = -c/(2.0*b);
      dfr2 = dfr1;
      return true;
    }
    else {
      return false;
    }
  }  
        
  //Second derivative is 6ax + 2b
  function d2f(x) {
    return 6.0*a*x + 2.0*b;
  }

  //Second derivative is zero for x = -b/3a
  function df2Root() {
    if (a !== 0.0) {
      df2r = -b / (3.0*a);
      return true;
    }
    else {	
      return false;
    }	
  }
  
  function calculateZones() {
    //Default value which is the color of the curve
    zone1 = 'curve-litegray';
    zone2 = 'curve-litegray';
    zone3 = 'curve-litegray';
    zone4 = 'curve-litegray';

    //Function is increasing outside of [dfr1, dfr2]
    if (a > 0.0) {
      if (risingRb.isChecked) {	
        zone1 = 'curve-yellow';
        zone4 = 'curve-yellow';
      }
      else if (fallingRb.isChecked) {	
        zone2 = 'curve-green';
        zone3 = 'curve-green';
      }
      else if (concaveRb.isChecked) {
        zone1 = 'curve-orange';
        zone2 = 'curve-orange';
      }
      else if (convexRb.isChecked) {
        zone3 = 'curve-red';
        zone4 = 'curve-red';
      }
    }
    //Function is increasing inside of [dfr1, dfr2]
    else if (a < 0.0) {
      if (fallingRb.isChecked) {
        zone1 = 'curve-green';
        zone4 = 'curve-green';
      }
      else if (risingRb.isChecked) {	
        zone2 = 'curve-yellow';
        zone3 = 'curve-yellow';
      }
      else if (concaveRb.isChecked) {
        zone3 = 'curve-orange';
        zone4 = 'curve-orange';
      }
      else if (convexRb.isChecked) {
        zone1 = 'curve-red';
        zone2 = 'curve-red';
      }
    }
    //a = 0: function becomes bx^2 + cx + d, derivative 2bx + c, root at -c/2bx
    else {
      if (b > 0.0) {
        if (risingRb.isChecked) {	
          zone3 = 'curve-yellow';
          zone4 = 'curve-yellow';
        }
        else if (fallingRb.isChecked) {	
          zone1 = 'curve-green';
          zone2 = 'curve-green';
        }
        else if (concaveRb.isChecked) {
        }
        //Always convex
        else if (convexRb.isChecked) {
          zone1 = 'curve-red';
          zone2 = 'curve-red';
          zone3 = 'curve-red';
          zone4 = 'curve-red';
        }
      }
      else if (b < 0.0) {
        if (risingRb.isChecked) {	
          zone1 = 'curve-yellow';
          zone2 = 'curve-yellow';
        }
        else if (fallingRb.isChecked) {	
          zone3 = 'curve-green';
          zone4 = 'curve-green';
        }
         //Always concave
        else if (concaveRb.isChecked) {
          zone1 = 'curve-orange';
          zone2 = 'curve-orange';
          zone3 = 'curve-orange';
          zone4 = 'curve-orange';
        }
        else if (convexRb.isChecked) {
        }
      }
      //a = 0, b = 0: function becomes cx + d, derivative c, no root, rising
      //everywhere if c > 0, falling everywhere if c < 0, monotonous if c = 0
      else {
        if (risingRb.isChecked) {	
          if (c > 0.0) {	
            zone1 = 'curve-yellow';
            zone2 = 'curve-yellow';
            zone3 = 'curve-yellow';
            zone4 = 'curve-yellow';
          }	
        }
        else if (fallingRb.isChecked) {	
          if (c < 0.0) {	
            zone1 = 'curve-green';
            zone2 = 'curve-green';
            zone3 = 'curve-green';
            zone4 = 'curve-green';
          }	
        }
        else if (concaveRb.isChecked) {
        }
        else if (convexRb.isChecked) {
        }
      }
    }
    zone1Curve.setClass(zone1);
    zone2Curve.setClass(zone2);
    zone3Curve.setClass(zone3);
    zone4Curve.setClass(zone4);
  }
  
  //f(x) = ax^3 + bx^2 + cx + d
  function setFunctionString() {
    var aStr = '', bStr = '', cStr = '', dStr = '', 
    str1 = 'f(x) = ', //String that goes in front of ^3
    str2 = '',        //String that goes in front of ^2
    str3 = '',        //String that goes in front of ^1
    str4 = '';        //String that goes in front of ^0

    //Get the string representation of the 4 coefficients a, b, c, d
    if (a !== 0.0) {
      aStr = (Math.abs(a)).toFixed(2);
    }    
    if (b !== 0.0) {
      bStr = (Math.abs(b)).toFixed(2);
    }      
    if (c !== 0.0) {
      cStr = (Math.abs(c)).toFixed(2);
    }  
    if (d !== 0.0) {
      dStr = (Math.abs(d)).toFixed(2);
    }  
    
    //Coefficient
    if (a > 0.0) {
      str1 += aStr + ' x';
    } 
    else if (a < 0.0) {
      str1 += '-' + aStr + ' x';
    }
    //Exponent
    if (a !== 0.0) {
      fText.setText(1, ' 3');
    }
    else {
      fText.setText(1, '');
    }
                        
    //Coefficient
    if (b > 0.0) {
       //Nothing in front
      if (a === 0.0) {
       str2 += bStr + ' x';
      } 
      else {
        str2 += ' + ' + bStr + ' x';
      }
    }
    else if (b < 0.0) {
      //Nothing in front
      if (a === 0.0) {
        str2 += '-' + bStr + ' x';
      }  
      else {
        str2 += ' - ' + bStr + ' x';
      }  
    }
    //Exponent
    if (b !== 0.0) {
      fText.setText(3, ' 2');
    }
    else {
      fText.setText(3, '');
    }

    //Coefficients
    if (c > 0.0) {
       //Nothing in front
      if (a === 0.0 && b === 0.0) {
        str3 += cStr + ' x';
      }  
      else {
        str3 += ' + ' + cStr + ' x';
      }  
    }
    else if (c < 0.0) {
        //Nothing in front
        if (a === 0.0 && b === 0.0) {
          str3 += '-' + cStr + 'x';
        }  
        else {
          str3 += ' - ' + cStr + 'x';
        }  
    }
    
    if (d > 0.0) {
      //Nothing in front
      if (a === 0.0 && b === 0.0 && c === 0.0) {
        str4 += dStr;
      }  
      else {
        str4 += ' + ' + dStr;
      }  
    }
    else if (d < 0.0) {
      //Nothing in front
      if (a === 0.0 && b === 0.0 && c === 0.0) {
        str4 += '-' + dStr;
      }  
      else {
        str4 += ' - ' + dStr;
      }  
    }
    
    if (a === 0.0 && b === 0.0 && c === 0.0 && d === 0.0) {
      str1 += '0';
    }  
    
    fText.setText(0, str1);
    fText.setText(2, str2);
    fText.setText(4, str3 + str4);
  }

  function calculatePosString() {
    return 'f(' + x.toFixed(2) + ') = ' + y.toFixed(2);
  }
  
  function radioButtonMouseDown(radioButton) {
    drawGraph();
  }
  
  function sliderMouseDown(slider) {
    if (slider == xSlider) {
      drawPos();
    }
    else {
      if (slider === aSlider) {
        a = aSlider.value;
      }
      else if (slider === bSlider) {
        b = bSlider.value;
      }
      else if (slider === cSlider) {
        c = cSlider.value;
      }
      else if (slider === dSlider) {
        d = dSlider.value;
      }
      drawGraph();
      drawPos();
      setFunctionString();
      updateState();
    }  
  }
   
  function sliderMouseDrag(slider) {
    sliderMouseDown(slider);
  } 
   
  function sliderMouseUp(slider) {
     sliderMouseDown(slider);
  }   
  
  function graphHideReadouts(mpos) {
    xReadoutText.setText(0, 'x =');
    yReadoutText.setText(0, 'y =');
  }
  
  function graphShowReadouts(mpos) {
    xReadoutText.setText(0, 'x = ' + (mpos.x).toFixed(2));
    yReadoutText.setText(0, 'y = ' + (mpos.y).toFixed(2));
  }

  function drawPos() {
    x = xSlider.value;
    y = f(x);
    posLine.setXY(x, ymin, x, y);
    posDiamond.setXY(x, y);
    //Update the readout
    posText.setText(0, calculatePosString());
  }
  
  function drawGraph() {
    var dfRootsExist = dfRoots();
    var df2RootExist = df2Root();
            
    //No value for dfr1 and dfr2. Give them the value of df2r, if it exists
    if (!dfRootsExist) {
      if (df2RootExist) {
        dfr1 = df2r;
        dfr2 = df2r;
      }
      else {
        dfr1 = 0.0;
        dfr2 = 0.0;
      }
    }
            
    if (!df2RootExist) {
      if (dfRootsExist) {
        df2r = dfr1;
      }  
      else {
        df2r = 0.0;
      }
    }  
    
    //Set the curve segments
    calculateZones();
    zone1Curve.setPoints(f, xmin, dfr1);
    zone2Curve.setPoints(f, dfr1, df2r);
    zone3Curve.setPoints(f, df2r, dfr2);
    zone4Curve.setPoints(f, dfr2, xmax);
            
    if (dfRootsExist) {
      dfr1Diamond.setXY(dfr1, f(dfr1));
      dfr2Diamond.setXY(dfr2, f(dfr2));
      dfr1Diamond.setVisibility(true);
      dfr2Diamond.setVisibility(true);
    }
    else {
      dfr1Diamond.setVisibility(false);
      dfr2Diamond.setVisibility(false);
    }
            
    if (df2RootExist) {
      df2rDiamond.setXY(df2r, f(df2r));
      df2rDiamond.setVisibility(true);
    }
    else {
      df2rDiamond.setVisibility(false);
    }
  }  
});}(RequireJS.requirejs, RequireJS.require, RequireJS.define));