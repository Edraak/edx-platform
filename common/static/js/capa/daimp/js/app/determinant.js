define(function (require) {
  //Imports
  var $ = require('jquery'),
    WebFonts = require('webfonts'),
    U = require('utils'),
    Tool = require('tool'),
    Color = require('color'),
    Checkbox = require('checkbox'),
    Text = require('text'),
    Vector2d = require('vector2d'),
    Graph = require('graph'),
    Shape = require('shape');

  //UI
  var tool;
  var graph;
  var vTitle, vLabel, vxText, vyText, wTitle, wLabel, wxText, wyText
  var det, detLabel0, detLabel1, detLabel2, detLabel3, detLabel4, detLabel5, detLabel6;
  //Brackets surrounding matrix
  var vwLB, vwRB;
  var vSelected = false, wSelected = false;
  var v, w;  

  //Loads webfonts from Google's website then initializes the tool
  WebFonts.load(initializeTool); 

  function initializeTool() {
    //The try catch block checks if certain features are present.
    //If not, we exit and alert the user.
    try {
      U.testForFeatures(true, false, false); //Test for canvas only
    }
    catch (err) {
      window.alert(err.toString() + " The tool is disabled.");
    }
    initTool();
  }

  function initTool() {
    var toolElement = document.getElementById('tool');
    tool = new Tool(toolElement);
    
    //Graph
    graph = new Graph(20, 0, 380, 380);
    setGraph();

    //Drag related
    graph.addEventListener('mousedown', graphMouseDown);
    graph.addEventListener('mousedrag', graphMouseDrag);
    tool.add(graph);
    
    //v vector
    v = new Vector2d(4.0, 2.0);

    vTitle = new Text(450, 60, 0, 0);
    vTitle.text = "v";
    vTitle.textColor = Color.yellow;
    vTitle.textAlign = "center"; //Centered on mid point between brackets at 520 & 590
    tool.add(vTitle);

    vxText = new Text(440, 100);
    vxText.text = v.x.toFixed(2);
    vxText.textColor = Color.yellow;
    tool.add(vxText);
    vyText = new Text(440, 130);
    vyText.text = v.y.toFixed(2);
    vyText.textColor = Color.yellow;
    tool.add(vyText);

    detLabel0 = new Text(390, 115);
    detLabel0.text = "det ";
    detLabel0.textColor = Color.litegray;
    tool.add(detLabel0);

    //w vector
    w = new Vector2d(1.0, 3.0);

    wTitle = new Text(490, 60);
    wTitle.text = "w";
    wTitle.textColor = Color.cyan;
    wTitle.textAlign = "center"; //Centered on mid point between brackets at 720 & 790
    tool.add(wTitle);

    wxText = new Text(480, 100);
    wxText.text = w.x.toFixed(2);
    wxText.textColor = Color.cyan;
    tool.add(wxText);
    wyText = new Text(480, 130);
    wyText.text = w.y.toFixed(2);
    wyText.textColor = Color.cyan;
    tool.add(wyText);
    
    //Brackets
    vwLB = new Shape(422, 80, 25, 51);
    vwRB  = new Shape(507, 80, 25, 51);
    tool.add(vwLB);
    tool.add(vwRB);

    //Line 1
    detLabel1 = new Text(535, 115);
    detLabel1.text = " = vx.wy - vy.wx";
    detLabel1.textColor = Color.litegray;
    tool.add(detLabel1);
    //Line 2
    detLabel2 = new Text(535, 165);
    calculateDet1();
    detLabel2.text = " = " + getDetStr1();
    detLabel2.textColor = Color.litegray;
    tool.add(detLabel2);
    //Line 3
    detLabel3 = new Text(504, 235);
    detLabel3.text = "Area = b.h";
    detLabel3.textColor = Color.solOrange;
    tool.add(detLabel3);
    //Line 4
    detLabel4 = new Text(537, 285);
    calculateDet2();
    detLabel4.text = " = " + getDetStr2();
    detLabel4.textColor = Color.solOrange;
    tool.add(detLabel4);
    //Line 5
    detLabel5 = new Text(513, 355);
    detLabel5.text = "v.w = |v||w|cos \u03B8";
    detLabel5.textColor = Color.litegray;
    tool.add(detLabel5);
    //Line 6
    detLabel6 = new Text(537, 405);
    calculateDet3();
    detLabel6.text = " = " + getDetStr3();
    detLabel6.textColor = Color.litegray;
    tool.add(detLabel6);
    
    //Loop through all the components that were added and draw them
    tool.draw();
    
    //Now draw our graph
    drawGraph();
    //And the brackets surrounding the matrix
    drawBrackets();
  }

  function setGraph() {
    //x axis
    graph.xText = "x";
    graph.yText = "y";
    graph.xmin = -6.0;
    graph.xmax = 6.0;
    graph.xspan = 12.0;
    graph.xShortTickMin = 0.0;
    graph.xShortTickMax = 0.0;
    graph.xShortTickStep = 0.0;
    graph.xLongTickMin = -6.0;
    graph.xLongTickMax = 6.0;
    graph.xLongTickStep = 1.0;
    graph.xLabelMin = -6.0;
    graph.xLabelMax = 6.0;
    graph.xLabelStep = 1.0;
    graph.xGridMin = -5.0;
    graph.xGridMax = 5.0;
    graph.xGridStep = 1.0;
    graph.xLabelDecimalDigits = 0;

    //y axisn
    graph.ymin = -6.0;
    graph.ymax = 6.0;
    graph.yspan = 12.0;
    graph.yShortTickMin = 0.0;
    graph.yShortTickMax = 0.0;
    graph.yShortTickStep = 0.0;
    graph.yLongTickMin = -6.0;
    graph.yLongTickMax = 6.0;
    graph.yLongTickStep = 1.0;
    graph.yLabelMin = -6.0;
    graph.yLabelMax = 6.0;
    graph.yLabelStep = 1.0;
    graph.yGridMin = -5.0;
    graph.yGridMax = 5.0;
    graph.yGridStep = 1.0;
    graph.yLabelDecimalDigits = 0;

    graph.x0 = 0.0;
    graph.y0 = 0.0;

    graph.showHorizontalCrosshair = false;
    graph.showVerticalCrosshair = false;
  }

  function graphMouseDown(args) {
    var distv = distance(v.x, v.y, args.x, args.y);
    var distw = distance(w.x, w.y, args.x, args.y);

    if (distv <= distw) {
      v.x = args.x;
      v.y = args.y;
      vSelected = true;
      wSelected = false;
    }
    else {
      w.x = args.x;
      w.y = args.y;
      wSelected = true;
      vSelected = false;
    }

    drawGraph();
    drawText();
  }

  function graphMouseDrag(args) {
    if (vSelected) {
      v.x = args.x;
      v.y = args.y;
    }
    else {
      w.x = args.x;
      w.y = args.y;
    }

    //Mouse drag works outside of the graph. Clip to borders if it is the case.
    //TO DO: Simplify the following when the vector class is written
    if (v.x > graph.xmax) {
      v.x = graph.xmax;
    }  
    else if (v.x < graph.xmin) {
      v.x = graph.xmin;
    }  
    if (v.y > graph.ymax) {
      v.y = graph.ymax;
    }  
    else if (v.y < graph.ymin) {
      v.y = graph.ymin;
    }  

    if (w.x > graph.xmax) {
      w.x = graph.xmax;
    }  
    else if (w.x < graph.xmin) {
      w.x = graph.xmin;
    }  
    if (w.y > graph.ymax) {
      w.y = graph.ymax;
    }  
    else if (w.y < graph.ymin) {
      w.y = graph.ymin;
    }

    drawGraph();
    drawText();
  }

  function distance(x1, y1, x2, y2) {
    return Math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
  }
  
  function drawBrackets() {
    vwLB.drawLeftBracket(0, 0, 50, Color.litegray);
    vwRB.drawRightBracket(20, 0, 50, Color.litegray);
  }

  function drawGraph() {
    graph.updateDrawingZone();

    var vmag = v.mag();
    var vphase = v.phase();
    var wmag = w.mag();
    var wphase = w.phase();
    var vdotw = dot(v, w);
    var projwv; //projection of w on v
    var sumvw;

    if (vmag !== 0.0 && wmag !== 0.0) {
      projwv = projection(w, v);
      sumvw = add(v, w);

      //First draw the fill of the parallelogram
      var xx = [0.0, v.x, sumvw.x, w.x];
      var yy = [0.0, v.y, sumvw.y, w.y];
      //graph.drawShape(xx, yy, Color.himidgray);
      graph.fillShape(xx, yy, Color.solOrange);

      //Projection line of w onto v 
      graph.drawLine(0.0, 0.0, projwv.x, projwv.y, Color.sOlorange);

      //Missing edges of the parallelogram
      graph.drawLine(v.x, v.y, sumvw.x, sumvw.y, Color.midgray);
      graph.drawLine(w.x, w.y, sumvw.x, sumvw.y, Color.midgray);
      //Height
      graph.drawLine(w.x, w.y, projwv.x, projwv.y, Color.solOrange);
      graph.drawArc(0.0, 0.0, 25, vphase, wphase, true, Color.green); //Radius is in pixels for the moment
    }

    //Check to see if the vectors have length 0.
    //If so, replace the arrow head by a dot
    if (vmag !== 0.0) {
      graph.drawArrow(0.0, 0.0, v.x, v.y, Color.yellow);
    }
    else {
      graph.drawPoint(0.0, 0.0, Color.yellow);
    }

    if (wmag !== 0.0) {
      graph.drawArrow(0.0, 0.0, w.x, w.y, Color.cyan);
    }
    else {
      graph.drawPoint(0.0, 0.0, Color.cyan);
    }

    //Projection point of w onto v 
    graph.drawPoint(projwv.x, projwv.y, Color.solOrange);
  }

  function drawText() //TO DO: the text labels should redraw in daimp.js when their value is changed
  {
    vxText.text = v.x.toFixed(2);
    vyText.text = v.y.toFixed(2);
    vxText.draw();
    vyText.draw();

    wxText.text = w.x.toFixed(2);
    wyText.text = w.y.toFixed(2);
    wxText.draw();
    wyText.draw();

    calculateDet1();
    detLabel2.text = " = " + getDetStr1();
    detLabel2.draw();
    calculateDet2();
    detLabel4.text = " = " + getDetStr2();
    detLabel4.draw();
    calculateDet3();
    detLabel6.text = " = " + getDetStr3();
    detLabel6.draw();

    //Around input vector (starts 20 before baseline of text) TO DO: Write routine that calculates height of text.
    //tool.drawLeftBracket(520, 80, 50, Color.litegray);
    //tool.drawRightBracket(645, 80, 50, Color.litegray);
  }

  function calculateDet1() {
    det = v.x * w.y - v.y * w.x;
  }

  function calculateDet2() {
    det = v.mag() * height(w, v).mag();
  }

  function calculateDet3() {
    det = v.mag() * w.mag() * Math.cos(phase(v, w));
  }

  function getDetStr1() {
    return "(" + v.x.toFixed(2) + ").(" + w.y.toFixed(2) + ") - (" + w.x.toFixed(2) + ").(" + v.y.toFixed(2) + ") = " + det.toFixed(2);
  }

  function getDetStr2() {
    return "(" + v.mag().toFixed(2) + ").(" + height(w, v).mag().toFixed(2) + ") = " + det.toFixed(2);
  }

  function getDetStr3() {
    return "(" + v.mag().toFixed(2) + ").(" + w.mag().toFixed(2) + ").(" + Math.cos(phase(v, w)).toFixed(2) + ") = " + det.toFixed(2);
  }

  function dot(v, w) {
    return v.x * w.x + v.y * w.y;
  }

  function phase(v, w) {
    //return Math.acos(dot(v, w)/(v.mag()*w.mag()));
    return w.phase() - v.phase();
  }

  function normalize(v) {
    return new Vector2d(v.x / v.mag(), v.y / v.mag());
  }

  function projection(w, v) //projection of w on v
  {
    var projmag = dot(v, w) / v.mag();
    var proj = normalize(v);
    proj.scale(projmag);
    return proj;
  }

  function height(w, v) //height of projection of w on v
  {
    var h = substract(w, projection(w, v));
    return h;
  }

  function add(v, w) {
    var sum = new Vector2d(v.x + w.x, v.y + w.y);
    return sum;
  }

  function substract(v, w) {
    var sub = new Vector2d(v.x - w.x, v.y - w.y);
    return sub;
  }
});