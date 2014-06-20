define(['backbone', 'js/models/group_configuration'],
function(Backbone, GroupConfigurationModel) {
    'use strict';
    var GroupConfigurationCollection = Backbone.Collection.extend({
        model: GroupConfigurationModel,
        url: function() { return CMS.URL.TEXTBOOKS; }
    });
    return GroupConfigurationCollection;
});
