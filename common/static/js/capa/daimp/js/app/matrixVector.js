(function (requirejs, require, define) {
define(function (require) {
  //Imports
  //var $ = require('jquery'),
  //var WebFonts = require('webfonts'),
  var U = require('utils'),
    Tool = require('tool'),
    Color = require('color'),
    Checkbox = require('checkbox'),
    HSlider = require('hslider'),
    VSlider = require('vslider'),
    Text = require('text'),
    Label = require('label'),
    Graph = require('graph');
    Button = require('button');
    Shape = require('shape');

  //UI
  var tool;
  var graph;
  var vinxSlider, vinySlider, rSlider, thetaSlider, a11Slider, a12Slider,
  a21Slider, a22Slider;
  var eigenlinesCb, eigenvectorsCb;
  var vinTitle, vinLabel, vinxText, vinyText, voutTitle, voutLabel, voutxText, 
  voutyText;
  var eigenval1Text, eigenvect1xText, eigenvect1yText, eigenval2Text, 
  eigenvect2xText, eigenvect2yText;
  var matrixLabel;
  //Brackets surround vectors and matrix
  var vinLB, vinRB, voutLB, voutRB, matLB, matRB;
  //Temporary button
  var testButton;

  var vinx,
    viny,
    voutx,
    vouty,
    r,
    theta,
    a11,
    a12,
    a21,
    a22;

  var eigen;
  
  //var state = {};
  
  //This is where we define what variables constitute the state.
  /*function defineState() {
    for (var i = 0; i < arguments.length; i++) {
      //Set field to its name by default
      state[arguments[i]] = arguments[i];
    }  
  }*/
  
  function updateState() {
    /*state.vinx = vinx;
    state.viny = viny;
    state.voutx = voutx;
    state.vouty = vouty;
    state.r = r;
    state.theta = theta;
    state.a11 = a11;
    state.a12 = a12;
    state.a21 = a21;
    state.a22 = a22;*/
    
    //$("input#stateField").val(JSON.stringify(state));
    updateHiddenInputField();
  }    

  //Loads webfonts from Google's website then initializes the tool
  //WebFonts.load(initializeTool);

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
  
  
  function  getInputField() {
    var problem = $('#tool').parents('.problem');
    return problem.find('input[type="hidden"][name!="tool_name"][name!="tool_initial_state"]');
    };     
  
  function updateHiddenInputField() {
    var input_field = getInputField();
    var value = {'vinx': parseFloat(vinx), 'viny': parseFloat(viny), 'voutx': parseFloat(voutx),'vouty': parseFloat(vouty)};
    input_field.val(JSON.stringify(value));
  }

  function initTool() {
    var initial_state = $("input#tool_initial_state").val()
    var saved_state = getInputField().val();
    
    //Initial state from xml file 
    if (saved_state === '') {
      //initial_state = JSON.parse(initial_state);
      vinx = parseFloat(initial_state); //initial_state.vinx;
      viny = parseFloat(initial_state); //initial_state.viny;
    }
    //Saved state
    else {
      saved_state = JSON.parse(saved_state);
      vinx = saved_state.vinx;
      viny = saved_state.viny;
    }
    
    //Load vinx from xml
    //vinx = parseFloat($("input#tool_initial_state").val());
    //viny = 1.0;
    a11 = 1.0;
    a12 = 1.0;
    a21 = 1.0;
    a22 = 0.0;
    
    var toolElement = document.getElementById('tool');
    tool = new Tool(toolElement);
   
    //Graph
    //Was graph = new Graph(90, 40, 390, 340);
    graph = new Graph(30, 0, 380, 380);
    setGraph();
    
    //Drag related
    graph.addEventListener('mousedown', function(mpos) {
                          graphMouseDown(mpos);});
    graph.addEventListener('mousedrag', function(mpos) {
                          graphMouseDown(mpos);});
    graph.addEventListener('mouseup', function(mpos) {
                          graphMouseDown(mpos);});  
    
    tool.add(graph);

    initialize();
    
     //Brackets
    vinLB = new Shape(482, 80, 25, 51);
    vinRB  = new Shape(527, 80, 25, 51);
    voutLB  = new Shape(682, 80, 25, 51);
    voutRB  = new Shape(727, 80, 25, 51);
    matLB  = new Shape(440, 195, 25, 96);
    matRB  = new Shape(775, 195, 25, 96);
    
    tool.add(vinLB);
    tool.add(vinRB);
    tool.add(voutLB);
    tool.add(voutRB);
    tool.add(matLB);
    tool.add(matRB);

    //Sliders
    vinySlider = new VSlider(0, 0, 65, 380);
    vinySlider.addEventListener("mousedown", vinySliderMouseDown);
    vinySlider.addEventListener("mousedrag", vinySliderMouseDown);
    tool.add(vinySlider);

    vinxSlider = new HSlider(20, 350, 400, 40);
    vinxSlider.addEventListener("mousedown", vinxSliderMouseDown);
    vinxSlider.addEventListener("mousedrag", vinxSliderMouseDown);
    tool.add(vinxSlider);

    rSlider = new HSlider(20, 450, 300, 40);
    rSlider.addEventListener("mousedown", rSliderMouseDown);
    rSlider.addEventListener("mousedrag", rSliderMouseDown);
    tool.add(rSlider);

    thetaSlider = new HSlider(20, 500, 300, 40);
    thetaSlider.addEventListener("mousedown", thetaSliderMouseDown);
    thetaSlider.addEventListener("mousedrag", thetaSliderMouseDown);
    tool.add(thetaSlider);

    a11Slider = new HSlider(415, 200, 200, 40);
    a11Slider.addEventListener("mousedown", a11SliderMouseDown);
    a11Slider.addEventListener("mousedrag", a11SliderMouseDown);
    tool.add(a11Slider);

    a12Slider = new HSlider(600, 200, 200, 40);
    a12Slider.addEventListener("mousedown", a12SliderMouseDown);
    a12Slider.addEventListener("mousedrag", a12SliderMouseDown);
    tool.add(a12Slider);

    a21Slider = new HSlider(415, 250, 200, 40);
    a21Slider.addEventListener("mousedown", a21SliderMouseDown);
    a21Slider.addEventListener("mousedrag", a21SliderMouseDown);
    tool.add(a21Slider);

    a22Slider = new HSlider(600, 250, 200, 40);
    a22Slider.addEventListener("mousedown", a22SliderMouseDown);
    a22Slider.addEventListener("mousedrag", a22SliderMouseDown);
    tool.add(a22Slider);

    setSliders();

    //Input vector
    vinTitle = new Text(470, 60);
    vinTitle.text = "Input vector";
    vinTitle.textColor = Color.yellow;
    vinTitle.textAlign = "center";
    tool.add(vinTitle);

    vinxText = new Text(500, 100);
    vinxText.text = vinx.toFixed(2);
    vinxText.textColor = Color.yellow;
    tool.add(vinxText);
   
    vinyText = new Text(500, 130);
    vinyText.text = viny.toFixed(2);
    vinyText.textColor = Color.yellow;
    tool.add(vinyText);

    vinLabel = new Text(450, 115);
    vinLabel.text = "v = ";
    vinLabel.textColor = Color.yellow;
    tool.add(vinLabel);

    //Output vector
    voutTitle = new Text(665, 60);
    voutTitle.text = "Output vector";
    voutTitle.textColor = Color.cyan;
    voutTitle.textAlign = "center";
    tool.add(voutTitle);

    voutxText = new Text(700, 100);
    voutxText.text = voutx.toFixed(2);
    voutxText.textColor = Color.cyan;
    tool.add(voutxText);
    
    voutyText = new Text(700, 130);
    voutyText.text = vouty.toFixed(2);
    voutyText.textColor = Color.cyan;
    tool.add(voutyText);

    voutLabel = new Text(640, 115);
    voutLabel.text = "Av = ";
    voutLabel.textColor = Color.cyan;
    tool.add(voutLabel);

    //Matrix label
    matrixLabel = new Text(405, 255);
    matrixLabel.text = "A = ";
    matrixLabel.textColor = Color.green;
    tool.add(matrixLabel);

    //Eigenvalues checkox
    eigenlinesCb = new Checkbox(465, 364, 12, 12);
    eigenlinesCb.text = "Eigenlines";
    eigenlinesCb.textColor = Color.green;
    eigenlinesCb.addEventListener("mousedown", checkboxMouseDown);
    tool.add(eigenlinesCb);

    //Eigenvectors checkox
    eigenvectorsCb = new Checkbox(465, 400, 12, 12);
    eigenvectorsCb.text = "Eigenvectors";
    eigenvectorsCb.textColor = Color.green;
    eigenvectorsCb.addEventListener("mousedown", checkboxMouseDown);
    eigenvectorsCb.setVisibility(false);
    tool.add(eigenvectorsCb);

    //Eigenvalues and eigenvectors readouts
    eigenval1Text = new Text(465, 480);
    eigenval1Text.hasSubSuperscript = true;
    eigenval1Text.text = "\u03BB_{1} = ";
    eigenval1Text.textColor = Color.green;
    eigenval1Text.setVisibility(false);
    tool.add(eigenval1Text);

    eigenvect1xText = new Text(565, 480);
    eigenvect1xText.hasSubSuperscript = true;
    eigenvect1xText.text = "e_{1x} = ";
    eigenvect1xText.textColor = Color.green;
    eigenvect1xText.setVisibility(false);
    tool.add(eigenvect1xText);

    eigenvect1yText = new Text(665, 480);
    eigenvect1yText.hasSubSuperscript = true;
    eigenvect1yText.text = "e_{1y} = ";
    eigenvect1yText.textColor = Color.green;
    eigenvect1yText.setVisibility(false);
    tool.add(eigenvect1yText);

    eigenval2Text = new Text(465, 510);
    eigenval2Text.hasSubSuperscript = true;
    eigenval2Text.text = "\u03BB_{0} = ";
    eigenval2Text.textColor = Color.green;
    eigenval2Text.setVisibility(false);
    tool.add(eigenval2Text);

    eigenvect2xText = new Text(565, 510);
    eigenvect2xText.hasSubSuperscript = true;
    eigenvect2xText.text = "e_{2x} = ";
    eigenvect2xText.textColor = Color.green;
    eigenvect2xText.setVisibility(false);
    tool.add(eigenvect2xText);

    eigenvect2yText = new Text(665, 510);
    eigenvect2yText.hasSubSuperscript = true;
    eigenvect2yText.text = "e_{2y} = ";
    eigenvect2yText.textColor = Color.green;
    eigenvect2yText.setVisibility(false);
    tool.add(eigenvect2yText);
    
    //This is temporary, a button used to checkout our state.
    /*testButton = new Button(465, 540, 50, 20);
    testButton.text = "Test";
    testButton.addEventListener("mousedown", testJSON);
    tool.add(testButton);*/
    
    //Loop through all the components that were added and draw them
    tool.draw();
    
    //Now draw our graph
    drawGraph();
    //And the brackets surrounding the vectors and matrix
    drawBrackets();
    //setState("a11", "a12", "a21", "a22");
    
    updateHiddenInputField()
  }
  
  /*function testJSON() {
    console.log("Test JSON");
  }*/  

  function initialize() {
    r = calculateR();
    theta = calculateTheta();
    voutx = calculatevoutx();
    vouty = calculatevouty();
    eigen = getEigen();
  }

  function setSliders() {
    //x Slider
    vinxSlider.xmin = -6.0;
    vinxSlider.xmax = 6.0;
    vinxSlider.xspan = 12.0;
    vinxSlider.setValue(vinx);
    vinxSlider.shortTickStep = 0.0;
    vinxSlider.longTickStep = 1.0;
    vinxSlider.labelStep = 1.0;
    vinxSlider.text = "x";
    vinxSlider.textColor = Color.yellow;
    vinxSlider.valueDecimalDigits = 2;
    vinxSlider.labelDecimalDigits = 0;

    //y Slider
    vinySlider.ymin = -6.0;
    vinySlider.ymax = 6.0;
    vinySlider.yspan = 12.0;
    vinySlider.setValue(viny);
    vinySlider.shortTickStep = 0.0;
    vinySlider.longTickStep = 1.0;
    vinySlider.labelStep = 1.0;
    vinySlider.text = "y";
    vinySlider.textColor = Color.yellow;
    vinySlider.valueDecimalDigits = 2;
    vinySlider.labelDecimalDigits = 0;

    //r Slider
    rSlider.xmin = 0.0;
    rSlider.xmax = 8.0;
    rSlider.xspan = 8.0;
    rSlider.setValue(r);
    rSlider.shortTickStep = 0.0;
    rSlider.longTickStep = 1.0;
    rSlider.labelStep = 1.0;
    rSlider.text = "r";
    rSlider.textColor = Color.yellow;
    rSlider.valueDecimalDigits = 2;
    rSlider.labelDecimalDigits = 0;

    //theta Slider
    thetaSlider.xmin = 0.0;
    thetaSlider.xmax = 2.0;
    thetaSlider.xspan = 2.0;
    thetaSlider.setValue(theta);
    thetaSlider.shortTickStep = 0.5;
    thetaSlider.longTickStep = 1.0;
    thetaSlider.labelStep = 1.0;
    thetaSlider.text = "\u03B8";
    thetaSlider.textColor = Color.yellow;
    thetaSlider.valueDecimalDigits = 2;
    thetaSlider.automaticLabels = false;
    thetaSlider.labels = [new Label(0.0, "0"), new Label(0.5, "\u03C0 / 2"), new Label(1.5, "3\u03C0 / 2"), new Label(1.0, "\u03C0"), new Label(2.0, "2\u03C0")];
    thetaSlider.hasPI = true;

    //MATRIX SLIDERS

    //a11 Slider
    a11Slider.xmin = -6.0;
    a11Slider.xmax = 6.0;
    a11Slider.xspan = 12.0;
    a11Slider.setValue(a11);
    a11Slider.shortTickStep = 1.0;
    a11Slider.longTickStep = 3.0;
    a11Slider.labelStep = 3.0;
    a11Slider.text = "";
    a11Slider.textColor = Color.green;
    a11Slider.valueDecimalDigits = 1;
    a11Slider.labelDecimalDigits = 0;

    //a12 Slider
    a12Slider.xmin = -6.0;
    a12Slider.xmax = 6.0;
    a12Slider.xspan = 12.0;
    a12Slider.setValue(a12);
    a12Slider.shortTickStep = 1.0;
    a12Slider.longTickStep = 3.0;
    a12Slider.labelStep = 3.0;
    a12Slider.text = "";
    a12Slider.textColor = Color.green;
    a12Slider.valueDecimalDigits = 1;
    a12Slider.labelDecimalDigits = 0;

    //a21 Slider
    a21Slider.xmin = -6.0;
    a21Slider.xmax = 6.0;
    a21Slider.xspan = 12.0;
    a21Slider.setValue(a21);
    a21Slider.shortTickStep = 1.0;
    a21Slider.longTickStep = 3.0;
    a21Slider.labelStep = 3.0;
    a21Slider.text = "";
    a21Slider.textColor = Color.green;
    a21Slider.valueDecimalDigits = 1;
    a21Slider.labelDecimalDigits = 0;

    //a22 Slider
    a22Slider.xmin = -6.0;
    a22Slider.xmax = 6.0;
    a22Slider.xspan = 12.0;
    a22Slider.setValue(a22);
    a22Slider.shortTickStep = 1.0;
    a22Slider.longTickStep = 3.0;
    a22Slider.labelStep = 3.0;
    a22Slider.text = "";
    a22Slider.textColor = Color.green;
    a22Slider.valueDecimalDigits = 1;
    a22Slider.labelDecimalDigits = 0;
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
    graph.xLongTickMin = 0.0;
    graph.xLongTickMax = 0.0;
    graph.xLongTickStep = 0.0;
    graph.xLabelMin = 0.0;
    graph.xLabelMax = 1.0;
    graph.xLabelStep = 0.0;
    graph.xGridMin = -5.0;
    graph.xGridMax = 5.0;
    graph.xGridStep = 1.0;
    graph.xLabelDecimalDigits = 0;

    //y axis
    graph.ymin = -6.0;
    graph.ymax = 6.0;
    graph.yspan = 12.0;
    graph.yShortTickMin = 0.0;
    graph.yShortTickMax = 9.0;
    graph.yShortTickStep = 0.0;
    graph.yLongTickMin = 0.0;
    graph.yLongTickMax = 0.0;
    graph.yLongTickStep = 0.0;
    graph.yLabelMin = 0.0;
    graph.yLabelMax = 1.0;
    graph.yLabelStep = 0.0;
    graph.yGridMin = -5.0;
    graph.yGridMax = 5.0;
    graph.yGridStep = 1.0;
    graph.yLabelDecimalDigits = 0;

    graph.x0 = 0.0;
    graph.y0 = 0.0;

    graph.showHorizontalCrosshair = false;
    graph.showVerticalCrosshair = false;
  }

  function vinxSliderMouseDown() {
    vinx = vinxSlider.xvalue;
    r = calculateR();
    theta = calculateTheta();
    voutx = calculatevoutx();
    vouty = calculatevouty();
    rSlider.setValue(r);
    thetaSlider.setValue(theta / Math.PI);
    drawGraph();
    drawText();
    updateState();
  }

  function vinySliderMouseDown() {
    viny = vinySlider.yvalue;
    r = calculateR();
    theta = calculateTheta();
    voutx = calculatevoutx();
    vouty = calculatevouty();
    rSlider.setValue(r);
    thetaSlider.setValue(theta / Math.PI);
    drawGraph();
    drawText();
    updateState();
  }

  function rSliderMouseDown() {
    r = rSlider.xvalue;
    vinx = calculatevinx();
    viny = calculateviny();
    voutx = calculatevoutx();
    vouty = calculatevouty();
    vinxSlider.setValue(vinx);
    vinySlider.setValue(viny);
    drawGraph();
    drawText();
    updateState();
  }

  function thetaSliderMouseDown() {
    theta = Math.PI * thetaSlider.xvalue;
    vinx = calculatevinx();
    viny = calculateviny();
    voutx = calculatevoutx();
    vouty = calculatevouty();
    vinxSlider.setValue(vinx);
    vinySlider.setValue(viny);
    drawGraph();
    drawText();
    updateState();
  }

  function a11SliderMouseDown() {
    a11 = a11Slider.xvalue;
    voutx = calculatevoutx();
    vouty = calculatevouty();
    eigen = getEigen();
    drawGraph();
    drawText();
    updateState();
  }

  function a12SliderMouseDown() {
    a12 = a12Slider.xvalue;
    voutx = calculatevoutx();
    vouty = calculatevouty();
    eigen = getEigen();
    drawGraph();
    drawText();
    updateState();
  }

  function a21SliderMouseDown() {
    a21 = a21Slider.xvalue;
    voutx = calculatevoutx();
    vouty = calculatevouty();
    eigen = getEigen();
    drawGraph();
    drawText();
    updateState();
  }

  function a22SliderMouseDown() {
    a22 = a22Slider.xvalue;
    voutx = calculatevoutx();
    vouty = calculatevouty();
    eigen = getEigen();
    drawGraph();
    drawText();
    updateState();
  }

  function graphMouseDown(mpos) {
    vinx = mpos.x;
    viny = mpos.y;
    r = calculateR();
    theta = calculateTheta();
    voutx = calculatevoutx();
    vouty = calculatevouty();
    vinxSlider.setValue(vinx);
    vinySlider.setValue(viny);
    rSlider.setValue(r);
    thetaSlider.setValue(theta / Math.PI);
    vinxSlider.draw();
    vinySlider.draw();
    rSlider.draw();
    thetaSlider.draw();
    drawGraph();
    drawText();
    updateState();
  }
  
  function checkboxMouseDown() {
    if (eigenlinesCb.isChecked) {
      eigenvectorsCb.setVisibility(true);
    }  
    else {
      eigenvectorsCb.setVisibility(false);
    }
    drawGraph(); //To draw or erase eigenlines
    drawText(); //To draw or erase eigenvalues and eigenvectors
    
    if (eigenvectorsCb.isChecked) {
      eigenval1Text.setVisibility(true);
      eigenvect1xText.setVisibility(true);
      eigenvect1yText.setVisibility(true);
      eigenval2Text.setVisibility(true);
      eigenvect2xText.setVisibility(true);
      eigenvect2yText.setVisibility(true);
    }
    else {
      eigenval1Text.setVisibility(false);
      eigenvect1xText.setVisibility(false);
      eigenvect1yText.setVisibility(false);
      eigenval2Text.setVisibility(false);
      eigenvect2xText.setVisibility(false);
      eigenvect2yText.setVisibility(false);
    }    
  }

  function calculateR() {
    return Math.sqrt(vinx * vinx + viny * viny);
  }

  function calculateTheta() {
    var ang = Math.atan2(viny, vinx);
    if (ang >= 0.0) {
      return ang;
    }  
    else {
      return 2.0 * Math.PI + ang;
    }  
  }

  //TO DO: Use daimp vector class here
  function phase(x, y) {
    var ang = Math.atan2(y, x);
    if (ang >= 0.0) {
      return ang;
    }  
    else {
      return 2.0 * Math.PI + ang;
    }  
  }

  function isCloseToEigenvector(e) {
    return Math.abs(phase(e.x, e.y) - phase(vinx, viny));
  }

  function calculatevinx() {
    return r * Math.cos(theta);
  }

  function calculateviny() {
    return r * Math.sin(theta);
  }

  function calculatevoutx() {
    return a11 * vinx + a12 * viny;
  }

  function calculatevouty() {
    return a21 * vinx + a22 * viny;
  }

  function Eigen(lambda, x, y) {
    this.val = lambda;
    this.x = x;
    this.y = y;
  }

  function getDeterminant(m11, m12, m21, m22) {
    return m11 * m22 - m12 * m21;
  }

  //Characteristic equation lambda^2 - (a11+a22)lambda + (a11a22-a12a21) = 0
  //Set b = a11+a22, c = a11a22-a12a21
  function getEigen() {
    var b = a11 + a22;
    var c = a11 * a22 - a12 * a21;
    var det = b * b - 4.0 * c;
    var e1, e2;
    var lambda;
    var result = [];

    //Two real eigenvalues
    if (det > 0.0) {
      lambda = (b - Math.sqrt(det)) / 2.0;
      //Arbitrarily choose x coordinate to be 1
      if (a12 !== 0.0) {
        e1 = new Eigen(lambda, 1.0, - (a11 - lambda) / a12);
      }  
      else if (a22 !== 0.0) {
        e1 = new Eigen(lambda, 1.0, - (a21 - lambda) / a22);
      }  

      lambda = (b + Math.sqrt(det)) / 2.0;
      //Arbitrarily choose x coordinate to be 1
      if (a12 !== 0) {
        e2 = new Eigen(lambda, 1.0, - (a11 - lambda) / a12);
      }  
      else if (a22 !== 0.0) {
        e2 = new Eigen(lambda, 1.0, - (a21 - lambda) / a22);
      }  

      result[0] = e1;
      result[1] = e2;
    }
    //One double real eigenvalue
    else if (det === 0.0) {
      lambda = b / 2.0;
      //Arbitrarily choose x coordinate to be 1
      if (a12 !== 0.0) {
        e1 = new Eigen(lambda, 1.0, - (a11 - lambda) / a12);
      }  
      else if (a22 !== 0.0) {
        e1 = new Eigen(lambda, 1.0, - (a21 - lambda) / a22);
      }  

      result[0] = e1;
    }
    //Complex eigenvalues, return an empty array for the moment
    return result;
  }

  function drawBrackets() {
    vinLB.drawLeftBracket(0, 0, 50, Color.yellow);
    vinRB.drawRightBracket(20, 0, 50, Color.yellow);
    voutLB.drawLeftBracket(0, 0, 50, Color.cyan);
    voutRB.drawRightBracket(20, 0, 50, Color.cyan);
    matLB.drawLeftBracket(0, 0, 95, Color.green);
    matRB.drawRightBracket(20, 0, 95, Color.green);
  }
  
  function drawGraph() {
    //graph.updateDrawingZone(); Should we use this?
    graph.draw();
    //Check to see if the vectors have length 0.
    //If so, replace the arrow head by a dot.
    if (Math.sqrt(vinx * vinx + viny * viny) !== 0) {
      graph.drawArrow(0.0, 0.0, vinx, viny, Color.yellow);
    }  
    else {
      graph.drawPoint(0.0, 0.0, Color.yellow);
    }  

    if (Math.sqrt(voutx * voutx + vouty * vouty) !== 0) {
      graph.drawArrow(0.0, 0.0, voutx, vouty, Color.cyan);
    }  
    else {
      graph.drawPoint(0.0, 0.0, Color.cyan);
    }  

    if (eigenlinesCb.isChecked) {
      drawEigenvalues();
    }  
  }

  function drawEigenvalues() {
    var eigenbis = [];
    var minAngle, minAngleIndex, angle;
    var color, alpha;
    
    if (eigen.length === 2) {
      eigenbis[0] = new Eigen(eigen[0].val, - eigen[0].x, - eigen[0].y);
      eigenbis[1] = new Eigen(eigen[1].val, - eigen[1].x, - eigen[1].y);
       //Angle that the input vector makes with the four directions
      angle = [];
      angle[0] = isCloseToEigenvector(eigen[0]);
      angle[1] = isCloseToEigenvector(eigenbis[0]); //Opposite direction
      angle[2] = isCloseToEigenvector(eigen[1]);
      angle[3] = isCloseToEigenvector(eigenbis[1]); //Opposite direction
      minAngle = Number.MAX_VALUE;
      minAngleIndex = -1;
      for (var i = 0; i < 4; i++) {
        if (angle[i] < minAngle) {
          minAngle = angle[i];
          minAngleIndex = i;
        }
      }
      alpha = 1.0 - 4.0 * minAngle / Math.PI;
      //Draw what is needed now
      color = Color.green;
      graph.ctx.save();
      graph.ctx.globalAlpha = alpha;

      if (minAngleIndex === 0 || minAngleIndex === 1) //Highlight the closest
      {
        if (minAngle < Math.PI / 4.0) {
          //Clip line in both direction
          graph.drawLine(0.0, 0.0,
                         100.0 * eigen[0].x, 100.0 * eigen[0].y, color);
          graph.drawLine(0.0, 0.0,
                         100.0 * eigenbis[0].x, 100.0 * eigenbis[0].y, color);
        }
      }
      else {
        if (minAngle < Math.PI / 4.0) {
          graph.drawLine(0.0, 0.0,
                         100.0 * eigen[1].x, 100.0 * eigen[1].y, color);
          graph.drawLine(0.0, 0.0,
                         100.0 * eigenbis[1].x, 100.0 * eigenbis[1].y, color);
        }
      }

      graph.ctx.restore();
    } 
    else if (eigen.length === 1) {
      eigenbis[0] = new Eigen(eigen[0].val, - eigen[0].x, - eigen[0].y);
      //Angle that the input vector makes with the two directions
      angle = []; 
      angle[0] = isCloseToEigenvector(eigen[0]);
      angle[1] = isCloseToEigenvector(eigenbis[0]); //Opposite direction
      minAngle = Math.min(angle[0], angle[1]);
      alpha = 1.0 - 4.0 * minAngle / Math.PI;
      //Draw what is needed now
      color = Color.green;
      graph.ctx.save();
      graph.ctx.globalAlpha = alpha;

      if (minAngle < Math.PI / 4.0) {
        //Clip line in both direction
        graph.drawLine(0.0, 0.0, 
                       100.0 * eigen[0].x, 100.0 * eigen[0].y, color);
        graph.drawLine(0.0, 0.0,
                       100.0 * eigenbis[0].x, 100.0 * eigenbis[0].y, color);
      }

      graph.ctx.restore();
    }
  }

  //TO DO: the text labels should redraw in daimp.js when their value is changed
  function drawText() 
  {
    vinxText.text = vinx.toFixed(2);
    vinyText.text = viny.toFixed(2);
    vinxText.draw();
    vinyText.draw();

    voutxText.text = voutx.toFixed(2);
    voutyText.text = vouty.toFixed(2);
    voutxText.draw();
    voutyText.draw();

    //Around input vector (starts 20 before baseline of text)
    //TO DO: Write routine that calculates height of text.
    //tool.drawLeftBracket(508, 80, 50, Color.yellow);
    //tool.drawRightBracket(578, 80, 50, Color.yellow);

    //Around output vector
    //tool.drawLeftBracket(740, 80, 50, Color.cyan);
    //tool.drawRightBracket(810, 80, 50, Color.cyan);

    //Around matrix
    //tool.drawLeftBracket(510, 200, 85, Color.green);
    //tool.drawRightBracket(910, 200, 85, Color.green);

    //Eigenvalues and eigenvectors
    var e1Str, e1xStr, e1yStr, e2Str, e2xStr, e2yStr;

    if (eigen.length === 2) {//Two real eigenvalues
      e1Str = eigen[0].val.toFixed(2);
      e1xStr = eigen[0].x.toFixed(2);
      e1yStr = eigen[0].y.toFixed(2);
      e2Str = eigen[1].val.toFixed(2);
      e2xStr = eigen[1].x.toFixed(2);
      e2yStr = eigen[1].y.toFixed(2);

    }
    else if (eigen.length === 1) { //One double real value
      e1Str = eigen[0].val.toFixed(2);
      e1xStr = eigen[0].x.toFixed(2);
      e1yStr = eigen[0].y.toFixed(2);
      e2Str = "          ";
      e2xStr = "          ";
      e2yStr = "          ";
    }
    else {
      e1Str = "          ";
      e1xStr = "          ";
      e1yStr = "          ";
      e2Str = "          ";
      e2xStr = "          ";
      e2yStr = "          ";
    }

    eigenval1Text.text = "\u03BB_{1} = " + e1Str;
    eigenvect1xText.text = "e_{1x} = " + e1xStr;
    eigenvect1yText.text = "e_{1y} = " + e1yStr;

    eigenval2Text.text = "\u03BB_{2} = " + e2Str;
    eigenvect2xText.text = "e_{2x} = " + e2xStr;
    eigenvect2yText.text = "e_{2y} = " + e2yStr;

    if (eigenlinesCb.isChecked && eigenvectorsCb.isChecked) {
      eigenval1Text.draw();
      eigenvect1xText.draw();
      eigenvect1yText.draw();
      eigenval2Text.draw();
      eigenvect2xText.draw();
      eigenvect2yText.draw();
    }
  }
  
  return initializeTool;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));