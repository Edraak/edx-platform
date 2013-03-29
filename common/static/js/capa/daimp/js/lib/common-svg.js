//Loads the aliases of all our libraries and modules
requirejs.config({
  baseUrl: 'js',
  paths: {
    'tool': 'lib/tool-svg',
    'component': 'lib/component-svg',
    'checkbox': 'lib/checkbox-svg',
    'utils': 'lib/utils-svg',
    'webfonts': 'lib/webfonts',
  }  
});