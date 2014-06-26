define([
    'js/views/baseview', 'jquery', 'js/views/group_configuration_details',
    'js/views/group_configuration_edit'
], function(
    BaseView, $, GroupConfigurationDetailsView, GroupConfigurationEditView
) {
    'use strict';
    var GroupConfigurationsItem = BaseView.extend({
        tagName: 'section',
        attributes: {
            'tabindex': -1
        },

        className: function () {
            var index = this.model.collection.indexOf(this.model);

            return [
                'group-configuration',
                'group-configurations-list-item',
                'group-configurations-list-item-' + index
            ].join(' ');
        },

        initialize: function() {
            this.listenTo(this.model, 'change:editing', this.render);
            this.listenTo(this.model, 'remove', this.remove);
        },

        render: function() {
            // Removes a view from the DOM, and calls stopListening to remove
            // any bound events that the view has listenTo'd.
            if (this.view) {
                this.view.remove();
            }

            if (this.model.get('editing')) {
                this.view = new GroupConfigurationEditView({
                    model: this.model
                });
            } else {
                this.view = new GroupConfigurationDetailsView({
                    model: this.model
                });
            }

            this.$el.html(this.view.render().el);

            return this;
        }
    });

    return GroupConfigurationsItem;
});
