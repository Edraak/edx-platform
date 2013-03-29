define(function (require) {
  //Imports
  var $ = require('jquery'),
    WebFonts = require('webfonts'),
    U = require('utils'),
    Tool = require('tool'),
    Color = require('color'),
    HSlider = require('hslider'),
    Text = require('text'),
    RadioButtonGroup = require('radiobuttongroup'),
    RadioButton = require('radiobutton'),
    Graph = require('graph');
    
  //UI
  var tool;
  var graph;
  var aSlider, bSlider, cSlider, dSlider, xSlider;
  var risingRb, fallingRb, concaveRb, convexRb, rbg;
  var fText, posText;
  var xReadout, yReadout;
  //x,y bounds of graph
  var xmin = -6.0, xmax = 6.0, ymin = -6.0, ymax = 6.0;
  //Coefficients of our function
  var a = 1.0, b = -2.0, c = 0.5, d = 1.0;
  //Position of x slider
  var x = -0.5;
  //Roots of first and second derivatives
  var dfr1, dfr2, df2r;
  //The different zones of the graph each having its own color.
  //They are set in calculateZones
  var zone1 = Color.litegray, zone2 = Color.litegray,
      zone3 = Color.litegray, zone4 = Color.litegray; 
  //Mouse x and y readouts
  var xposStr = '', yposStr = '';    

  //Loads webfonts from Google's website then initializes the tool
  WebFonts.load(initializeTool); 

  function initializeTool() {
    //The try catch block checks if certain features are present.
    //If not, we exit and alert the user.
    try {
      U.testForFeatures(true, false, false); //Test for canvas only
    }
    catch (err) {
      window.alert(err.toString() + ' The tool is disabled.');
    }
    initTool();
  }

  function initTool() {
    var toolElement = document.getElementById('tool');
    tool = new Tool(toolElement);
    
    //Graph
    graph = new Graph(50, 50, 480, 480);
    
    //x axis
    graph.xText = "x";
    graph.xmin = xmin;
    graph.xmax = xmax;
    graph.xspan = xmax - xmin;
    graph.xShortTickMin = xmin;
    graph.xShortTickMax = xmax;
    graph.xShortTickStep = 1.0;
    graph.xLongTickMin = xmin;
    graph.xLongTickMax = xmax;
    graph.xLongTickStep = 2.0;
    graph.xLabelMin = xmin;
    graph.xLabelMax = xmax;
    graph.xLabelStep = 2.0;
    graph.showxGrid = false;
    graph.xLabelDecimalDigits = 1;

    //y axis
    graph.yText = "y";
    graph.ymin = ymin;
    graph.ymax = ymax;
    graph.yspan = ymax - ymin;
    graph.yShortTickMin = ymin;
    graph.yShortTickMax = ymax;
    graph.yShortTickStep = 1.0;
    graph.yLongTickMin = ymin;
    graph.yLongTickMax = ymax;
    graph.yLongTickStep = 2.0;
    graph.yLabelMin = ymin;
    graph.yLabelMax = ymax;
    graph.yLabelStep = 2.0;
    graph.showyGrid = false;
    graph.yLabelDecimalDigits = 1;

    graph.x0 = 0.0;
    graph.y0 = 0.0;
    
    graph.setReadouts(true, true); 
    //Drag related
    graph.addEventListener('mousedown', function(mpos) {
                          graphMouseDown(mpos);});
    graph.addEventListener('mousedrag', function(mpos) {
                          graphMouseDown(mpos);});
    graph.addEventListener('mouseup', function(mpos) {
                          graphMouseDown(mpos);});  
    //Crosshair related                      
    graph.addEventListener('mouseover', function(mpos) {
                          graphMouseOver(mpos);});                                           
    graph.addEventListener('mousemove', function(mpos) {
                          graphMouseOver(mpos);}); 
    graph.addEventListener('mouseout', function() {
                          graphMouseOver();});                                            
    
    tool.add(graph);
    
    //Sliders
    //a slider
    aSlider = new HSlider(graph.right - 20, graph.top + 40, 301, 50);
    aSlider.xmin = -2.0;
    aSlider.xmax = 2.0;
    aSlider.xspan = 4.0;
    aSlider.setValue(a);
    aSlider.shortTickStep = 0.5;
    aSlider.longTickStep = 1.0;
    aSlider.labelStep = 1.0;
    aSlider.text = 'a';
    aSlider.textColor = Color.litegray;
    aSlider.labelDecimalDigits = 1;
    aSlider.valueDecimalDigits = 2;
    aSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(aSlider);});
    aSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(aSlider);});
    aSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(aSlider);});
    tool.add(aSlider);                          
    
    //b slider
    bSlider = new HSlider(aSlider.left, aSlider.top + 50, 301, 50);
    bSlider.xmin = -2.0;
    bSlider.xmax = 2.0;
    bSlider.xspan = 4.0;
    bSlider.setValue(b);
    bSlider.shortTickStep = 0.5;
    bSlider.longTickStep = 1.0;
    bSlider.labelStep = 1.0;
    bSlider.text = 'b';
    bSlider.textColor = Color.litegray;
    bSlider.labelDecimalDigits = 1;
    bSlider.valueDecimalDigits = 2;
    bSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(bSlider);});
    bSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(bSlider);});
    bSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(bSlider);});
    tool.add(bSlider);
    
    //c slider
    cSlider = new HSlider(bSlider.left, bSlider.top + 50, 301, 50);
    cSlider.xmin = -2.0;
    cSlider.xmax = 2.0;
    cSlider.xspan = 4.0;
    cSlider.setValue(c);
    cSlider.shortTickStep = 0.5;
    cSlider.longTickStep = 1.0;
    cSlider.labelStep = 1.0;
    cSlider.text = 'c';
    cSlider.textColor = Color.litegray;
    cSlider.labelDecimalDigits = 1;
    cSlider.valueDecimalDigits = 2;
    cSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(cSlider);});
    cSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(cSlider);});
    cSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(cSlider);});
    tool.add(cSlider);
    
    //d slider
    dSlider = new HSlider(cSlider.left, cSlider.top + 50, 301, 50);
    dSlider.xmin = -2.0;
    dSlider.xmax = 2.0;
    dSlider.xspan = 4.0;
    dSlider.setValue(d);
    dSlider.shortTickStep = 0.5;
    dSlider.longTickStep = 1.0;
    dSlider.labelStep = 1.0;
    dSlider.text = 'd';
    dSlider.textColor = Color.litegray;
    dSlider.labelDecimalDigits = 1;
    dSlider.valueDecimalDigits = 2;
    dSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(dSlider);});
    dSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(dSlider);});
    dSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(dSlider);});
    tool.add(dSlider);
    
    //x slider under the graph
    xSlider = new HSlider(graph.left - 10, graph.bottom - 33,
                          graph.width + 21, 50);
    xSlider.xmin = -6.0;
    xSlider.xmax = 6.0;
    xSlider.xspan = 12.0;
    xSlider.setValue(x);
    xSlider.shortTickStep = 1.0;
    xSlider.longTickStep = 2.0;
    xSlider.labelStep = 2.0;
    xSlider.text = '';
    xSlider.textColor = Color.litegray;
    xSlider.labelDecimalDigits = 1;
    xSlider.valueDecimalDigits = 2;
    xSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(xSlider);});
    xSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(xSlider);});
    xSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(xSlider);});
    tool.add(xSlider);
    
    //Radio buttons
    risingRb = new RadioButton(aSlider.left + 50, dSlider.top + 60, 200, 100);
    risingRb.text = 'Rising';
    risingRb.isChecked = true;
    risingRb.textColor = Color.yellow;
    risingRb.addEventListener('mousedown',  function() {
                              radioButtonMouseDown(risingRb);});
    tool.add(risingRb);
    fallingRb = new RadioButton(risingRb.left, risingRb.top + 25, 100, 100);
    fallingRb.text = 'Falling';
    fallingRb.textColor = Color.green;
    fallingRb.addEventListener('mousedown',  function() {
                              radioButtonMouseDown(fallingRb);});
    tool.add(fallingRb);
    concaveRb = new RadioButton(fallingRb.left, fallingRb.top + 25, 100, 100);
    concaveRb.text = 'Concave';
    concaveRb.textColor = Color.orange;
    concaveRb.addEventListener('mousedown',  function() {
                              radioButtonMouseDown(concaveRb);});
    tool.add(concaveRb);
    convexRb = new RadioButton(concaveRb.left, concaveRb.top + 25, 100, 100);
    convexRb.text = 'Convex';
    convexRb.textColor = Color.red;
    convexRb.addEventListener('mousedown',  function() {
                              radioButtonMouseDown(convexRb);});
    tool.add(convexRb);
    //Radio button group
    rbg = new RadioButtonGroup(risingRb, fallingRb, concaveRb, convexRb);
    
    //Text for function
    fText = new Text(aSlider.left + 30, convexRb.top + 70);
    tool.add(fText);
    posText = new Text(fText.left, fText.top + 25);
    tool.add(posText);
    //Text for mouse readout
    xReadout = new Text(convexRb.left + 20, posText.top + 56);
    xReadout.text = 'x = ';
    tool.add(xReadout);
    yReadout = new Text(xReadout.left, xReadout.top + 25);
    yReadout.text = 'y = ';
    tool.add(yReadout);
    
    //Loop through all the components that were added and draw them
    tool.draw();
    //Now draw our curve and point
    drawGraph();
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
    zone1 = Color.litegray;
    zone2 = Color.litegray;
    zone3 = Color.litegray;
    zone4 = Color.litegray;

    //Function is increasing outside of [dfr1, dfr2]
    if (a > 0.0) {
      if (risingRb.isChecked) {	
        zone1 = Color.yellow;
        zone4 = Color.yellow;
      }
      else if (fallingRb.isChecked) {	
        zone2 = Color.green;
        zone3 = Color.green;
      }
      else if (concaveRb.isChecked) {
        zone1 = Color.orange;
        zone2 = Color.orange;
      }
      else if (convexRb.isChecked) {
        zone3 = Color.red;
        zone4 = Color.red;
      }
    }
    //Function is increasing inside of [dfr1, dfr2]
    else if (a < 0.0) {
      if (fallingRb.isChecked) {
        zone1 = Color.green;
        zone4 = Color.green;
      }
      else if (risingRb.isChecked) {	
        zone2 = Color.yellow;
        zone3 = Color.yellow;
      }
      else if (concaveRb.isChecked) {
        zone3 = Color.orange;
        zone4 = Color.orange;
      }
      else if (convexRb.isChecked) {
        zone1 = Color.red;
        zone2 = Color.red;
      }
    }
    //a = 0: function becomes bx^2 + cx + d, derivative 2bx + c, root at -c/2bx
    else {
      if (b > 0.0) {
        if (risingRb.isChecked) {	
          zone3 = Color.yellow;
          zone4 = Color.yellow;
        }
        else if (fallingRb.isChecked) {	
          zone1 = Color.green;
          zone2 = Color.green;
        }
        else if (concaveRb.isChecked) {
        }
        //Always convex
        else if (convexRb.isChecked) {
          zone1 = Color.red;
          zone2 = Color.red;
          zone3 = Color.red;
          zone4 = Color.red;
        }
      }
      else if (b < 0.0) {
        if (risingRb.isChecked) {	
          zone1 = Color.yellow;
          zone2 = Color.yellow;
        }
        else if (fallingRb.isChecked) {	
          zone3 = Color.green;
          zone4 = Color.green;
        }
         //Always concave
        else if (concaveRb.isChecked) {
          zone1 = Color.orange;
          zone2 = Color.orange;
          zone3 = Color.orange;
          zone4 = Color.orange;
        }
        else if (convexRb.isChecked) {
        }
      }
      //a = 0, b = 0: function becomes cx + d, derivative c, no root, rising
      //everywhere if c > 0, falling everywhere if c < 0, monotonous if c = 0
      else {
        if (risingRb.isChecked) {	
          if (c > 0.0) {	
            zone1 = Color.yellow;
            zone2 = Color.yellow;
            zone3 = Color.yellow;
            zone4 = Color.yellow;
          }	
        }
        else if (fallingRb.isChecked) {	
          if (c < 0.0) {	
            zone1 = Color.green;
            zone2 = Color.green;
            zone3 = Color.green;
            zone4 = Color.green;
          }	
        }
        else if (concaveRb.isChecked) {
        }
        else if (convexRb.isChecked) {
        }
      }
    }
  }
  
  //Function is ax^3 + bx^2 + cx + d
  function calculateFunctionString() {
    var aStr = '', bStr = '', cStr = '', dStr = '', funcStr = 'f(x) = ';
            
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
    
    if (a > 0.0) {
      funcStr += aStr + 'x^{3}';
    } 
    else if (a < 0.0) {
      funcStr += '-' + aStr + 'x^{3}';
    }
                        
    if (b > 0.0) {
       //Nothing in front
      if (a === 0.0) {
       funcStr += bStr + 'x^{2}';
      } 
      else {
        funcStr += ' + ' + bStr + 'x^{2}';
      }
    }
    else if (b < 0.0) {
      //Nothing in front
      if (a === 0.0) {
        funcStr += '-' + bStr + 'x^{2}';
      }  
      else {
        funcStr += ' - ' + bStr + 'x^{2}';
      }  
    }

    if (c > 0.0) {
       //Nothing in front
      if (a === 0.0 && b === 0.0) {
        funcStr += cStr + 'x';
      }  
      else {
        funcStr += ' + ' + cStr + 'x';
      }  
    }
    else if (c < 0.0) {
        //Nothing in front
        if (a === 0.0 && b === 0.0) {
          funcStr += '-' + cStr + 'x';
        }  
        else {
          funcStr += ' - ' + cStr + 'x';
        }  
    }
    
    if (d > 0.0) {
      //Nothing in front
      if (a === 0.0 && b === 0.0 && c === 0.0) {
        funcStr += dStr;
      }  
      else {
        funcStr += ' + ' + dStr;
      }  
    }
    else if (d < 0.0) {
      //Nothing in front
      if (a === 0.0 && b === 0.0 && c === 0.0) {
        funcStr += '-' + dStr;
      }  
      else {
        funcStr += ' - ' + dStr;
      }  
    }
    
    if (a === 0.0 && b === 0.0 && c === 0.0 && d === 0.0) {
      funcStr += '0';
    }  

    return funcStr;
  }
  
  function radioButtonMouseDown(radioButton) {
    drawGraph();
  }
  
  function sliderMouseDown(slider) {
    if (slider === aSlider) {
      a = aSlider.xvalue;
    }
    else if (slider === bSlider) {
      b = bSlider.xvalue;
    }
    else if (slider === cSlider) {
      c = cSlider.xvalue;
    }
    else if (slider === dSlider) {
      d = dSlider.xvalue;
    }
    else { //xSlider
      x = xSlider.xvalue;
    }
    drawGraph();
  }
   
  function sliderMouseDrag(slider) {
    sliderMouseDown(slider);
  } 
   
  function sliderMouseUp(slider) {
     sliderMouseDown(slider);
  }   
  
  //Drag related
  function graphMouseDown(mpos) {
    xposStr = '';
    yposStr = '';
    drawGraph();
  }
  
  //Crosshair related
  function graphMouseOver(mpos) {
    //Bug: figure out why this is necessary
    if (typeof mpos !== 'undefined') { 
      xposStr = (mpos.x).toFixed(2);
      yposStr = (mpos.y).toFixed(2);
    }
    else {
      xposStr = '';
      yposStr = '';
    }  
    drawGraph();
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
    
    graph.draw();
    //Draw the curve segments
    calculateZones();
    graph.drawCurve(f, xmin, dfr1, zone1);
    graph.drawCurve(f, dfr1, df2r, zone2);
    graph.drawCurve(f, df2r, dfr2, zone3);
    graph.drawCurve(f, dfr2, xmax, zone4);
    //Draw the points on top of them
    var dfRootsColor = Color.litegray, df2RootColor = Color.litegray;
    if (risingRb.isChecked) {
      dfRootsColor = Color.yellow;
    }  
    else if (fallingRb.isChecked) {
      dfRootsColor = Color.green;
    }  
    else if (concaveRb.isChecked) {
      df2RootColor = U.orange;
    }  
    else if (convexRb.isChecked) {
      df2RootColor = U.red;
    }  
            
    //Special case for a = 0, we draw the two roots of the derivative in the 
    //color of concave and convex
    if (a === 0.0) {
      if (concaveRb.isChecked && b < 0.0) {
        dfRootsColor = U.orange;
      }
      else if (convexRb.isChecked && b < 0.0) {
          dfRootsColor = U.red;
      }
    }
    
    dfRootsColor = Color.purple;
    df2RootColor = Color.cyan;
            
    if (dfRootsExist) {
      graph.drawDiamond(dfr1, f(dfr1), dfRootsColor);
      graph.drawDiamond(dfr2, f(dfr2), dfRootsColor);
    }
            
    if (df2RootExist) {
      graph.drawDiamond(df2r, f(df2r), df2RootColor);
    }
    
    var y = f(x);
    var dy = df(x);
    var d2y = d2f(x);
            
    graph.drawLine(x, graph.ymin, x, y, Color.darkgray);
    graph.drawDiamond(x, y, Color.white);
    
    //Draw all the function string
    fText.text = calculateFunctionString();
    fText.draw();
    posText.text = 'f(' + x.toFixed(2) + ') = ' + y.toFixed(2);
    posText.draw();
    //Draw the mouse x and y readouts
    xReadout.text = 'x = ' + xposStr;
    yReadout.text = 'y = ' + yposStr;
    xReadout.draw();
    yReadout.draw();
    
    graph.drawCrosshairs();
  }  
});