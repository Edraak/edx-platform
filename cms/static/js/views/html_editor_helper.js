define(["jquery.tinymce"], //, 'js/utils/handle_iframe_binding', "utility"],
    function(TinyMCE) { //}, IframeBinding) {

    var editWithTinyMCE = function(model, contentName, baseAssetUrl, textArea) {
        var content = rewriteStaticLinks(model.get(contentName), baseAssetUrl, '/static/');
        model.set(contentName, content);
        
        tinyMCE.init({
            // General options
        	mode : "specific_textareas",
            editor_selector : "mceEditor",
            theme : "modern",
            menubar : false,

            // Toolbar options
            plugins : "image,codemirror",
            toolbar: "formatselect,fontselect,bold,italic,underline,forecolor,|,bullist,numlist,outdent,indent,|,blockquote,wrapAsCode,|,link,unlink,|,image,code",
            block_formats: "Paragraph=p;Preformatted=pre;Header 1=h1;Header 2=h2;Header 3=h3",

            codemirror: {
                indentOnInit: true, // Whether or not to indent code on init. 
                path: 'CodeMirror', // Path to CodeMirror distribution
            },

        });

    };


//        var changeContentToPreview = function (model, contentName, baseAssetUrl) {
//            var content = rewriteStaticLinks(model.get(contentName), '/static/', baseAssetUrl);
//            // Modify iframe (add wmode=transparent in url querystring) and embed (add wmode=transparent as attribute)
//            // tags in html string (content) so both tags will attach to dom and don't create z-index problem for other popups
//            // Note: content is modified before assigning to model because embed tags should be modified before rendering
//            // as they are static objects as compared to iframes
//            content = IframeBinding.iframeBindingHtml(content);
//            model.set(contentName, content);
//            return content;
//        };

        return {'editWithTinyMCE': editWithTinyMCE}; //, 'changeContentToPreview': changeContentToPreview};
    }
);