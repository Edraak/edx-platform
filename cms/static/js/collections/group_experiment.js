define(['backbone', 'js/models/group_experiment'],
function(Backbone, GroupExperimentModel) {
    'use strict';
    var GroupExperimentCollection = Backbone.Collection.extend({
        model: GroupExperimentModel,
        url: function() { return CMS.URL.GROUP_EXPERIMENTS; }
    });
    return GroupExperimentCollection;
});
