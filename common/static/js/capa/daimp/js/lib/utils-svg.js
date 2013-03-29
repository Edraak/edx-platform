define(function (require) {
  
  var TWO_PI = 2.0 * Math.PI;
  var PI_DIV_2 = Math.PI / 2.0;
  var ONE_EIGHTY_DIV_PI = 180.0/Math.PI;
  var PI_DIV_ONE_EIGHTY = Math.PI/180.0;
  var SVG_NS = 'http://www.w3.org/2000/svg';
  
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

  //Inheritance
  function copyPrototype(descendant, parent) {
    var sConstructor = parent.toString();
    var aMatch = sConstructor.match(/\s*function (.*)\(/);
    if (aMatch !== null) {
      descendant.prototype[aMatch[1]] = parent;
    }
    for (var m in parent.prototype) {
      descendant.prototype[m] = parent.prototype[m];
    }
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
               "svg").createSVGRect;
      
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
  

  ////////// PUBLIC CONSTANTS AND FUNCTIONS
  var utils = {
    //Constants
    TWO_PI: TWO_PI,
    PI_DIV_2: PI_DIV_2,
    //Functions
    degToRad: degToRad,
    radToDeg: radToDeg,
    getxPix: getxPix,
    getxFromPix: getxFromPix,
    getyPix: getyPix,
    getyFromPix: getyFromPix,
    log10: log10,
    copyPrototype: copyPrototype,
    testForFeatures: testForFeatures,
    testForCanvas: testForCanvas,
    testForWebGL: testForWebGL,
    testFor3DRenderer: testFor3DRenderer,
    testForSVG: testForSVG
  };

  return utils;
});