define(
    [
        "jquery", "underscore",
        "js/views/abstract_editor", "js/views/feedback_prompt",
        "js/views/feedback_notification", "js/models/uploads", "js/views/uploads"

    ],
function($, _, AbstractEditor, PromptView, NotificationView, FileUpload, UploadDialog) {
    "use strict";
    var Translations = AbstractEditor.extend({
        events : {
            "click .setting-clear" : "clear",
            "click .create-setting" : "addEntry",
            "click .remove-setting" : "remove",
            "click .upload-setting" : "upload",
            "change select" : "onChangeHandler"
        },

        templateName: "metadata-translations-entry",
        templateItemName: "metadata-translations-item",

        initialize: function () {
            var templateName = _.result(this, 'templateItemName'),
                tpl = document.getElementById(templateName).text;

            if(!tpl) {
                console.error("Couldn't load template for item: " + templateName);
            }

            this.templateItem = _.template(tpl);
            AbstractEditor.prototype.initialize.apply(this, arguments);
        },

        getDropdown: function () {
            var dropdown,
                disableOptions = function (element, values) {
                    var dropdown = $(element).clone();

                    _.each(values, function(value, key) {
                        var option = dropdown[0].options.namedItem(key);

                        if (option) {
                            option.disabled = true;
                        }
                    });

                    return dropdown;
                };

            return function (values) {
                if (dropdown) {
                    return disableOptions(dropdown, values);
                }

                dropdown = document.createElement('select');
                dropdown.options.add(new Option());
                _.each(this.model.get('languages'), function(lang, index) {
                    var option = new Option();

                    option.setAttribute('name', lang.code);
                    option.value = lang.code;
                    option.text = lang.label;
                    dropdown.options.add(option);
                });

                return disableOptions(dropdown, values);
            };
        }(),

        getValueFromEditor: function () {
            var dict = {},
                items = this.$el.find('ol').find('.list-settings-item');

            _.each(items, function(element, index) {
                var key = $(element).find('select').val(),
                    value = $(element).find('.input').val();

                // Keys should be unique, so if our keys are duplicated and
                // second key is empty or key and value are empty just do
                // nothing. Otherwise, it'll be overwritten by the new value.
                if (value === '') {
                    if (key === '' || key in dict) {
                        return false;
                    }
                }

                dict[key] = value;
            });

            return dict;
        },

        setValueInEditor: function (values) {
            var self = this,
                frag = document.createDocumentFragment(),
                dropdown = self.getDropdown(values);

            _.each(values, function(value, key) {
                var html = $(self.templateItem({
                        'lang': key,
                        'value': value,
                        'url': self.model.get('urlRoot') + '/' + key
                    })).prepend(dropdown.clone().val(key))[0];

                frag.appendChild(html);
            });

            this.$el.find('ol').html([frag]);
        },

        addEntry: function(event) {
            event.preventDefault();
            // We don't call updateModel here since it's bound to the
            // change event
            var dict = $.extend(true, {}, this.model.get('value'));
            dict[''] = '';
            this.setValueInEditor(dict);
            this.$el.find('.create-setting').addClass('is-disabled');
        },

        removeFromEditor: function(entry) {
            this.setValueInEditor(_.omit(this.model.get('value'), entry));
            this.updateModel();
            this.$el.find('.create-setting').removeClass('is-disabled');
        },

        upload: function (event) {
            var self = this,
                target = $(event.currentTarget),
                lang = target.data('lang'),
                model = new FileUpload({
                    title: gettext('Upload translation.'),
                    fileFormats: ['srt']
                }),
                view = new UploadDialog({
                    model: model,
                    url: self.model.get('urlRoot') + '/' + lang,
                    onSuccess: function (response) {
                        if (!response['filename']) { return; }

                        var dict = $.extend(true, {}, self.model.get('value'));

                        dict[lang] = response['filename'];
                        self.model.setValue(dict);
                    }
                });

            $('.wrapper-view').after(view.show().el);
        },

        remove: function (event) {
            if (event && event.preventDefault) {
                event.preventDefault();
            }

            var self = this,
                target = $(event.currentTarget),
                lang = target.data('lang'),
                filename = target.data('value');

            // If file was uploaded, send an ajax request to remove the translation.
            if (lang && filename) {
                new PromptView.Warning({
                    title: gettext('Delete this translation?'),
                    message: gettext('Deleting this translation is permanent and cannot be undone.'),
                    actions: {
                        primary: {
                            text: gettext('Yes, delete this translation'),
                            click: function (view) {
                                view.hide();

                                var notification = new NotificationView.Mini({
                                    title: gettext('Deleting&hellip;'),
                                }).show();

                                $.ajax({
                                    url: self.model.get('urlRoot') + '/' + lang,
                                    type: 'DELETE',
                                    dataType: 'json',
                                    success: function (response) {
                                        // remove field from view.
                                        self.removeFromEditor(lang);
                                        notification.hide();
                                    }
                                });
                            }
                        },
                        secondary: {
                            text: gettext('Cancel'),
                            click: function (view) {
                                view.hide();
                            }
                        }
                    }
                }).show();
            } else {
                // If file isn't uploaded, just remove this field from view.
                this.removeFromEditor(lang);
            }
        },

        enableAdd: function() {
            this.$el.find('.create-setting').removeClass('is-disabled');
        },

        revertModel: function () {
            AbstractEditor.prototype.clear.apply(this, arguments);
            if (_.isNull(this.model.getValue())) {
                this.$el.find('.create-setting').removeClass('is-disabled');
            }
        },

        clear: function() {
            var self = this,
                values = _.values(self.getValueFromEditor()).filter(_.identity),
                defaultValues = _.values(self.model.get('default_value')),
                difference = _.difference(values, defaultValues);

            // If we have a `difference`, it means, that some files were uploaded
            // and we send an ajax request to remove them on backend.
            if (difference.length){
                new PromptView.Warning({
                    title: gettext('Delete translations?'),
                    message: gettext('Deleting these translations are permanent and cannot be undone.'),
                    actions: {
                        primary: {
                            text: gettext('Yes, delete these translations'),
                            click: function (view) {
                                view.hide();

                                var notification = new NotificationView.Mini({
                                    title: gettext('Deleting&hellip;'),
                                }).show();

                                $.ajax({
                                    url: self.model.get('urlRoot') + '/',
                                    type: 'DELETE',
                                    dataType: 'json',
                                    success: function (response) {
                                        self.revertModel();
                                        notification.hide();
                                    }
                                });
                            }
                        },
                        secondary: {
                            text: gettext('Cancel'),
                            click: function (view) {
                                view.hide();
                            }
                        }
                    }
                }).show();
            } else {
                // If files aren't uploaded, just revert the model and update view.
                this.revertModel();
            }
        },

        onChangeHandler: function (event) {
            this.showClearButton();
            this.enableAdd();
            this.updateModel();
        }
    });

    return Translations;
});
