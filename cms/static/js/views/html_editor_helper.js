define(["jquery.tinymce", 'js/utils/handle_iframe_binding', "utility"],
    function(TinyMCE, IframeBinding) {

    var editWithTinyMCE = function(model, contentName, baseAssetUrl, textArea) {
        var content = rewriteStaticLinks(model.get(contentName), baseAssetUrl, '/static/');
        model.set(contentName, content);
        
        tinyMCE.init({
            // General options
        	mode : "specific_textareas",
            editor_selector : "mceEditor",
            theme : "advanced",
            plugins : "pagebreak,style,layer,table,save,advhr,advimage,advlink,emotions,iespell,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template",

            // Theme options
            theme_advanced_buttons1 : "save,newdocument,|,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,styleselect,formatselect,fontselect,fontsizeselect",
            theme_advanced_buttons2 : "cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,cleanup,help,code,|,insertdate,inserttime,preview,|,forecolor,backcolor",
            theme_advanced_buttons3 : "tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,media,advhr,|,print,|,ltr,rtl,|,fullscreen",
            theme_advanced_buttons4 : "insertlayer,moveforward,movebackward,absolute,|,styleprops,|,cite,abbr,acronym,del,ins,attribs,|,visualchars,nonbreaking,template,pagebreak",
            theme_advanced_toolbar_location : "top",
            theme_advanced_toolbar_align : "left",
            theme_advanced_statusbar_location : "bottom",
            theme_advanced_resizing : true,

        });

    };
	

        var changeContentToPreview = function (model, contentName, baseAssetUrl) {
            var content = rewriteStaticLinks(model.get(contentName), '/static/', baseAssetUrl);
            // Modify iframe (add wmode=transparent in url querystring) and embed (add wmode=transparent as attribute)
            // tags in html string (content) so both tags will attach to dom and don't create z-index problem for other popups
            // Note: content is modified before assigning to model because embed tags should be modified before rendering
            // as they are static objects as compared to iframes
            content = IframeBinding.iframeBindingHtml(content);
            model.set(contentName, content);
            return content;
        };

        return {'editWithTinyMCE': editWithTinyMCE, 'changeContentToPreview': changeContentToPreview};
    }
);