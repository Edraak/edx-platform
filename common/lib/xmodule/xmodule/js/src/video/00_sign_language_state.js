(function (define) {

define(
'video/00_sign_language_state.js',
[],
function () {
"use strict";
    // SignLanguageState object - what this module "exports".
    return {
        getIsActive: function () {
            var isActive = $.cookie('use_sign_language');

            // Defaults both undefined and null to true
            if (isActive === false || isActive === 'false') {
                return false;
            } else {
                return true;
            }
        },
        setIsActive: function (newIsActive) {
            newIsActive = !!newIsActive;  // To keep it simple true or false

            $.cookie('use_sign_language', newIsActive, {
                expires: 3650,
                path: '/'
            });
        },
        shouldShowTooltip: function () {
            return !$.cookie('disable_sign_language_tooltip');
        },
        disableTooltip: function () {
            return $.cookie('disable_sign_language_tooltip', true);
        }
    }
});
}(RequireJS.define));

