(function(requirejs, require, define) {
define('utils',['require'],function (require) {
  
  var TWO_PI = 2.0 * Math.PI;
  var PI_DIV_2 = Math.PI / 2.0;
  var ONE_EIGHTY_DIV_PI = 180.0/Math.PI;
  var PI_DIV_ONE_EIGHTY = Math.PI/180.0;
  var SVG_NS = 'http://www.w3.org/2000/svg';
  var STR = {
              //Upper case Greek letters
              'Alpha': '\u0391',
              'Beta': '\u0392',
              'Gamma': '\u0393',
              'Delta': '\u0394',
              'Epsilon': '\u0395',
              'Zeta': '\u0396',
              'Eta':  '\u0397',
              'Theta':  '\u0398',
              'Iota': '\u0399',
              'Kappa': '\u039A',
              'Lambda': '\u039B',
              'Mu': '\u039C',
              'Nu': '\u039D',
              'Xi': '\u039E',
              'Omicron': '\u039F',
              'Pi': '\u03A0',
              'Rho': '\u03A1',
              'Sigma': '\u03A3',
              'Tau': '\u03A4',
              'Upsilon': '\u03A5',
              'Phi': '\u03A6',
              'Chi': '\u03A7',
              'Psi': '\u03A8',
              'Omega': '\u03A9',
              //Lower case Greek letters
              'alpha': '\u03B1',
              'beta': '\u03B2',
              'gamma': '\u03B3',
              'delta': '\u03B4',
              'epsilon': '\u03B5',
              'zeta': '\u03B6',
              'eta': '\u03B7',
              'theta': '\u03B8',
              'iota': '\u03B9',
              'kappa': '\u03BA',
              'lambda': '\u03BB',
              'mu': '\u03BC',
              'nu': '\u03BD',
              'xi': '\u03BE',
              'omicron': '\u03BF',
              'pi': '\u03C0',
              'rho': '\u03C1',
              'sigmafinal': '\u03C2',  
              'sigma': '\u03C3',
              'tau': '\u03C4',
              'upsilon': '\u03C5',
              'phi': '\u03C6',
              'phisymbol': '\u03D5',
              'chi': '\u03C7',
              'psi': '\u03C8',
              'omega': '\u03C9',
              //Symbols
              'degree': '\u00B0'
  };

  //Running index that keeps track of number of generated clip-paths for graphs
  var nbClipPath = 0;

  function degToRad(ang) {
    return PI_DIV_ONE_EIGHTY*ang;
  }
  
  function radToDeg(ang) {
    return ONE_EIGHTY_DIV_PI*ang;
  }   

  function getxPix(fx, fleft, fwidth, wleft, wwidth) {
    return Math.round(wleft + wwidth * (fx - fleft) / fwidth);
  }

  function getxFromPix(wx, wleft, wwidth, fleft, fwidth) {
    return fleft + fwidth * (wx - wleft) / wwidth;
  }

  function getyPix(fy, fbottom, fheight, wbottom, wheight) {
    return Math.round(wbottom - wheight * (fy - fbottom) / fheight);
  }

  function getyFromPix(wy, wbottom, wheight, fbottom, fheight) {
    return fbottom + fheight * (wbottom - wy) / wheight;
  }

  function log10(x) {
    return Math.log(x) / Math.LN10;
  }
  
  function createClipPath(node, x, y, width, height) {
    var clipPath = document.createElementNS(SVG_NS, 'clipPath');
    var rect = document.createElementNS(SVG_NS, 'rect');
    var uniqueID = 'graph-clip-path' + parseInt(nbClipPath, 10);
    clipPath.setAttribute('id', uniqueID);
    nbClipPath++;
    rect.setAttribute('x', x);
    rect.setAttribute('y', y);
    rect.setAttribute('width', width);
    rect.setAttribute('height', height);
    node.appendChild(clipPath);
    clipPath.appendChild(rect);
    
    return uniqueID;
  }
  
  //Drawing routines
  function createLine(node, x1, y1, x2, y2, cssClass) {
    var line = document.createElementNS(SVG_NS, 'line');
    node.appendChild(line);
    line.setAttribute('x1', x1);
    line.setAttribute('y1', y1);
    line.setAttribute('x2', x2);
    line.setAttribute('y2', y2);
    line.setAttribute('class', cssClass);
    
    return line;
  }
  
  function createRect(node, x, y, width, height, cssClass) {
    var rect = document.createElementNS(SVG_NS, 'rect');
    node.appendChild(rect);
    rect.setAttribute('x', x);
    rect.setAttribute('y', y);
    rect.setAttribute('width', width);
    rect.setAttribute('height', height);
    rect.setAttribute('class', cssClass);
    
    return rect;
  }
  
  function createCircle(node, x, y, radius, cssClass) {
    var circle = document.createElementNS(SVG_NS, 'circle');
    node.appendChild(circle);
    circle.setAttribute('cx', x);
    circle.setAttribute('cy', y);
    circle.setAttribute('r', radius);
    circle.setAttribute('class', cssClass);
    
    return circle;
  }
  
  function createPolygon(points, cssClass) {
    var polygon = document.createElementNS(SVG_NS, 'polygon');
    polygon.setAttribute('points', points.join(','));
    polygon.setAttribute('class', cssClass);
    
    return polygon;
  }
  
  function createPolyline(points, cssClass) {
    var curve = document.createElementNS(SVG_NS, 'polyline');
    curve.setAttribute('points', points.join(','));
    curve.setAttribute('class', cssClass);
    
    return curve;
  }
  
  function createText(node, x, y, str, cssClass) {
    var text = document.createElementNS(SVG_NS, 'text');
    node.appendChild(text);
    text.setAttribute('x', x);
    text.setAttribute('y', y);
    text.setAttribute('class', cssClass);
    text.textContent = str;
    
    return text;
  }
  
  function createStyledText(textNode, str) {
    var tspan = document.createElementNS(SVG_NS, 'tspan');
    tspan.textContent = str;
    textNode.appendChild(tspan);
    
    return tspan;
  }
  
  function setVisibility(node, isVisible) {
    if (isVisible) {
      node.setAttribute('visibility', 'visible');
    }
    else {
      node.setAttribute('visibility', 'hidden');
    }  
  }
  
  //Checks to see if JQuery is loaded and available (for use in edX)
  function testForJQuery() {
    return (typeof jQuery !== 'undefined');
  }
  
  //Checks to see if certain features are available and enabled:
  //Canvas
  //WebGL
  //Audio libraries
  //SVG
  function testForFeatures(testForCanvas, testForWebGL,
                           testForAudio, testForSVG) {
    var testCanvas, gl, contextNames, hasWebAudio, hasAudioData, hasSVG,
        msg1, msg2, msg3, msg4;
    msg1 = "Your browser does not support the Canvas element.";
    msg2 = "Your browser does not support WebGL," +
           "or it is not enabled by default.";
    msg3 = "Your browser does not support Web Audio API nor Audio Data API.";
    msg4 = "Your browser does not support SVG.";
    
    if (testForCanvas) {
      testCanvas = document.createElement("canvas");
      
      if (!testCanvas.getContext) {
        throw msg1;
      }
    }
    
    if (testForWebGL) {
      testCanvas = document.createElement("canvas");
      gl = null;
      contextNames = ["experimental-webgl", "webgl", "moz-webgl", "webkit-3d"];
      for (var i = 0; i < contextNames.length; i++) {
        try {
          gl = testCanvas.getContext(contextNames[i]);
          if (gl) {
            break;
          }
        }
        catch (e) {
        }
      }
      
      if (!gl) {
        throw msg2;
      }
    }
    
    if (testForAudio) {
      //Test for Web Audio API --> Webkit browsers ie Chrome & Safari
      //https://dvcs.w3.org/hg/audio/raw-file/tip/webaudio/specification.html
      //The audio object is then: new webkitAudioContext();
      hasWebAudio = !!window.webkitAudioContext;
      //Test for Audio Data API --> Firefox 4 and ulterior
      //https://wiki.mozilla.org/Audio_Data_API
      ////The audio object is then: new new Audio();
      hasAudioData = !!new Audio().mozSetup;
      
      if (!(hasWebAudio || hasAudioData)) {
        throw msg3;
      }
    }
    
    //http://stackoverflow.com/questions/654112/
    //how-do-you-detect-support-for-vml-or-svg-in-a-browser
    if (testForSVG) {
      hasSVG = !!document.createElementNS && 
               !!document.createElementNS('http://www.w3.org/2000/svg', 
               'svg').createSVGRect;
      
      if (!hasSVG) {
        throw msg4;
      }
    }
  }
  
  //Checks to see if Canvas is available and enabled.
  function testForCanvas() {
    var testCanvas = document.createElement("canvas");
    
    if (testCanvas.getContext) {
      return true;
    }
    else {
      return false;
    }
  }
  
  //Checks to see if WebGL is available and enabled.
  function testForWebGL() {
    var testCanvas = document.createElement("canvas");
    var gl = null;
    var contextNames = ["experimental-webgl", "webgl", "moz-webgl",
                        "webkit-3d"];
    for (var i = 0; i < contextNames.length; i++) {
      try {
        gl = testCanvas.getContext(contextNames[i]);
        if (gl) {
          break;
        }
      }
      catch (e) {
      }
    }

    if (gl) {
      return true;
    }
    else {
      return false;
    }
  }
  
  //Test for Web Audio API --> Webkit browsers ie Chrome & Safari
  //https://dvcs.w3.org/hg/audio/raw-file/tip/webaudio/specification.html
  //The audio object is then: new webkitAudioContext();
  function testForChromeAudio() {
    return !!window.webkitAudioContext;
  }
  
  //Test for Audio Data API --> Firefox 4 and ulterior
  //https://wiki.mozilla.org/Audio_Data_API
  ////The audio object is then: new Audio();
  function testForMozAudio() {
    return !!new Audio().mozSetup;
  }
  
  //Change function names to supportsFeature instaed of testForFeature
  function testForSVG() {
    return !!document.createElementNS && 
           !!document.createElementNS('http://www.w3.org/2000/svg', 
           "svg").createSVGRect;
  }
  
  //Check to see if we have 3D capability either with WebGL (fast) or
  //Canvas (slow).
  //If we have WebGL, we will use a WebGLRenderer. Otherwise, if we have Canvas,
  //we will use CanvasRenderer.
  function testFor3DRenderer() {
    var msg = "Your browser does not support WebGL or it is not enabled by " +
              "default. It also does not support the Canvas element.";
    
    if (!(testForWebGL() || testForCanvas())) {
      throw msg;
    }
  }
  
  function loadCSS(url) {
    //Dynamically load a style sheet
    var link = document.createElement('link'); 
    link.type = 'text/css'; 
    link.rel = 'stylesheet'; 
    link.href = url;
    document.getElementsByTagName('head')[0].appendChild(link);
  }

  ////////// PUBLIC CONSTANTS AND FUNCTIONS
  var utils = {
    //Constants
    SVG_NS: SVG_NS,
    TWO_PI: TWO_PI,
    PI_DIV_2: PI_DIV_2,
    STR: STR,
    //Functions
    degToRad: degToRad,
    radToDeg: radToDeg,
    getxPix: getxPix,
    getxFromPix: getxFromPix,
    getyPix: getyPix,
    getyFromPix: getyFromPix,
    log10: log10,
    createClipPath: createClipPath,
    createLine: createLine,
    createRect: createRect,
    createCircle: createCircle,
    createPolyline: createPolyline,
    createPolygon: createPolygon,
    createText: createText,
    createStyledText: createStyledText,
    setVisibility: setVisibility,
    testForFeatures: testForFeatures,
    testForCanvas: testForCanvas,
    testForWebGL: testForWebGL,
    testFor3DRenderer: testFor3DRenderer,
    testForSVG: testForSVG,
    testForJQuery: testForJQuery,
    loadCSS: loadCSS
  };

  return utils;
});
define('component',['require','utils'],function (require) {

  //Imports
  var U = require('utils');
  
  function Component(x, y, width, height) {
    //Default values
    //Position component at (0,0) with width and height equal to 100
    this.x = (typeof x === 'undefined') ? 0 : x;
    this.y = (typeof y === 'undefined') ? 0 : y;
    this.width = (typeof width === 'undefined') ? 100 : width;
    this.height = (typeof height === 'undefined') ? 100 : height;
    
    this.node = document.createElementNS(U.SVG_NS, 'g'); 
    //this.node.setAttribute('class', 'daimp-component');
    this.node.setAttribute('pointer-events', 'all');
    this.setPosition(x, y);
    this.eventListeners = {};
  }

  Component.prototype.setPosition = function (x, y) {
    this.x = x;
    this.y = y;
    this.node.setAttribute('transform',
                           'translate(' +
                           parseInt(this.x, 10) + ',' +
                           parseInt(this.y, 10) + ')');
  };
  
  //Change this later on
  Component.prototype.setPosRot = function (trans) {
    this.node.setAttribute('transform', trans);
  };
  
  Component.prototype.setSize = function (width, height) {
    this.width = width;
    this.height = height;
  };
  
  //A combination of the two previous functions
  Component.prototype.setBounds = function (x, y, width, height) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
    this.setSize();
    this.setPosition();
  };
  
  Component.prototype.calculateBBox = function () {
    var nodeBBox = this.node.getBBox();
    this.bBox = document.createElementNS(U.SVG_NS, 'rect');
    this.bBox.setAttribute('class', 'bBox');
    this.bBox.setAttribute('x', nodeBBox.x);
    this.bBox.setAttribute('y', nodeBBox.y);
    this.bBox.setAttribute('width', nodeBBox.width);
    this.bBox.setAttribute('height', nodeBBox.height);
    this.node.appendChild(this.bBox);
  };
  
  Component.prototype.toBack = function () {
  };
  
  Component.prototype.toFront = function () {
  };

  Component.prototype.setVisibility = function(bool) {
    this.isVisible = bool;
    
    if (this.isVisible) {
      this.node.setAttribute('visibility', 'visible');
    }
    else {
      this.node.setAttribute('visibility', 'hidden');
    }  
  };
  
  Component.prototype.addEventListener = function (type, eventListener) {
    if (!(type in this.eventListeners)) {
      this.eventListeners[type] = eventListener;
    }
  };

  Component.prototype.removeEventListener = function (type) {
    if (type in this.eventListeners) {
      delete this.eventListeners[type];
    }
  };

  Component.prototype.fireEvent = function (event, parameters) {
    if (typeof event === "string") {
      if (this.eventListeners[event] !== undefined) {
        (this.eventListeners[event])(parameters);
      }
    } else {
      throw new Error("Event object missing 'type' property.");
    }
  };
  
  //Slightly modified http://www.javascripter.net/faq/eventpreventdefault.htm
  //The event that gets here is already either an event or window.event
  Component.prototype.cancelDefaultAction = function (event) {
    if (event.preventDefault) { //FF
      event.preventDefault();
    }
    event.returnValue = false; //IE
    return false;
  };

  //This will get the mouse coordinates on the bounding box attached to every
  //component.
  Component.prototype.getMousePosition = function (event) {
    event = event || window.event;
    
    //Might be useful later on, keep for the moment
    /*var paddingLeft = window.getComputedStyle(this.bBox, null).getPropertyValue('padding-left');
    var borderLeftWidth =  window.getComputedStyle(this.bBox, null).getPropertyValue('border-left-width');
    var paddingTop = window.getComputedStyle(this.bBox, null).getPropertyValue('padding-top');
    var borderTopWidth =  window.getComputedStyle(this.bBox, null).getPropertyValue('border-top-width');*/

    
    //The following works in recent versions of Chrome and Firefox
    //But there is a bug in Safari:
    //https://bugs.webkit.org/show_bug.cgi?id=96361
    //https://bugs.webkit.org/show_bug.cgi?id=27183
    //http://stackoverflow.com/questions/4850821/svg-coordinates-with-transform-matrix
    //http://tech.groups.yahoo.com/group/svg-developers/message/55496

    /*var p = this.tool.svg.createSVGPoint();
    p.x = event.clientX; 
    p.y = event.clientY; 
    p = p.matrixTransform(this.bBox.getScreenCTM().inverse());
    return {
      x: p.x,
      y: p.y
    };*/
    
    //Get position of bBox node in viewport coordinates
    var bcRect = this.bBox.getBoundingClientRect();
    p = this.tool.svg.createSVGPoint();
    //Get mouse click position in viewport coordinates
    p.x = event.clientX - bcRect.left;
    p.y = event.clientY - bcRect.top; 

    return {
      x: p.x,
      y: p.y
    };
  };

  return Component;
});
define('button',['require','utils','component'],function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  
  function Button(x, y, width, height) {
    //Call super class
    Component.call(this, x, y, width, height);
    
    this.isPressed = false;
    this.text = 'A button';
    
    this.background = U.createRect(this.node, 0, 0, width, height, 
                                   'button-background');
    this.leftBorder = U.createLine(this.node, 0, height, 0, 0, 
                                   'button-light-border');
    this.topBorder = U.createLine(this.node, 0, 0, width, 0,
                                  'button-light-border');
    this.rightBorder = U.createLine(this.node, width, 0, width, height, 
                                    'button-dark-border');
    this.bottomBorder = U.createLine(this.node, width, height, 0, height,  
                                     'button-dark-border');
    
    this.xt = width/2;
    this.yt = height/2; 
    this.label = U.createText(this.node,
                              this.xt, this.yt + 4,
                              this.text, 'button-label');
    this.label.setAttribute('text-anchor', 'middle');
  }
  //Inheritance
  Button.prototype = Object.create(Component.prototype);
  
  Button.prototype.bindEvents = function() {
    //Bind mouseDown, mouseUp to the correct context
    //Otherwise 'this' in mouseDown, mouseUp would refer to
    //the source of the event, the canvas
    this.mouseDown = this.mouseDown.bind(this);
    this.mouseUp = this.mouseUp.bind(this);
    //Register the click that will check/uncheck the checkbox
    this.bBox.addEventListener('mousedown', this.mouseDown, false);
    //mouseup is attached later, on the mousedown
  };
  
  Button.prototype.mouseDown = function (event) {
    this.isPressed = true;
    
    this.leftBorder.setAttribute('class', 'button-dark-border');
    this.topBorder.setAttribute('class', 'button-dark-border');
    this.rightBorder.setAttribute('class', 'button-light-border');
    this.bottomBorder.setAttribute('class', 'button-light-border');
    this.label.setAttribute('x', this.xt + 1);
    this.label.setAttribute('y', this.yt + 4 + 1);
    
    this.fireEvent('mousedown', this);
    document.addEventListener('mouseup', this.mouseUp, false);
    this.cancelDefaultAction(event);
  };
  
  Button.prototype.mouseUp = function (event) {
    this.isPressed = false;
    
    this.leftBorder.setAttribute('class', 'button-light-border');
    this.topBorder.setAttribute('class', 'button-light-border');
    this.rightBorder.setAttribute('class', 'button-dark-border');
    this.bottomBorder.setAttribute('class', 'button-dark-border');
    this.label.setAttribute('x', this.xt);
    this.label.setAttribute('y', this.yt + 4);
    
    this.fireEvent('mouseup', this);
    //Remove the previous event listener, as it is no longer useful
    document.removeEventListener('mouseup', this.mouseUp, true);
    this.cancelDefaultAction(event);
  };

  return Button;
});
define('checkbox',['require','utils','component'],function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  
  function Checkbox(x, y, width, height) {
    //Call super class
    Component.call(this, x, y, width, height);
    
    this.isChecked = false;
    this.backSquare = U.createRect(this.node, 0, 0, 12, 12,  
                                   'checkbox-back-square');
    this.frontSquare = U.createRect(this.node, 2, 2, 8, 8, 
                                    'checkbox-front-square');
    if (this.isChecked) {
      this.frontSquare.setAttribute('visibility', 'visible');
    }
    else {
      this.frontSquare.setAttribute('visibility', 'hidden');
    }  

    this.tSpans = [];
      
    //Create the text node which will subsequently contain tspan elements
    this.label = U.createText(this.node, 20, 12, '', 'checkbox-label');
  }
  //Inheritance
  Checkbox.prototype = Object.create(Component.prototype);

  Checkbox.prototype.addText = function() {
    //First argument is our string
    var styledText = U.createStyledText(this.label, arguments[0]);  
    //Second argument, if it exists, is a css class
    if (arguments.length === 2) {
      styledText.setAttribute('class', arguments[1]);
    }
    this.tSpans.push(styledText);
  };

  Checkbox.prototype.setText = function(index, str) {
    this.tSpans[index].textContent = str;  
  };

  Checkbox.prototype.setClass = function(index, cssClass) {
    this.tSpans[index].setAttribute('class', cssClass);  
  };
  
  Checkbox.prototype.setFrontSquareClass = function(cssClass) {
    this.frontSquare.setAttribute('class', cssClass);
  };

  Checkbox.prototype.bindEvents = function() {
    //Bind mouseDown to the correct context
    //Otherwise 'this' in mouseDown would refer to the source of the event,
    //the canvas
    this.mouseDown = this.mouseDown.bind(this);
    //Register the click that will check/unckeck the checkbox
    this.bBox.addEventListener('mousedown', this.mouseDown, false); 
    //this.bBox.getAttribute('width')
  };

  Checkbox.prototype.setChecked = function (bool) {
    this.isChecked = bool;
    
    if (this.isChecked) {
      this.frontSquare.setAttribute('visibility', 'visible');
    }
    else {
      this.frontSquare.setAttribute('visibility', 'hidden');
    }
  };
  
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
define('point',['require'],function (require) {

  //Imports
  //var Tool = require('tool');
  var SVG_NS = 'http://www.w3.org/2000/svg';

  function Point(graph, x, y, radius, cssClass) {
    this.graph = graph;
    this.point = document.createElementNS(SVG_NS, 'circle');
    this.setXY(x, y);
    this.setRadius(radius);
    this.setClass(cssClass);
    this.graph.node.appendChild(this.point);
  };

  Point.prototype.setXY = function (x, y) {
    this.point.setAttribute('cx', this.graph.getxPix(x));
    this.point.setAttribute('cy', this.graph.getyPix(y));  
  };
  
  Point.prototype.setRadius = function (radius) {
    this.point.setAttribute('r', radius);
  };
  
  Point.prototype.setClass = function (cssClass) {
    this.point.setAttribute('class', cssClass);
  };

  Point.prototype.setVisibility = function(bool) {
    if (bool) {
      this.point.setAttribute('visibility', 'visible');
    }
    else {
      this.point.setAttribute('visibility', 'hidden');
    }  
  };

  return Point;
});
define('graph',['require','utils','component','point'],function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  var Point = require('point');
  
  function Graph(x, y, width, height) {
    //Call super class
    Component.call(this, x, y, width, height);
    
    this.xText = "x";
    this.yText = "y";

    this.xMin = -10.0;
    this.xMax = 10.0;
    this.xSpan = 10.0;
    this.yMin = -10.0;
    this.yMax = 10.0;
    this.ySpan = 10.0;

    this.x0 = 0.0;
    this.y0 = 0.0;
    this.wx0 = 0;
    this.wy0 = 0;

    this.xShortTickStep = 1.0;
    this.xShortTickMin = this.xMin;
    this.xShortTickMax = this.xMax;

    this.xLongTickStep = 2.0;
    this.xLongTickMin = this.xMin;
    this.xLongTickMax = this.xMax;

    this.xLabelStep = 2.0;
    this.xLabelMin = this.xMin;
    this.xLabelMax = this.xMax;

    this.xGridStep = 2.0;
    this.xGridMin = this.xMin;
    this.xGridMax = this.xMax;

    this.xZeroHasDecimalPoint = true;
    this.xTextXOffset = 10;
    this.xLabelYOffset = 8;
    this.xLabelDecimalDigits = 1;

    this.yShortTickStep = 1.0;
    this.yShortTickMin = this.yMin;
    this.yShortTickMax = this.yMax;

    this.yLongTickStep = 2.0;
    this.yLongTickMin = this.yMin;
    this.yLongTickMax = this.yMax;

    this.yLabelStep = 2.0;
    this.yLabelMin = this.yMin;
    this.yLabelMax = this.yMax;

    this.yGridStep = 2.0;
    this.yGridMin = this.yMin;
    this.yGridMax = this.yMax;

    this.formatYZero = true; //TO DO
    this.yTextYOffset = -10;
    this.yLabelXOffset = -10;
    this.yLabelDecimalDigits = 1;

     //Used when we have for example PI labelling on the x or y-axis
    this.hasXScale = false;
    this.xScale = 0.0;
    this.hasYScale = false;
    this.yScale = 0.0;

    this.hasxLog = false; //TODO
    this.hasyLog = false; //TODO
    this.xPowerMin = 1; //TODO
    this.xPowerMax = 5; //TODO
    this.yPowerMin = 1; //TODO
    this.yPowerMax = 5; //TODO

    //Readouts
    this.hasHCrosshair = false;
    this.hasVCrosshair = false;
    
    this.mouseInside = false;
    this.isDragging = false;
    this.isReading = false;
    this.hasReadout = false;
    
    //Creates a rectangle clipPath with an id
    //Refer to it then with attribute clip-path = 'url(#this.id)'
    this.clipPath = U.createClipPath(this.node, 0, 0, this.width, this.height);
    
    //ACTUAL CREATION OF ELEMENTS
    
    //Background
    this.drawingZone = U.createRect(this.node,
                       0, 0,
                       this.width, this.height, 
                       'graph-background');
    
    //Borders
    U.createRect(this.node,
                 0, 0,
                 this.width, this.height, 
                 'graph-borders');
  }
  //Inheritance
  Graph.prototype = Object.create(Component.prototype);
  
  //Visibility of every element of the graph
  //Everything is shown by default

  Graph.prototype.showBorder = function(show) {
    if (show) {
      this.border.setAttribute('visibility', 'visible');
    }
    else {
      this.border.setAttribute('visibility', 'hidden');
    }
  };

  Graph.prototype.showXAxis = function(show) {
    if (show) {
      this.xAxis.setAttribute('visibility', 'visible');
    }
    else {
      this.xAxis.setAttribute('visibility', 'hidden');
    }
  };

  Graph.prototype.showXText = function(show) {
    if (show) {
      this.xText.setAttribute('visibility', 'visible');
    }
    else {
      this.xText.setAttribute('visibility', 'hidden');
    }
  };

  Graph.prototype.showXGrid = function(show) {
    if (show) {
      this.xGrid.setAttribute('visibility', 'visible');
    }
    else {
      this.xGrid.setAttribute('visibility', 'hidden');
    }
  };

  Graph.prototype.showXShortTicks = function(show) {
    if (show) {
      this.xShortTicks.setAttribute('visibility', 'visible');
    }
    else {
      this.xShortTicks.setAttribute('visibility', 'hidden');
    }
  };

  Graph.prototype.showXLongTicks = function(show) {
    if (show) {
      this.xLongTicks.setAttribute('visibility', 'visible');
    }
    else {
      this.xLongTicks.setAttribute('visibility', 'hidden');
    }
  };

  Graph.prototype.showXLabels = function(show) {
    var i, len;
    if (show) {
      for (i = 0, len = this.xLabels.length; i < len; i++) {
        this.xLabels[i].setAttribute('visibility', 'visible');
      }  
    }
    else {
      for (i = 0, len = this.xLabels.length; i < len; i++) {
        this.xLabels[i].setAttribute('visibility', 'hidden');
      }  
    }
  };

  Graph.prototype.showYAxis = function(show) {
    if (show) {
      this.yAxis.setAttribute('visibility', 'visible');
    }
    else {
      this.yAxis.setAttribute('visibility', 'hidden');
    }
  };

  Graph.prototype.showYText = function(show) {
    if (show) {
      this.yText.setAttribute('visibility', 'visible');
    }
    else {
      this.yText.setAttribute('visibility', 'hidden');
    }
  };

  Graph.prototype.showYGrid = function(show) {
    if (show) {
      this.yGrid.setAttribute('visibility', 'visible');
    }
    else {
      this.yGrid.setAttribute('visibility', 'hidden');
    }
  };

  Graph.prototype.showYShortTicks = function(show) {
    if (show) {
      this.yShortTicks.setAttribute('visibility', 'visible');
    }
    else {
      this.yShortTicks.setAttribute('visibility', 'hidden');
    }
  };

  Graph.prototype.showYLongTicks = function(show) {
    if (show) {
      this.yLongTicks.setAttribute('visibility', 'visible');
    }
    else {
      this.yLongTicks.setAttribute('visibility', 'hidden');
    }
  };

  Graph.prototype.showYLabels = function(show) {
    var i, len;
    if (show) {
      for (i = 0, len = this.yLabels.length; i < len; i++) {
        this.yLabels[i].setAttribute('visibility', 'visible');
      }  
    }
    else {
      for (i = 0, len = this.yLabels.length; i < len; i++) {
        this.yLabels[i].setAttribute('visibility', 'hidden');
      }  
    }
  };

  Graph.prototype.showCrosshairs = function(showHCrosshair, showVCrosshair) {
    this.showHCrosshair(showHCrosshair);
    this.showVCrosshair(showVCrosshair);
  };

  Graph.prototype.showHCrosshair = function(showHCrosshair) {
    if (showHCrosshair) {
      this.hCrosshair.setAttribute('visibility', 'visible');
    }
    else {
      this.hCrosshair.setAttribute('visibility', 'hidden');
    }
  };

  Graph.prototype.showVCrosshair = function(showVCrosshair) {
    if (showVCrosshair) {
      this.vCrosshair.setAttribute('visibility', 'visible');
    }
    else {
      this.vCrosshair.setAttribute('visibility', 'hidden');
    }
  };

  Graph.prototype.setPlottingBounds = function (xMin, xMax, yMin, yMax) {
    this.xMin = xMin;
    this.xMax = xMax;
    this.yMin = yMin;
    this.yMax = yMax;
    this.xSpan = xMax - xMin;
    this.ySpan = yMax - yMin;
  };

  Graph.prototype.setXAxis = function (y0) {
    this.y0 = y0;
    this.wy0 = this.getyPix(this.y0);
    this.xAxis = document.createElementNS(U.SVG_NS, 'g');
    U.createLine(this.xAxis,
                 0, this.wy0,
                 this.width + 6, this.wy0,
                 'graph-axis');
    U.createLine(this.xAxis,
                 this.width + 3, this.wy0 - 3,
                 this.width + 3, this.wy0 + 3,
                 'graph-axis');
    U.createLine(this.xAxis,
                 this.width + 4, this.wy0 - 2,
                 this.width + 4, this.wy0 + 2,
                 'graph-axis');
    U.createLine(this.xAxis,
                 this.width + 5, this.wy0 - 1,
                 this.width + 5, this.wy0 + 1,
                 'graph-axis');
    this.node.appendChild(this.xAxis);
  };

  Graph.prototype.setXText = function () {
    var str;

    //Argument is: xText
    if (arguments.length === 1) {
      str = arguments[0];
    }
    //Arguments are: xTextOffset, xTextXOffset
    else if (arguments.length === 2) {
      str = arguments[0];
      this.xTextXOffset = arguments[1];
    }
    wx = this.width + this.xTextXOffset;
    wy = this.getyPix(this.y0);
    this.xText = U.createText(this.node, 
                              wx, wy,
                              str, 'graph-x-axis-text');
  };

  Graph.prototype.setXGrid = function () {
    var x;
    var wx;

    //Argument is: xGridStep
    if (arguments.length === 1) {
      this.xGridStep = arguments[0];
      this.xGridMin = this.xMin + arguments[0]; //Don't draw grid on left border
      this.xGridMax = this.xMax - arguments[0]; //Don't draw grid on right border
    }
    //Arguments are: xGridStep, xGridMin, xGridMax
    else if (arguments.length === 3) {
      this.xGridStep = arguments[0];
      this.xGridMin = arguments[1];
      this.xGridMax = arguments[2];
    }  

    this.xGrid = document.createElementNS(U.SVG_NS, 'g');
    if (this.xGridStep > 0) {
      for (x = this.xGridMin; x <= this.xGridMax; x += this.xGridStep) {
        wx = this.getxPix(x);
        if (wx > this.width) {
          wx = this.width;
        }  
        U.createLine(this.xGrid,
                     wx, this.height,
                     wx, 0,
                     'graph-grid');
      }
    }
    this.node.appendChild(this.xGrid);  
  };

  Graph.prototype.setXShortTicks = function () {
    var x;
    var wx;

    //Argument is: xShortTickStep
    if (arguments.length === 1) {
      this.xShortTickStep = arguments[0];
      this.xShortTickMin = this.xMin;
      this.xShortTickMax = this.xMax;
    }
    //Arguments are: xShortTickStep, xShortTickMin, xShortTickMax
    else if (arguments.length === 3) {
      this.xShortTickStep = arguments[0];
      this.xShortTickMin = arguments[1];
      this.xShortTickMax = arguments[2];
    }  
    this.xShortTicks = document.createElementNS(U.SVG_NS, 'g');
    if (this.xShortTickStep > 0) {
      for (x = this.xShortTickMin; x <= this.xShortTickMax;
           x += this.xShortTickStep) {
        wx = this.getxPix(x);
        if (wx > this.width) {
          wx = this.width;
        }
        U.createLine(this.xShortTicks,
                     wx, this.height,
                     wx, this.height + 2,
                     'graph-long-ticks'); 
      }
    }
    this.node.appendChild(this.xShortTicks);
  };

  Graph.prototype.setXLongTicks = function () {
    var x;
    var wx;

    //Argument is: xLongTickStep
    if (arguments.length === 1) {
      this.xLongTickStep = arguments[0];
      this.xLongTickMin = this.xMin;
      this.xLongTickMax = this.xMax;
    }
    //Arguments are: xLongTickStep, xLongTickMin, xLongTickMax
    else if (arguments.length === 3) {
      this.xLongTickStep = arguments[0];
      this.xLongTickMin = arguments[1];
      this.xLongTickMax = arguments[2];
    }
    this.xLongTicks = document.createElementNS(U.SVG_NS, 'g');
    if (this.xLongTickStep > 0) {
      for (x = this.xLongTickMin; x <= this.xLongTickMax;
           x += this.xLongTickStep) {
        wx = this.getxPix(x);
        if (wx > this.width) {
          wx = this.width;
        }
        U.createLine(this.xLongTicks,
                     wx, this.height,
                     wx, this.height + 4,
                     'graph-long-ticks'); 
      }
    }
    this.node.appendChild(this.xLongTicks);
  };

  Graph.prototype.setAutomaticXLabels = function () {
    var wx, wy;
    var str;
    
    //Argument are: xLabelStep, xLabelDecimalDigits
    if (arguments.length === 2) {
      this.xLabelStep = arguments[0];
      this.xLabelDecimalDigits = arguments[1];
      this.xLabelMin = this.xMin;
      this.xLabelMax = this.xMax;
    }
    //Argument are: xLabelStep, xLabelDecimalDigits, xZeroHasDecimalPoint
    else if (arguments.length === 3) {
      this.xLabelStep = arguments[0];
      this.xLabelDecimalDigits = arguments[1];
      this.xZeroHasDecimalPoint = arguments[2];
      this.xLabelMin = this.xMin;
      this.xLabelMax = this.xMax;
    }
    //Arguments are: xLabelStep, xLabelDecimalDigits, xZeroHasDecimalPoint,
    //xLabelMin, xLabelMax
    else if (arguments.length === 5) {
      this.xLabelStep = arguments[0];
      this.xLabelDecimalDigits = arguments[1];
      this.xZeroHasDecimalPoint = arguments[2];
      this.xLabelMin = arguments[3];
      this.xLabelMax = arguments[4];
    }
    //Arguments are: xLabelStep, xLabelDecimalDigits, xZeroHasDecimalPoint, 
    //xLabelMin, xLabelMax, xLabelYOffset
    else if (arguments.length === 6) {
      this.xLabelStep = arguments[0];
      this.xLabelDecimalDigits = arguments[1];
      this.xZeroHasDecimalPoint = arguments[2];
      this.xLabelMin = arguments[3];
      this.xLabelMax = arguments[4];
      this.xLabelYOffset = argument[5];
    }

    wy = this.height + this.xLabelYOffset;
    
    //The following doesn't work, use an array instead
    //this.xLabels = document.createElementNS(U.SVG_NS, 'g');
    this.xLabels = [];

    if (this.xLabelStep > 0.0) {
      for (x = this.xLabelMin; x <= this.xLabelMax; x += this.xLabelStep) {
        wx = this.getxPix(x);

        if (Math.abs(x) < 0.00001 && this.xZeroHasDecimalPoint) {
          str = "0";
        }  
        else {
          str = x.toFixed(this.xLabelDecimalDigits);
        }  
        this.xLabels.push(U.createText(this.node, 
                          wx, wy,
                          str, 'graph-x-axis-labels'));
      }
    }
  };

  Graph.prototype.setXLabels = function () {
    var wy;
    var str;
    var labels;
    var xLabel;
    
    //Argument is: xLabels
    if (arguments.length === 1) {
      labels = arguments[0];
    }
    //Arguments are: xLabels, xLabelYOffset;
    else if (arguments.length === 2) {
      labels = arguments[0];
      this.xLabelYOffset = arguments[1];
    }
    wy = this.height + this.xLabelYOffset;
    //The following doesn't work, use an array instead
    //this.xLabels = document.createElementNS(U.SVG_NS, 'g');
    this.xLabels = [];
    for (var i = 0, len = labels.length; i < len; i++) {
        xLabel = labels[i];
        wx = this.getxPix(xLabel.x);
        this.xLabels.push(U.createText(this.node, 
                          wx, wy,
                          xLabel.str, 'graph-x-axis-labels'));
    }
  };

  Graph.prototype.setYAxis = function (x0) {
    this.x0 = x0;
    this.wx0 = this.getxPix(this.x0);
    this.yAxis = document.createElementNS(U.SVG_NS, 'g');
    U.createLine(this.yAxis,
                 this.wx0, this.height,
                 this.wx0, -6,
                 'graph-axis');
    U.createLine(this.yAxis,
                 this.wx0 - 3, -3,
                 this.wx0 + 3, -3,
                 'graph-axis');
    U.createLine(this.yAxis,
                 this.wx0 - 2, -4,
                 this.wx0 + 2, -4,
                 'graph-axis');
    U.createLine(this.yAxis,
                 this.wx0 - 1, -5,
                 this.wx0 + 1, -5,
                 'graph-axis');
    this.node.appendChild(this.yAxis);
  };

  Graph.prototype.setYText = function () {
    var str;

    //Argument is: yText
    if (arguments.length === 1) {
      str = arguments[0];
    }
    //Arguments are: yTextOffset, yTextYOffset
    else if (arguments.length === 2) {
      str = arguments[0];
      this.yTextYOffset = arguments[1];
    }
    wx = this.getxPix(this.x0);
    wy = this.yTextYOffset;
    this.yText = U.createText(this.node, 
                              wx, wy - 3,
                              str, 'graph-y-axis-text');
  };

  Graph.prototype.setYGrid = function () {
    var y;
    var wy;

    //Argument is: yGridStep
    if (arguments.length === 1) {
      this.yGridStep = arguments[0];
      this.yGridMin = this.yMin + arguments[0]; //Don't draw grid on bottom border
      this.yGridMax = this.yMax - arguments[0]; //Don't draw grid on top border
    }
    //Arguments are: yGridStep, yGridMin, yGridMax
    else if (arguments.length === 3) {
      this.yGridStep = arguments[0];
      this.yGridMin = arguments[1];
      this.yGridMax = arguments[2];
    }  
    
    this.yGrid = document.createElementNS(U.SVG_NS, 'g');
    if (this.yGridStep > 0) {
      for (y = this.yGridMin; y <= this.yGridMax; y += this.yGridStep) {
        wy = this.getyPix(y);
        if (wy < 0) {
          wy = 0;
        }  
        U.createLine(this.yGrid,
                     0, wy,
                     this.width, wy,
                     'graph-grid');
      }
    }
    this.node.appendChild(this.yGrid);
  };

  Graph.prototype.setYShortTicks = function () {
    //Argument is: yShortTickStep
    if (arguments.length === 1) {
      this.yShortTickStep = arguments[0];
      this.yShortTickMin = this.yMin;
      this.yShortTickMax = this.yMax;
    }
    //Arguments are: yShortTickStep, yShortTickMin, yShortTickMax
    else if (arguments.length === 3) {
      this.yShortTickStep = arguments[0];
      this.yShortTickMin = arguments[1];
      this.yShortTickMax = arguments[2];
    }
    this.yShortTicks = document.createElementNS(U.SVG_NS, 'g');
    if (this.yShortTickStep > 0) {
      for (y = this.yShortTickMin; y <= this.yShortTickMax;
           y += this.yShortTickStep) {
        wy = this.getyPix(y);
        if (wy < 0) {
          wy = 0;
        }
        U.createLine(this.yShortTicks,
                     0, wy,
                     -2, wy,
                     'graph-long-ticks'); 
      }
    }
    this.node.appendChild(this.yShortTicks);
  };

  Graph.prototype.setYLongTicks = function () {
    //Argument is: yShortTickStep
    if (arguments.length === 1) {
      this.yLongTickStep = arguments[0];
      this.yLongTickMin = this.yMin;
      this.yLongTickMax = this.yMax;
    }
    //Arguments are: yShortTickStep, yShortTickMin, yShortTickMax
    else if (arguments.length === 3) {
      this.yLongTickStep = arguments[0];
      this.yLongTickMin = arguments[1];
      this.yLongTickMax = arguments[2];
    }
    this.yLongTicks = document.createElementNS(U.SVG_NS, 'g');
    if (this.yLongTickStep > 0) {
      for (y = this.yLongTickMin; y <= this.yLongTickMax;
           y += this.yLongTickStep) {
        wy = this.getyPix(y);
        if (wy < 0) {
          wy = 0;
        }
        U.createLine(this.yLongTicks,
                     0, wy,
                     -4, wy,
                     'graph-long-ticks'); 
      }
    }
    this.node.appendChild(this.yLongTicks);  
  };

  Graph.prototype.setAutomaticYLabels = function () {
    var wx; 
    var str;
    //Argument are: yLabelStep, yLabelDecimalDigits
    if (arguments.length === 2) {
      this.yLabelStep = arguments[0];
      this.yLabelDecimalDigits = arguments[1];
      this.yLabelMin = this.yMin;
      this.yLabelMax = this.yMax;
    }
    //Argument are: yLabelStep, yLabelDecimalDigits, yZeroHasDecimalPoint
    else if (arguments.length === 3) {
      this.yLabelStep = arguments[0];
      this.yLabelDecimalDigits = arguments[1];
      this.yZeroHasDecimalPoint = arguments[2];
      this.yLabelMin = this.yMin;
      this.yLabelMax = this.yMax;
    }
    //Arguments are: yLabelStep, yLabelDecimalDigits, yZeroHasDecimalPoint,
    //yLabelMin, yLabelMax
    else if (arguments.length === 5) {
      this.yLabelStep = arguments[0];
      this.yLabelDecimalDigits = arguments[1];
      this.yZeroHasDecimalPoint = arguments[2];
      this.yLabelMin = arguments[3];
      this.yLabelMax = arguments[4];
    }
    //Arguments are: yLabelStep, yLabelDecimalDigits, yZeroHasDecimalPoint, 
    //yLabelMin, yLabelMax, yLabelYOffset
    else if (arguments.length === 6) {
      this.yLabelStep = arguments[0];
      this.yLabelDecimalDigits = arguments[1];
      this.yZeroHasDecimalPoint = arguments[2];
      this.yLabelMin = arguments[3];
      this.yLabelMax = arguments[4];
      this.yLabelXOffset = argument[5];
    }
    
    wx = this.yLabelXOffset;
    //The following doesn't work, use an array instead
    //this.yLabels = document.createElementNS(U.SVG_NS, 'g');
    this.yLabels = [];

    if (this.yLabelStep > 0.0) {
      for (y = this.yLabelMin; y <= this.yLabelMax; y += this.yLabelStep) {
        wy = this.getyPix(y);

        if (Math.abs(y) < 0.00001 && this.yZeroHasDecimalPoint) {
          str = "0";
        }  
        else {
          str = y.toFixed(this.yLabelDecimalDigits);
        }  
        this.yLabels.push(U.createText(this.node, 
                          wx, wy,
                          str, 'graph-y-axis-labels'));
      }
    }
  };

  Graph.prototype.setYLabels = function () {
    var wy;
    var str;
    var labels;
    var yLabel;
    
    //Argument is: yLabels
    if (arguments.length === 1) {
      labels = arguments[0];
    }
    //Arguments are: yLabels, yLabelXOffset;
    else if (arguments.length === 2) {
      labels = arguments[0];
      this.yLabelXOffset = arguments[1];
    }
    wx = this.yLabelXOffset;
    //The following doesn't work, use an array instead
    //this.yLabels = document.createElementNS(U.SVG_NS, 'g');
    this.yLabels = [];

    for (var i = 0, len = labels.length; i < len; i++) {
      yLabel = labels[i];
      wy = this.getyPix(yLabel.y);
      this.yLabels.push(U.createText(this.node, 
                        wx, wy,
                        yLabel.str, 'graph-y-axis-labels'));
    }
  };

  Graph.prototype.setCrosshairs = function (hasHCrosshair, hasVCrosshair) {
    this.hasHCrosshair = hasHCrosshair;
    this.hasVCrosshair = hasVCrosshair;

    //Horizontal line
    if (this.hasHCrosshair) {
      //Initially, aligned with x-axis
      this.hCrosshair = U.createLine(this.node,
                                     0, 100,
                                     this.width, 100,
                                     'graph-crosshair');
      //Initially hidden
      this.showHCrosshair(false);
    }
    //Vertical line
    if (this.hasVCrosshair) {
      //Initially aligned with y-axis
      this.vCrosshair = U.createLine(this.node,
                                     100, 0,
                                     100, this.height,
                                     'graph-crosshair');
      //Initially hidden
      this.showVCrosshair(false);
    }
    this.hasReadout = hasHCrosshair || hasVCrosshair;
  };

  Graph.prototype.setXScale = function (xScale) {
    this.hasXScale = true;
    this.xScale = xScale;
  };
  
  Graph.prototype.setYScale = function (yScale) {
    this.hasYScale = true;
    this.yScale = yScale;
  };    

  Graph.prototype.getxPix = function (x) {
    return Math.round(this.width * (x - this.xMin) / this.xSpan);
  };

  Graph.prototype.getyPix = function (y) {
    return Math.round(this.height * (this.yMax - y) / this.ySpan);
  };

  Graph.prototype.getxFromPix = function (wx) {
    if (!this.hasXScale) {
      return (this.xMin + this.xSpan * wx / this.width);
    }
    else {
      return this.xScale*(this.xMin + this.xSpan * wx / this.width);
    }
  };

  Graph.prototype.getyFromPix = function (wy) {
    if (!this.hasYScale) {
      return (this.yMax - this.ySpan * wy / this.height);
    }
    else {
      return this.yScale*(this.yMax - this.ySpan * wy / this.height);
    }
  };

  Graph.prototype.inBounds = function (pt) {
    if ((0 <= pt.x) && (pt.x <= this.width) && 
        (0 <= pt.y) && (pt.y <= this.height)) {
      this.mouseInside = true;
      return true;
    }
    else {
      this.mouseInside = false;
      return false;
    }  
  };

  Graph.prototype.clipToBounds = function (pt) {
    if (pt.x < 0) {
      pt.x = 0;
    }
    else if (pt.x > this.width) {
      pt.x = this.width;
    }
    if (pt.y < 0) {
      pt.y = 0;
    }
    else if (pt.y > this.height) {
      pt.y = this.height;
    }  
  };

  //We want our bounding box to cover only the drawing area
  Graph.prototype.resizeBBox = function() {
    this.bBox.setAttribute('x', 0);
    this.bBox.setAttribute('y', 0);
    this.bBox.setAttribute('width', this.width);
    this.bBox.setAttribute('height', this.height);
  };

  //We want our bounding box to cover only the drawing area
  Graph.prototype.bBoxToFront = function() {
    this.node.appendChild(this.bBox);
  };
    
  Graph.prototype.bindEvents = function() {
    //Bind mouse events to the correct context
    //Otherwise 'this' would refer to the source of the event,
    //drawingZone rectangle
    this.mouseDown = this.mouseDown.bind(this);
    this.mouseMove = this.mouseMove.bind(this);
    this.mouseUp = this.mouseUp.bind(this);
    this.mouseOver = this.mouseOver.bind(this);
    this.mouseOut = this.mouseOut.bind(this);
    
    //Add the necessary events
    //This one is for dragging
    this.bBox.addEventListener('mousedown', this.mouseDown);
    //And this one for mouse readouts
    this.bBox.addEventListener('mouseover', this.mouseOver);
    this.bBox.addEventListener('mouseout', this.mouseOut);
      
    //These are attached later, on mousedown
    //this.canvas.addEventListener('mousemove', this.mouseMove);
    //this.canvas.addEventListener('mouseup', this.mouseUp);
    //This is attached later, on mouseover, is there is a readout
    //this.canvas.addEventListener('mouseout', this.mouseOut);
  };
  
  Graph.prototype.mouseOver = function (event) {
    event = event || window.event;
    
    //Add a mouse move event listener to track mouse readouts
    //but not during a drag that could go in and out of bBox:
    //we track drags outside of the graph
    if (!this.isDragging && (this.hasReadout)) {
      this.bBox.addEventListener('mousemove', this.mouseMove, false);
      
      mpos = this.getMousePosition(event);
      xm = this.getxFromPix(mpos.x);
      ym = this.getyFromPix(mpos.y);
      //
      if (this.hasHCrosshair) {
        //Move horizontal crosshair to mouse location
        this.hCrosshair.setAttribute('x1', 0);
        this.hCrosshair.setAttribute('y1', mpos.y);
        this.hCrosshair.setAttribute('x2', this.width);
        this.hCrosshair.setAttribute('y2', mpos.y);
        //Show it
        this.showHCrosshair(true);
      }
      if (this.hasVCrosshair) {
        //Move vertical crosshair to mouse location
        this.vCrosshair.setAttribute('x1', mpos.x);
        this.vCrosshair.setAttribute('y1', 0);
        this.vCrosshair.setAttribute('x2', mpos.x);
        this.vCrosshair.setAttribute('y2', this.height);
        //Show it
         this.showVCrosshair(true);
      }
      //Trigger mouse over event
      this.fireEvent('mouseover', {
        x: xm,
        y: ym,
        wx: mpos.x,
        wy: mpos.y
      });
    }  
  };

  Graph.prototype.mouseDown = function (event) { 
    var mpos = this.getMousePosition(event);
    event = event || window.event;
    
    if (this.hasReadout) {
      //First remove the mousemove listener that has been added
      this.bBox.removeEventListener('mousemove', this.mouseMove, true);
      //Then hide the horizontal & vertical crosshairs
      if (this.hasHCrosshair) {
        this.showHCrosshair(false);
      }
      if (this.hasVCrosshair) {
        this.showVCrosshair(false);
      }
    }  
           
    this.isDragging = true;
    var xm = this.getxFromPix(mpos.x);
    var ym = this.getyFromPix(mpos.y);
    this.fireEvent("mousedown", {
      x: xm,
      y: ym,
      wx: mpos.x,
      wy: mpos.y
    });
    //Track the mouse movement outside of the component
    document.addEventListener('mousemove', this.mouseMove, true);
    //Track if a mouse up occurs outside of the component
    document.addEventListener('mouseup', this.mouseUp, true);
    this.cancelDefaultAction(event);  
  };

  Graph.prototype.mouseMove = function (event) {
    var mpos, xm, ym;
    event = event || window.event;

    //Drag mode
    if (this.isDragging) {
      mpos = this.getMousePosition(event);
      this.clipToBounds(mpos); //As we could be dragging outside of the graph
      xm = this.getxFromPix(mpos.x);
      ym = this.getyFromPix(mpos.y);
      this.fireEvent('mousedrag', {
        x: xm,
        y: ym,
        wx: mpos.x,
        wy: mpos.y
      });
    }
    //Readout mode
    else {
      mpos = this.getMousePosition(event);
      xm = this.getxFromPix(mpos.x);
      ym = this.getyFromPix(mpos.y);
      if (this.hasHCrosshair) {
        //Move horizontal crosshair to mouse location
        this.hCrosshair.setAttribute('x1', 0);
        this.hCrosshair.setAttribute('y1', mpos.y);
        this.hCrosshair.setAttribute('x2', this.width);
        this.hCrosshair.setAttribute('y2', mpos.y);
      }
      if (this.hasVCrosshair) {
        //Move vertical crosshair to mouse location
        this.vCrosshair.setAttribute('x1', mpos.x);
        this.vCrosshair.setAttribute('y1', 0);
        this.vCrosshair.setAttribute('x2', mpos.x);
        this.vCrosshair.setAttribute('y2', this.height);
      }
      this.fireEvent('mousemove', {
        x: xm,
        y: ym,
        wx: mpos.x,
        wy: mpos.y
      });      
    }  
    this.cancelDefaultAction(event);  
  };

  Graph.prototype.mouseUp = function (event) {
    var mposini = this.getMousePosition(event);
    var mpos = this.getMousePosition(event);
    var xm, ym;
    event = event || window.event;

    //To avoid mouse up when mouse down happened on another component
    if (this.isDragging) {
      this.clipToBounds(mpos);
      xm = this.getxFromPix(mpos.x);
      ym = this.getyFromPix(mpos.y);
      this.fireEvent("mouseup", {
        x: xm,
        y: ym,
        wx: mpos.x,
        wy: mpos.y
      });
      //Remove the previous event listeners, as they are no longer useful
      document.removeEventListener('mousemove', this.mouseMove, true);
      document.removeEventListener('mouseup', this.mouseUp, true);
      this.isDragging = false;
    }  
    if (this.hasReadout && this.inBounds(mposini)) {
      
      this.bBox.addEventListener('mousemove', this.mouseMove, false);
      
      xm = this.getxFromPix(mpos.x);
      ym = this.getyFromPix(mpos.y);
      
      if (this.hasHCrosshair) {
        //Move horizontal crosshair to mouse location
        this.hCrosshair.setAttribute('x1', 0);
        this.hCrosshair.setAttribute('y1', mpos.y);
        this.hCrosshair.setAttribute('x2', this.width);
        this.hCrosshair.setAttribute('y2', mpos.y);
        //Show it
        this.showHCrosshair(true);
      }
      if (this.hasVCrosshair) {
        //Move vertical crosshair to mouse location
        this.vCrosshair.setAttribute('x1', mpos.x);
        this.vCrosshair.setAttribute('y1', 0);
        this.vCrosshair.setAttribute('x2', mpos.x);
        this.vCrosshair.setAttribute('y2', this.height);
        //Show it
        this.showVCrosshair(true);
      }

      //Trigger mouse up event
      this.fireEvent('mouseup', {
        x: xm,
        y: ym,
        wx: mpos.x,
        wy: mpos.y
      });
    }
    this.cancelDefaultAction(event);
  };
  
  Graph.prototype.mouseOut = function (event) {
    var mpos, xm, ym;
    event = event || window.event;

    if (this.hasReadout) {
      mpos = this.getMousePosition(event);
      xm = this.getxFromPix(mpos.x);
      ym = this.getyFromPix(mpos.y);
      if (this.hasHCrosshair) {
        //Hide it
        this.showHCrosshair(false);
      }
      if (this.hasVCrosshair) {
        //Hide it
         this.showVCrosshair(false);
      }
      this.bBox.removeEventListener('mousemove', this.mouseMove, true);
      //Trigger mouse out event
      this.fireEvent('mouseout', {
        x: xm,
        y: ym,
        wx: mpos.x,
        wy: mpos.y
      });
    }
  };

  return Graph;
});
define('slider',['require','utils','component'],function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  
  function Slider(x, y, width, height) {
    //Call super class
    Component.call(this, x, y, width, height);

    this.orientation = 'horizontal';
    this.min = 0.0;
    this.max = 10.0;
    this.span = 10.0;

    this.shortTickStep = 1.0;
    this.shortTickMin = this.min;
    this.shortTickMax = this.max;

    this.longTickStep = 2.0;
    this.longTickMin = this.min;
    this.longTickMax = this.max;

    this.labels = [];
    this.labelStep = 2.0;
    this.labelDecimalDigits = 1;
    this.zeroHasDecimalPoint = false;
    this.labelMin = this.min;
    this.labelMax = this.max;
    this.labelXOffset = -10; //Used in vslider
    this.labelYOffset = -10; //Used in hslider
    
    this.textXOffset = -10; //Used in hslider
    this.textYOffset = 10; //Used in vslider

    this.value = 0.0;
    this.valueDecimalDigits = 2;
    this.valueHasDegree = false;
    this.valueTextXOffset = 10; //Used in hslider
    this.valueTextYOffset = -10;  //Used in vslider

    this.mouseIsDragged = false;
    this.isInTickZone = false;
    this.isSelected = false;
    
    this.snapToTicks = false;

    this.hasScale = false;
    this.scale = 1.0;
  }
  //Inheritance
  Slider.prototype = Object.create(Component.prototype);

  //Visibility of every element of the slider
  //Everything is shown by default
  Slider.prototype.showAxis = function(show) {
    if (show) {
      this.axis.setAttribute('visibility', 'visible');
    }
    else {
      this.axis.setAttribute('visibility', 'hidden');
    }
  };
  
  Slider.prototype.showDarkTrack = function(show) {
    if (show) {
      this.darkTrack.setAttribute('visibility', 'visible');
    }
    else {
      this.darkTrack.setAttribute('visibility', 'hidden');
    }
  };
  
  Slider.prototype.showLightTrack = function(show) {
    if (show) {
      this.lightTrack.setAttribute('visibility', 'visible');
    }
    else {
      this.lightTrack.setAttribute('visibility', 'hidden');
    }
  };
  
  Slider.prototype.showKnobBody = function(show) {
    if (show) {
      this.knobLine1.setAttribute('visibility', 'visible');
      this.knobLine2.setAttribute('visibility', 'visible');
      this.knobLine3.setAttribute('visibility', 'visible');
      this.knobLine4.setAttribute('visibility', 'visible');
      this.knobLine5.setAttribute('visibility', 'visible');
    }
    else {
      this.knobLine1.setAttribute('visibility', 'hidden');
      this.knobLine2.setAttribute('visibility', 'hidden');
      this.knobLine3.setAttribute('visibility', 'hidden');
      this.knobLine4.setAttribute('visibility', 'hidden');
      this.knobLine5.setAttribute('visibility', 'hidden');
    }
  };
  
  Slider.prototype.showKnobPointer = function(show) {
    if (show) {
      this.knobPointer.setAttribute('visibility', 'visible');
    }
    else {
      this.knobPointer.setAttribute('visibility', 'hidden');
    }
  };
  
  Slider.prototype.showKnob = function(show) {
     if (show) {
      this.knob.setAttribute('visibility', 'visible');
    }
    else {
      this.knob.setAttribute('visibility', 'hidden');
    }
  };

  Slider.prototype.showLabels = function(show) {
    for (var i = 0, len = this.labels.length; i < len; i++) {
      if (show) {
        this.labels[i].setAttribute('visibility', 'visible');
      }
      else {
        this.labels[i].setAttribute('visibility', 'hidden');
      }
    }  
  };

  Slider.prototype.showText = function(show) {
     if (show) {
      this.text.setAttribute('visibility', 'visible');
    }
    else {
      this.text.setAttribute('visibility', 'hidden');
    }
  };

  Slider.prototype.showValue = function(show) {
     if (show) {
      this.valueText.setAttribute('visibility', 'visible');
    }
    else {
      this.valueText.setAttribute('visibility', 'hidden');
    }
  };

  Slider.prototype.setPlottingBounds = function (min, max) {
    this.min = min;
    this.max = max;
    this.span = this.max - this.min;
  };

  Slider.prototype.setShortTicks = function () {
    //Argument is: shortTickStep
    if (arguments.length === 1) {
      this.shortTickStep = arguments[0];
      this.shortTickMin = this.min;
      this.shortTickMax = this.max;
    }
    //Arguments are: shortTickStep, shortTickMin, shortTickMax
    else if (arguments.length === 3) {
      this.shortTickStep = arguments[0];
      this.shortTickMin = arguments[1];
      this.shortTickMax = arguments[2];
    } 
  };

  Slider.prototype.setLongTicks = function () {
    //Argument is: longTickStep
    if (arguments.length === 1) {
      this.longTickStep = arguments[0];
      this.longTickMin = this.min;
      this.longTickMax = this.max;
    }
    //Arguments are: longTickStep, longTickMin, longTickMax
    else if (arguments.length === 3) {
      this.longTickStep = arguments[0];
      this.longTickMin = arguments[1];
      this.longTickMax = arguments[2];
    }
  };

  Slider.prototype.setAutomaticLabels = function () {
    //Argument are: labelStep, labelDecimalDigits
    if (arguments.length === 2) {
      this.labelStep = arguments[0];
      this.labelDecimalDigits = arguments[1];
      this.labelMin = this.min;
      this.labelMax = this.max;
    }
    //Argument are: labelStep, labelDecimalDigits, zeroHasDecimalPoint
    else if (arguments.length === 3) {
      this.labelStep = arguments[0];
      this.labelDecimalDigits = arguments[1];
      this.zeroHasDecimalPoint = arguments[2];
      this.labelMin = this.min;
      this.labelMax = this.max;
    }
    //Arguments are: labelStep, labelDecimalDigits, zeroHasDecimalPoint,
    //labelMin, labelMax
    else if (arguments.length === 5) {
      this.labelStep = arguments[0];
      this.labelDecimalDigits = arguments[1];
      this.zeroHasDecimalPoint = arguments[2];
      this.labelMin = arguments[3];
      this.labelMax = arguments[4];
    }
    //Arguments are: labelStep, labelDecimalDigits, zeroHasDecimalPoint, 
    //labelMin, labelMax, labelXOffset or labelYOffset;
    else if (arguments.length === 6) {
      this.labelStep = arguments[0];
      this.labelDecimalDigits = arguments[1];
      this.zeroHasDecimalPoint = arguments[2];
      this.labelMin = arguments[3];
      this.labelMax = arguments[4];
      if (this.orientation === 'horizontal') {
        this.labelYOffset = arguments[5];
      }  
      else if (this.orientation === 'vertical') {
        this.labelXOffset = arguments[5];
      }
    }
  };

  Slider.prototype.clipToPlottingBounds = function (val) {
    if (val < this.min) {
      return this.min;
    }
    else if (val > this.max) {
      return this.max;
    }
    else {
      return val;
    }
  };
  
  Slider.prototype.clipToBounds = function (wval) {
    if (this.orientation === 'horizontal') {
      if (wval > this.width) {
        return this.width;
      }
      else if (wval < 0) {
        return 0;
      }
      else {
        return wval;
      } 
    }
    else { //this.orientation === 'vertical')
      if (wval > this.height) {
        return this.height;
      }
      else if (wval < 0) {
        return 0;
      }
      else {
        return wval;
      } 
    }
  };

  Slider.prototype.updateValueText = function () {
    var val, str;

    if (this.hasXScale) {
      val = this.xScale * this.value;
    }
    else {
      val = this.value;
    }  
    str = val.toFixed(this.valueDecimalDigits);
    if (this.valueHasDegree) {
      str += U.STR.degree;
    }
    this.valueText.textContent = str;
  };

  Slider.prototype.bindEvents = function() {
    //Bind events to the correct context
    //Otherwise 'this' in mouseDown would refer to the source of the event,
    //bBox rectangle
    this.mouseDown = this.mouseDown.bind(this);
    this.mouseMove = this.mouseMove.bind(this);
    this.mouseUp = this.mouseUp.bind(this);
   
    this.bBox.addEventListener('mousedown', this.mouseDown, false);
    //Mousemove and mouse up will be added on mousedown only 
  };

  Slider.prototype.mouseDown = function (event) {
    var mpos = this.getMousePosition(event);
    event = event || window.event;

    this.isSelected = true;
    this.getClickZone(mpos);
    this.getValue(mpos);
    this.updateKnobPosition();
    this.updateValueText();
    this.fireEvent('mousedown');
    //Track the mouse movement outside of the component
    document.addEventListener('mousemove', this.mouseMove, true);
    //Track if a mouse up occurs outside of the component
    document.addEventListener('mouseup', this.mouseUp, true);
    this.cancelDefaultAction(event);
  };
  
  Slider.prototype.mouseMove = function (event) {
    event = event || window.event;

    if (this.isSelected) {
      var mpos = this.getMousePosition(event);
      this.getValue(mpos);
      this.updateKnobPosition();
      this.updateValueText();
      this.fireEvent("mousedrag");
    }
    this.cancelDefaultAction(event);  
  };

  Slider.prototype.mouseUp = function (event) {
    var mpos = this.getMousePosition(event);
    event = event || window.event;
    
    //To avoid mouse up when mouse down happened on another component
    if (this.isSelected) {
      this.getValue(mpos);
      this.updateKnobPosition();
      this.updateValueText();
      this.fireEvent("mouseup");
      //Remove the previous event listeners, as they are no longer useful
      document.removeEventListener('mousemove', this.mouseMove, true);
      document.removeEventListener('mouseup', this.mouseUp, true);
    }  
    this.isSelected = false;
    this.cancelDefaultAction(event);
  };
  
  return Slider;
});
 
