define(["jquery", "underscore", "underscore.string", "gettext", "js/views/baseview",
    "coffee/src/views/module_edit", "js/models/module_info",
    "js/collections/xblock_type", "js/models/xblock_type", "js/views/xblock_type_list"],
    function($, _, str, gettext, BaseView, ModuleEditView, ModuleModel,
             XBlockTypeCollection, XBlockType, XBlockTypeListView) {
        var AddXBlockDialog = BaseView.extend({
            events : {
                "click .action-add": "add",
                "click .action-cancel": "cancel"
            },

            options: $.extend({}, BaseView.prototype.options, {
                type: "prompt",
                closeIcon: false,
                icon: false
            }),

            initialize: function() {
                var collection;
                this.template = _.template($("#add-xblock-modal-tpl").text());
            },

            loadXBlockTypeInfo: function(xblockTypeInfoURL, options) {
                var collection = new XBlockTypeCollection();
                collection.url = xblockTypeInfoURL;
                this.collection = collection;
                collection.fetch(options);
            },

            render: function() {
                this.$el.html(this.template());
            },

            renderXBlockTypes: function() {
                var listView = new XBlockTypeListView({el: this.$('.xblock-list'), collection: this.collection});
                listView.render();
                this.listView = listView;
                return this;
            },

            showXBlockTypes: function(xblockTypeInfoUrl) {
                var self = this;
                if (!this.listView) {
                    this.loadXBlockTypeInfo(xblockTypeInfoUrl, {
                        success: function() {
                            self.renderXBlockTypes();
                            self.show();
                        }
                    });
                } else {
                    this.show();
                }
            },

            cancel: function(event) {
                event.preventDefault();
                this.hide();
            },

            show: function() {
                $('body').addClass('dialog-is-shown');
                this.$('.wrapper-dialog-add-xblock').addClass('is-shown');
            },

            hide: function() {
                $('body').removeClass('dialog-is-shown');
                this.$('.wrapper-dialog-add-xblock').removeClass('is-shown');
            },

            add: function(event) {
                var listView = this.listView,
                    card = listView.selectedCard,
                    editView = this.editView,
                    xblockName,
                    locator,
                    lastComponent;
                event.preventDefault();
                if (card) {
                    locator = card.data('locator');
                    if (locator) {
                        editView.duplicateComponent(event, null, locator);
                    } else {
                        xblockName = card.data('id');
                        editView.addNewComponent(event, { category: xblockName });
                    }
                    this.hide();
                    listView.clearSelection();
                    listView.$el.scrollTop();
                }
                return false;
            }
        });

        return AddXBlockDialog;
    });
