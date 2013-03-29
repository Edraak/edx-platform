define(function (require) {
  //Imports
  var $ = require('jquery'),
    WebFonts = require('webfonts'),
    U = require('utils'),
    Tool = require('tool'),
    Color = require('color'),
    Text = require('text'),
    TextBox = require('textbox'),
    MiniSlider = require('minislider'),
    RowArrow = require('rowarrow'),
    RadioButton = require('radiobutton'),
    RadioButtonGroup = require('radiobuttongroup'),
    Button = require('button');

  var tool, matrixdisplay, minisliders, matrixvalues, userMat = [], solMat = [];
  var scalingLabel, scalarInput;
  var rowarrows, ghostBuffer, rowpositions;
  var stagingArrow, stagingDisplay, stagingPosition;
  var radiobuttons;
  var sliderVisibleX = -1, sliderVisibleY = -1;
  var switchRB, multiplyRB, addRB;
  //Text output of solution & user steps
  var textSolTitle, textStepsTitle;
  var textSols = [];
  var textSteps = [];
  var errorMsgDisplay, editingDisabled = false;
  var cols = 6;
  var rows = 5;

  //Loads webfonts from Google's website then initializes the tool
  WebFonts.load(initializeTool);

  function initializeTool() {
    //The try catch block checks if certain features are present.
    //If not, we exit and alert the user.
    try {
      U.testForFeatures(true, false, false); //Test for canvas only
      initTool();
      draw();
    }
    catch (err) {
      window.alert(err.toString() + " The tool is disabled.");
    }
  }

  //This will be used later on to style the tool externally
  function loadJSON() {
    $.ajax({
      url: 'config.json',
      dataType: "json",
      success: function (data) {
        $.each(data, function (key, val) {
          window.alert("key=" + key + " " + "val=" + val);
        });
      }
    });
  }

  function initTool() {
    //Get daimp canvas
    var daimpCanvas = $('#daimp')[0];
    //To disable text selection outside the canvas
    daimpCanvas.onselectstart = function () {
      return false;
    };
    //Create an offscreen buffer
    var daimpBuffer = document.createElement('canvas');
    daimpBuffer.width = daimpCanvas.width;
    daimpBuffer.height = daimpCanvas.height;

    //Get the container
    var container = document.getElementById("container");

    tool = new Tool(800, 800, daimpCanvas, daimpBuffer, $(daimpCanvas), container);

    switchRB = new RadioButton(100, 35, 110, 45);
    switchRB.text = "Switch";
    switchRB.isChecked = true;
    switchRB.addEventListener("mousedown", radioButtonMouseDown);
    tool.add(switchRB);

    multiplyRB = new RadioButton(200, 35, 210, 45);
    multiplyRB.text = "Multiply";
    multiplyRB .addEventListener("mousedown", radioButtonMouseDown);
    tool.add(multiplyRB);

    addRB = new RadioButton(300, 35, 310, 45);
    addRB.text = "Add";
    addRB.addEventListener("mousedown", radioButtonMouseDown);
    tool.add(addRB);

    radiobuttons = new RadioButtonGroup(switchRB, multiplyRB, addRB);

    // make the scaling factor UI, hidden by default
    scalingLabel = new Text(100, 100);
    scalingLabel.text = "Scaling factor:";
    tool.add(scalingLabel);
    scalingLabel.getBB();
    scalingLabel.isVisible = false;

    scalarInput = new TextBox(200, scalingLabel.bBox.top - 2, 50);
    tool.add(scalarInput);
    scalarInput.setVisibility(false);
    scalarInput.node.addEventListener('keydown', function (event) {
      var keycode = event.keyCode || event.charCode;
      var ENTERKEY = 13;
      if (keycode === ENTERKEY) {
        var temp = scalarInput.getFloat();
        if (isNaN(temp)) {
          this.value = temp = rowmult;
        }
        rowmult = temp;
        this.blur();
      }
    });
    
    var x, y;
    var basex = 133, basey = 200;
    var rowspacing = 25, colspacing = 50; //Was 27

    // make components for the staging display
    var bb, middleY;
    stagingDisplay = new Array(cols);
    for (x =0; x < cols; x ++) {
      stagingDisplay[x] = new Text(basex + colspacing * x, basey - 50);
      stagingDisplay[x].text = '--';
      stagingDisplay[x].textAlign = 'right';
      stagingDisplay[x].isVisible = false;
      tool.add(stagingDisplay[x]);
    }

    bb = stagingDisplay[0].getBB();
    middleY = (bb.top + bb.bottom) / 2;
    stagingArrow = new RowArrow(basex - 46, middleY, 10, 5);
    stagingArrow.row = -1; // this one is constant (indicates its not in the matrix)
    stagingArrow.origRow = -1; // this one points to the original row
    stagingArrow.isVisible = false;
    stagingArrow.addEventListener("mousedown", arrowMouseDown);
    tool.add(stagingArrow);

    stagingPosition = {
      left: stagingArrow.bBox.left,
      top: bb.top,
      bottom: bb.bottom,
      right: 200 + colspacing * cols
    };

    //Do a matrix!
    matrixvalues = new Array(rows);
    for (y = 0; y < rows; y++) {
      matrixvalues[y] = new Array(cols);
      for (x = 0; x < cols; x++) {
        matrixvalues[y][x] = Math.random() * 2 - 1;
      }
    }
    
    //Copy our initial matrix into our array of matrices
    userMat.push(deepCopy(matrixvalues));
    solMat.push(deepCopy(matrixvalues));

    matrixdisplay = new Array(rows);
    minisliders = new Array(rows);
    rowarrows = new Array(rows);
    rowpositions = new Array(rows);
    for (y = 0; y < rows; y++) {
      matrixdisplay[y] = new Array(cols);
      minisliders[y] = new Array(cols);

      for (x = 0; x < cols; x++) {
        matrixdisplay[y][x] = new Text(basex + colspacing * x,
                                       basey + rowspacing * y);
        matrixdisplay[y][x].text = matrixvalues[y][x].toFixed(2);
        matrixdisplay[y][x].textAlign = 'right';
        matrixdisplay[y][x].col = x;
        matrixdisplay[y][x].row = y;
        matrixdisplay[y][x].addEventListener("mousedown", matrixMouseDown);
        tool.add(matrixdisplay[y][x]);

        bb = matrixdisplay[y][x].getBB();

        minisliders[y][x] = new MiniSlider(bb.left + Math.floor(bb.width / 2), bb.top - 1);
        minisliders[y][x].col = x;
        minisliders[y][x].row = y;
        minisliders[y][x].zIndex = matrixdisplay[y][x].zIndex + 1;
        minisliders[y][x].addEventListener("mousedown", sliderMouseHandler);
        minisliders[y][x].addEventListener("mousedrag", sliderMouseHandler);
        minisliders[y][x].isVisible = false;
        tool.add(minisliders[y][x]);

        minisliders[y][x].xmin = -1.0;
        minisliders[y][x].xmax = 1.0;
        minisliders[y][x].xspan = 2.0;
        minisliders[y][x].setValue(matrixvalues[y][x]);
      }

      bb = matrixdisplay[y][0].getBB();
      middleY = (bb.top + bb.bottom) / 2;

      rowarrows[y] = new RowArrow(basex - 46, middleY, 10, 5);
      rowarrows[y].row = y;
      rowarrows[y].addEventListener("mousedown", arrowMouseDown);
      tool.add(rowarrows[y]);

      rowpositions[y] = {
        left: rowarrows[y].bBox.left,
        top: bb.top,
        middle: middleY,
        bottom: bb.bottom,
        baseLine: matrixdisplay[y][0].anchorTop,
        right: basex + colspacing * cols
      };
    }

    // error message
    basex = 70;
    basey += rowspacing * (rows - 1) + 50;
    errorMsgDisplay = new Text(basex, basey);
    errorMsgDisplay.text = "";
    errorMsgDisplay.textColor = Color.red;
    tool.add(errorMsgDisplay);

    //Text columns on the right to display solution & user steps
    var nlines = 20;
    rowspacing = 25;

    //Solution column
    basex = 550;
    basey = 50;
    //First the column title
    var callback1 = function() {
      matrixvalues = deepCopy(solMat[0]);
      upperTriangulate(matrixvalues, rows, cols);
      printAllSols();
      goToSol(solMat.length-1);
      draw();
    };
    textSolTitle = new Text(basex, basey);
    textSolTitle.text = "Solution";
    textSolTitle.addEventListener("mousedown", callback1);
    tool.add(textSolTitle);

    basey += 50;
    //Columns under
    var callback2 = function(val) {
      goToSol(val.src.y);
    };
    for (y = 0; y < nlines; y++) {
      textSols[y] = new Text(basex, basey + rowspacing * y);
      textSols[y].text = "";
      textSols[y].y = y; // + 1; // offset because of the original array
      textSols[y].addEventListener("mousedown", callback2);
      tool.add(textSols[y]);
    }
    textSols[0].text = "initial";
    
    //User steps column
    basex = 800;
    basey = 50;
    //First the column title
    textStepsTitle = new Text(basex, basey);
    textStepsTitle.text = "User steps";
    tool.add(textStepsTitle);
    basey += 50;
    
    var callback3 = function(val) {
      goToStep(val.src.y);
    };
    for (y = 0; y < nlines; y++) {
      textSteps[y] = new Text(basex, basey + rowspacing * y);
      textSteps[y].text = "";
      textSteps[y].y = y; // + 1; // offset because of the original array
      textSteps[y].addEventListener("mousedown", callback3);
      tool.add(textSteps[y]);
    }
    textSteps[0].text = "Initial";

    // undo button
    basey += rowspacing * (nlines - 1) + 50;
    var undoButton = new Button(basex, basey, basex + 100, basey + 25);
    undoButton.text = "Undo";
    undoButton.addEventListener("mousedown", function () {
      if (userMat.length <= 1) {
        return;
      }
      popStep();
      printAllSteps();
      goToStep(userMat.length-1);
      draw();
    });
    tool.add(undoButton);

    // do hover behavior
    textSolTitle.isSelected = true;
    var hoverListener = makeHoverListener();
    textSolTitle.addEventListener("mousemove", hoverListener);
    textSolTitle.addEventListener("mouseup", hoverListener);

    ghostBuffer = document.createElement('canvas');
    // DEBUG document.body.appendChild(ghostBuffer);

    document.addEventListener('keydown', canvasKeyDown, false);
  }

  function makeHoverListener() {
    var hoverCandidates = [].concat(
      textSolTitle,
      textSols,
      textSteps,
      stagingArrow,
      rowarrows
    );

    var textHoverAction = function () {
      var hoverColor = Color.litegray;
      if (this.isHovered) {
        this.storeTextColor = this.textColor;
        this.textColor = hoverColor;
      }
      else {
        this.textColor = this.storeTextColor;
      }
      this.draw();
    };

    var arrowHoverAction = function () {
      if (this.isHovered) {
        this.storeArrowColor = this.arrowColor;
        this.arrowColor = Color.solOrange;
      }
      else {
        this.arrowColor = this.storeArrowColor;
      }
      this.draw();
    };

    var i, len = hoverCandidates.length;
    for (i =0; i < len; i ++) {
      var hc = hoverCandidates[i];

      if (hc instanceof Text) {
        hc.addEventListener("hover", textHoverAction);
      }
      else if (hc instanceof RowArrow) {
        hc.addEventListener("hover", arrowHoverAction);
      }
    }

    return function (e) {
      var mpos = e.mouse;

      var i, len = hoverCandidates.length;
      for (i =0; i < len; i ++) {
        var hc = hoverCandidates[i];

        var wasHovered = hc.isHovered || false;
        hc.isHovered = (hc.isVisible && hc.isInside(mpos));

        if (wasHovered !== hc.isHovered) {
          hc.fireEvent("hover");
        }
      }
    };
  }
  
  function deepCopy(arr) {
    if (Array.isArray(arr)) {
      var l = arr.length;
      var newarr = new Array(l);
      
      for (var i = 0; i < l; i++) {
        newarr[i] = deepCopy(arr[i]);
      }
      return newarr;
    }
    return arr;
  }
  
  function draw() {
    //tool.paintBuffer();
    tool.setPaintOn("canvas");
    tool.paint();

    //update();
  }
  
  function radioButtonMouseDown(rb) {
    radiobuttons.unselectAll(rb);

    var showScale = multiplyRB.isChecked || addRB.isChecked;
    var showStage = addRB.isChecked;

    scalingLabel.isVisible = showScale;
    scalarInput.setVisibility(showScale);
    if (showScale && isNaN(scalarInput.getFloat())) {
      scalarInput.node.value = rowmult;
    }

    // reset staging and display?
    stagingArrow.origRow = -1;
    stagingArrow.isVisible = false; // will appear with display values
    for (var x =0, cols = stagingDisplay.length; x < cols; x ++) {
      stagingDisplay[x].isVisible = showStage;
      stagingDisplay[x].text = '--';
      stagingDisplay[x].textColor = Color.white;
    }

    draw();
  }

  function matrixMouseDown(param) {
    var x = param.src.col;
    var y = param.src.row;

    // if we are clicking on the visible one, hide it
    if (sliderVisibleX === x && sliderVisibleY === y) {
      hideVisibleSlider();
    }
    else { // switch!
      showSlider(x, y);
    }
  }

  function showSlider(x, y) {
    hideVisibleSlider();

    if (editingDisabled) {
      return makeHistoryError();
    }

    // color the text being changed
    var md = matrixdisplay[y][x];
    md.storeTextColor = md.textColor;
    md.textColor = Color.litegray;
    md.draw();

    minisliders[y][x].isVisible = true;
    minisliders[y][x].draw();

    // update state
    sliderVisibleX = x;
    sliderVisibleY = y;
  }

  function hideVisibleSlider() {
    if (sliderVisibleX >= 0) {
      // revert text color
      var md = matrixdisplay[sliderVisibleY][sliderVisibleX];
      md.textColor = md.storeTextColor;
      md.draw();

      // hide it
      var ms = minisliders[sliderVisibleY][sliderVisibleX];
      ms.isVisible = false;

      // redraw components behind the slider.
      tool.paintBox({
        left: ms.bBox.left,
        top: ms.bBox.top,
        right: ms.bBox.right,
        bottom: ms.bBox.bottom + ms.anchorTriangleHeight
      });

      // update state
      sliderVisibleX = -1;
      sliderVisibleY = -1;
    }
  }

  function sliderMouseHandler(param) {
    var x = param.src.col;
    var y = param.src.row;

    matrixdisplay[y][x].clear();
    matrixvalues[y][x] = minisliders[y][x].xvalue;
    matrixdisplay[y][x].text = matrixvalues[y][x].toFixed(2);
    matrixdisplay[y][x].draw();
  }

  function canvasKeyDown(event) {
    var TABKEY = 9;
    var LEFTKEY = 37;
    var UPKEY = 38;
    var RIGHTKEY = 39;
    var DOWNKEY = 40;
    var ESCKEY = 27;
    var SPACEKEY = 32;

    var keycode = event.keyCode || event.charCode;

    // current slider state
    var x = sliderVisibleX;
    var y = sliderVisibleY;
    var xmax = minisliders[0].length;
    var ymax = minisliders.length;
    var noSliderVisible = (x === -1 && y === -1);
    var sliderChange = false;

    if (keycode === TABKEY) {
      sliderChange = true;

      if (!event.shiftKey) {
        if (noSliderVisible) {
          y = 0; // puts it at (-1,0) so tab will make it (0,0)
        }

        x++;
        if (x === xmax) { // wrap around
          x = 0;
          y++;
          if (y === ymax) { // wrap
            y = 0;
          }
        }
      }
      else {
        if (noSliderVisible) {
          x = xmax;
          y = ymax - 1;
        }

        x--;
        if (x === -1) {
          x = xmax - 1;
          y--;
          if (y === -1) {
            y = ymax - 1;
          }
        }
      }
    }
    else if (event.ctrlKey) {
      // I never liked switches... sorry
      if (keycode === RIGHTKEY) {
        sliderChange = true;

        if (noSliderVisible) {
          y = 0;
        }

        x++;
        if (x === xmax) {
          x = 0;
        }
      }
      else if (keycode === LEFTKEY) {
        sliderChange = true;

        if (noSliderVisible) {
          x = xmax;
          y = 0;
        }

        x--;
        if (x === -1) {
          x = xmax - 1;
        }
      }
      else if (keycode === DOWNKEY) {
        sliderChange = true;

        if (noSliderVisible) {
          x = 0;
        }

        y++;
        if (y === ymax) {
          y = 0;
        }
      }
      else if (keycode === UPKEY) {
        sliderChange = true;

        if (noSliderVisible) {
          x = 0;
          y = ymax;
        }

        y--;
        if (y === -1) {
          y = ymax - 1;
        }
      }
    }

    // that's it for changing between sliders
    if (sliderChange) {
      showSlider(x, y);
      event.preventDefault();
      return;
    }

    if (keycode === ESCKEY && !noSliderVisible) {
      hideVisibleSlider();
      event.preventDefault();
      return;
    }

    // the control key was not pressed, so maybe it's a command for the slider
    if (!noSliderVisible) {
      var ms = minisliders[y][x];
      var fakempos = {};
      var diff = (event.shiftKey) ? 3 : 1; // in pixels

      if (keycode === RIGHTKEY || keycode === UPKEY) {
        fakempos.x = ms.wxvalue + diff;
      }
      else if (keycode === LEFTKEY || keycode === DOWNKEY) {
        fakempos.x = ms.wxvalue - diff;
      }
      else if (keycode === SPACEKEY) {
        fakempos.x = ms.wxvalue + diff;
        if (fakempos.x > ms.wxmax) { // loop
          fakempos.x = ms.wxmin;
        }
      }

      if (fakempos.x !== undefined) {
        ms.getValue(fakempos);
        ms.draw();
        ms.fireEvent("mousedrag", {
          src: ms
        });

        event.preventDefault();
        return;
      }
    }
  }
  
  function arrowMouseDown(param) {
    hideVisibleSlider();
    if (editingDisabled) {
      return makeHistoryError();
    }

    if (switchRB.isChecked) {
      beginRowDrag(param);
    }
    else if (multiplyRB.isChecked) {
      multiplyRow(param);
    }
    else if (addRB.isChecked) {
      beginAddDrag(param);
    }
  }
  
  function multiplyRow(param)
  {
    var arrow = param.src;
    var y = arrow.row;
    var cols = matrixdisplay[y].length;

    // check the value first
    var temp = scalarInput.getFloat();
    if (isNaN(temp)) {
      scalarInput.node.value = rowmult;
      return;
    }

    // so we're good, lets do it!
    rowmult = temp;

    for (var x = 0; x < cols; x++) {
      matrixvalues[y][x] *= rowmult;
      matrixdisplay[y][x].text = matrixvalues[y][x].toFixed(2);
    }

    //Record the step
    sourceRow = y;
    pushStep(MULT_STEP, sourceRow, rowmult);

    draw();
  }

  function addScaledRow(destRow, factor, srcRow) {
    var cols = matrixvalues[destRow].length;
    var x, tempval;

    for (x =0; x < cols; x ++) {
      matrixvalues[destRow][x] += factor * matrixvalues[srcRow][x];
      matrixdisplay[destRow][x].text = matrixvalues[destRow][x].toFixed(2);
    }
  }
    
  function beginRowDrag(param) {
    var arrow = param.src;
    var y = arrow.row;
    var cols = matrixdisplay[y].length;
    var i;
    
    //For history purpose, register which row is being dragged
    sourceRow = y;

    // prep the canvas
    hideVisibleSlider();
    arrow.draw();
    for (i = 0; i < cols; i++) {
      matrixdisplay[y][i].draw();
    }

    // find the size
    var ghostX = arrow.bBox.left;
    var bb = matrixdisplay[y][cols - 1].getBB();
    var ghostY = bb.top;
    var ghostWidth = bb.right - ghostX;
    var ghostHeight = bb.bottom - ghostY;

    // copy row into buffer
    ghostBuffer.width = ghostWidth;
    ghostBuffer.height = ghostHeight;
    var buffctx = ghostBuffer.getContext('2d');
    buffctx.drawImage(tool.canvas,
                      ghostX, ghostY, ghostWidth, ghostHeight,
                      0, 0, ghostWidth, ghostHeight);

    // hide our elements
    arrow.storeAnchorLeft = arrow.anchorLeft; // must be 'visible' if we want events
    arrow.setAnchor(-10, arrow.anchorTop);
    for (i = 0; i < cols; i++) {
      matrixdisplay[y][i].isVisible = false;
    }

    var config = {
      row: y,
      origRow: y,
      dx: param.mouse.x - ghostX,
      dy: param.mouse.y - ghostY,
      ghostX: ghostX,
      ghostY: ghostY,
      ghostWidth: ghostWidth,
      ghostHeight: ghostHeight,
      mode: SWITCH_STEP,
      eventHandler: arrow
    };

    arrow.isSelected = true; // get the other mouse events
    var handlers = makeDragHandlers(config);
    arrow.addEventListener("mousemove", handlers.mm);
    arrow.addEventListener("mouseup", handlers.mu);
  }

  function beginAddDrag(param) {
    var arrow = param.src;
    var fromStaging = (arrow.row === -1);
    var y = fromStaging ? arrow.origRow : arrow.row;
    var cols = matrixdisplay[y].length;
    var i;

    //For history purpose, register which row is being dragged
    sourceRow = y;

    // prep the canvas for copying
    if (!fromStaging) {
      // first scale the values and put it in staging
      var temp = scalarInput.getFloat();
      if (isNaN(temp)) {
        scalarInput.node.value = rowmult;
      }

      // so we're good, lets do it!
      rowmult = temp;

      var tempval, temptext, tempcol;
      for (var x = 0; x < cols; x++) {
        stagingDisplay[x].clear(); // get rid of the old

        tempval = matrixvalues[y][x] * rowmult;
        temptext = tempval.toFixed(2);
        var color = Color.white;
        if (tempval < 0) {
          tempcol = Color.red;
        }
        else if (tempval > 0) {
          tempcol = Color.green;
          temptext = '+' + temptext;
        }

        stagingDisplay[x].text = temptext;
        stagingDisplay[x].textColor = tempcol;

        stagingDisplay[x].draw();
      }

      stagingArrow.isVisible = true;
      stagingArrow.origRow = y;
      stagingArrow.draw();
    }

    // find the size
    var ghostX = arrow.bBox.left;
    var rowClicked = (fromStaging ? stagingDisplay : matrixdisplay[y]);
    var ghostY = rowClicked[0].getBB().top;
    var ghostWidth = stagingPosition.right - stagingPosition.left;
    var ghostHeight = stagingPosition.bottom - stagingPosition.top;

    // copy row into buffer
    ghostBuffer.width = ghostWidth;
    ghostBuffer.height = ghostHeight;
    var buffctx = ghostBuffer.getContext('2d');
    buffctx.drawImage(tool.canvas,
    stagingPosition.left, stagingPosition.top, ghostWidth, ghostHeight,
    0, 0, ghostWidth, ghostHeight);

    var config = {
      row: y,
      origRow: y,
      dx: param.mouse.x - ghostX,
      dy: param.mouse.y - ghostY,
      ghostX: ghostX,
      ghostY: ghostY,
      ghostWidth: ghostWidth,
      ghostHeight: ghostHeight,
      mode: ADD_STEP,
      eventHandler: arrow
    };

    arrow.isSelected = true; // get the other mouse events
    var handlers = makeDragHandlers(config);
    arrow.addEventListener("mousemove", handlers.mm);
    arrow.addEventListener("mouseup", handlers.mu);
  }

  function nearestRow(x, y) {
    var ret = 0, rowpos,
      shortestDist = Math.abs(rowpositions[0].middle - y);

    for (var i = 0, len = rowpositions.length; i < len; i++) {
      rowpos = rowpositions[i];
      var idist = Math.abs(y - rowpos.middle);
      if (idist < shortestDist) {
        ret = i;
        shortestDist = idist;
      }
    }

    var maxDist = rowpositions[1].middle - rowpositions[0].middle;
    if (shortestDist > maxDist) {
      ret = -1;
    }
    maxDist *= 2;
    if (x < rowpositions[0].left - maxDist ||
        x > rowpositions[0].right + maxDist) {
      ret = -1;
    }

    return ret;
  }

  function swapPair(row1, row2) {
    // swap pointers in the arrays
    var tempvals = matrixvalues[row1];
    var tempmd = matrixdisplay[row1];
    var tempms = minisliders[row1];
    var temparrow = rowarrows[row1];

    matrixvalues[row1] = matrixvalues[row2];
    matrixdisplay[row1] = matrixdisplay[row2];
    minisliders[row1] = minisliders[row2];
    rowarrows[row1] = rowarrows[row2];

    matrixvalues[row2] = tempvals;
    matrixdisplay[row2] = tempmd;
    minisliders[row2] = tempms;
    rowarrows[row2] = temparrow;

    positionRow(row1);
    positionRow(row2);
  }

  function positionRow(y) {
    var pos = rowpositions[y];
    for (var x = 0, cols = matrixdisplay[y].length; x < cols; x++) {
      matrixdisplay[y][x].anchorTop = pos.baseLine;
      matrixdisplay[y][x].row = y;
      matrixdisplay[y][x].getBB();

      var aleft = minisliders[y][x].anchorLeft;
      var atop = matrixdisplay[y][x].bBox.top - 1;
      minisliders[y][x].setAnchor(aleft, atop);
      minisliders[y][x].row = y;
    }

    rowarrows[y].setAnchor(rowarrows[y].anchorLeft, pos.middle);
    rowarrows[y].row = y;
  }

  function moveRow(from, to) {
    var y, ret =[];
    if (from < to) {
      for (y = from; y < to; y++) {
        swapPair(y, y + 1);
        ret.push(y);
      }
      ret.push(to);
    }
    else if (from > to) {
      for (y = from; y > to; y--) {
        swapPair(y - 1, y);
        ret.push(y);
      }
      ret.push(to);
    }

    return ret;
  }

  function previewAddRow(orig, from, to) {
    if (from === to) {
      return []; // nothing to change
    }

    var ret =[];
    if (from !== orig && from !== -1) {
      // we have previously added our values in
      // so take them out
      addScaledRow(from, -rowmult, orig);
      ret.push(from);
    }

    if (to !== orig && to !== -1) {
      // preview the addition
      addScaledRow(to, rowmult, orig);
      ret.push(to);
    }

    return ret;
  }

  //Type of elementary row operation
  var INITIAL = 0, SWITCH_STEP = 1, MULT_STEP = 2, ADD_STEP = 3;
  
  var sourceRow, destRow, rowmult = 1.5;
  var steps = []; //Stores all the steps
  pushStep(INITIAL, 0, 1.0, 0);
  var currentStep = 0;
  var sols = []; //Stores all the solution steps
  pushSol(INITIAL, 0, 1.0, 0);
  
  //Adds a Gaussian elimination step
  function pushStep(type, srcRow, mult, destRow) {
    //Record the matrix
    if (type !== INITIAL) {
      userMat.push(deepCopy(matrixvalues));
    }

    //Sloppy, code better later on
    if (type === SWITCH_STEP) {
      steps.push({type: SWITCH_STEP,
                  srcRow: srcRow, mult: mult, destRow: destRow});
    }
    else if (type === MULT_STEP) {
      steps.push({type: MULT_STEP,
                  srcRow: srcRow, mult: mult, destRow: destRow});
    }
    else if (type === ADD_STEP) {
      steps.push({type: ADD_STEP,
                  srcRow: srcRow, mult: mult, destRow: destRow});
    }
    else if (type === INITIAL){
      steps.push({type: INITIAL,
                  srcRow: srcRow, mult: mult, destRow: destRow});
    }

    currentStep++;
    
    //Update the text fields
    printAllSteps();
    if (tool !== undefined) { // fix a bug
      draw();
    }
  }
  
  //TO DO: only one function with the above
  function pushSol(type, srcRow, mult, destRow) {
    //Record the matrix
    if (type !== INITIAL) {
      solMat.push(deepCopy(matrixvalues));
    }
  
    //Sloppy, code better later on
    if (type === SWITCH_STEP) {
      sols.push({type: SWITCH_STEP,
                 srcRow: srcRow, mult: mult, destRow: destRow});
    }
    else if (type === MULT_STEP) {
      sols.push({type: MULT_STEP,
                  srcRow: srcRow, mult: mult, destRow: destRow});
    }
    else if (type === ADD_STEP) {
      sols.push({type: ADD_STEP,
                  srcRow: srcRow, mult: mult, destRow: destRow});
    }
    else if (type === INITIAL) {
      sols.push({type: INITIAL,
                  srcRow: srcRow, mult: mult, destRow: destRow});
    }
  }
   
  //Remove a step
  function popStep() {
    steps.pop();
    userMat.pop();
  }
  
  function stepBack() {
    if (currentStep !== 0) {
      currentStep--;
    }
    else {
      window.alert('You are at the beginning.');
    }
  }
  
  function stepForward() {
    if (currentStep !== steps.length) {
      currentStep++;
    }
    else {
      window.alert('You are at the end.');
    }
  }
  
  function printAllSteps() {
    var str, i;
    // simultaneously print the steps and clear the ones afterward
    for (i = 0; i < textSteps.length; i++) {
      if (i < steps.length) {
        str = getStepStr(steps[i].type, steps[i].srcRow,
                         steps[i].mult, steps[i].destRow);
      }
      else {
        str = "";
      }
      textSteps[i].text = str;
    }
  }

  //TO DO: Combine with the function above
  function printAllSols() {
    var str, i;
    for (i =0; i < textSols.length; i ++) {
      if (i < sols.length) {
        str = getStepStr(sols[i].type, sols[i].srcRow,
                         sols[i].mult, sols[i].destRow);
      }
      else {
        str = "";
      }
      textSols[i].text = str;
    }
  }

  function getStepStr(type, srcRow, mult, destRow) {
    //Arrays are zero indexed, add one for regular matrix notation
    srcRow += 1;
    destRow += 1;
    if (type === SWITCH_STEP) {
      return 'L' + srcRow.toString() + ' <=> ' +
             'L' + destRow.toString();
    }
    else if (type === MULT_STEP) {
      return mult.toFixed(2) + 'L' + srcRow.toString() + ' => ' +
             'L' + srcRow.toString();
    }
    else if (type === ADD_STEP) {
      return mult.toFixed(2) + 'L' + srcRow.toString() + ' + ' +
             'L' + destRow.toString() + ' => ' +
             'L' + destRow.toString();
    }
    else if (type === INITIAL) {
      return 'initial';
    }
  }

  function goToStep(pos) {
    matrixvalues = deepCopy(userMat[pos]);

    //Update display
    for (var x, y = 0; y < rows; y++) {
      for (x = 0; x < cols; x++) {
        matrixdisplay[y][x].text = matrixvalues[y][x].toFixed(2);
      }
    }

    editingDisabled = (pos !== userMat.length - 1);
    errorMsgDisplay.text = "";

    draw();
  }
  
  function goToSol(pos) {
    
    matrixvalues = deepCopy(solMat[pos]);
      
    //Update display
    for (var x, y = 0; y < rows; y++) {
      for (x = 0; x < cols; x++) {
        matrixdisplay[y][x].text = matrixvalues[y][x].toFixed(2);
      }
    }

    editingDisabled = true;
    errorMsgDisplay.text = "";

    draw();
  }
  
  function makeHistoryError() {
    errorMsgDisplay.text = "Cannot edit entries in history mode; go to newest step in user steps";
    errorMsgDisplay.draw();
  }

  // Convert an mxn matrix A to upper diagonal form
  function upperTriangulate(A, m, n)
  {
    var i, j, k, l, q;

    //Traverse all the rows from top to bottom
    for (i = 0; i < m; i++) {
      //Find row under row i with maximum on column i
      var maxRow = i;
      
      for (k = i+1; k < m; k++) {
        if (Math.abs(A[k][i]) > Math.abs(A[maxRow][i])) {
          maxRow = k;
        }
      }
      if (maxRow !== i) {
        swapRows(A, i, maxRow);
        //Record previous operation
        pushSol(SWITCH_STEP, i, 1.0, maxRow); //TO DO: 1.0 not used
      }

      // Eliminate lower diagonal elements of A
      // by using A[i][i] as pivot
      q = 1.0/A[i][i];
      
      //First set A[i][i] to 1 TO DO: A[i][i] == 0
      for (l = i; l < n; l++) {
        A[i][l] *= q;
      }
      //Record previous operation
      pushSol(MULT_STEP, i, q, i);
      //Do the rows under
      for (k = i+1; k < m; k++) {
        q = A[k][i];
        for (l = i; l < n; l++) {
          A[k][l] = A[k][l] - q*A[i][l];
        }
        //Record previous operation
        pushSol(ADD_STEP, i, -q, k);
      }
    }
  }
  
  function swapRows(a, r1, r2) {
    var n = a[r1].length; //Number of columns
    for (var j = 0; j < n; j++) {
      var tmp = a[r2][j];
      a[r2][j] = a[r1][j];
      a[r1][j] = tmp;
    }
  }
  
  //For debugging purposes
  /*function outputMatrix(mat) {
    var m = mat.length;
    var n = mat[0].length;
    var i, j, str;
    
    console.log("Rows: " + m.toFixed(0) + " " + "Cols: " + n.toFixed(0));
    
    for (i = 0; i < m; i++) {
      str = "";
      for (j = 0; j < n; j++) {
        str += mat[i][j].toFixed(2) + "  ";
      }
      console.log(str);
    }
  }*/

  function makeDragHandlers(drag) {
    var mm = function (param) {
      // find the new position
      var newx = param.mouse.x - drag.dx;
      var newy = param.mouse.y - drag.dy;

      // find the closest "row gap"
      var newrow = nearestRow(newx, newy + drag.ghostHeight / 2);
      var changed =[];
      if (drag.mode === SWITCH_STEP) {
        // changed = moveRow(drag.row, newrow);
      }
      else { //drag.mode === ADD_STEP
        changed = previewAddRow(drag.origRow, drag.row, newrow);
      }

      // update components that have changed
      // we could just call draw(), it doesn't seem too slow
      var ghostBox = {
        top: drag.ghostY - 10,
        bottom:  drag.ghostY + drag.ghostHeight + 10,
        left: drag.ghostX - 10,
        right: drag.ghostX + drag.ghostWidth + 10
      };

      tool.paintBox(ghostBox);
      for (var i =0; i < changed.length; i ++) {
        tool.paintBox(rowpositions[changed[i]]);
      }

      // set the new position
      drag.ghostX = newx;
      drag.ghostY = newy;
      drag.row = newrow;

      // draw dotted box
      // apparently its hard to do

      // copy the row again
      tool.ctx.save();
      tool.ctx.globalAlpha = 0.6;
      //This causes a bug in Firefox on OSX only
      //drag.ghostWidth > ghostBuffer.width =>
      //"Index or size is negative or greater than the allowed amount"
      /*tool.ctx.drawImage(ghostBuffer,
                         0, 0,
                         drag.ghostWidth, drag.ghostHeight,
                         drag.ghostX, drag.ghostY,
                         drag.ghostWidth, drag.ghostHeight);*/
      tool.ctx.drawImage(ghostBuffer,
                         0, 0,
                         ghostBuffer.width, ghostBuffer.height,
                         drag.ghostX, drag.ghostY,
                         ghostBuffer.width, ghostBuffer.height);
      tool.ctx.restore();
    };

    var mu = function (param) {
      if (drag.mode === SWITCH_STEP) {
        // show our elements
        var y = drag.origRow;
        var arrow = rowarrows[y];
        arrow.setAnchor(arrow.storeAnchorLeft, arrow.anchorTop);
        for (var i = 0, len = matrixdisplay[y].length; i < len; i++) {
          matrixdisplay[y][i].isVisible = true;
        }

        // do the switch
        if (drag.row !== drag.origRow && drag.row !== -1) {
          swapPair(drag.row, drag.origRow);
        }
      }

      drag.eventHandler.isSelected = false;
      drag.eventHandler.removeEventListener("mousemove", mm);
      drag.eventHandler.removeEventListener("mouseup", mu);

      //Record the step?
      destRow = drag.row;
      if (destRow !== sourceRow && destRow !== -1) {
        pushStep(drag.mode, sourceRow, rowmult, destRow);
      }

      // redraw the tool and get rid of any artifacts
      draw();
    };

    return {
      mm: mm,
      mu: mu
    };
  }
});