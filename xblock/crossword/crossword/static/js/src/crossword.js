/* Javascript for CrosswordXBlock. */
function CrosswordXBlock(runtime, element) {

    var incrementCountUrl = runtime.handlerUrl(element, 'increment_count');
    var saveUrl = runtime.handlerUrl(element, 'save_settings');

    function updateCount(result) {
        $('.count', element).text(result.count);
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

    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