define('hslider',['require','utils','slider'],function (require) {

  //Imports
  var U = require('utils');
  var Slider = require('slider');
  
  function HSlider(x, y, width, height) {
    //Call super class
    Slider.call(this, x, y, width, height);

    this.orientation = 'horizontal';
    //Specific to horizontal slider
    this.wyAxis = 0;
    this.wyTrack = this.wyAxis + 5;
    this.wxValue = 0;
    
    //The following do not change and are put in constructor
    this.axis = U.createLine(this.node,
                             0, this.wyAxis,
                             this.width, this.wyAxis, 
                             'slider-axis');                            
    
    this.darkTrack = U.createLine(this.node,
                                  0, this.wyTrack,
                                  this.width, this.wyTrack, 
                                  'slider-dark-track');
    
    this.lightTrack = U.createLine(this.node,
                                   0, this.wyTrack + 2,
                                   this.width, this.wyTrack + 2, 
                                   'slider-light-track');
    
    this.knob = document.createElementNS(U.SVG_NS, 'g'); 
    this.knob.setAttribute('pointer-events', 'all');
    
    //Knob body
    this.knobLine1 = U.createLine(this.knob,
                                  this.wxValue + 1, this.wyTrack - 1,
                                  this.wxValue + 1, this.wyTrack + 4,
                                  'slider-knob-body');
    this.knobLine2 = U.createLine(this.knob,
                                  this.wxValue - 1, this.wyTrack - 1,
                                  this.wxValue - 1, this.wyTrack + 4,
                                  'slider-knob-body');
    this.knobLine3 = U.createLine(this.knob,
                                  this.wxValue, this.wyTrack - 1,
                                  this.wxValue, this.wyTrack + 4,
                                  'slider-knob-body');
    this.knobLine4 = U.createLine(this.knob,
                                  this.wxValue + 2, this.wyTrack,
                                  this.wxValue + 2, this.wyTrack + 3,
                                  'slider-knob-body');
    this.knobLine5 = U.createLine(this.knob,
                                  this.wxValue - 2, this.wyTrack,
                                  this.wxValue - 2, this.wyTrack + 3,
                                  'slider-knob-body');
    
    //Knob pointer
    this.knobPointer = U.createLine(this.knob, 
                                    this.wxValue, this.wyTrack - 3, 
                                    this.wxValue, this.wyTrack + 4, 
                                    'slider-knob-pointer');
    
    this.node.appendChild(this.knob);
  }
  //Inheritance
  HSlider.prototype = Object.create(Slider.prototype);

  HSlider.prototype.setShortTicks = function () {
    var x, wx;
    
    //Call overidden method which sets:
    //this.shortTickStep [this.shortTickMin, this.shortTickMax]
    Slider.prototype.setShortTicks.apply(this, arguments);
    
    this.shortTicks = document.createElementNS(U.SVG_NS, 'g');
    if (this.shortTickStep > 0) {
      for (x = this.shortTickMin; x <= this.shortTickMax;
           x += this.shortTickStep) {
        wx = this.getxPix(x);
        if (wx > this.width) {
          wx = this.width;
        }
        U.createLine(this.shortTicks,
                     wx, this.wyAxis,
                     wx, this.wyAxis - 2,
                     'slider-short-ticks'); 
      }
    }
    this.node.appendChild(this.shortTicks);
  };

  HSlider.prototype.setLongTicks = function () {
    var x, wx;
    
    //Call overidden method which sets:
    //this.longTickStep [this.longTickMin, this.longTickMax]
    Slider.prototype.setLongTicks.apply(this, arguments);
    
    this.longTicks = document.createElementNS(U.SVG_NS, 'g');
    if (this.longTickStep > 0) {
      for (x = this.longTickMin; x <= this.longTickMax;
           x += this.longTickStep) {
        wx = this.getxPix(x);
        if (wx > this.width) {
          wx = this.width;
        }
        U.createLine(this.longTicks,
                     wx, this.wyAxis,
                     wx, this.wyAxis - 4,
                     'slider-long-ticks'); 
      }
    }
    this.node.appendChild(this.longTicks);
  };

  HSlider.prototype.setAutomaticLabels = function () {
    var x, wx, wy, str;
    
    //Call overidden method which sets:
    //this.labelStep, this.labelDecimalDigits
    //[this.labelMin, this.labelMax, zeroHasDecimalPoint, labelYOffset]
    Slider.prototype.setAutomaticLabels.apply(this, arguments);
    
    wy = this.wyAxis + this.labelYOffset;
    //The following doesn't work, use an array instead
    //this.labels = document.createElementNS(U.SVG_NS, 'g');

    if (this.labelStep > 0.0) {
      for (x = this.labelMin; x <= this.labelMax; x += this.labelStep) {
        wx = this.getxPix(x);

        if (Math.abs(x) < 0.00001 && !this.zeroHasDecimalPoint) {
          str = "0";
        }  
        else {
          str = x.toFixed(this.labelDecimalDigits);
        }  
        this.labels.push(U.createText(this.node, 
                          wx, wy,
                          str, 'hslider-labels'));
      }
    }
  };

  HSlider.prototype.setLabels = function () {
    var wx, wy, str, lbs, lb;

    //Argument is: labels
    if (arguments.length === 1) {
      lbs = arguments[0];
    }
    //Arguments are: labels, labelYOffset;
    else if (arguments.length === 2) {
      lbs = arguments[0];
      this.labelYOffset = arguments[1];
    }
    
    wy = this.wyAxis + this.labelYOffset;
    //The following doesn't work, use an array instead
    //this.xLabels = document.createElementNS(U.SVG_NS, 'g');
    for (var i = 0, len = lbs.length; i < len; i++) {
        wx = this.getxPix(lbs[i].x);
        this.labels.push(U.createText(this.node, 
                         wx, wy,
                         lbs[i].str, 'hslider-labels'));
    }
  };

  HSlider.prototype.setText = function () {
    var str, cssClass;

    //Argument is: text
    if (arguments.length === 1) {
      str = arguments[0];
      cssClass = 'hslider-text'; //Default
    }
    //Arguments are: text, cssClass
    else if (arguments.length === 2) {
      str = arguments[0];
      cssClass = arguments[1];
    }
    //Arguments are: text, cssClass, textXOffset
    else if (arguments.length === 3) {
      str = arguments[0];
      cssClass = arguments[1];
      this.textXOffset = arguments[2];
    }
    this.text = U.createText(this.node, 
                             this.textXOffset,
                             this.wyTrack + 3,
                             str, cssClass);
  };
  
  HSlider.prototype.setValue = function () {
    var cssClass;
    //Argument is: value
    if (arguments.length === 1) {
      this.value = arguments[0];
      cssClass = 'hslider-value-text'; //Default
    }
    //Arguments are: value, valueDecimalDigits
    else if (arguments.length === 2) {
      this.value = arguments[0];
      this.valueDecimalDigits = arguments[1];
      cssClass = 'hslider-value-text'; //Default
    }
    //Arguments are: value, valueDecimalDigits, cssClass
    else if (arguments.length === 3) {
      this.value = arguments[0];
      this.valueDecimalDigits = arguments[1];
      cssClass = arguments[2];
    }
    //Arguments are: value, valueDecimalDigits, cssClass, valueHasDegree
    else if (arguments.length === 4) {
      this.value = arguments[0];
      this.valueDecimalDigits = arguments[1];
      cssClass = arguments[2];
      this.valueHasDegree = arguments[3];
    }
    //Arguments are: value, valueDecimalDigits, cssClass, valueHasDegree,
    //valueTextXOffset
    else if (arguments.length === 5) {
      this.value = arguments[0];
      this.valueDecimalDigits = arguments[1];
      cssClass = arguments[2];
      this.valueHasDegree = arguments[3];
      this.valueTextXOffset = arguments[4];
    }

    this.value = this.clipToPlottingBounds(this.value);
    
    if (typeof this.valueText === 'undefined') {
      this.valueText = U.createText(this.node, 
                                    this.width + this.valueTextXOffset,
                                    this.wyTrack + 3,
                                    '', cssClass);
    }
    this.wxValue = this.getxPix(this.value);
    this.updateKnobPosition();
    this.updateValueText(); 
  };

  HSlider.prototype.getValue = function (pt) {
    if (this.isInTickZone || this.snapToTicks) {
      this.wxValue = this.findNearestTick(pt);
    }
    else {
      this.wxValue = pt.x;
    }
    this.wxValue= this.clipToBounds(this.wxValue);
    this.value = this.getxFromPix(this.wxValue);
  };

  HSlider.prototype.getClickZone = function (pt) {
    //if (pt.y <= this.wyAxis) {
    if (pt.y <= 10) {  
      this.isInTickZone = true;
    }
    else {
      this.isInTickZone = false;
    }  
  };    
  
  HSlider.prototype.findNearestTick = function (pt) {
    var x;
    var wx;
    var wxc = pt.x;
    //Distance between wxc (mouse click position) and wx (tick position)
    var currentDist; 
    var minDist = Number.MAX_VALUE; //Min value between wxc and wx
    var step; // Step between small or large ticks
    var result;

    if (this.longTickStep > 0) { //Long ticks are visible
      step = this.longTickStep;
    }  
    if (this.shortTickStep > 0) { //Short ticks are visible
      step = this.shortTickStep;
    }  

    //Small or large ticks visible
    if (this.shortTickStep > 0 || this.longTickStep > 0) {
      for (x = this.min; x <= this.max; x += step) {
        wx = this.getxPix(x);
        currentDist = Math.abs(wxc - wx);
        if (currentDist < minDist) {
          minDist = currentDist;
          result = wx;
        }
      }
    }
    else { //No ticks are visible, return wxc
      result = wxc;
    }  

    return result;
  };

  HSlider.prototype.updateKnobPosition = function () {
    this.knob.setAttribute('transform', 'translate(' +
    parseInt(this.wxValue, 10) + ', 0)');  
  };

  HSlider.prototype.getxPix = function (x) {
    return Math.round(this.width * (x - this.min) / this.span);
  };

  HSlider.prototype.getxFromPix = function (wx) {
    return (this.min + this.span * wx / this.width);
  };

  HSlider.prototype.resizeBBox = function() {
    this.bBox.setAttribute('x', 0);
    this.bBox.setAttribute('y', -10);
    this.bBox.setAttribute('width', this.width);
    this.bBox.setAttribute('height', 20);
  };

  return HSlider;
});
define('radiobutton',['require','utils','component'],function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  
  function RadioButton(x, y, width, height) {
    //Call super class
    Component.call(this, x, y, width, height);

    this.isChecked = false;
    this.group = null; //This changes if the radio button is added to a group
    this.backCircle = U.createCircle(this.node, 0, 0, 6,  
                                     'radiobutton-back-circle');
    this.frontCircle = U.createCircle(this.node, 0, 0, 4, 
                                      'radiobutton-front-circle');
    if (this.isChecked) {
      this.frontCircle.setAttribute('visibility', 'visible');
    }
    else {
      this.frontCircle.setAttribute('visibility', 'hidden');
    }

    this.tSpans = []; 
    //Create the text node which will subsequently contain tspan elements
    this.label = U.createText(this.node, 14, 6, '', 'radiobutton-label');
  }
  //Inheritance
  RadioButton.prototype = Object.create(Component.prototype);

  RadioButton.prototype.addText = function() {
    //First argument is our string
    var styledText = U.createStyledText(this.label, arguments[0]);  
    //Second argument, if it exists, is a css class
    if (arguments.length === 2) {
      styledText.setAttribute('class', arguments[1]);
    }
    this.tSpans.push(styledText);
  };

  RadioButton.prototype.setText = function(index, str) {
    this.tSpans[index].textContent = str;  
  };

  RadioButton.prototype.setClass = function(index, cssClass) {
    this.tSpans[index].setAttribute('class', cssClass);  
  };
  
  RadioButton.prototype.setFrontCircleClass = function(cssClass) {
    this.frontCircle.setAttribute('class', cssClass);
  };
  
  RadioButton.prototype.bindEvents = function() {
    //Bind mouseDown to the correct context
    //Otherwise 'this' in mouseDown would refer to the source of the event,
    //the canvas
    this.mouseDown = this.mouseDown.bind(this);
    //Register the click that will check/unckeck the checkbox
    this.bBox.addEventListener('mousedown', this.mouseDown, false); 
    //this.bBox.getAttribute('width')
  };
  
  RadioButton.prototype.setChecked = function(isChecked) {
    this.isChecked = isChecked;
    if (isChecked) {  
      this.frontCircle.setAttribute('visibility', 'visible');
    }
    else {
      this.frontCircle.setAttribute('visibility', 'hidden');
    }
  };
  
  RadioButton.prototype.mouseDown = function (event) {
    event = event || window.event;
    
    //Unselect all the other radiobuttons of the group
    if (this.group !== null) {
      var rbs = this.group.radioButtons;
      for (var i = 0; i < rbs.length; i++) {
          rbs[i].setChecked(false);
      }
      this.setChecked(true);
    }
    else {
      this.setChecked(!this.isChecked);
    } 
    
    this.fireEvent('mousedown', this);
    this.cancelDefaultAction(event);
  };

  return RadioButton;
});
define('radiobuttongroup',['require'],function (require) {

  //The parameters are radio buttons
  function RadioButtonGroup() {
    this.radioButtons = Array.prototype.slice.call(arguments, 0);

    // give the radio buttons pointers back to the group
    for (var i = 0; i < this.radioButtons.length; i++) {
      this.radioButtons[i].group = this;
    }
  }

  RadioButtonGroup.prototype.add = function () {
    var args = Array.prototype.slice.call(arguments, 0);
    var oldLen = this.radioButtons.length;
    this.radioButtons = this.radioButtons.concat(args);

    // give the radio buttons pointers back to the group
    for (var i = oldLen; i < this.radioButtons.length; i++) {
      this.radioButtons[i].group = this;
    }
  };

  RadioButtonGroup.prototype.remove = function (radioButton) {
    for (var i = 0; i < this.radioButtons.length; i ++) {
      if (this.radioButtons[i] === radioButton) {
        this.radioButtons.splice(i, 1);
      }
    }

    radioButton.group = null;
  };

  return RadioButtonGroup;
});
define('text',['require','utils','component'],function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');
  
  function Text(x, y) {
    //Call super class
    Component.call(this, x, y);
    
    this.tSpans = [];
      
    //Create the text node which will subsequently contain tspan elements
    this.text = U.createText(this.node, 0, 0, '', 
                             'daimp-text');
  }  
  //Inheritance
  Text.prototype = Object.create(Component.prototype);

  Text.prototype.addText = function(str, cssClass) {
    var styledText = U.createStyledText(this.text, str);
    styledText.setAttribute('class', cssClass);
    //styledText.setAttribute('dx', -2);
    styledText.setAttribute('y', 0);
    this.tSpans.push(styledText);
  };

  Text.prototype.addSuperScript = function(str, cssClass) {
    var styledText = U.createStyledText(this.text, str);
    styledText.setAttribute('class', cssClass);
    //styledText.setAttribute('dx', 2);
    styledText.setAttribute('y', -5);
    this.tSpans.push(styledText);
  };

  Text.prototype.addSubScript = function(str, cssClass) {
    var styledText = U.createStyledText(this.text, str);
    styledText.setAttribute('class', cssClass);
    //styledText.setAttribute('dx', 2);
    styledText.setAttribute('y', 3);
    this.tSpans.push(styledText);
  };

  Text.prototype.setText = function(index, str) {
    this.tSpans[index].textContent = str;  
  };

  Text.prototype.setClass = function(index, cssClass) {
    this.tSpans[index].setAttribute('class', cssClass);  
  };

  return Text;
});
define('tool',['require','utils','component'],function (require) {

  //Imports
  var U = require('utils');
  var Component = require('component');

  function Tool(container, width, height) {
    //Container is the name of the div (or other element)
    //containing the svg element
    this.container = container;
    //Default values
    //The max available width when integrated in edX is 818 px
    this.width = (typeof width === 'undefined') ? 818 : width;
    this.height = (typeof height === 'undefined') ? 575 : height;
    this.svg = document.createElementNS(U.SVG_NS, 'svg');
    this.svg.setAttribute('version', '1.2');
    this.svg.setAttribute('baseProfile', 'tiny');
    this.svg.setAttribute('width', this.width);
    this.svg.setAttribute('height', this.height);
    this.container.appendChild(this.svg);
    
    this.eventListeners = {};
    this.tool = null; //This will change when component is added to tool
    //Disable text selection when clicking on div
    this.onselectstart = function () {
      return false;
    };
  }

  Tool.prototype.addEventListener = function (type, eventListener) {
    if (!(type in this.eventListeners)) {
      this.eventListeners[type] = eventListener;
    }  
  };

  Tool.prototype.removeEventListener = function (type) {
    if (type in this.eventListeners) {
      delete this.eventListeners[type];
    }
  };

  Tool.prototype.fireEvent = function (event, parameters) {
    if (typeof event === "string") {
      (this.eventListeners[event])(parameters);
    }  
    else {
      throw new Error("Event object missing 'type' property.");
    }  
  };

  Tool.prototype.add = function (comp) {
    comp.tool = this;
    this.svg.appendChild(comp.node);
    /*if (typeof comp.calculateBBox === 'function') { 
      comp.calculateBBox();
    }
    if (typeof comp.bindEvents === 'function') { 
      comp.bindEvents();
    }   */ 
    //Necessary??? this.components.push(comp);
  };
  
  Tool.prototype.remove = function (comp) {
    /*comp.tool = null;
    this.container.removeChild(comp.canvas);
    for (var i = 0; i < this.components.length; i++) {
      if (this.components[i] === comp) {
        this.components.splice(i, 1);
      }
    }*/  
  };
  
  return Tool;
});
define('vslider',['require','utils','slider'],function (require) {

  //Imports
  var U = require('utils');
  var Slider = require('slider');
  
  function VSlider(x, y, width, height) {
    //Call super class
    Slider.call(this, x, y, width, height);

    this.orientation = 'vertical';
    //Specific to horizontal slider
    this.wxAxis = 0;
    this.wxTrack = this.wxAxis + 5;
    this.wyValue = 0;
    
    //The following do not change and are put in constructor
    this.axis = U.createLine(this.node,
                             this.wxAxis, 0,
                             this.wxAxis, this.height, 
                             'slider-axis');                            
    
    this.darkTrack = U.createLine(this.node,
                                  this.wxTrack, 0,
                                  this.wxTrack, this.height, 
                                  'slider-dark-track');
    
    this.lightTrack = U.createLine(this.node,
                                   this.wxTrack + 2, 0,
                                   this.wxTrack + 2, this.height,
                                   'slider-light-track');
    
    this.knob = document.createElementNS(U.SVG_NS, 'g'); 
    this.knob.setAttribute('pointer-events', 'all');
    
    //Knob body
    this.knobLine1 = U.createLine(this.knob,
                                  this.wxTrack - 1, this.wyValue + 1,
                                  this.wxTrack + 4, this.wyValue + 1,
                                  'slider-knob-body');
    this.knobLine2 = U.createLine(this.knob,
                                  this.wxTrack - 1, this.wyValue - 1,
                                  this.wxTrack + 4, this.wyValue - 1,
                                  'slider-knob-body');
    this.knobLine3 = U.createLine(this.knob,
                                  this.wxTrack - 1, this.wyValue,
                                  this.wxTrack + 4, this.wyValue,
                                  'slider-knob-body');
    this.knobLine4 = U.createLine(this.knob,
                                  this.wxTrack, this.wyValue + 2,
                                  this.wxTrack + 3, this.wyValue + 2,
                                  'slider-knob-body');
    this.knobLine5 = U.createLine(this.knob,
                                  this.wxTrack, this.wyValue - 2,
                                  this.wxTrack + 3, this.wyValue - 2,
                                  'slider-knob-body');
    
    //Knob pointer
    this.knobPointer = U.createLine(this.knob, 
                                    this.wxTrack - 3, this.wyValue,
                                    this.wxTrack + 4, this.wyValue, 
                                    'slider-knob-pointer');
    
    this.node.appendChild(this.knob);
  }
  //Inheritance
  VSlider.prototype = Object.create(Slider.prototype);

  VSlider.prototype.setShortTicks = function () {
    var y, wy;
    
    //Call overidden method which sets:
    //this.shortTickStep [this.shortTickMin, this.shortTickMax]
    Slider.prototype.setShortTicks.apply(this, arguments);
    
    this.shortTicks = document.createElementNS(U.SVG_NS, 'g');
    if (this.shortTickStep > 0) {
      for (y = this.shortTickMin; y <= this.shortTickMax;
           y += this.shortTickStep) {
        wy = this.getyPix(y);
        if (wy < 0) {
          wy = 0;
        }
        U.createLine(this.shortTicks,
                     this.wxAxis, wy,
                     this.wxAxis - 2, wy,
                     'slider-short-ticks'); 
      }
    }
    this.node.appendChild(this.shortTicks);
  };

  VSlider.prototype.setLongTicks = function () {
    var y, wy;
    
    //Call overidden method which sets:
    //this.longTickStep [this.longTickMin, this.longTickMax]
    Slider.prototype.setLongTicks.apply(this, arguments);
    
    this.longTicks = document.createElementNS(U.SVG_NS, 'g');
    if (this.longTickStep > 0) {
      for (y = this.longTickMin; y <= this.longTickMax;
           y += this.longTickStep) {
        wy = this.getyPix(y);
        if (wy < 0) {
          wy = 0;
        }
        U.createLine(this.longTicks,
                     this.wxAxis, wy,
                     this.wxAxis - 4, wy,
                     'slider-long-ticks'); 
      }
    }
    this.node.appendChild(this.longTicks);
  };

  VSlider.prototype.setAutomaticLabels = function () {
    var y, wx, wy, str;
    
    //Call overidden method which sets:
    //this.labelStep, this.labelDecimalDigits
    //[this.labelMin, this.labelMax, zeroHasDecimalPoint, labelYOffset]
    Slider.prototype.setAutomaticLabels.apply(this, arguments);
    
    wx = this.wxAxis + this.labelXOffset;
    //The following doesn't work, use an array instead
    //this.labels = document.createElementNS(U.SVG_NS, 'g');

    if (this.labelStep > 0.0) {
      for (y = this.labelMin; y <= this.labelMax; y += this.labelStep) {
        wy = this.getyPix(y);

        if (Math.abs(y) < 0.00001 && !this.zeroHasDecimalPoint) {
          str = "0";
        }  
        else {
          str = y.toFixed(this.labelDecimalDigits);
        }  
        this.labels.push(U.createText(this.node, 
                          wx, wy,
                          str, 'vslider-labels'));
      }
    }
  };

  VSlider.prototype.setLabels = function () {
    var wx, wy, str, lbs, lb;

    //Argument is: labels
    if (arguments.length === 1) {
      lbs = arguments[0];
    }
    //Arguments are: labels, labelYOffset;
    else if (arguments.length === 2) {
      lbs = arguments[0];
      this.labelXOffset = arguments[1];
    }
    
    wx = this.wxAxis + this.labelYOffset;
    //The following doesn't work, use an array instead
    //this.xLabels = document.createElementNS(U.SVG_NS, 'g');
    for (var i = 0, len = lbs.length; i < len; i++) {
        wy = this.getyPix(lbs[i].y);
        this.labels.push(U.createText(this.node, 
                         wx, wy,
                         lbs[i].str, 'vslider-labels'));
    }
  };

  VSlider.prototype.setText = function () {
    var str, cssClass;

    //Argument is: text
    if (arguments.length === 1) {
      str = arguments[0];
      cssClass = 'vslider-text'; //Default
    }
    //Arguments are: text, cssClass
    else if (arguments.length === 2) {
      str = arguments[0];
      cssClass = arguments[1];
    }
    //Arguments are: text, cssClass, textXOffset
    else if (arguments.length === 3) {
      str = arguments[0];
      cssClass = arguments[1];
      this.textYOffset = arguments[2];
    }
    this.text = U.createText(this.node, 
                             this.wxTrack,
                             this.height + this.textYOffset,
                             str, cssClass);
  };
  
  VSlider.prototype.setValue = function () {
    var cssClass;
    //Argument is: value
    if (arguments.length === 1) {
      this.value = arguments[0];
      cssClass = 'vslider-value-text'; //Default
    }
    //Arguments are: value, valueDecimalDigits
    else if (arguments.length === 2) {
      this.value = arguments[0];
      this.valueDecimalDigits = arguments[1];
      cssClass = 'vslider-value-text'; //Default
    }
    //Arguments are: value, valueDecimalDigits, cssClass
    else if (arguments.length === 3) {
      this.value = arguments[0];
      this.valueDecimalDigits = arguments[1];
      cssClass = arguments[2];
    }
    //Arguments are: value, valueDecimalDigits, cssClass, valueHasDegree
    else if (arguments.length === 4) {
      this.value = arguments[0];
      this.valueDecimalDigits = arguments[1];
      cssClass = arguments[2];
      this.valueHasDegree = arguments[3];
    }
    //Arguments are: value, valueDecimalDigits, cssClass, valueHasDegree,
    //valueTextYOffset
    else if (arguments.length === 5) {
      this.value = arguments[0];
      this.valueDecimalDigits = arguments[1];
      cssClass = arguments[2];
      this.valueHasDegree = arguments[3];
      this.valueTextYOffset = arguments[4];
    }

    this.value = this.clipToPlottingBounds(this.value);

    if (typeof this.valueText === 'undefined') {
      this.valueText = U.createText(this.node,
                                    this.wxTrack, 
                                    this.valueTextYOffset,
                                    '', cssClass);
    }
    this.wyValue = this.getyPix(this.value);
    this.updateKnobPosition();
    this.updateValueText(); 
  };

  VSlider.prototype.getValue = function (pt) {
    if (this.isInTickZone || this.snapToTicks) {
      this.wyValue = this.findNearestTick(pt);
    }
    else {
      this.wyValue = pt.y;
    }
    this.wyValue= this.clipToBounds(this.wyValue);
    this.value = this.getyFromPix(this.wyValue);
  };
  //TO CHECK
  VSlider.prototype.getClickZone = function (pt) {
    //if (pt.y <= this.wyAxis) {
    if (pt.x <= 10) {  
      this.isInTickZone = true;
    }
    else {
      this.isInTickZone = false;
    }  
  };    
  
  VSlider.prototype.findNearestTick = function (pt) {
    var y;
    var wy;
    var wyc = pt.y;
    //Distance between wxc (mouse click position) and wx (tick position)
    var currentDist; 
    var minDist = Number.MAX_VALUE; //Min value between wxc and wx
    var step; // Step between small or large ticks
    var result;

    if (this.longTickStep > 0) { //Long ticks are visible
      step = this.longTickStep;
    }  
    if (this.shortTickStep > 0) { //Short ticks are visible
      step = this.shortTickStep;
    }  

    //Small or large ticks visible
    if (this.shortTickStep > 0 || this.longTickStep > 0) {
      for (y = this.min; y <= this.max; y += step) {
        wy = this.getyPix(y);
        currentDist = Math.abs(wyc - wy);
        if (currentDist < minDist) {
          minDist = currentDist;
          result = wy;
        }
      }
    }
    else { //No ticks are visible, return wxc
      result = wyc;
    }  

    return result;
  };

  VSlider.prototype.updateKnobPosition = function () {
    this.knob.setAttribute('transform', 'translate(0,' +
    parseInt(this.wyValue, 10) + ')');  
  };

  VSlider.prototype.getyPix = function (y) {
    return Math.round(this.height * (this.max - y) / this.span);
  };

  VSlider.prototype.getyFromPix = function (wy) {
    return (this.max - this.span * wy / this.height);
  };

  Slider.prototype.resizeBBox = function() {
    this.bBox.setAttribute('x', -10);
    this.bBox.setAttribute('y', 0);
    this.bBox.setAttribute('width', 20);
    this.bBox.setAttribute('height', this.height);
  };

  return VSlider;
});
define('webfonts',[],function () {  
  //##### Loads and uses WebFonts #####
  //WebFont Loader: https://developers.google.com/webfonts/docs/webfont_loader
  //active is called when the fonts are loaded. We then initialize the tool.
  //When integrated in edX, Open Sans will be available and this won't be 
  //necessary. 
  function load(callback)
  {
    if (navigator.onLine) {
      //Global variable needed by following webfont.js
      WebFontConfig = {
        //Normal & bold Open Sans font
        google: {families: ['Open+Sans:400,700:latin,greek']},
                //Without the timeout,
                //Chrome would sometime draw the tool with no text.
                //A timeout too low fails quite often
                active: function() {setTimeout(callback, 25);}
      }; 
    
      //Loads the script dynamically. Would be better if this happened earlier
      var wf = document.createElement('script');
      wf.src = ('https:' === document.location.protocol ? 'https' : 'http') +
              '://ajax.googleapis.com/ajax/libs/webfont/1/webfont.js';
      wf.type = 'text/javascript';
      wf.async = 'true';
      var s = document.getElementsByTagName('script')[0];
      s.parentNode.insertBefore(wf, s);
    }
    //Don't block initialization of tool if not online. Use default fonts.
    //Doesn't work on Firefox if File > Work offline not checked
    //TO DO: Would be nice to have the Open Sans fonts locally
    else {
      callback();
    }   
  }
  
  return {load: load};
});
define('arc',['require','utils'],function (require) {

  //Imports
  var U = require('utils');
                                      
  function Arc(graph, xc, yc, radius, startAngle, endAngle, inDegrees,
              clockwise, cssClass) {
    this.graph = graph;
    this.xc = xc;
    this.yc = yc;
    this.radius = radius;
    this.inDegrees = inDegrees;
    this.clockwise = clockwise;
    this.convertAngles(startAngle, endAngle);
    this.arc = document.createElementNS(U.SVG_NS, 'path');
    this.setdAttribute();
    //this.setTransform();
    this.setClass(cssClass);
    this.graph.node.appendChild(this.arc);
  }

  Arc.prototype.convertAngles = function (startAngle, endAngle) {
    if (this.inDegrees) {
      this.startAngle = U.degToRad(startAngle);
      this.endAngle = U.degToRad(endAngle);
    }
    else {
      this.startAngle = startAngle;
      this.endAngle = endAngle;
    }
  };

  Arc.prototype.setXY = function (xc, yc) {
    this.xc = xc;
    this.yc = yc;
    this.setTransform();
  };

  Arc.prototype.setAngles = function (startAngle, endAngle, clockwise) {
    var startAngle, endAngle;
    //Arguments are: startAngle, endAngle
    if (arguments.length === 2) {
      startAngle = arguments[0];
      endAngle = arguments[1];
    }
    else if (arguments.length === 3) {
      startAngle = arguments[0];
      endAngle = arguments[1];
      this.clockwise = arguments[2];
    }  
    this.convertAngles(startAngle, endAngle);
    this.setdAttribute();
  };

  Arc.prototype.setRadius = function (radius) {
    this.radius = radius;
    this.setdAttribute();
  };

  /*Arc.prototype.setTransform = function () {
    this.arc.setAttribute('transform',
                          'translate(' +
                          parseInt(this.graph.getxPix(this.xc)) + ',' +
                          parseInt(this.graph.getyPix(this.yc)) + ')'
                          );
  };*/

  Arc.prototype.setdAttribute = function () {
    var wxs, wys, wxe, wye;
    var largeArcFlag, sweepFlag;
    var dAngle;
    var str;
    
    //Creates an arc of radius this.radius centered on origin

    //Get start point
    wxs = this.graph.getxPix(this.xc) +
          Math.round(this.radius * Math.cos(this.startAngle));
    wys = this.graph.getyPix(this.yc) -
          Math.round(this.radius * Math.sin(this.startAngle));
    //Get end point
    wxe = this.graph.getxPix(this.xc) + 
          Math.round(this.radius * Math.cos(this.endAngle));
    wye = this.graph.getyPix(this.yc) -
          Math.round(this.radius * Math.sin(this.endAngle));

    dAngle = this.endAngle - this.startAngle;

    if (this.clockwise) {
      if (dAngle < Math.PI) {
        //Connect start point to end point using an arc > 180 degrees
        largeArcFlag = '1,';
        //Clockwise
        sweepFlag = '1,';
      }
      else {
        //Connect start point to end point using an arc < 180 degrees
        largeArcFlag = '0,';
        //Clockwise
        sweepFlag = '1,';
      }
    }
    else {
      if (dAngle < Math.PI) {
        //Connect start point to end point using an arc < 180 degrees
        largeArcFlag = '0,';
        //Anti-clockwise
        sweepFlag = '0,'; 
      }
      else {
        //Connect start point to end point using an arc > 180 degrees
        largeArcFlag = '1,';
        //Anti-clockwise
        sweepFlag = '0,'; 
      }
    }
    str = '0,' + largeArcFlag + sweepFlag;
    
    this.arc.setAttribute('d', 
                          'M ' +
                          parseInt(wxs) + ',' +
                          parseInt(wys) + //Breaks in Firefox if ',' +
                          'A ' +
                          parseInt(this.radius) + ',' +
                          parseInt(this.radius) + ',' +
                          str +
                          parseInt(wxe) + ',' +
                          parseInt(wye)
                          );
  };
  
  Arc.prototype.setClass = function (cssClass) {
    this.arc.setAttribute('class', cssClass);
  };

  Arc.prototype.setVisibility = function(bool) {
    if (bool) {
      this.arc.setAttribute('visibility', 'visible');
    }
    else {
      this.arc.setAttribute('visibility', 'hidden');
    }  
  };

  return Arc;
});
define('arrow',['require','utils'],function (require) {

  //Imports
  var U = require('utils');

  function Arrow(graph, x1, y1, x2, y2, cssClass) {
    this.graph = graph;
    //Arrow line
    this.line = document.createElementNS(U.SVG_NS, 'line');
    this.line.setAttribute('clip-path',
                           'url(#' + this.graph.clipPath + ')');
    this.graph.node.appendChild(this.line);
    //Unfortunately, clip-path does not work on a transformed element ie it will
    //clip the shape before the transform is applied. So we do the
    //transformation ourselves, in setXY.
    /*Doesn't work with clip-path
    this.headPath.setAttribute('d', 
                               'M 0 0' + ' ' +
                               'L ' + parseInt(-base) + ' ' + parseInt(height) +
                               ' ' + parseInt(base) + ' ' + parseInt(height) + 
                               ' 0 0');
    */
    //Arrow head
    this.head = document.createElementNS(U.SVG_NS, 'path');
    this.head.setAttribute('clip-path',
                           'url(#' + this.graph.clipPath + ')');
    this.graph.node.appendChild(this.head);
    this.setXY(x1, y1, x2, y2);
    this.setClass(cssClass);
  };

  Arrow.prototype.setXY = function (x1, y1, x2, y2) {
    var wx1 = this.graph.getxPix(x1);
    var wy1 = this.graph.getyPix(y1);
    var wx2 = this.graph.getxPix(x2);
    var wy2 = this.graph.getyPix(y2);
    this.line.setAttribute('x1', wx1);
    this.line.setAttribute('y1', wy1);
    this.line.setAttribute('x2', wx2);
    this.line.setAttribute('y2', wy2);
    //Arrow head
    var base = 5; //In pixels
    var height = 10; //In pixels
    var wxv = wx2 - wx1;
    var wyv = wy2 - wy1;
    var ang = -(Math.PI/2.0 + Math.atan2(wyv, wxv));
    
    /*Doesn't work with clip-path
    ang *= 180.0/Math.PI;
    this.head.setAttribute('transform',
                           'translate(' +
                           parseInt(wx2) + ',' +
                           parseInt(wy2) + ')' + ' ' +
                           'rotate(' + parseInt(90-ang) + ')');
    */
    var c = Math.cos(ang);
    var s = Math.sin(ang);
    //Rotate and then translate
    var wx3 = Math.round(c*(-base) + s*(height) + wx2);
    var wy3 = Math.round(-s*(-base) + c*(height) + wy2);
    var wx4 = Math.round(c*(base) + s*(height) + wx2);
    var wy4 = Math.round(-s*(base) + c*(height) + wy2);


    this.head.setAttribute('d', 
                           'M ' + parseInt(wx2) + ' ' + parseInt(wy2) +
                           'L ' + parseInt(wx3) + ' ' + parseInt(wy3) +
                           ' ' + parseInt(wx4) + ' ' + parseInt(wy4) + 
                           ' ' + parseInt(wx2) + ' ' + parseInt(wy2));
  };
  
  Arrow.prototype.setClass = function (cssClass) {
    this.line.setAttribute('class', cssClass);
    this.head.setAttribute('class', cssClass);
  };

  Arrow.prototype.setVisibility = function(bool) {
    if (bool) {
      this.line.setAttribute('visibility', 'visible');
      this.head.setAttribute('visibility', 'visible');
    }
    else {
      this.line.setAttribute('visibility', 'hidden');
      this.head.setAttribute('visibility', 'hidden');
    }  
  };

  return Arrow;
});
define('curve',['require','utils'],function (require) {

  //Imports
  var U = require('utils');

  function Curve() {
    this.polyline = document.createElementNS(U.SVG_NS, 'polyline');
    this.graph = arguments[0]; //Always first argument
    //Argument are: graph, pts, cssClass
    if (arguments.length === 3) {
      this.setPoints(arguments[1]);
      this.polyline.setAttribute('class', arguments[2]);
    }
    //Argument are: graph, xCoords, yCoords, cssClass
    else if (arguments.length === 4) {
      this.setPoints(arguments[1], arguments[2]);
      this.polyline.setAttribute('class', arguments[3]);
    }
    //Argument are: graph, function to plot, xlow, xhigh, cssClass
    else if (arguments.length === 5) {
      this.setPoints(arguments[1], arguments[2], arguments[3]);
      this.polyline.setAttribute('class', arguments[4]);
    }
    this.polyline.setAttribute('clip-path',
                               'url(#' + this.graph.clipPath + ')');
    this.graph.node.appendChild(this.polyline);
  };

  Curve.prototype.setPoints = function () {
    var points = [];
    //Arguments are: an array of successive x,y values
    if (arguments.length === 1) {
      var pts = arguments[0];
      for (var i = 0, len = pts.length; i < len; i += 2) {
        points.push(this.graph.getxPix(pts[i]));
        points.push(this.graph.getyPix(pts[i+1]));
      }
    }
    //Arguments are: an array of x values, an array of y values
    else if (arguments.length === 2) {
      var xarr = arguments[0];
      var yarr = arguments[1];
      for (var i = 0, len = xarr.length; i < len; i++) {
        points.push(this.graph.getxPix(xarr[i]));
        points.push(this.graph.getyPix(yarr[i]));
      }
    }
    //Arguments are: function to plot, xlow, xhigh
    else if (arguments.length === 3) {
      var x, y, wx, wy;
      //Function
      var f = arguments[0];
      //Get the left and right pixel bounds
      var wxlow = this.graph.getxPix(arguments[1]);
      var wxhigh = this.graph.getxPix(arguments[2]);

      //First point
      x = arguments[1];
      wx = this.graph.getxPix(x);
      y = f(x);
      wy = this.graph.getyPix(y);
      //points.push(wx);
      //points.push(this.graph.getyPix(0.0));
      points.push(wx);
      points.push(wy);

      //Now iterate pixel by pixel
      while (wx < wxhigh) {
        wx++;
        x = this.graph.getxFromPix(wx);
        y = f(x);
        wy = this.graph.getyPix(y);
        points.push(wx);
        points.push(wy);
      }
      //points.push(wx);
      //points.push(this.graph.getyPix(0.0));
    }    
    this.polyline.setAttribute('points', points.join(','));  
  };

  Curve.prototype.setClass = function(cssClass) {
    this.polyline.setAttribute('class', cssClass);
  };
  
  Curve.prototype.translate = function (x, y) {
    this.polyline.setAttribute('transform',
                              'translate(' +
                              parseInt(this.graph.getxPix(x) - 
                                       this.graph.getxPix(0.0)) + ',' +
                              parseInt(this.graph.getyPix(y) - 
                                       this.graph.getyPix(0.0)) + ')');
  }                            
  return Curve;
});
define('diamond',['require','utils'],function (require) {

  //Imports
  var U = require('utils');

  function Diamond(graph, x, y, radius, cssClass) {
    this.graph = graph;
    this.radius = radius;
    this.point = document.createElementNS(U.SVG_NS, 'path');
    this.point.setAttribute('clip-path',
                           'url(#' + this.graph.clipPath + ')');
    this.setXY(x, y);
    //Doesn't work with clip-path this.setRadius(radius);
    this.setClass(cssClass);
    this.graph.node.appendChild(this.point);
  };

  Diamond.prototype.setXY = function (x, y) {
    /*Doesn't work with clip-path
    this.point.setAttribute('transform',
                            'translate(' +
                             parseInt(this.graph.getxPix(x)) + ',' +
                             parseInt(this.graph.getyPix(y)) + ')'
                           );
    */
    //Coordinates of center
    var wxc = this.graph.getxPix(x);
    var wyc = this.graph.getyPix(y);
    
    this.point.setAttribute('d', 
                            'M ' + 
                            parseInt(wxc - this.radius) + ' ' +
                            parseInt(wyc) + ' ' +
                            'L ' +
                            parseInt(wxc) + ' ' +
                            parseInt(wyc - this.radius) + ' ' +
                            'L ' + 
                            parseInt(wxc + this.radius) + ' ' +
                            parseInt(wyc) + ' ' +
                            'L ' + ' ' +
                            parseInt(wxc) + ' ' +
                            parseInt(wyc + this.radius) + ' ' +
                            'Z'
                           );
  };
  
  /*Diamond.prototype.setRadius = function (radius) {
    //Unfortunately, clip-path does not work on a transformed element ie it will
    //clip the shape before the transform is applied. So we do the
    //transformation ourselves, in setXY.
    Doesn't work with clip-path
    this.point.setAttribute('d', 
                            'M ' + parseInt(-radius) + ' 0 ' +
                            'L ' + ' 0 ' + parseInt(radius) + ' ' +
                            'L ' + parseInt(radius) + ' 0 ' +
                            'L ' + ' 0 ' + parseInt(-radius) + ' ' +
                            'Z '
                           );
  };*/
  
  Diamond.prototype.setClass = function (cssClass) {
    this.point.setAttribute('class', cssClass);
  };

  Diamond.prototype.setVisibility = function(bool) {
    if (bool) {
      this.point.setAttribute('visibility', 'visible');
    }
    else {
      this.point.setAttribute('visibility', 'hidden');
    }  
  };

  return Diamond;
});
define('line',['require','utils'],function (require) {

  //Imports
  var U = require('utils');

  function Line(graph, x1, y1, x2, y2, cssClass) {
    this.graph = graph;
    this.line = document.createElementNS(U.SVG_NS, 'line');
    this.line.setAttribute('clip-path',
                           'url(#' + this.graph.clipPath + ')');
    this.setXY(x1, y1, x2, y2);
    this.setClass(cssClass);
    this.graph.node.appendChild(this.line);
  };

  Line.prototype.setXY = function (x1, y1, x2, y2) {
    this.line.setAttribute('x1', this.graph.getxPix(x1));
    this.line.setAttribute('y1', this.graph.getyPix(y1));
    this.line.setAttribute('x2', this.graph.getxPix(x2));
    this.line.setAttribute('y2', this.graph.getyPix(y2)); 
  };
  
  Line.prototype.setClass = function (cssClass) {
    this.line.setAttribute('class', cssClass);
  };

  Line.prototype.setVisibility = function(bool) {
    if (bool) {
      this.line.setAttribute('visibility', 'visible');
    }
    else {
      this.line.setAttribute('visibility', 'hidden');
    }  
  };

  return Line;
});
define('rectangle',['require','utils'],function (require) {

  //Imports
  var U = require('utils');

  function Rectangle(graph, x, y, width, height, cssClass) {
    this.graph = graph;
    this.rectangle = document.createElementNS(U.SVG_NS, 'rect');
    this.setRectangle(x, y, width, height);
    this.setClass(cssClass);
    this.graph.node.appendChild(this.rectangle);
  };

  //Sets a rectangle, bottom left at x, y with a width and heigh
  Rectangle.prototype.setRectangle = function (x, y, width, height) {
    this.rectangle.setAttribute('x', this.graph.getxPix(x));
    this.rectangle.setAttribute('y', this.graph.getyPix(y + height));
    this.rectangle.setAttribute('width', this.graph.getxPix(x + width) -
                                         this.graph.getxPix(x));
    this.rectangle.setAttribute('height', this.graph.getyPix(y) - 
                                          this.graph.getyPix(y + height));
  };
  
  Rectangle.prototype.setClass = function (cssClass) {
    this.rectangle.setAttribute('class', cssClass);
  };

  return Rectangle;
});
define("lib/common", function(){});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));