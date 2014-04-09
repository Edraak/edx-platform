// Workarounds for cross-browser compatibility

// inspired by stackoverflow:
// http://stackoverflow.com/questions/9385213/how-to-make-internet-explorer-emulate-pointer-eventsnone/17978235#17978235
var pointerEventsNone = function (selector) {
	$(selector).on("click", function(event) {
		// Only for ie <= 10, since it does not support pointer-events.
		// Note that jquery.browser is deprecated in 1.9.
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
};
pointerEventsNone(".ui-disabled");
pointerEventsNone(".is-disabled");