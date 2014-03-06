define(["backbone", "js/models/xblock_type"],
    function(Backbone, XBlockTypeModel) {
        var XBlockTypeCollection = Backbone.Collection.extend({
            model: XBlockTypeModel,
            url: function() { return "url_not_defined"; }
        });
        return XBlockTypeCollection;
    });
