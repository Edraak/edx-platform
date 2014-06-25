define(['js/views/baseview', 'jquery', 'js/views/show_group_configuration'],
function(BaseView, $, ShowGroupConfigurationView) {
    'use strict';
    var ListGroupConfigurations = BaseView.extend({
        tagName: 'div',
        className: 'group-configurations-list',
        events: { },

        initialize: function() {
            this.emptyTemplate = this.loadTemplate('no-group-configurations');
            this.listenTo(this.collection, 'all', this.render);
            this.listenTo(this.collection, 'destroy', this.handleDestroy);
        },

        render: function() {
            var configurations = this.collection;
            if(configurations.length === 0) {
                this.$el.html(this.emptyTemplate());
            } else {
                var frag = document.createDocumentFragment();

                configurations.each(function(configuration) {
                    var view = new ShowGroupConfigurationView({
                        model: configuration
                    });

                    frag.appendChild(view.render().el);
                });

                this.$el.html([frag]);
            }
            return this;
        },

        handleDestroy: function(model, collection) {
            collection.remove(model);
        }
    });

    return ListGroupConfigurations;
});
