define(["jquery", "underscore", "underscore.string", "js/views/baseview", "js/views/outline"], function($, _, str, BaseView, OutlineView) {
    var MoveComponentDialog = BaseView.extend({
        events : {
            "click .action-move": "move",
            "click .action-cancel": "hide"
        },

        options: $.extend({}, BaseView.prototype.options, {
            type: "prompt",
            closeIcon: false,
            icon: false
        }),

        initialize: function() {
            this.template = _.template($("#move-component-tpl").text());
        },

        render: function() {
            this.$el.html(this.template());
            this.outline = new OutlineView({el: $('#move-outline')});
            this.outline.root = this.xBlockInfo;
            this.outline.render();
            return this;
        },

        show: function() {
            $('body').addClass('dialog-is-shown');
            this.$('.wrapper-dialog-move-component').addClass('is-shown');
        },

        hide: function() {
            $('body').removeClass('dialog-is-shown');
            this.$('.wrapper-dialog-move-component').removeClass('is-shown');
        },

        move: function() {
            this.hide();
        }
    });

    return MoveComponentDialog;
});
