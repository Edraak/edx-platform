/* Javascript for CrosswordXBlock. */
function CrosswordXBlock(runtime, element) {

    var incrementCountUrl = runtime.handlerUrl(element, 'increment_count');
    var saveUrl = runtime.handlerUrl(element, 'save_settings');

    function updateCount(result) {
        $('.count', element).text(result.count);
    }

    CrosswordXBlock.prototype.setMetadataEditor = function(metadataEditor) {
        this.metadataEditor = metadataEditor;
    }

    CrosswordXBlock.prototype.save = function() {
        return false;
    }

    $('p', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: incrementCountUrl,
            data: JSON.stringify({"hello": "world"}),
            success: updateCount
        });
    });

    $('.crossword-save-button', element).click(function(eventObject) {
        runtime.notify('save', {state: 'start'});
        $.ajax({
            type: "POST",
            url: saveUrl,
            data: metadataEditor.getModifiedMetadataValues(),
            success: runtime.notify('save', {state: 'end'})
        });
    });

    $('.crossword-cancel-button', element).click(function(eventObject) {
        runtime.notify('cancel', {});
    });

    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}


