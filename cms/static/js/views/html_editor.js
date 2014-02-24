define(["js/views/baseview", "jquery.tinymce", "js/views/feedback_notification", "js/views/html_editor_helper", "js/utils/modal"],
    function(BaseView, TinyMCE, NotificationView, HtmlEditorHelper, ModalUtils) {
	
	var CourseInfoHandoutView = BaseView.extend({
		
        events: {
            "click .save-button" : "onSave",
            "click .cancel-button" : "onCancel",
            "click .edit-button" : "onEdit"
        },
        
        initialize: function() {
            this.template = _.template($("#course_info_handouts-tpl").text());
            var self = this;
            this.model.fetch({
                complete: function() {
                    self.render();
                },
                reset: true
            });
        },
        
        render: function () {
//        	HtmlEditorHelper.changeContentToPreview(
//                this.model, 'data', this.options['base_asset_url']);
//
            this.$el.html(
                $(this.template({
                    model: this.model
                }))
            );
            $('.handouts-content').html(this.model.get('data'));
            this.$preview = this.$el.find('.handouts-content');
            this.$form = this.$el.find(".edit-handouts-form");
            this.$editor = this.$form.find('.handouts-content-editor');
            this.$form.hide();

            return this;
        },
        
        onEdit: function(event) {
            var self = this;
            this.render();
            this.$editor.val(this.$preview.html());

            
            this.$form.show();

            HtmlEditorHelper.editWithTinyMCE(
            	  self.model, 'data', self.options['base_asset_url'], this.$editor.get(0));

            ModalUtils.showModalCover(false, function() { self.closeEditor() });
        },
        
        onSave: function(event) {
        	var editor_text = tinyMCE.get('handouts').getContent();
        	
            $('#handout_error').removeClass('is-shown');
            $('.save-button').removeClass('is-disabled');
            if ($('.tinyMCE-lines').find('.cm-error').length == 0){
            	
            	if (editor_text == "") {
            		editor_text = "<p>&nbsp;</p>";
            	}
            		
                this.model.set('data',  editor_text);
                var saving = new NotificationView.Mini({
                    title: gettext('Saving&hellip;')
                });
                saving.show();
                this.model.save({}, {
                    success: function() {
                        saving.hide();
                    }
                });
                this.render();
                this.$form.hide();
                this.closeEditor();

                analytics.track('Saved Course Handouts', {
                    'course': course_location_analytics
                });
            }else{
                $('#handout_error').addClass('is-shown');
                $('.save-button').addClass('is-disabled');
                event.preventDefault();
            }
        },
        
        onCancel: function(event) {
            $('#handout_error').removeClass('is-shown');
            $('.save-button').removeClass('is-disabled');
            this.$form.hide();
            this.closeEditor();
        },
        
        closeEditor: function() {
            $('#handout_error').removeClass('is-shown');
            $('.save-button').removeClass('is-disabled');
            this.$form.hide();
            ModalUtils.hideModalCover();
            this.$form.find('.CodeMirror').remove();
            this.$codeMirror = null;
        }
        
        
        
	});
	return CourseInfoHandoutView;
});