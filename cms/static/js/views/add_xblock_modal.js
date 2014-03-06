define(["jquery", "underscore", "underscore.string", "js/views/baseview",
    "coffee/src/views/module_edit", "js/models/module_info",
    "js/collections/xblock_type", "js/models/xblock_type", "js/views/xblock_type_list"],
    function($, _, str, BaseView, ModuleEditView, ModuleModel, XBlockTypeCollection, XBlockType, XBlockTypeListView) {
        var AddXBlockDialog = BaseView.extend({
            events : {
                "click .action-add": "add",
                "click .action-cancel": "hide"
            },

            options: $.extend({}, BaseView.prototype.options, {
                type: "prompt",
                closeIcon: false,
                icon: false
            }),

            initialize: function() {
                var collection;
                this.template = _.template($("#add-xblock-modal-tpl").text());
                collection = new XBlockTypeCollection();
                collection.add(new XBlockType({
                    id: 'acid',
                    display_name: 'Acid XBlock',
                    screen_shot: 'http://vikparuchuri.github.io/boston-python-ml/assets/img/multiple_choice_problem.png',
                    summary: "This is a simple XBlock used for testing."
                }));
                collection.add(new XBlockType({
                    id: 'acid-parent',
                    display_name: 'Acid Parent XBlock',
                    screen_shot: 'http://vikparuchuri.github.io/boston-python-ml/assets/img/multiple_choice_problem.png',
                    summary: "This is a simple XBlock that can test parenting."
                }));
                collection.add(new XBlockType({
                    id: 'conditional',
                    display_name: 'Conditional',
                    screen_shot: 'http://vikparuchuri.github.io/boston-python-ml/assets/img/multiple_choice_problem.png',
                    summary: "This provides a conditional rendering of its children."
                }));
                collection.add(new XBlockType({
                    id: 'another',
                    display_name: 'Yet Another XBlock',
                    screen_shot: 'http://vikparuchuri.github.io/boston-python-ml/assets/img/multiple_choice_problem.png',
                    summary: "This is yet another xblock that does something or other."
                }));
                this.collection = collection;
            },

            render: function() {
                var listView;
                this.$el.html(this.template());
                listView = new XBlockTypeListView({el: this.$('.xblock-list'), collection: this.collection});
                listView.render();
                this.listView = listView;
                return this;
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
                var card = this.listView.selectedCard,
                    xblockName = card.data('id'),
                    editView = this.editView,
                    callback;
//                editView.createComponent(event, )
                this.hide();
            }
        });

        return AddXBlockDialog;
    });
