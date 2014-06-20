define(['js/views/baseview', 'underscore', 'gettext'],
function(BaseView, _, gettext) {
    'use strict';
    var ShowGroupConfiguration = BaseView.extend({
        tagName: 'section',
        className: 'group-configuration',
        events: {
            'click .show-groups': 'showGroups',
            'click .hide-groups': 'hideGroups'
        },

        initialize: function() {
            this.template = _.template(
                $('#show-group-configurations-tpl').text()
            );
            this.listenTo(this.model, 'change', this.render);
        },

        render: function() {
            var attrs = $.extend({}, this.model.attributes, {
                course: window.course.attributes,
                groupsCountMessage: this.getGroupsCountTitle()
            });

            this.$el.html(this.template(attrs));
            return this;
        },

        showGroups: function(e) {
            if(e && e.preventDefault) { e.preventDefault(); }
            this.model.set('showGroups', true);
        },

        hideGroups: function(e) {
            if(e && e.preventDefault) { e.preventDefault(); }
            this.model.set('showGroups', false);
        },

        getGroupsCountTitle: function () {
            var count = this.model.get('groups').length,
                message = ngettext(
                    'Contains %(count)s group', 'Contains %(count)s groups',
                    count
                );

            return interpolate(message, { count: count }, true);
        }
    });

    return ShowGroupConfiguration;
});
