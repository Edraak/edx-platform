(function (requirejs, require, define) {
define(function (require) {
  var Font = require('font');

  var TWO_PI = 2.0 * Math.PI;
  var PI_DIV_2 = Math.PI / 2.0;
  var ONE_EIGHTY_DIV_PI = 180.0/Math.PI;
  var PI_DIV_ONE_EIGHTY = Math.PI/180.0;
  
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

  ////////// GENERAL DRAWING ROUTINES //////////
  function drawLine(c, x1, y1, x2, y2) {
    //Vertical line. Without adding 0.5, the line would be 2 pixels wide.
    if (x1 === x2) {
      x1 += 0.5;
      x2 += 0.5;
    }
    else if (x2 > x1) {
      x2 += 1;
    }
    else {
      x1 += 1;
    }

    //Horizontal line. Without adding 0.5, the line would be 2 pixels wide.
    if (y1 === y2) {
      y1 += 0.5;
      y2 += 0.5;
    }
    else if (y2 > y1) {
      y2 += 1;
    }
    else {
      y1 += 1;
    }

    c.beginPath();
    c.moveTo(x1, y1);
    c.lineTo(x2, y2);
    c.stroke();
  }

  //Always add 0.5 since lines of delimiting a rectangle are always horizontal or vertical
  function drawRect(c, left, top, right, bottom) {
    c.strokeRect(left + 0.5, top + 0.5, right - left, bottom - top);
  }

  function fillRect(c, left, top, right, bottom) {
    c.fillRect(left, top, right - left + 1, bottom - top + 1);
  }

  //Not used for the moment
  function clearRect(c, left, top, right, bottom) {
    c.clearRect(left, top, right - left + 1, bottom - top + 1);
  }

  function drawPixel(c, x, y) {
    c.fillRect(x, y, 1, 1);
  }

  function drawPoint(c, x, y, radius) {
    c.beginPath();
    //Last param is anticlockwise
    c.arc(x + 0.5, y + 0.5, radius, 0, TWO_PI, true);
    c.fill();
  }

  function drawHollowPoint(c, x, y, radius) {
    c.beginPath();
    //Last param is anticlockwise
    c.arc(x + 0.5, y + 0.5, radius, 0, TWO_PI, true);
    c.stroke();
  }

  function drawCircle(c, x1, y1, x2, y2) {
    var radius = Math.abs(x2 - x1) / 2;
    c.beginPath();
    //Last param is anticlockwise
    c.arc(x1 + radius + 0.5, y1 + radius + 0.5, radius, 0, TWO_PI, true);
    c.stroke();
  }

  function fillCircle(c, x1, y1, x2, y2) {
    var radius = Math.abs(x2 - x1) / 2;
    c.beginPath();
    //Last param is anticlockwise
    c.arc(x1 + 0.5 + radius, y1 + radius + 0.5, radius, 0, TWO_PI, true);
    c.fill();
  }

  function drawTriangle(c, x1, y1, x2, y2, x3, y3) {
    c.beginPath();
    c.moveTo(x1 + 0.5, y1 + 0.5);
    c.lineTo(x2 + 0.5, y2 + 0.5);
    c.lineTo(x3 + 0.5, y3 + 0.5);
    c.closePath();
    c.stroke();
  }

  function fillTriangle(c, x1, y1, x2, y2, x3, y3) {
    c.beginPath();
    c.moveTo(x1 + 0.5, y1 + 0.5);
    c.lineTo(x2 + 0.5, y2 + 0.5);
    c.lineTo(x3 + 0.5, y3 + 0.5);
    c.closePath();
    c.fill();
  }

  function drawHalfCircle(c, x, y, radius, concaveDown) {
    c.beginPath();
    if (concaveDown) {
      c.arc(x + 0.5, y + 0.5, radius, 0, Math.PI, true);
    }
    else {
      c.arc(x + 0.5, y + 0.5, radius, Math.PI, 0, true);
    }
    c.stroke();
  }

  function drawArc(c, x, y, radius, start, end, counterclockwise) {
    c.beginPath();
    //We use -start and -end to have it work because angle are positive if
    //clockwise...
    c.arc(x + 0.5, y + 0.5, radius, -start, -end, true);
    c.stroke();
  }

  function getCoords(x1, y1, x2, y2) {
    var result = [];
    //Vertical line. Without adding 0.5, the line would be 2 pixels wide.
    if (x1 === x2) {
      x1 += 0.5;
      x2 += 0.5;
    }
    else if (x2 > x1) {
      x2 += 1;
    }
    else {
      x1 += 1;
    }
    //Horizontal line. Without adding 0.5, the line would be 2 pixels wide.
    if (y1 === y2) {
      y1 += 0.5;
      y2 += 0.5;
    }
    else if (y2 > y1) {
      y2 += 1;
    }
    else {
      y1 += 1;
    }

    result[0] = x1;
    result[1] = y1;
    result[2] = x2;
    result[3] = y2;

    return result;
  }

  function drawShape(c, x, y) //x and y are arrays of pixels
  {
    c.beginPath();
    var coords;
    var last = x.length - 1;

    //To have boundaries of the shape on the pixels defining them...
    for (var i = 0; i < last; i++) {
      coords = getCoords(x[i], y[i], x[i + 1], y[i + 1]);
      c.moveTo(coords[0], coords[1]);
      c.lineTo(coords[2], coords[3]);
    }

    //Connect last and first
    coords = getCoords(x[last], y[last], x[0], y[0]);
    c.moveTo(coords[0], coords[1]);
    c.lineTo(coords[2], coords[3]);

    c.stroke();
  }

  //TO DO: The following routine fills with offsets. Fix it.
  //Also, transparency does not belong here!
  function fillShape(c, x, y) //x and y are arrays of pixels
  {
    c.beginPath();
    c.globalAlpha = 0.5;
    var last = x.length - 1;

    c.moveTo(x[0], y[0]);

    //To have boundaries of the shape on the pixels defining them...
    for (var i = 1; i <= last; i++) {
      c.lineTo(x[i], y[i]);
    }

    c.fill();
    c.globalAlpha = 1.0;
  }

  function drawDiamond(c, x, y, h) {
    var xc = x + 0.5;
    var yc = y + 0.5;

    c.beginPath();
    c.moveTo(xc - h, yc);
    c.lineTo(xc, yc - h);
    c.lineTo(xc + h, yc);
    c.lineTo(xc, yc + h);
    c.closePath();

    c.fill();
  }

  function drawX(c, x, y, h) {
    var xc = x + 0.5;
    var yc = y + 0.5;

    c.beginPath();
    c.moveTo(xc + h, yc - h);
    c.lineTo(xc - h, yc + h);
    c.moveTo(xc - h, yc - h);
    c.lineTo(xc + h, yc + h);
    c.stroke();
  }

  function drawArrow(c, x1, y1, x2, y2, base, height) {
    var xs1 = x1 + 0.5;
    var ys1 = y1 + 0.5;
    var xs2 = x2 + 0.5;
    var ys2 = y2 + 0.5;
    var xv = x2 - x1;
    var yv = y2 - y1;
    var ang = Math.atan2(-yv, xv);

    c.beginPath();
    //Arrow line
    c.moveTo(xs1, ys1);
    c.lineTo(xs2, ys2);
    c.stroke();
    //Arrow head, first draw a triangle with top on origin then translate/rotate
    //to orient and fit on line
    c.save();
    c.beginPath();
    c.translate(xs2, ys2);
    c.rotate(PI_DIV_2 - ang);

    c.moveTo(0, 0);
    c.lineTo(-base, height);
    c.lineTo(base, height);
    c.closePath();
    c.fill();
    c.restore();
  }

  //////// TEXT ROUTINES ////////
  function parseSubSuperScriptText(str) {
    str = str || '';
    var len = str.length;
    var i = 0;
    var start;
    var end;
    var found = false;
    var text = [];
    var type;
    var ntext = "";

    while (i < len) {
      if (str[i] === "_") { //Encountered a potential subscript _
        type = "sub";
      }
      else if (str[i] === "^") {//Encountered a potential superscript ^
        type = "sup";
      }

      if (type === "sub" || type === "sup") {
        if (str[i + 1] === "{") {
          i += 2; //Discard _{ or ^{
          start = i;
          found = false;
          while (i < len) //Look for }
          {
            if (str[i] === "}") {
              found = true;
              end = i;
              break;
            }
            i++;
          }
          if (found && end > start) //Discard empty subscript ie _{}
          {
            //Store previous normal text if not empty and tag it as so
            if (ntext.length !== 0) {
              text.push({
                s: ntext,
                type: "normal"
              });
              ntext = "";
            }
            //Store subscript or superscript and tag it as so
            if (type === "sub") {
              text.push({
                s: str.substring(start, end),
                type: "sub"
              });
            }
            else if (type === "sup") {
              text.push({
                s: str.substring(start, end),
                type: "sup"
              });
            }
            i = end + 1;
          }
          else {
            i = start - 2; //Nothing was found, backtrack to _ or ^
          }
        }
      }
      ntext += str[i];
      //We've reached the end, store normal text if not empty and tag it as so
      if (i === len - 1 && ntext.length !== 0)  {
        text.push({
          s: ntext,
          type: "normal"
        });
      }
      i++;
    }

    return text;
  }

  function subSuperScriptLength(c, text, fNormal, fSubSup) {
    var fontNormal = fNormal;
    var fontSubSup = fSubSup;

    // allow regular or parsed string
    if (typeof text === "string") {
      return subSuperScriptLength(c,
                                  parseSubSuperScriptText(text),
                                  fontNormal,
                                  fontSubSup);
    }

    var xpos = 0;

    for (var i = 0; i < text.length; i++) {
      if (text[i].type === "normal") {
        c.font = fontNormal;
      }
      else if (text[i].type === "sub") {
        c.font = fontSubSup;
      }
      else {
        c.font = fontSubSup;
      }
      xpos += c.measureText(text[i].s).width + 2;
    }

    if (text.length) {
      xpos -= 2; // added 2 extra at the end
    }

    return xpos;
  }

  function drawSubSuperScript(c, str, x, y, xway, yway, fNormal, fSubSup) {
    //var fontNormal = (typeof fNormal === 'undefined') ? Font.normalText : fNormal;
    //var fontSubSup = (typeof fSubSup === 'undefined') ? Font.subSupText : fSubSup;

    var fontNormal = fNormal;
    var fontSubSup = fSubSup;

    c.textAlign = "left";
    c.textBaseline = (typeof yway === 'undefined') ? "alphabetic" : yway;

    var text = parseSubSuperScriptText(str);
    var len = subSuperScriptLength(c, text, fontNormal, fontSubSup);
    var xposIni = x;
    var yposIni = y;
    var xpos, ypos;

    if (xway === "left") {
      xpos = xposIni;
    }
    else if (xway === "right") {
      xpos = xposIni - len;
    }
    else if (xway === "center") {
      xpos = xposIni - len / 2;
    }

    //Draw the text
    for (var i = 0; i < text.length; i++) {
      if (text[i].type === "normal") {
        c.font = fontNormal;
        ypos = yposIni;
      }
      else if (text[i].type === "sub") {
        c.font = fontSubSup;
        ypos = yposIni + 3;
      }
      else {
        c.font = fontSubSup;
        ypos = yposIni - 5;
      }
      c.fillText(text[i].s, xpos, ypos);
      //Advance x position
      xpos += c.measureText(text[i].s).width + 2;
    }
  }

  // http://stackoverflow.com/questions/1134586/how-can-you-find-the-height-of-text-on-an-html-canvas#answer-9847841
  function measureFont(font) {
    var text = document.createElement('span');
    text.style.font = font;
    text.textContent = 'Hg';

    var block = document.createElement('div');
    block.style.display = 'inline-block';
    block.style.width = '1px';
    block.style.height = '0px';

    var div = document.createElement('div');
    div.style.position = "relative";
    div.appendChild(text);
    div.appendChild(block);

    document.body.appendChild(div);

    var result;
    try {
      result = {};

      block.style.verticalAlign = 'baseline';
      result.ascent = block.offsetTop - text.offsetTop;

      block.style.verticalAlign = 'bottom';
      result.height = block.offsetTop - text.offsetTop;

      result.descent = result.height - result.ascent;

    }
    finally {
      document.body.removeChild(div);
    }

    return result;
  }

  // correct the values in font.js
  Font.normalSize = measureFont(Font.normalText);
  Font.labelSize =  measureFont(Font.labelText);
  Font.subSupSize = measureFont(Font.subSupText);

  // given (x,y) and text, it will tell you the bBox of the drawn text
  // also convenient to get a consistent cross-browser text behavior
  function findTextbBox(ctx, x, y,
			text, xway, yway) {

    var width = subSuperScriptLength(ctx, text,
                                     Font.normalText, Font.subSupText);
    var height = Font.subSupSize.height + 8; // 8 includes the sub/sup differences

    var padding = 2; //px
    width += 2 * padding;
    height += 2 * padding;

    x -= padding;
    y -= padding;

    if (xway === 'left') {
      x -= 0;
    }
    else if (xway === 'center') {
      x -= Math.ceil(width / 2);
    }
    else if (xway === 'right') {
      x -= width;
    }

    y -= 5; // offset for superscripts
    if (yway === 'top') {
      y -= 0;
    }
    else if (yway === 'middle') {
      y -= Math.ceil(Font.subSupSize.height / 2);
    }
    else if (yway === 'alphabetic') {
      y -= Font.subSupSize.ascent;
    }
    else if (yway === 'bottom') {
      y -= Font.subSupSize.height;
    }

    return [x, y, width, height];
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
  function testForFeatures(testForCanvas, testForWebGL, testForAudio) {
    var testCanvas, gl, contextNames, hasWebAudio, hasAudioData,
        msg1, msg2, msg3;
    msg1 = "Your browser does not support the Canvas element.";
    msg2 = "Your browser does not support WebGL," +
           "or it is not enabled by default.";
    msg3 = "Your browser does not support Web Audio API nor Audio Data API.";
    
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
    drawLine: drawLine,
    drawRect: drawRect,
    fillRect: fillRect,
    clearRect: clearRect,
    drawPixel: drawPixel,
    drawPoint: drawPoint,
    drawHollowPoint: drawHollowPoint,
    drawCircle: drawCircle,
    fillCircle: fillCircle,
    drawTriangle: drawTriangle,
    fillTriangle: fillTriangle,
    drawHalfCircle: drawHalfCircle,
    drawArc: drawArc,
    getCoords: getCoords,
    drawShape: drawShape,
    fillShape: fillShape,
    drawDiamond: drawDiamond,
    drawX: drawX,
    drawArrow: drawArrow,
    drawSubSuperScript: drawSubSuperScript,
    subSuperScriptLength: subSuperScriptLength,
    measureFont: measureFont,
    findTextbBox: findTextbBox,
    copyPrototype: copyPrototype,
    testForFeatures: testForFeatures,
    testForCanvas: testForCanvas,
    testForWebGL: testForWebGL,
    testFor3DRenderer: testFor3DRenderer
  };

  return utils;
});
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));