define(["backbone", "js/collections/xblock_info"], function(Backbone, XBlockInfoCollection) {
    var XBlockInfo = Backbone.Model.extend({

        defaults: {
            "id": null,
            "display_name": null,
            "category": null,
            "is_draft": null,
            "is_container": null,
            "children": []
        }
    });
    return XBlockInfo;
});
