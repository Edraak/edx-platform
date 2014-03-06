define(["js/views/baseview", "underscore"],
    function(BaseView, _) {
        var XBlockTypeView = BaseView.extend({

            initialize: function() {
                this.template = _.template($("#card-tpl").text());
            },

            render: function() {
                var type = this.model,
                    html;
                html = this.template({
                    id: type.get('id'),
                    title: type.get('display_name'),
                    summary: type.get('summary'),
                    preview: type.get('screen_shot')
                });
                this.setElement(html);
                return this;
            }
        });

        return XBlockTypeView;
    }); // end define()
