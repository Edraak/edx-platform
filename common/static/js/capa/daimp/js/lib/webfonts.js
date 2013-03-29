(function (requirejs, require, define) {
define(function () {  
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
}(RequireJS.requirejs, RequireJS.require, RequireJS.define));