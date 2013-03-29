define(function (require) {
  //Imports
  var $ = require('jquery'),
    WebFonts = require('webfonts'),
    U = require('utils'),
    Tool = require('tool'),
    Color = require('color'),
    HSlider = require('hslider'),
    Text = require('text'),
    Checkbox = require('checkbox'),
    Graph = require('graph'),
    Label = require('label');
    
  //UI
  var tool;
  var sumGraph, entryGraph, abGraph;
  var ampSlider, phiSlider, aSlider, bSlider, wSlider;
  var abCb, ampPhiCb;
  var redText, greenText, yellowText, cyanText, bText;
  //x,y bounds of various graphs
  //They are the same for sum graph and entry graph
  var xmin = -4.0, xmax = 4.0, ymin = -3.0, ymax = 3.0;
  var xmin1 = -3.0, xmax1 = 3.0; 
  //Initial value of various sliders
  var amp = 2.0, phi = 90.0, a = 1.0, b = -1.0, w = 1.5;

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
    
    //Sum graph
    sumGraph = new Graph(0, 0, 360, 290);
    //x axis
    sumGraph.xText = "t";
    sumGraph.xmin = xmin;
    sumGraph.xmax = xmax;
    sumGraph.xspan = xmax - xmin;
    sumGraph.xShortTickMin = xmin;
    sumGraph.xShortTickMax = xmax;
    sumGraph.xShortTickStep = 0.0;
    sumGraph.xLongTickMin = xmin;
    sumGraph.xLongTickMax = xmax;
    sumGraph.xLongTickStep = 1.0;
    sumGraph.xLabelMin = xmin;
    sumGraph.xLabelMax = xmax;
    sumGraph.xLabelStep = 1.0;
    sumGraph.showxGrid = false;
    sumGraph.xLabelDecimalDigits = 0;
    //y axis
    sumGraph.yText = "x";
    sumGraph.ymin = ymin;
    sumGraph.ymax = ymax;
    sumGraph.yspan = ymax - ymin;
    sumGraph.yShortTickMin = ymin;
    sumGraph.yShortTickMax = ymax;
    sumGraph.yShortTickStep = 0.0;
    sumGraph.yLongTickMin = ymin;
    sumGraph.yLongTickMax = ymax;
    sumGraph.yLongTickStep = 1.0;
    sumGraph.yLabelMin = ymin;
    sumGraph.yLabelMax = ymax;
    sumGraph.yLabelStep = 1.0;
    sumGraph.showyGrid = false;
    sumGraph.yLabelDecimalDigits = 0;
    //origin
    sumGraph.x0 = 0.0;
    sumGraph.y0 = 0.0;                              
    tool.add(sumGraph);
    
    //Entry graph
    entryGraph = new Graph(0, 275, 360, 290);
    //x axis
    entryGraph.xText = "t";
    entryGraph.xmin = xmin;
    entryGraph.xmax = xmax;
    entryGraph.xspan = xmax - xmin;
    entryGraph.xShortTickMin = xmin;
    entryGraph.xShortTickMax = xmax;
    entryGraph.xShortTickStep = 0.0;
    entryGraph.xLongTickMin = xmin;
    entryGraph.xLongTickMax = xmax;
    entryGraph.xLongTickStep = 1.0;
    entryGraph.xLabelMin = xmin;
    entryGraph.xLabelMax = xmax;
    entryGraph.xLabelStep = 1.0;
    entryGraph.showxGrid = false;
    entryGraph.xLabelDecimalDigits = 0;
    //y axis
    entryGraph.yText = "x";
    entryGraph.ymin = ymin;
    entryGraph.ymax = ymax;
    entryGraph.yspan = ymax - ymin;
    entryGraph.yShortTickMin = ymin;
    entryGraph.yShortTickMax = ymax;
    entryGraph.yShortTickStep = 0.0;
    entryGraph.yLongTickMin = ymin;
    entryGraph.yLongTickMax = ymax;
    entryGraph.yLongTickStep = 1.0;
    entryGraph.yLabelMin = ymin;
    entryGraph.yLabelMax = ymax;
    entryGraph.yLabelStep = 1.0;
    entryGraph.showyGrid = false;
    entryGraph.yLabelDecimalDigits = 0;
    //origin
    entryGraph.x0 = 0.0;
    entryGraph.y0 = 0.0;                              
    tool.add(entryGraph);
    
    //ab graph
    abGraph = new Graph(580, 165, 230, 230);
    //x axis
    abGraph.xText = "a";
    abGraph.xmin = xmin1;
    abGraph.xmax = xmax1;
    abGraph.xspan = xmax1 - xmin1;
    abGraph.xShortTickMin = xmin1;
    abGraph.xShortTickMax = xmax1;
    abGraph.xShortTickStep = 0.0;
    abGraph.xLongTickMin = xmin1;
    abGraph.xLongTickMax = xmax1;
    abGraph.xLongTickStep = 1.0;
    abGraph.xLabelMin = xmin1;
    abGraph.xLabelMax = xmax1;
    abGraph.xLabelStep = 1.0;
    abGraph.showxGrid = false;
    abGraph.xLabelDecimalDigits = 0;
    //y axis
    abGraph.yText = "b";
    abGraph.ymin = ymin;
    abGraph.ymax = ymax;
    abGraph.yspan = ymax - ymin;
    abGraph.yShortTickMin = ymin;
    abGraph.yShortTickMax = ymax;
    abGraph.yShortTickStep = 0.0;
    abGraph.yLongTickMin = ymin;
    abGraph.yLongTickMax = ymax;
    abGraph.yLongTickStep = 1.0;
    abGraph.yLabelMin = ymin;
    abGraph.yLabelMax = ymax;
    abGraph.yLabelStep = 1.0;
    abGraph.showyGrid = false;
    abGraph.yLabelDecimalDigits = 0;
    //origin
    abGraph.x0 = 0.0;
    abGraph.y0 = 0.0;                              
    tool.add(abGraph);
    
    //Text to the right of top graph
    redText = new Text(sumGraph.right + 50, sumGraph.top + 60);
    redText.textColor = Color.red;
    redText.text = 'A cos(\u03C9t - \u03D5)';
    greenText = new Text(redText.left, redText.top + 25);
    greenText.textColor = Color.green;
    greenText.text = 'a cos(\u03C9t) + b sin(\u03C9t)';
    tool.add(redText);
    tool.add(greenText);
    
    //amp slider
    ampSlider = new HSlider(sumGraph.right, sumGraph.top + 125, 220, 50);
    ampSlider.xmin = 0.0;
    ampSlider.xmax = 3.0;
    ampSlider.xspan = 3.0;
    ampSlider.setValue(amp);
    ampSlider.shortTickStep = 0.5;
    ampSlider.longTickStep = 1.0;
    ampSlider.labelStep = 1.0;
    ampSlider.text = 'A';
    ampSlider.textColor = Color.red;
    ampSlider.labelDecimalDigits = 0;
    ampSlider.valueDecimalDigits = 2;
    ampSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(ampSlider);});
    ampSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(ampSlider);});
    ampSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(ampSlider);});
    tool.add(ampSlider);                          
    
    //phi slider
    phiSlider = new HSlider(ampSlider.left, ampSlider.top + 50, 220, 50);
    phiSlider.xmin = -180.0;
    phiSlider.xmax = 180.0;
    phiSlider.xspan = 360.0;
    phiSlider.setValue(phi);
    phiSlider.shortTickStep = 45.0;
    phiSlider.longTickStep = 90;
    phiSlider.labelStep = 180.0;
    phiSlider.text = '\u03D5';
    phiSlider.textColor = Color.red;
    phiSlider.labelDecimalDigits = 0;
    phiSlider.valueDecimalDigits = 0;
    phiSlider.hasDegree = true;
    phiSlider.automaticLabels = false;
    phiSlider.labels = [new Label(-180.0, "-\u03C0"),
                        new Label(0.0, "0"),
                        new Label(180.0, "\u03C0")];
    phiSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(phiSlider);});
    phiSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(phiSlider);});
    phiSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(phiSlider);});
    tool.add(phiSlider);
    
    //Text to the right of bottom graph
    yellowText = new Text(entryGraph.right + 50, entryGraph.top + 60);
    yellowText.textColor = Color.yellow;
    yellowText.text = 'a cos(\u03C9t)';
    cyanText = new Text(yellowText.left, yellowText.top + 25);
    cyanText.textColor = Color.cyan;
    cyanText.text = 'b sin(\u03C9t)';
    tool.add(yellowText);
    tool.add(cyanText);
    
    //a slider
    aSlider = new HSlider(entryGraph.right, entryGraph.top + 125, 220, 50);
    aSlider.xmin = -2.0;
    aSlider.xmax = 2.0;
    aSlider.xspan = 4.0;
    aSlider.setValue(a);
    aSlider.shortTickStep = 0.5;
    aSlider.longTickStep = 1.0;
    aSlider.labelStep = 1.0;
    aSlider.text = 'a';
    aSlider.textColor = Color.yellow;
    aSlider.labelDecimalDigits = 0;
    aSlider.valueDecimalDigits = 2;
    aSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(aSlider);});
    aSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(aSlider);});
    aSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(aSlider);});
    tool.add(aSlider);
    
    //b slider
    bSlider = new HSlider(aSlider.left, aSlider.top + 50, 220, 50);
    bSlider.xmin = -2.0;
    bSlider.xmax = 2.0;
    bSlider.xspan = 4.0;
    bSlider.setValue(b);
    bSlider.shortTickStep = 0.5;
    bSlider.longTickStep = 1.0;
    bSlider.labelStep = 1.0;
    bSlider.text = 'b';
    bSlider.textColor = Color.cyan;
    bSlider.labelDecimalDigits = 0;
    bSlider.valueDecimalDigits = 2;
    bSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(bSlider);});
    bSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(bSlider);});
    bSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(bSlider);});
    tool.add(bSlider);
    
    //w slider
    wSlider = new HSlider(abGraph.left, abGraph.bottom + 110, 165, 50);
    wSlider.xmin = 0.0;
    wSlider.xmax = 3.0;
    wSlider.xspan = 3.0;
    wSlider.setValue(w);
    wSlider.shortTickStep = 0.5;
    wSlider.longTickStep = 1.0;
    wSlider.labelStep = 1.0;
    wSlider.text = '\u03C9';
    wSlider.textColor = Color.litegray;
    wSlider.labelDecimalDigits = 0;
    wSlider.valueDecimalDigits = 2;
    wSlider.addEventListener('mousedown',  function() {
                              sliderMouseDown(wSlider);});
    wSlider.addEventListener('mousedrag',  function() {
                              sliderMouseDrag(wSlider);});
    wSlider.addEventListener('mouseup',  function() {
                              sliderMouseUp(wSlider);});
    tool.add(wSlider);
    
    //Checkboxes
    abCb = new Checkbox(abGraph.left + 115, abGraph.bottom + 20, 100, 50);
    abCb.text = 'a,';
    abCb.textColor = Color.yellow;
    abCb.addEventListener('mousedown',  function() {
                          checkboxMouseDown(abCb);});
    tool.add(abCb);
    //TO DO: Have rich text for checkboxes instead of the following
    bText = new Text(abGraph.left + 147, abGraph.bottom + 37);
    bText.textColor = Color.cyan;
    bText.text = 'b';
    tool.add(bText);
    
    ampPhiCb = new Checkbox(abCb.left, abCb.top + 25, 100, 50);
    ampPhiCb.text = 'A,\u03D5';
    ampPhiCb.textColor = Color.red;
    ampPhiCb.addEventListener('mousedown',  function() {
                               checkboxMouseDown(ampPhiCb);});
    tool.add(ampPhiCb);
    
    //Convert phi to radians
    phi = U.degToRad(90.0);
    
    //Text for function redText, greenText, yellowText, cyanText;
    /*redText = new Text(ampSlider.left + 30, abCb.top + 70);
    tool.add(redText);
    greenText = new Text(ampSlider.left + 30, abCb.top + 70);
    tool.add(greenText);
    yellowText = new Text(ampSlider.left + 30, abCb.top + 70);
    tool.add(yellowText);
    cyanText = new Text(ampSlider.left + 30, abCb.top + 70);
    tool.add(cyanText);*/
    
    //Loop through all the components that were added and draw them
    tool.draw();
    //Now draw our graphs
    drawSumGraph();
    drawEntryGraph();
    drawabGraph();
  }
  
  function checkboxMouseDown(checkbox) {
    drawabGraph();
  }
  
  function sliderMouseDown(slider) {
    if (slider === ampSlider) {
      amp = ampSlider.xvalue;
    }
    else if (slider === phiSlider) {
      phi = U.degToRad(phiSlider.xvalue);
    }
    else if (slider === aSlider) {
      a = aSlider.xvalue;
      drawEntryGraph();
    }
    else if (slider === bSlider) {
      b = bSlider.xvalue;
      drawEntryGraph();
    }
    else { //wSlider
      w = wSlider.xvalue;
    }
    drawSumGraph();
    drawabGraph();
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
    sumGraph.draw();
    sumGraph.drawCurve(fAmpPhi, xmin, xmax, Color.red);
    sumGraph.drawCurve(fSum, xmin, xmax, Color.green);
  }  
  
  function drawEntryGraph() {  
    entryGraph.draw();
    entryGraph.drawCurve(fEntryCos, xmin, xmax, Color.yellow);
    entryGraph.drawCurve(fEntrySin, xmin, xmax, Color.cyan);  
  }
  
  function drawabGraph() {  
    var x, y;
    abGraph.draw();
    
    if (abCb.isChecked) {
      abGraph.drawLine(0.0, 0.0, a, 0.0, Color.yellow);
      abGraph.drawLine(a, 0.0, a, b, Color.cyan);
      abGraph.drawDiamond(a, b, Color.green);
    }
    if (ampPhiCb.isChecked) {
      x = amp*Math.cos(phi);
      y = amp*Math.sin(phi);
      abGraph.drawArc(0.0, 0.0, amp/2.0, 0.0, phi, true, false, Color.red); 
      abGraph.drawLine(0.0, 0.0, x, y, Color.red);
      abGraph.drawDiamond(x, y, Color.red); 
    }                
  }
});