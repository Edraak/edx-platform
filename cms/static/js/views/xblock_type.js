define(["js/views/baseview", "underscore"],
    function(BaseView, _) {
        var XBlockTypeView = BaseView.extend({

            initialize: function() {
                this.template = _.template($("#card-tpl").text());
            },

            render: function() {
                var type = this.model,
                    html,
                    name = type.get('name'),
                    title = type.get('display_name'),
                    summary = type.get('summary'),
                    preview = type.get('screenshot');
                if (!title) {
                    title = name.replace(/_/g, ' ');
                }
                if (!preview) {
                    preview = 'http://vikparuchuri.github.io/boston-python-ml/assets/img/multiple_choice_problem.png';
                }
                html = this.template({
                    id: name,
                    title: title,
                    summary: summary,
                    preview: preview
                });
                this.setElement(html);
                return this;
            }
        });

        return XBlockTypeView;
    }); // end define()
