define(
    [
        "jquery", "underscore",
        "js/views/abstract_editor", "js/views/feedback_prompt",
        "js/views/feedback_notification", "js/models/uploads", "js/views/uploads"

    ],
function($, _, AbstractEditor, PromptView, NotificationView, FileUpload, UploadDialog) {

    var Translations = AbstractEditor.extend({
        events : {
            "click .setting-clear" : "clear",
            "click .create-setting" : "addEntry",
            "click .remove-setting" : "removeEntry",
            "click .upload-setting" : "uploadEntry"
        },

        templateName: "metadata-translations-entry",
        templateItemName: "metadata-translations-item",

        initialize: function () {
            var self = this,
                templateName = _.result(this, 'templateItemName'),
                tpl = document.getElementById(templateName).text;

            if(!tpl) {
                console.error("Couldn't load template for item: " + templateName);
            }

            this.templateItem = _.template(tpl);

            this.$el.on('change', 'select', function () {
                self.showClearButton();
                self.enableAdd();
                self.updateModel();
            });

            AbstractEditor.prototype.initialize.apply(this, arguments);
        },

        getDropdown: function () {
            var dropdown,
                filter = function (element, values) {
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
                    return filter(dropdown, values);
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

                return filter(dropdown, values);
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

        uploadEntry: function (event) {
            var self = this,
                target = $(event.currentTarget),
                lang = target.data('lang'),
                model = new FileUpload({
                  fileFormats: ['srt']
                }),
                view = new UploadDialog({
                    model: model,
                    url: self.model.get('urlRoot') + '/' + lang,
                    onSuccess: function (response) {
                        var dict = $.extend(true, {}, self.model.get('value'));

                        dict[lang] = response['videoId'];
                        self.model.setValue(dict);
                    }
                });

            $('.wrapper-view').after(view.show().el);
        },

        removeEntry: function (event) {
            if (event && event.preventDefault) {
                event.preventDefault();
            }

            var self = this,
                target = $(event.currentTarget),
                lang = target.data('lang'),
                filename = target.data('value');

            // If language is chosen, delete translation for current language
            if (lang && filename) {
                new PromptView.Warning({
                    title: gettext('Delete this translation?'),
                    message: gettext('Deleting this translation is permanent and cannot be undone.'),
                    actions: {
                        primary: {
                            text: gettext('Yes, delete this translation'),
                            click: function (view) {
                                view.hide();

                                notification = new NotificationView.Mini({
                                    title: gettext('Deleting&hellip;'),
                                });

                                notification.show();

                                $.ajax({
                                    url: self.model.get('urlRoot') + '/' + lang,
                                    type: 'DELETE',
                                    dataType: 'json',
                                    success: function (view) {
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
                // If language isn't chosen, just remove this field from view.
                self.removeFromEditor(lang);
            }
        },

        enableAdd: function() {
            this.$el.find('.create-setting').removeClass('is-disabled');
        },

        clear: function() {
            var self = this,
                currentLanguages = _.keys(self.model.get('value')),
                defaultValue = _.keys(self.model.get('default_value')),
                languages = _.difference(currentLanguages, defaultValue);

            // FIXME: Values should also be checked
            if (languages.length){
                new PromptView.Warning({
                    title: gettext('Delete translations?'),
                    message: gettext('Deleting these translations are permanent and cannot be undone.'),
                    actions: {
                        primary: {
                            text: gettext('Yes, delete these translations'),
                            click: function (view) {
                                view.hide();

                                notification = new NotificationView.Mini({
                                    title: gettext('Deleting&hellip;'),
                                });

                                notification.show();

                                $.ajax({
                                    url: self.model.get('urlRoot') + '/',
                                    type: 'DELETE',
                                    dataType: 'json',
                                    success: function (view) {
                                        notification.hide();
                                        AbstractEditor.prototype.clear.apply(self, arguments);
                                        if (_.isNull(self.model.getValue())) {
                                            self.$el.find('.create-setting').removeClass('is-disabled');
                                        }
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
                AbstractEditor.prototype.clear.apply(self, arguments);
                if (_.isNull(self.model.getValue())) {
                    this.$el.find('.create-setting').removeClass('is-disabled');
                }
            }
        }
    });

    return Translations;
});
