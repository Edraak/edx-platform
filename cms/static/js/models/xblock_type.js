define(["backbone"], function(Backbone) {
    var XBlockType = Backbone.Model.extend({

        defaults: {
            "id": null,
            "display_name": null,
            "category": null,
            "enabled": true
        }
    });
    return XBlockType;
});
