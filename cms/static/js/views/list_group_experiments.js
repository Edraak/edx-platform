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
                var frag = document.createDocumentFragment();

                experiments.each(function(experiment) {
                    var view = new ShowGroupExperimentView({
                        model: experiment
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
    return ListGroupExperiments;
});
