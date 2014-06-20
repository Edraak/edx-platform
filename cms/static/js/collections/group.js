define(['backbone', 'js/models/group'], function(Backbone, GroupModel) {
    'use strict';
    var GroupCollection = Backbone.Collection.extend({
        model: GroupModel,
        comparator: 'order',
        nextOrder: function() {
            if(!this.length) {
                return 1;
            }
            return this.last().get('order') + 1;
        },
        isEmpty: function() {
            return this.length === 0 || this.every(function(m) {
                return m.isEmpty();
        });
        }
    });
    return GroupCollection;
});
