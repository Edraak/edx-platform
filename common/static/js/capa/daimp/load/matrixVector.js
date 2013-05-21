(function(requirejs, require, define) {
  //TO FIX --> VERY IMPORTANT
  //Hack to detect if the script has already been loaded, which happens when the
  //check button is pressed or when the tool is used in a sequential.
  //In that case, we have to reload the page, the tool will go blank otherwise.
  var n = 0;
  $("script").each(function() {
    if ($(this).attr("src") === "/static/js/capa/daimp/load/matrixVector.js") {
      n++;
    }
  });
  if (n === 1) {
    requirejs.config({
      baseUrl: '/static/js/capa/daimp'
    });
    //Load common code then load the application
    require(['lib/common'], function () {
      require(['app/matrixVector']);
    });
  }
  else if (n > 1) {
    //Force reload
    window.location.reload();
  }
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));