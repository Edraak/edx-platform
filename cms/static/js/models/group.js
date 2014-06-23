define(['backbone', 'backbone.associations'], function(Backbone) {
    'use strict';
    var Group = Backbone.AssociatedModel.extend({
        defaults: function() {
            return {
                name: '',
                order: this.collection ? this.collection.nextOrder() : 1
            };
        },

        isEmpty: function() {
            return !this.get('name');
        },

        toJSON: function() {
            return {
                name: this.get('name')
            };
        },

        // NOTE: validation functions should return non-internationalized error
        // messages. The messages will be passed through gettext in the
        // template.
        validate: function(attrs) {
            if (!attrs.name) {
                return {
                    message: 'Group name is required',
                    attributes: {name: true}
                };
            }
        }
    });
    return Group;
});
