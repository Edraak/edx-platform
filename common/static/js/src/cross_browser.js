// Workarounds for cross-browser compatibility

var disabledElements = ".ui-disabled .is-disabled";

// inspired by stackoverflow:
// http://stackoverflow.com/questions/9385213/how-to-make-internet-explorer-emulate-pointer-eventsnone/17978235#17978235
$(disabledElements).on("click", function(event) {
	// Only for ie <= 10, since it does not support pointer-events.
	// Note that jquery.browser is be deprecated in 1.9.
	if ($.browser.msie && ($.browser.version < 11)) {
		event.preventDefault();
		$(this).hide(0, function () {
			var BottomElement = document.elementFromPoint(
				event.clientX, event.clientY
			);
            console.log(BottomElement);
			$(BottomElement).click();
			$(this).show();
		});
	};
});
