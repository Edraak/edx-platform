define([
    'js/views/baseview', 'underscore', 'underscore.string', 'jquery', 'gettext'
],
function(BaseView, _, str, $, gettext) {
    'use strict';
    _.str = str; // used in template
    var GroupEdit = BaseView.extend({
        tagName: 'li',
        events: {
            'change .group-name': 'changeName',
            'focus .group-name': 'onFocus',
            'blur .group-name': 'onBlur'
        },

        className: function() {
            var index = this.model.collection.indexOf(this.model);
            return 'field-group group group-' + index;
        },

        initialize: function() {
            this.template = this.loadTemplate('group-edit');
            this.listenTo(this.model, 'change', this.render);
        },

        render: function() {
            var index = this.model.collection.indexOf(this.model);

            this.$el.html(this.template({
                name: this.model.escape('name'),
                allocation: this.getAllocation(),
                index: index,
                groupId: this.getGroupId(index),
                error: this.model.validationError
            }));

            return this;
        },

        changeName: function(event) {
            if(event && event.preventDefault) { event.preventDefault(); }
            this.model.set({
                name: this.$('.group-name').val()
            }, {silent: true});

            return this;
        },

        getAllocation: function() {
            return Math.floor(100 / this.model.collection.length);
        },

        getGroupId: (function () {
            /*
                Translators: Dictionary used for creation ids for default group
                names. For example: A, B, AA in Group A, Group B, ..., Group AA,
                etc.
            */
            var dict = gettext('ABCDEFGHIJKLMNOPQRSTUVWXYZ').split(''),
                len = dict.length;

            var divide = function(numerator, denominator) {
                if (denominator === 0) {
                    return null;
                }

                return {
                    quotient: Math.floor(numerator/denominator),
                    remainder: numerator % denominator
                };
            };

            return function getId(number) {
                var id = '',
                    result = divide(number, len),
                    index;

                if (result) {
                    index = result.quotient - 1;

                    if (index < len) {
                      if (index > -1) {
                        id += dict[index];
                      }
                    } else {
                        id += getId(index);
                    }

                    return id + dict[result.remainder];
                }

                return number;
            };
        }()),

        onFocus: function () {
            this.$el.closest('.groups-fields').addClass('is-focused');
        },

        onBlur: function () {
            this.$el.closest('.groups-fields').removeClass('is-focused');
        }
    });

    return GroupEdit;
});
