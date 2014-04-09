describe("Tests for cross_browser.js", function() {
	describe("Test for disabled links in IE", function() {

		beforeEach(function (){
			setFixtures("<div><a class='ui-disabled' href='://www.example.com'>link</a></div>");
		});

		it("affirms that jquery version is less than 1.9", function() {
			expect($.fn.jquery.split(".") < [1, 9]).toBe(true);
		});

		it("prevents click events on disabled links", function() {
			// mock $.browser
			$.browser = {"msie": true, "version": "10.0"};
			$("a").click();
			expect('click').toHaveBeenPreventedOn("a");
			expect('click').toHaveBeenTriggeredOn("div");
		});

		it("does not prevent click events on disabled links for other browsers", function() {
			var browsers = [
				{"msie": true, "version": "11.0"},
				{"mozilla": true, "version": "28.0"}
			];
			for (var i = 0; i < browsers.length; i++) {
				// mock $.browser
				$.browser = browsers[i];
				$("a").click();
				expect('click').not.toHaveBeenPreventedOn("a");
			};
		});
	});
});
