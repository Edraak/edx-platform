;(function (define) {
    'use strict';
    define([
            'jquery',
            'underscore',
            'js/student_account/views/FormView'
        ],
        function($, _, FormView) {

        return FormView.extend({
            el: '#register-form',

            tpl: '#register-tpl',

            events: {
                'click .js-register': 'submitForm',
                'click .login-provider': 'thirdPartyAuth',
                'contextmenu #register-confirm_email': 'preventCopyPaste',
                'cut #register-confirm_email': 'preventCopyPaste',
                'copy #register-confirm_email': 'preventCopyPaste',
                'paste #register-confirm_email': 'preventCopyPaste',
                'contextmenu #register-confirm_password': 'preventCopyPaste',
                'cut #register-confirm_password': 'preventCopyPaste',
                'copy #register-confirm_password': 'preventCopyPaste',
                'paste #register-confirm_password': 'preventCopyPaste'
            },

            formType: 'register',

            submitButton: '.js-register',

            preRender: function( data ) {
                this.providers = data.thirdPartyAuth.providers || [];
                this.hasSecondaryProviders = (
                    data.thirdPartyAuth.secondaryProviders && data.thirdPartyAuth.secondaryProviders.length
                );
                this.currentProvider = data.thirdPartyAuth.currentProvider || '';
                this.errorMessage = data.thirdPartyAuth.errorMessage || '';
                this.platformName = data.platformName;
                this.autoSubmit = data.thirdPartyAuth.autoSubmitRegForm;

                this.listenTo( this.model, 'sync', this.saveSuccess );
            },

            render: function( html ) {
                var fields = html || '';

                $(this.el).html( _.template( this.tpl, {
                    /* We pass the context object to the template so that
                     * we can perform variable interpolation using sprintf
                     */
                    context: {
                        fields: fields,
                        currentProvider: this.currentProvider,
                        errorMessage: this.errorMessage,
                        providers: this.providers,
                        hasSecondaryProviders: this.hasSecondaryProviders,
                        platformName: this.platformName
                    }
                }));

                this.postRender();

                if (this.autoSubmit) {
                    $(this.el).hide();
                    $('#register-honor_code').prop('checked', true);
                    this.submitForm();
                }

                return this;
            },

            thirdPartyAuth: function( event ) {
                var providerUrl = $(event.currentTarget).data('provider-url') || '';

                if ( providerUrl ) {
                    window.location.href = providerUrl;
                }
            },

            saveSuccess: function() {
                // Edraak (google-analytics): Send event on registration success
                if (ga) {
                  ga('send', 'event', {
                    eventCategory: 'Registration',
                    eventAction: 'Submit',
                    eventLabel: 'Register',
                    eventValue: 1,
                    transport: 'beacon'
                  });
                }

                if (fbq) {
                  fbq('track', 'CompleteRegistration', {status: 'successful'});
                }

                if (snaptr) {
                  snaptr('track', 'SIGN_UP', {success: 1});
                }

                this.trigger('auth-complete');
            },

            saveError: function( error ) {
                // Edraak (google-analytics): Send event on registration failure
                if (ga) {
                  ga('send', 'event', {
                    eventCategory: 'Registration',
                    eventAction: 'Submit',
                    eventLabel: 'Register',
                    eventValue: 0,
                    transport: 'beacon'
                  });
                }
                if (fbq) {
                  fbq('track', 'CompleteRegistration', {status: 'failed'});
                }
                if(snaptr) {
                  snaptr('track', 'SIGN_UP', {success: 0});
                }
                $(this.el).show(); // Show in case the form was hidden for auto-submission
                this.errors = _.flatten(
                    _.map(
                        JSON.parse(error.responseText),
                        function(error_list) {
                            return _.map(
                                error_list,
                                function(error) { return '<li>' + error.user_message + '</li>'; }
                            );
                        }
                    )
                );
                this.setErrors();
                this.toggleDisableButton(false);
            },

            postFormSubmission: function() {
                if (_.compact(this.errors).length) {
                    // The form did not get submitted due to validation errors.
                    $(this.el).show(); // Show in case the form was hidden for auto-submission
                }
            },

            //Edraak
            //Disable copying and pasting into confirm email and confirm password fields
            preventCopyPaste: function(event) {
                event.preventDefault();
            }
        });
    });
}).call(this, define || RequireJS.define);
