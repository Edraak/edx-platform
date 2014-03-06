define(["jquery", "underscore", "js/views/baseview", "js/views/xblock_type"],
    function($, _, BaseView, XBlockTypeView) {
        var XBlockTypeListView = BaseView.extend({
            events : {
                'click .card': 'selectCard'
            },

            render: function() {
                var self = this,
                    root = this.root,
                    xblockTypes = this.collection,
                    table;
                this.$el.html('<div class="xblock-type-table"></div>');
                this.tableBody = this.$('.xblock-type-table');
                xblockTypes.each(_.bind(this.renderType, this));

                return this;
            },

            renderType: function(type) {
                var view = new XBlockTypeView({model: type});
                this.tableBody.append(view.render().el);
            },

            selectCard: function(event) {
                var card = this.$(event.target).closest('.card'),
                    oldCard = this.selectedCard;
                if (oldCard) {
                    oldCard.toggleClass('is-selected');
                }
                card.toggleClass('is-selected');
                this.selectedCard = card;
            }
        });

        return XBlockTypeListView;
    });
