define(['js/views/baseview', 'jquery', 'js/views/show_group_experiment'],
function(BaseView, $, ShowGroupExperimentView) {
    'use strict';
    var ListGroupExperiments = BaseView.extend({
        tagName: 'div',
        className: 'group-experiments-list',
        events: { },

        initialize: function() {
            this.emptyTemplate = this.loadTemplate('no-group-experiments');
            this.listenTo(this.collection, 'all', this.render);
            this.listenTo(this.collection, 'destroy', this.handleDestroy);
        },

        render: function() {
            var experiments = this.collection;
            if(experiments.length === 0) {
                this.$el.html(this.emptyTemplate());
            } else {
                this.$el.empty();
                var that = this;
                experiments.each(function(experiment) {
                    var view = new ShowGroupExperimentView({
                        model: experiment
                    });
                    that.$el.append(view.render().el);
                });
            }
            return this;
        },

        handleDestroy: function(model, collection) {
            collection.remove(model);
        }
    });
    return ListGroupExperiments;
});
