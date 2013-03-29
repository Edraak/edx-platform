define(function (require) {
  //Imports
  var $ = require('jquery'),
    WebFonts = require('webfonts'),
    U = require('utils'),
    Tool = require('tool'),
    Color = require('color'),
    HSlider = require('hslider'),
    RadioButton = require('radiobutton'),
    RadioButtonGroup = require('radiobuttongroup'),
    VSlider = require('vslider'),
    Text = require('text'),
    Label = require('label'),
    RichText = require('richtext'),
    TextBox = require('textbox'),
    DropDown = require('dropdown'),
    MiniSlider = require('minislider'),
    Graph = require('graph');
    
    require('three'); //Attaches THREE to window object
     
  //##### 2D VARIABLES #####
  var tool;
  var lineRb, boxRb, rbGroup;
  
  //##### 3D VARIABLES #####
  // set the scene size
  var WIDTH = 500, HEIGHT = 500;

  // set some camera attributes
  var VIEW_ANGLE = 45,
      ASPECT = WIDTH / HEIGHT,
      NEAR = 0.1,
      FAR = 10000;
      
  var container, renderer, camera, scene, controls, directionalLight, ambientLight;
  var matrixValues, paramDisplay, paramSliders;
  var plane1, plane2, plane3, face1, face2, missingLines;
  var axes, ticks;

  //Loads webfonts from Google's website then initializes the tool
  WebFonts.load(initializeTool); 

  function initializeTool() {
    //The try catch block checks if certain features are present.
    //If not, we exit and alert the user.
    try {
      U.testFor3DRenderer(); //Test for WebGL or Canvas
      initTool();
      draw();
      animate();
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
  
    //##### 2D PART #####
    //Get daimp canvas
    var daimpCanvas = document.getElementById("daimp");
    //To disable text selection outside the canvas
    daimpCanvas.onselectstart = function () {
      return false;
    };
    //Create an offscreen buffer
    var daimpBuffer = document.createElement('canvas');
    daimpBuffer.width = daimpCanvas.width;
    daimpBuffer.height = daimpCanvas.height;

    var element = daimpCanvas;
    tool = new Tool(800, 800, daimpCanvas, daimpBuffer, element);
    //Axes checkboxes
    lineRb = new RadioButton(50, 50, 62, 62);
    lineRb.text = "Line axes";
    lineRb.textColor = Color.white;
    lineRb.addEventListener("mousedown", radioButtonMouseDown);
    tool.add(lineRb);
    boxRb = new RadioButton(50, 75, 62, 87);
    boxRb.text = "Box axes";
    boxRb.textColor = Color.white;
    boxRb.isChecked = true;
    boxRb.addEventListener("mousedown", radioButtonMouseDown);
    tool.add(boxRb);
    //Radio button group
    rbGroup = new RadioButtonGroup(lineRb, boxRb);

    // values for the 3 planes
    var numPlanes = 3;
    var paramsPerPlane = 4;
    matrixValues = new Array(numPlanes);
    var scale, x, y, z;
    for (y = 0; y < numPlanes; y++) {
      matrixValues[y] = new Array(paramsPerPlane);
      for (x = 0; x < paramsPerPlane; x++) {
        scale = (x === 3) ? 25 : 1;
        matrixValues[y][x] = scale * (Math.random() * 2 - 1);
      }
    }

    // controls for the 3 planes
    var basey = 150, rowspacing = 25;
    var paramXcoords = [50, 115, 180, 245];
    var planeColors = [Color.red, Color.green, Color.blue];
    var labelXcoords = [85, 150, 215];
    var labelText = ["x  +","y  +", "z  ="];
    paramDisplay = new Array(numPlanes);
    paramSliders = new Array(numPlanes);
    var tempText, bb;
    var md = function (e) {
      controls.enabled = false;
      sliderMouseHandler(e);
    };
    var mu = function (e) {
      controls.enabled = true;
    };
    for (y = 0; y < numPlanes; y++) {
      paramDisplay[y] = new Array(paramsPerPlane);
      paramSliders[y] = new Array(paramsPerPlane);

      for (x = 0; x < paramsPerPlane; x++) {
        paramDisplay[y][x] = new Text(paramXcoords[x],
                                       basey + rowspacing * y);
        var digits = (x === 3) ? 1 : 2;
        paramDisplay[y][x].text = matrixValues[y][x].toFixed(digits);
        paramDisplay[y][x].col = x;
        paramDisplay[y][x].row = y;
        paramDisplay[y][x].addEventListener("mousedown", matrixMouseDown);
        tool.add(paramDisplay[y][x]);

        bb = paramDisplay[y][x].getBB();

        paramSliders[y][x] = new MiniSlider(bb.left + Math.floor(bb.width / 2), bb.top - 1);
        paramSliders[y][x].col = x;
        paramSliders[y][x].row = y;
        paramSliders[y][x].zIndex = paramDisplay[y][x].zIndex + 1;
        paramSliders[y][x].addEventListener("mousedown", md);
        paramSliders[y][x].addEventListener("mousedrag", sliderMouseHandler);
        paramSliders[y][x].addEventListener("mouseup", mu);
        paramSliders[y][x].isVisible = false;
        tool.add(paramSliders[y][x]);

        scale = (x === 3) ? 25 : 1;
        paramSliders[y][x].xmin = -scale;
        paramSliders[y][x].xmax = scale;
        paramSliders[y][x].xspan = 2 * scale;
        paramSliders[y][x].setValue(matrixValues[y][x]);
      }

      for (x =0; x < labelText.length; x ++) {
        tempText = new Text(labelXcoords[x],
                            basey + rowspacing * y);
        tempText.text = labelText[x];
        tempText.textColor = planeColors[y];
        tool.add(tempText);
      }
    }
    
    //#####3D PART #####
    //Grab our container div
    container = document.getElementById("container");
    var container3D = document.createElement('div');
    container.appendChild(container3D);
    
    //Create the Three.js renderer, add it to our div
    if (U.testForWebGL()) {
      renderer = new THREE.WebGLRenderer();
    }
    else { //If we got up to here, Canvas is enabled 
      renderer = new THREE.CanvasRenderer();
    }  
    renderer.setSize(WIDTH, HEIGHT);
    renderer.setClearColor(new THREE.Color(0x000000), 1.0);
    container3D.appendChild(renderer.domElement);
    var jq = $(container3D);
    jq.css({
      'position': 'absolute',
      'left': 400,
      'top': 50
    });

    //Create a new scene
    scene = new THREE.Scene();

    //Create a new camera
    camera = new THREE.PerspectiveCamera(VIEW_ANGLE,
                                         ASPECT,
                                         NEAR,
                                         FAR);
    //container3D.addEventListener('mousedown', begin3dDrag);
    camera.position.z = 500;

    //Create mouse controls. Not part of usual Three.js distro
    //Had to fetch the file in examples/js/control, copy it
    //to extras and rebuild Three.js with utils/build_all.sh
    //Later on figure out what is not necessary in extras and do not
    //include it in the build.
    controls = new THREE.TrackballControls(camera);
    controls.rotateSpeed = 1.0;
    controls.zoomSpeed = 1.2;
    controls.panSpeed = 0.8;
    controls.noZoom = false;
    controls.noPan = false;
    controls.staticMoving = true;
    controls.dynamicDampingFactor = 0.3;
    controls.keys = [65, 83, 68];
    controls.addEventListener('change', render);


    // test out some coordinate axes
    var v = function (x,y,z) {
      return new THREE.Vector3(x,y,z);
    };

    var axisLen = 100;
    var l = axisLen;
    var tickSpacing = 20;
    var tickLen = 3;
    //Line axes
    var axisGeometry = new THREE.Geometry();
    axisGeometry.vertices.push(
      v(-axisLen, 0, 0), v(axisLen, 0, 0),
      v(0, -axisLen, 0), v(0, axisLen, 0),
      v(0, 0, -axisLen), v(0, 0, axisLen)
    );
    var axisMaterial = new THREE.LineBasicMaterial({
      color: 0xcccccc,
      lineWidth: 1
    });
    axes = new THREE.Line(axisGeometry, axisMaterial);
    axes.type = THREE.LinePieces;
    axes.visible = false;

    //Quick box axes => TO DO: this is better done with an indexed geometry like 
    //in Teal
    var face1Geom = new THREE.Geometry();
    face1Geom.vertices.push(
      v(-l, -l, -l), v(-l, l, -l),
      v(-l, l, l), v(-l, -l, l), v(-l, -l, -l)
    );
    face1 = new THREE.Line(face1Geom, axisMaterial);
    face1.type = THREE.LineStrip;

    var face2Geom = new THREE.Geometry();
    face2Geom.vertices.push(
      v(l, -l, -l), v(l, l, -l),
      v(l, l, l), v(l, -l, l), v(l, -l, -l)
    );
    face2 = new THREE.Line(face2Geom, axisMaterial);
    face2.type = THREE.LineStrip;

    //4 missing lines
    var missingLinesGeom = new THREE.Geometry();
    missingLinesGeom.vertices.push(
      v(-l, -l, -l), v(l, -l, -l),
      v(-l, l, -l), v(l, l, -l),
      v(-l, l, l), v(l, l, l),
      v(-l, -l, l), v(l, -l, l)
    );
    missingLines = new THREE.Line(missingLinesGeom, axisMaterial);
    missingLines.type = THREE.LinePieces;

    var tickGeometry = new THREE.Geometry();
    for (x = tickSpacing; x <= axisLen; x += tickSpacing) {
      tickGeometry.vertices.push(
        v(x, 0, 0), v(x, 0, tickLen),
        v(-x,0, 0), v(-x,0, tickLen),
        v(0, x, 0), v(tickLen, x, 0),
        v(0,-x, 0), v(tickLen,-x, 0),
        v(0, 0, x), v(tickLen, 0, x),
        v(0, 0,-x), v(tickLen, 0,-x)
      );
    }
    var ticks = new THREE.Line(tickGeometry, axisMaterial);
    ticks.type = THREE.LinePieces;

    // create a test surface
    var plotGeometry = new THREE.Geometry();
    var numSamples = 20, sampleSpacing = 5;
    for (x =0; x < numSamples; x ++) {
      for (z =0; z < numSamples; z ++) {

        plotGeometry.vertices.push(new THREE.Vector3(x * sampleSpacing, 0, z * sampleSpacing));

        if (x > 0 && z > 0) {
          plotGeometry.faces.push(new THREE.Face4(
            (x-1) + (z-1) * numSamples,
            x + (z-1) * numSamples,
            x + z * numSamples,
            (x-1) + z * numSamples
          ));
        }
      }
    }
    plotGeometry.dynamic = true;

    var plotMaterial = new THREE.MeshBasicMaterial({
      color: 0x99ccff,
      opacity: 0.8
    });
    var plot = new THREE.Mesh(plotGeometry, plotMaterial);
    plot.doubleSided = true;
    testPlot(plotGeometry, numSamples, sampleSpacing,
             function (x,z) { return Math.exp( - (x*x + z*z) / (axisLen*axisLen) * 4) * axisLen / 2; });

    //Create our 3 planes each representing one line of the augmented matrix
    /*var redMat = new THREE.MeshBasicMaterial({color: 0xff0000});
    redMat.side = THREE.DoubleSide;
    var greenMat = new THREE.MeshBasicMaterial({color: 0x00ff00});
    greenMat.side = THREE.DoubleSide;
    var blueMat = new THREE.MeshBasicMaterial({color: 0x0000ff});
    blueMat.side = THREE.DoubleSide;*/
    
    var redMat = new THREE.MeshPhongMaterial({
                       color: 0xff0000,
                       ambient: 0xff0000,
                       side: THREE.DoubleSide
                     });
                     
    var greenMat = new THREE.MeshLambertMaterial({
                         color: 0x00ff00,
                         ambient: 0x00ff00,
                         side: THREE.DoubleSide
                       });
                       
    var blueMat = new THREE.MeshLambertMaterial({
                         color: 0x0000ff,
                         ambient: 0x0000ff,
                         side: THREE.DoubleSide
                       });
    
    var planeGeom1 = new THREE.PlaneGeometry(100, 100);
    var planeGeom2 = new THREE.PlaneGeometry(100, 100);
    var planeGeom3 = new THREE.PlaneGeometry(100, 100);

    //This doesn't work anymore: plane1.doubleSided = true;
    plane1 = new THREE.Mesh(planeGeom1, redMat);
    plane2 = new THREE.Mesh(planeGeom2, greenMat);
    plane3 = new THREE.Mesh(planeGeom3, blueMat);

    updatePlane(0);
    updatePlane(1);
    updatePlane(2);

    //Create a point light
    directionalLight = new THREE.DirectionalLight(0xffffff);
    directionalLight.position.x = 10.0;
    directionalLight.position.y = 10.0;
    directionalLight.position.z = 10.0;
    //Create an ambient light
    ambientLight = new THREE.AmbientLight(0xaaaaaa);


    scene.add(axes);
    scene.add(face1);
    scene.add(face2);
    scene.add(missingLines);
    //scene.add(ticks);
    //scene.add(plot);
    scene.add(camera);
    scene.add(directionalLight);
    scene.add(ambientLight);
    scene.add(plane1);
    scene.add(plane2);
    scene.add(plane3);
  }

  function testPlot(geom, numSamples, sampleSpacing, f) {
    var x, z, val, i =0;
    for (x =0; x < numSamples; x ++) {
      for (z =0; z < numSamples; z ++) {
        val = f(x * sampleSpacing, z * sampleSpacing);
        geom.vertices[i].y = val;

        i ++;
      }
    }
  }

  /*function begin3dDrag(e) {
    var mx = e.clientX, my = e.clientY;

    var mm = function (e) {
      var dx = e.clientX - mx;
      var dy = e.clientY - my;

      camera.rotation.y -= dx*0.01; // camera doesn't actually use its rotation vec
      camera.position.x = 200 * Math.sin(camera.rotation.y);
      camera.position.y += dy;
      camera.position.z = 200 * Math.cos(camera.rotation.y);

      mx += dx;
      my += dy;

      window.requestAnimationFrame(render, renderer.domElement);
    };

    var mu = function (e) {
      window.removeEventListener('mousemove', mm);
      window.removeEventListener('mouseup', mu);
    };

    window.addEventListener('mousemove', mm);
    window.addEventListener('mouseup', mu);
  }*/
  
  function draw() {
    tool.setPaintOn("canvas");
    tool.paint();
  }
  
  function animate() {
    window.requestAnimationFrame(animate);
    controls.update();
  }
      
  function render() {
    renderer.render(scene, camera);
  }
  
  function radioButtonMouseDown(rb) {
    rbGroup.unselectAll(rb);
    
    if (lineRb.isChecked) {
      face1.visible = false;
      face2.visible = false;
      missingLines.visible = false;
      axes.visible = true;
    }  
    else {
      axes.visible = false;
      face1.visible = true;
      face2.visible = true;
      missingLines.visible = true;
    } 
    draw();
    render(); 
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

  var sliderVisibleX = -1, sliderVisibleY = -1;
  function showSlider(x, y) {
    hideVisibleSlider();

    // color the text being changed
    var md = paramDisplay[y][x];
    md.storeTextColor = md.textColor;
    md.textColor = Color.litegray;
    md.draw();

    paramSliders[y][x].isVisible = true;
    paramSliders[y][x].draw();

    // update state
    sliderVisibleX = x;
    sliderVisibleY = y;
  }

  function hideVisibleSlider() {
    if (sliderVisibleX >= 0) {
      // revert text color
      var md = paramDisplay[sliderVisibleY][sliderVisibleX];
      md.textColor = md.storeTextColor;
      md.draw();

      // hide it
      var ms = paramSliders[sliderVisibleY][sliderVisibleX];
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

    paramDisplay[y][x].clear();
    matrixValues[y][x] = paramSliders[y][x].xvalue;
    var digits = (x === 3) ? 1 : 2;
    paramDisplay[y][x].text = matrixValues[y][x].toFixed(digits);
    paramDisplay[y][x].draw();

    updatePlane(y);
  }

  function updatePlane(which) {
    var m = matrixValues[which];
    var plane = [plane1,plane2,plane3][which];

    plane.position.set(m[0],m[1],m[2]);
    plane.position.setLength(m[3]);
    var lookAtVec = new THREE.Vector3();
    if (m[3] === 0) {
      lookAtVec.set(m[0],m[1],m[2]);
    }
    plane.lookAt(lookAtVec);
    window.requestAnimationFrame(render, renderer.domElement);
  }

});