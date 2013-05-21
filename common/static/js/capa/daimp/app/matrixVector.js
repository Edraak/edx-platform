(function(requirejs, require, define) {
define('app/matrixVector',['require','webfonts','utils','component','tool','checkbox','hslider','vslider','text','graph','button','point','arrow','line'],function (require) {
  //Imports
  var WebFonts = require('webfonts'),
    U = require('utils'),
    Component = require('component'),
    Tool = require('tool'),
    Checkbox = require('checkbox'),
    HSlider = require('hslider'),
    VSlider = require('vslider'),
    Text = require('text'),
    Graph = require('graph'),
    Button = require('button'),
    Point = require('point'),
    Arrow = require('arrow'),
    Line = require('line');
  //UI
  var tool,
    graph,
    vinxSlider, vinySlider, rSlider, thetaSlider, a11Slider, a12Slider,
    a21Slider, a22Slider,
    eigenlinesCb, eigenvectorsCb,
    vinTitle, vinLabel, vinxText, vinyText, voutTitle, voutLabel, voutxText, 
    voutyText,
    eigenval1Text, eigenvect1xText, eigenvect1yText, eigenval2Text, 
    eigenvect2xText, eigenvect2yText,
    matrixLabel,
    //Brackets surround vectors and matrix
    vinLB, vinRB, voutLB, voutRB, matLB, matRB;
  //Shapes on graph
  var vinArrow, vinPoint, voutArrow, eigenLine1, eigenLine2;

  //State variables
  var vinx = 1.0,
    viny = 1.0,
    a11 = 1.0,
    a12 = 1.0,
    a21 = 1.0,
    a22 = 0.0;
  var    
    voutx,
    vouty,
    r,
    theta;

  var eigen;
  var inEdx = false;
  
  //For the time being, we test if we are running inside edX by testing for
  //JQuery --> Change that later on
  //In that case webfonts are available
  if (U.testForJQuery()) {
    inEdx = true;
    //Load related CSS file dynamically
    U.loadCSS('/static/css/capa/daimp/matrix-vector.css');
    initializeTool();
  }
  else {
    //Loads webfonts from Google's website then initializes the tool
    WebFonts.load(initializeTool); 
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
      var value = {'vinx': parseFloat(vinx), 'viny': parseFloat(viny),
                   'a11': parseFloat(a11), 'a12': parseFloat(a12),
                   'a21': parseFloat(a21), 'a22': parseFloat(a22)
                  };
      input_field.val(JSON.stringify(value));
    }  
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

  function initTool() {
    if (inEdx) {
      var initial_state = $('input#tool_initial_state').val();
      var saved_state = getInputField().val();
    
      //Initial state from xml file 
      if (saved_state === '') {
        initial_state = JSON.parse(initial_state);
        vinx = initial_state[0];
        viny = initial_state[1];
        a11 = initial_state[2];
        a12 = initial_state[3];
        a21 = initial_state[4];
        a22 = initial_state[5];
        //Add checkboxes state?
      }
      //Saved state
      else {
        saved_state = JSON.parse(saved_state);
        vinx = saved_state.vinx;
        viny = saved_state.viny;
        a11 = saved_state.a11;
        a12 = saved_state.a12;
        a21 = saved_state.a21;
        a22 = saved_state.a22;
        //Add checkboxes state?
      }
    }

    var toolContainer = document.getElementById('daimp-tool-container');
    tool = new Tool(toolContainer); //Default size of 818x575

    //Calculate all our variables from initially set state: vinx, viny, a11, 
    //a12, a21, a22
    r = calculateR();
    theta = calculateTheta();
    voutx = calculatevoutx();
    vouty = calculatevouty();
    eigen = getEigen();
   
    //Graph
    graph = new Graph(70, 40, 300, 300);
    graph.setPlottingBounds(-6.0, 6.0, -6.0, 6.0);
    graph.setXGrid(1.0);
    graph.setYGrid(1.0);
    graph.setXAxis(0.0);
    graph.setYAxis(0.0);
    graph.setXText('x');
    graph.setYText('y');
    tool.add(graph);
    graph.calculateBBox();
    graph.resizeBBox();
    graph.bindEvents();
    graph.addEventListener('mousedown', function(mpos) {
                          graphMouseDown(mpos);});
    graph.addEventListener('mousedrag', function(mpos) {
                          graphMouseDown(mpos);});
    graph.addEventListener('mouseup', function(mpos) {
                          graphMouseDown(mpos);});  

    //Sliders
    //x slider
    vinxSlider = new HSlider(70, 380, 300, 40);
    vinxSlider.setPlottingBounds(-6.0, 6.0);
    vinxSlider.setText('x', 'vinx-slider-text');
    vinxSlider.setLongTicks(1.0);
    vinxSlider.setValue(vinx, 2, 'vinx-slider-value-text');
    vinxSlider.setAutomaticLabels(1.0, 0, false);
    tool.add(vinxSlider);
    vinxSlider.calculateBBox();
    vinxSlider.resizeBBox();
    vinxSlider.bindEvents();
    vinxSlider.addEventListener("mousedown", vinxSliderMouseDown);
    vinxSlider.addEventListener("mousedrag", vinxSliderMouseDown);
    //y slider
    vinySlider = new VSlider(40, 40, 20, 300);
    vinySlider.setPlottingBounds(-6.0, 6.0);
    vinySlider.setText('y', 'viny-slider-text');
    vinySlider.setLongTicks(1.0);
    vinySlider.setValue(viny, 2, 'viny-slider-value-text');
    vinySlider.setAutomaticLabels(1.0, 0, false);
    tool.add(vinySlider);
    vinySlider.calculateBBox();
    vinySlider.resizeBBox();
    vinySlider.bindEvents();
    vinySlider.addEventListener("mousedown", vinySliderMouseDown);
    vinySlider.addEventListener("mousedrag", vinySliderMouseDown);
    //r slider
    rSlider = new HSlider(70, 450, 200, 40);
    rSlider.setPlottingBounds(0.0, 8.0);
    rSlider.setText('r', 'r-slider-text');
    rSlider.setLongTicks(1.0);
    rSlider.setValue(r, 2, 'r-slider-value-text');
    rSlider.setAutomaticLabels(1.0, 0, false);
    tool.add(rSlider);
    rSlider.calculateBBox();
    rSlider.resizeBBox();
    rSlider.bindEvents();
    rSlider.addEventListener("mousedown", rSliderMouseDown);
    rSlider.addEventListener("mousedrag", rSliderMouseDown);
    
    //theta slider
    thetaSlider = new HSlider(70, 500, 200, 40);
    thetaSlider.setPlottingBounds(0.0, 2.0);
    thetaSlider.setText(U.STR.theta, 'theta-slider-text');
    thetaSlider.setShortTicks(0.5);
    thetaSlider.setLongTicks(1.0);
    thetaSlider.setValue(theta, 2, 'theta-slider-value-text');
    thetaSlider.setLabels([
                           {x: 0.0, str: '0'},
                           {x: 0.5, str: U.STR.pi + '/2'},
                           {x: 1.0, str: U.STR.pi},
                           {x: 1.5, str: '3' + U.STR.pi + '/2'},
                           {x: 2.0, str: '2' + U.STR.pi}
                          ]);
    tool.add(thetaSlider);
    thetaSlider.calculateBBox();
    thetaSlider.resizeBBox();
    thetaSlider.bindEvents();
    thetaSlider.addEventListener("mousedown", thetaSliderMouseDown);
    thetaSlider.addEventListener("mousedrag", thetaSliderMouseDown);
    
    //a11 Slider
    a11Slider = new HSlider(460, 220, 120, 40);
    a11Slider.setPlottingBounds(-6.0, 6.0);
    a11Slider.setText('');
    a11Slider.setShortTicks(1.0);
    a11Slider.setLongTicks(3.0);
    a11Slider.setValue(a11, 1, 'a11-slider-value-text');
    a11Slider.setAutomaticLabels(3.0, 0, false);
    tool.add(a11Slider);
    a11Slider.calculateBBox();
    a11Slider.resizeBBox();
    a11Slider.bindEvents();
    a11Slider.addEventListener("mousedown", a11SliderMouseDown);
    a11Slider.addEventListener("mousedrag", a11SliderMouseDown);
    
    //a12 Slider
    a12Slider = new HSlider(635, 220, 120, 40);
    a12Slider.setPlottingBounds(-6.0, 6.0);
    a12Slider.setText('');
    a12Slider.setShortTicks(1.0);
    a12Slider.setLongTicks(3.0);
    a12Slider.setValue(a12, 1, 'a12-slider-value-text');
    a12Slider.setAutomaticLabels(3.0, 0, false);
    tool.add(a12Slider);
    a12Slider.calculateBBox();
    a12Slider.resizeBBox();
    a12Slider.bindEvents();
    a12Slider.addEventListener("mousedown", a12SliderMouseDown);
    a12Slider.addEventListener("mousedrag", a12SliderMouseDown);
    
    //a21 Slider
    a21Slider = new HSlider(460, 270, 120, 40);
    a21Slider.setPlottingBounds(-6.0, 6.0);
    a21Slider.setText('');
    a21Slider.setShortTicks(1.0);
    a21Slider.setLongTicks(3.0);
    a21Slider.setValue(a21, 1, 'a21-slider-value-text');
    a21Slider.setAutomaticLabels(3.0, 0, false);
    tool.add(a21Slider);
    a21Slider.calculateBBox();
    a21Slider.resizeBBox();
    a21Slider.bindEvents();
    a21Slider.addEventListener("mousedown", a21SliderMouseDown);
    a21Slider.addEventListener("mousedrag", a21SliderMouseDown);

    //a22 Slider
    a22Slider = new HSlider(635, 270, 120, 40);
    a22Slider.setPlottingBounds(-6.0, 6.0);
    a22Slider.setText('');
    a22Slider.setShortTicks(1.0);
    a22Slider.setLongTicks(3.0);
    a22Slider.setValue(a22, 1, 'a22-slider-value-text');
    a22Slider.setAutomaticLabels(3.0, 0, false);
    tool.add(a22Slider);
    a22Slider.calculateBBox();
    a22Slider.resizeBBox();
    a22Slider.bindEvents();
    a22Slider.addEventListener("mousedown", a22SliderMouseDown);
    a22Slider.addEventListener("mousedrag", a22SliderMouseDown);

    //Input vector
    vinTitle = new Text(470, 55);
    vinTitle.addText('Input vector', 'text-yellow');
    tool.add(vinTitle);

    vinxText = new Text(500, 95);
    vinxText.addText('1.00', 'text-yellow');
    tool.add(vinxText);
   
    vinyText = new Text(500, 125);
    vinyText.addText('1.00', 'text-yellow');
    tool.add(vinyText);

    vinLabel = new Text(450, 110);
    vinLabel.addText('v = ', 'text-yellow');
    tool.add(vinLabel);

    //Output vector
    voutTitle = new Text(665, 55);
    voutTitle.addText('Output vector', 'text-cyan');
    tool.add(voutTitle);

    voutxText = new Text(700, 95);
    voutxText.addText('2.00', 'text-cyan');
    tool.add(voutxText);
    
    voutyText = new Text(700, 125);
    voutyText.addText('1.00', 'text-cyan');
    tool.add(voutyText);

    voutLabel = new Text(640, 110);
    voutLabel.addText('Av = ', 'text-cyan');
    tool.add(voutLabel);

    //Matrix label
    matrixLabel = new Text(408, 245);
    matrixLabel.addText('A = ', 'text-green');
    tool.add(matrixLabel);
  
    //Eigenvalues checkbox
    eigenlinesCb = new Checkbox(465, 375, 12, 12);
    eigenlinesCb.setFrontSquareClass('eigenlines-checkbox-front-square');
    eigenlinesCb.addText('Eigenlines', 'eigenlines-checkbox-label');
    tool.add(eigenlinesCb);
    eigenlinesCb.calculateBBox();
    eigenlinesCb.bindEvents();
    eigenlinesCb.addEventListener('mousedown', checkboxMouseDown);

    //Eigenvectors checkbox
    eigenvectorsCb = new Checkbox(465, 415, 12, 12);
    eigenvectorsCb.setFrontSquareClass('eigenvectors-checkbox-front-square');
    eigenvectorsCb.addText('Eigenvectors', 'eigenvectors-checkbox-label');
    eigenvectorsCb.setVisibility(false);
    tool.add(eigenvectorsCb);
    eigenvectorsCb.calculateBBox();
    eigenvectorsCb.bindEvents();
    eigenvectorsCb.addEventListener('mousedown', checkboxMouseDown);

    //Eigenvalues and eigenvectors readouts
    eigenval1Text = new Text(465, 480);
    eigenval1Text.addText(U.STR.lambda, 'text-green');
    eigenval1Text.addSubScript('1', 'text-green');
    eigenval1Text.addText(' = ', 'text-green');
    eigenval1Text.setVisibility(false);
    tool.add(eigenval1Text);

    eigenvect1xText = new Text(565, 480);
    eigenvect1xText.addText('e', 'text-green');
    eigenvect1xText.addSubScript('1x', 'text-green');
    eigenvect1xText.addText(' = ', 'text-green');
    eigenvect1xText.setVisibility(false);
    tool.add(eigenvect1xText);

    eigenvect1yText = new Text(665, 480);
    eigenvect1yText.addText('e', 'text-green');
    eigenvect1yText.addSubScript('1y', 'text-green');
    eigenvect1yText.addText(' = ', 'text-green');
    eigenvect1yText.setVisibility(false);
    tool.add(eigenvect1yText);

    eigenval2Text = new Text(465, 510);
    eigenval2Text.addText(U.STR.lambda, 'text-green');
    eigenval2Text.addSubScript('2', 'text-green');
    eigenval2Text.addText(' = ', 'text-green');
    eigenval2Text.setVisibility(false);
    tool.add(eigenval2Text);

    eigenvect2xText = new Text(565, 510);
    eigenvect2xText.addText('e', 'text-green');
    eigenvect2xText.addSubScript('2x', 'text-green');
    eigenvect2xText.addText(' = ', 'text-green');
    eigenvect2xText.setVisibility(false);
    tool.add(eigenvect2xText);

    eigenvect2yText = new Text(665, 510);
    eigenvect2yText.addText('e', 'text-green');
    eigenvect2yText.addSubScript('2y', 'text-green');
    eigenvect2yText.addText(' = ', 'text-green');
    eigenvect2yText.setVisibility(false);
    tool.add(eigenvect2yText);
    
    //Now draw our graph
    //If vectors have a length of 0, hide them and show a dot instead, having
    //the color of the input vector, yellow
    eigenLine1 = new Line(graph, -6.0, -6.0, 6.0, 6.0, 'eigenlines');
    eigenLine2 = new Line(graph, -6.0, 6.0, 6.0, -6.0, 'eigenlines');
    vinArrow = new Arrow(graph, 0, 0, vinx, viny, 'vin-arrow');
    voutArrow = new Arrow(graph, 0, 0, voutx, vouty, 'vout-arrow');
    vinPoint = new Point(graph, 0.0, 0.0, 3, 'vin-point');
    vinPoint.setVisibility(false);
    
    graph.bBoxToFront();
    updateGraph();

    //Add brackets
    //vin
    addLeftBracket(480, 80, 50, 'vin-bracket');
    addRightBracket(550, 80, 50, 'vin-bracket');
    //vout
    addLeftBracket(680, 80, 50, 'vout-bracket');
    addRightBracket(750, 80, 50, 'vout-bracket');
    //matrix A
    addLeftBracket(440, 195, 90, 'mat-a-bracket');
    addRightBracket(800, 195, 90, 'mat-a-bracket');

    updateState();
    updateText();
}

  //Put the two following routines in library if they are ever used elsewhere
  function addLeftBracket(x, y, h, cssClass) {
    var l1, l2, l3;
    l1 = U.createLine(tool.svg, x, y, x, y + h, cssClass);
    l2 = U.createLine(tool.svg, x, y, x + 6, y, cssClass);
    l3 = U.createLine(tool.svg, x, y + h, x + 6, y + h, cssClass);
  }

  function addRightBracket(x, y, h, cssClass) {
    var l1, l2, l3;
    l1 = U.createLine(tool.svg, x, y, x, y + h, cssClass);
    l2 = U.createLine(tool.svg, x, y, x - 6, y, cssClass);
    l3 = U.createLine(tool.svg, x, y + h, x - 6, y + h, cssClass);
  }

  function vinxSliderMouseDown() {
    vinx = vinxSlider.value;
    r = calculateR();
    theta = calculateTheta();
    voutx = calculatevoutx();
    vouty = calculatevouty();
    rSlider.setValue(r);
    thetaSlider.setValue(theta / Math.PI);
    updateGraph();
    updateText();
    updateState();
  }

  function vinySliderMouseDown() {
    viny = vinySlider.value;
    r = calculateR();
    theta = calculateTheta();
    voutx = calculatevoutx();
    vouty = calculatevouty();
    rSlider.setValue(r);
    thetaSlider.setValue(theta / Math.PI);
    updateGraph();
    updateText();
    updateState();
  }

  function rSliderMouseDown() {
    r = rSlider.value;
    vinx = calculatevinx();
    viny = calculateviny();
    voutx = calculatevoutx();
    vouty = calculatevouty();
    vinxSlider.setValue(vinx);
    vinySlider.setValue(viny);
    updateGraph();
    updateText();
    updateState();
  }

  function thetaSliderMouseDown() {
    theta = Math.PI * thetaSlider.value;
    vinx = calculatevinx();
    viny = calculateviny();
    voutx = calculatevoutx();
    vouty = calculatevouty();
    vinxSlider.setValue(vinx);
    vinySlider.setValue(viny);
    updateGraph();
    updateText();
    updateState();
  }

  function a11SliderMouseDown() {
    a11 = a11Slider.value;
    voutx = calculatevoutx();
    vouty = calculatevouty();
    eigen = getEigen();
    updateGraph();
    updateText();
    updateState();
  }

  function a12SliderMouseDown() {
    a12 = a12Slider.value;
    voutx = calculatevoutx();
    vouty = calculatevouty();
    eigen = getEigen();
    updateGraph();
    updateText();
    updateState();
  }

  function a21SliderMouseDown() {
    a21 = a21Slider.value;
    voutx = calculatevoutx();
    vouty = calculatevouty();
    eigen = getEigen();
    updateGraph();
    updateText();
    updateState();
  }

  function a22SliderMouseDown() {
    a22 = a22Slider.value;
    voutx = calculatevoutx();
    vouty = calculatevouty();
    eigen = getEigen();
    updateGraph();
    updateText();
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
    updateGraph();
    updateText();
    updateState();
  }
  
  function checkboxMouseDown() {
    if (eigenlinesCb.isChecked) {
      eigenvectorsCb.setVisibility(true);
    }  
    else {
      eigenvectorsCb.setChecked(false);
      eigenvectorsCb.setVisibility(false);
    }
    updateGraph(); //To draw or erase eigenlines
    updateText(); //To draw or erase eigenvalues and eigenvectors
    
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
    /*vinLB.drawLeftBracket(0, 0, 50, Color.yellow);
    vinRB.drawRightBracket(20, 0, 50, Color.yellow);
    voutLB.drawLeftBracket(0, 0, 50, Color.cyan);
    voutRB.drawRightBracket(20, 0, 50, Color.cyan);
    matLB.drawLeftBracket(0, 0, 95, Color.green);
    matRB.drawRightBracket(20, 0, 95, Color.green);*/

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
  }
  
  function updateGraph() {
    //Check to see if the vectors have length 0.
    //If so, replace the arrow head by a dot.
    vinArrow.setXY(0.0, 0.0, vinx, viny);
    voutArrow.setXY(0.0, 0.0, voutx, vouty);
    voutArrow.head.setAttribute('clip-path',
                           'url(#' + voutArrow.graph.clipPath + ')');

    if (Math.sqrt(vinx * vinx + viny * viny) !== 0.0) {
      vinArrow.setVisibility(true);
      vinPoint.setVisibility(false);
    }  
    else {
      vinArrow.setVisibility(false);
      vinPoint.setVisibility(true);
    }  

    if (Math.sqrt(voutx * voutx + vouty * vouty) !== 0) {
      voutArrow.setVisibility(true);
    }  
    else {
      voutArrow.setVisibility(false);
    }  

    if (eigenlinesCb.isChecked) {
      eigenLine1.setVisibility(true);
      eigenLine2.setVisibility(true);  
      drawEigenvalues();
    }
    else {
      eigenLine1.setVisibility(false);
      eigenLine2.setVisibility(false);
    }
  }

  function drawEigenvalues() {
    var eigenbis = [];
    var minAngle, minAngleIndex, angle;
    var alpha;
    
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

      if (minAngleIndex === 0 || minAngleIndex === 1) //Highlight the closest
      {
        if (minAngle < Math.PI / 4.0) {
          //Clip line in both direction
          eigenLine1.setXY(0.0, 0.0,
                           100.0 * eigen[0].x, 100.0 * eigen[0].y);
          eigenLine1.line.setAttribute('style', 'opacity: ' + parseFloat(alpha) + ';');
          eigenLine2.setXY(0.0, 0.0,
                           100.0 * eigenbis[0].x, 100.0 * eigenbis[0].y);
          eigenLine2.line.setAttribute('style', 'opacity: ' + parseFloat(alpha) + ';');
        }
      }
      else {
        if (minAngle < Math.PI / 4.0) {
          eigenLine1.setXY(0.0, 0.0,
                           100.0 * eigen[1].x, 100.0 * eigen[1].y);
          eigenLine1.line.setAttribute('style', 'opacity: ' + parseFloat(alpha) + ';');
          eigenLine2.setXY(0.0, 0.0,
                           100.0 * eigenbis[1].x, 100.0 * eigenbis[1].y);
          eigenLine2.line.setAttribute('style', 'opacity: ' + parseFloat(alpha) + ';');
        }
      }
    } 
    else if (eigen.length === 1) {
      eigenbis[0] = new Eigen(eigen[0].val, - eigen[0].x, - eigen[0].y);
      //Angle that the input vector makes with the two directions
      angle = []; 
      angle[0] = isCloseToEigenvector(eigen[0]);
      angle[1] = isCloseToEigenvector(eigenbis[0]); //Opposite direction
      minAngle = Math.min(angle[0], angle[1]);
      alpha = 1.0 - 4.0 * minAngle / Math.PI;

      if (minAngle < Math.PI / 4.0) {
        //Clip line in both direction
        eigenLine1.setXY(0.0, 0.0, 
                         100.0 * eigen[0].x, 100.0 * eigen[0].y);
        eigenLine1.line.setAttribute('style', 'opacity: ' + parseFloat(alpha) + ';');
        eigenLine2.setXY(0.0, 0.0,
                         100.0 * eigenbis[0].x, 100.0 * eigenbis[0].y);
        eigenLine2.line.setAttribute('style', 'opacity: ' + parseFloat(alpha) + ';');
      }
    }
  }

  function updateText() 
  {
    vinxText.setText(0, vinx.toFixed(2));
    vinyText.setText(0, viny.toFixed(2));

    voutxText.setText(0, voutx.toFixed(2));
    voutyText.setText(0, vouty.toFixed(2));

    //Eigenvalues and eigenvectors
    var e1Str, e1xStr, e1yStr, e2Str, e2xStr, e2yStr;

    if (eigen.length === 2) { //Two real eigenvalues
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
      e2Str = '';
      e2xStr = '';
      e2yStr = '';
    }
    else {
      e1Str = '';
      e1xStr = '';
      e1yStr = '';
      e2Str = '';
      e2xStr = '';
      e2yStr = '';
    }

    eigenval1Text.setText(2, ' = ' + e1Str);
    eigenvect1xText.setText(2, ' = ' + e1xStr);
    eigenvect1yText.setText(2, ' = ' + e1yStr);

    eigenval2Text.setText(2, ' = ' + e2Str);
    eigenvect2xText.setText(2, ' = ' + e2xStr);
    eigenvect2yText.setText(2, ' = ' + e2yStr);
  }
});}(RequireJS.requirejs, RequireJS.require, RequireJS.define));