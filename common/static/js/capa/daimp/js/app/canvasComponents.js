define(function (require) {
  //Imports
  var $ = require('jquery'),
    WebFonts = require('webfonts'),
    U = require('utils'),
    Tool = require('tool'),
    Color = require('color'),
    HSlider = require('hslider'),
    VSlider = require('vslider'),
    Label = require('label'),
    Text = require('text'),
    RichText = require('richtext'),
    TextBox = require('textbox'),
    DropDown = require('dropdown'),
    Button = require('button'),
    Component = require('component'),
    Checkbox = require('checkbox'), 
    RadioButtonGroup = require('radiobuttongroup'),
    RadioButton = require('radiobutton'),
    Graph = require('graph'),
    MiniSlider = require('minislider');

  var tool, cb, rb1, rb2, rbg, bt, hsl, vsl, gr;

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
    
    //Test checkbox
    cb = new Checkbox(50, 50, 100, 100);
    cb.text = 'Some text. An equation: x_{0} = y^{2}';
    cb.addEventListener('mousedown', function() {console.log('MD cb')});
    tool.add(cb);
    
    //Test radio buttons
    rb1 = new RadioButton(50, 100, 200, 100);
    rb1.text = 'y = x^{2}';
    rb1.isChecked = true;
    rb1.textColor = Color.green;
    rb1.addEventListener('mousedown', function() {console.log('MD rb1')});
    tool.add(rb1);
    rb2 = new RadioButton(50, 150, 100, 100);
    rb2.text = 'y = x_{0}';
    rb2.textColor = Color.cyan;
    rb2.addEventListener('mousedown', function() {console.log('MD rb2')});
    tool.add(rb2);
    rb3 = new RadioButton(50, 200, 100, 100);
    rb3.text = 'y = A_{0}cos(\u03C9t + \u03B8) + t^{2}';
    rb3.textColor = Color.yellow;
    rb3.addEventListener('mousedown', function() {console.log('MD rb3')});
    tool.add(rb3);
    
    //Test radio button group
    rbg = new RadioButtonGroup(rb1, rb2, rb3);
    
    //Test button
    bt = new Button(50, 250, 100, 25);
    bt.text = 'A button';
    bt.addEventListener('mousedown', function() {console.log('MD bt')});
    bt.addEventListener('mouseup', function() {console.log('MU bt')});
    tool.add(bt);
    
    //Test horizontal slider
    hsl = new HSlider(10, 300, 280, 50);
    hsl.addEventListener('mousedown', function() {console.log('MD hsl')});
    hsl.addEventListener('mousedrag', function() {console.log('MDR hsl')});
    hsl.addEventListener('mouseup', function() {console.log('MU hsl')});
    hsl.xmin = 0.0;
    hsl.xmax = 2.0;
    hsl.xspan = 2.0;
    hsl.setValue(1.0);
    hsl.shortTickStep = 0.5;
    hsl.longTickStep = 1.0;
    hsl.labelStep = 1.0;
    hsl.text = '\u03B8';
    hsl.textColor = Color.yellow;
    hsl.valueDecimalDigits = 2;
    hsl.automaticLabels = false;
    hsl.labels = [new Label(0.0, '0'), new Label(0.5, '\u03C0 / 2'),
                  new Label(1.5, '3\u03C0 / 2'), new Label(1.0, '\u03C0'),
                  new Label(2.0, '2\u03C0')];
    hsl.hasPI = true;
    tool.add(hsl);
    
    //Test vertical slider
    vsl = new VSlider(20, 350, 80, 280);
    vsl.addEventListener('mousedown', function() {console.log('MD vsl')});
    vsl.addEventListener('mousedrag', function() {console.log('MDR vsl')});
    vsl.addEventListener('mouseup', function() {console.log('MU vsl')});
    vsl.ymin = 0.0;
    vsl.ymax = 2.0;
    vsl.yspan = 2.0;
    vsl.setValue(1.0);
    vsl.shortTickStep = 0.1;
    vsl.longTickStep = 0.5;
    vsl.labelStep = 0.5;
    vsl.text = 'y';
    vsl.textColor = Color.cyan;
    vsl.valueDecimalDigits = 2;
    vsl.labelDecimalDigits = 1;
    tool.add(vsl);
    
    //Test textbox
    var tb = new TextBox(450, 45);
    tb.node.value = "x + 3";
    tb.node.addEventListener('change', function () {console.log('change TB');});
    tb.node.addEventListener('input', function () {console.log('input TB');});
    tool.add(tb);

    //Test dropdown
    var dd = new DropDown(450, 100);
    dd.addEventListener('change', function (x) {
      console.log('change DD ' + '(' + x.oldInd + ' -> ' + x.newInd + ')');
    });
    dd.textOptions = ["f(x) = x - 0.5x^{3} + 0.04x^{5}",
                      "f(x) = e^{x}",
                      "f(x) = log_{e}(x)",
                      "f(x) = cos(sqrt(x)), for x>=0",
                      "f(x) = 1/x",
                      "f(x) = sin(x) + 1/8 * sin(8x)",
                      "f(x) = e^{-1/x^2} for x > 0; f(x) = 0 for x <= 0"];
    dd.which =0;
    tool.add(dd);
    
    //Test graph
    gr = new Graph(410, 200, 400, 400);
    gr.setReadouts(true, true); 
    //Drag related
    gr.addEventListener('mousedown', function(mpos) {
                          console.log('Mouse down gr: ' + 
                          'x = ' + mpos.x + '; y = ' + mpos.y +
                          '; wx = ' + mpos.wx + '; wy = ' + mpos.wy);
                          graphMouseDown(mpos);});
    gr.addEventListener('mousedrag', function(mpos) {
                          console.log('Mouse drag gr: ' + 
                          'x = ' + mpos.x + '; y = ' + mpos.y +
                          '; wx = ' + mpos.wx + '; wy = ' + mpos.wy);
                          graphMouseDown(mpos);});
    gr.addEventListener('mouseup', function(mpos) {
                          console.log('Mouse up gr: ' + 
                          'x = ' + mpos.x + '; y = ' + mpos.y +
                          '; wx = ' + mpos.wx + '; wy = ' + mpos.wy);
                          graphMouseDown(mpos);});  
    //Crosshair related                      
    gr.addEventListener('mouseover', function(mpos) {
                          console.log('Mouse over gr: ' + 
                          'x = ' + mpos.x + '; y = ' + mpos.y +
                          '; wx = ' + mpos.wx + '; wy = ' + mpos.wy);
                          graphMouseOver(mpos);});                                           
    gr.addEventListener('mousemove', function(mpos) {
                          console.log('Mouse move gr: ' + 
                          'x = ' + mpos.x + '; y = ' + mpos.y +
                          '; wx = ' + mpos.wx + '; wy = ' + mpos.wy);
                          graphMouseOver(mpos);}); 
    gr.addEventListener('mouseout', function() {
                          console.log('Mouse out gr');
                          graphMouseOver();});                                            
    
    tool.add(gr);

    // Text test
    var txt = new Text(450, 650);
    txt.xway = 'special';
    txt.alignCrit = '.'; // ie anchor goes over .
    txt.yway = 'top';
    txt.text = 'click me 0.0 x_{0} = y^{2}';
    tool.add(txt);

    // MiniSlider test
    var x = txt.anchorLeft - 8;
    var y = txt.anchorTop - 1;
    var ms = new MiniSlider(x, y);
    ms.addEventListener('change', function () {
      txt.text = ms.xvalue.toFixed(1);
      txt.draw();
    });
    txt.canvas.addEventListener('mousedown', function (event) {
      ms.setVisibility(!ms.isVisible);
    });
    tool.add(ms);

    // RichText test
    var rt = new RichText(625, 650);
    rt.node.style.color = 'white';
    rt.node.style.fontStyle = 'italic';
    rt.node.innerHTML = "<span style='color:red'>Hello</span> World";
    tool.add(rt);

    //Loop through all the components that were added and draw them
    tool.draw();
    //Now draw our curve and point
    drawGraph();
  }
  
  function f(x) {
    return 10.0*Math.sin(Math.PI*x);
  }
  
  var xpos = 0.0, ypos = 0.0;
  
  //Drag related
  function graphMouseDown(mpos) {
    xpos = mpos.x;
    ypos = mpos.y;
    drawGraph();
  }
  
  //Crosshair related
  function graphMouseOver(mpos) {
    drawGraph();
  }  
  
  function drawGraph() {
    gr.draw();
    gr.drawCurve(f, -1.0, 1.0, Color.yellow);
    gr.drawDiamond(xpos, ypos, Color.green);
    gr.drawCrosshairs();
  }  
});