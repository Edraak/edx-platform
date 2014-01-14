define(["backbone", "js/models/xblock_info"], function(Backbone, XBlockInfo) {
    var XBlockInfoCollection = Backbone.Collection.extend({
        model: XBlockInfo
    });
    return XBlockInfoCollection;
});
