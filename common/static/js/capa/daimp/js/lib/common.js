//Loads the aliases of all our libraries and modules
requirejs.config({
  baseUrl: 'js',
  paths: {
    'jquery': 'vendor/jquery-1.7.2.min',
    'three': 'vendor/three.min',
    'webfonts': 'lib/webfonts',
    'tool': 'lib/tool',
    'utils': 'lib/utils',
    'color': 'lib/color',
    'vector2d': 'lib/vector2d',
    'component': 'lib/component',
    'radiobutton': 'lib/radiobutton',
    'checkbox': 'lib/checkbox',
    'hslider': 'lib/hslider',
    'vslider': 'lib/vslider',
    'button': 'lib/button',
    'text': 'lib/text',
    'label': 'lib/label',
    'font': 'lib/font',
    'graph': 'lib/graph',
    'minislider': 'lib/minislider',
    'radiobuttongroup': 'lib/radiobuttongroup',
    'dropdown': 'lib/dropdown',
    'textbox': 'lib/textbox',
    'richtext': 'lib/richtext',
    'rowarrow': 'lib/rowarrow',
    'shape': 'lib/shape'
  },
  shim: {
    'three': {
      deps: [],
      exports: 'THREE' //Attaches "THREE" to the window object
    }
  }    
});