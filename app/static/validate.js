//
// Email Address Validation Plugin
// forked from https://github.com/validation/mailgun-demo/blob/master/mailgun_validator.js
//
// Attaching to a form:
//
//    $('jquery_selector').email_validator({
//        api_url: 'https://email-address-validator.herokuapp.com/validate'
//        api_key: 'api-key',
//        in_progress: in_progress_callback, // called when request is made to validator
//        success: success_callback,         // called when validator has returned
//        error: validation_error,           // called when an error reaching the validator has occured
//    });
//
// Sample JSON in success callback:
//
//  {
//      "is_valid": true,
//      "parts": {
//          "local_part": "john.smith@example.com",
//          "domain": "example.com",
//      },
//      "address": "john.smith@example.com",
//      "did_you_mean": null
//  }
//
// To integrate with ActionKit field validation and error display:
//    actionkit_email_validate_init($form, api_url);
//

(function( $ ) {
    $.fn.email_validator = function(options) {
        return this.each(function() {
            var thisElement = $(this);
            thisElement.focusout(function(e) {
                //Trim string and autocorrect whitespace issues
                var elementValue = thisElement.val();
                elementValue = $.trim(elementValue);
                thisElement.val(elementValue);

                //Attach event to options
                options.e = e;
                run_validator(elementValue, options, thisElement);
            });
        });
    };

    function run_validator(address_text, options, element) {
        //Abort existing AJAX Request to prevent flooding
        if(element.validationRequest) {
            element.validationRequest.abort();
            element.validationRequest = null;
        }

        // don't run validator without input
        if (!address_text) {
            return;
        }

        // validator is in progress
        if (options && options.in_progress) {
            options.in_progress(options.e);
        }

        // don't run dupicate calls
        if (element.validationLastSuccessReturn) {
            if (address_text == element.validationLastSuccessReturn.address) {
                if (options && options.success) {
                    options.success(element.validationLastSuccessReturn, options.e);
                }
                return;
            }
        }

        // length and @ syntax check
        var error_message = false;
        if (address_text.length > 512)
            error_message = 'Email address exceeds maxiumum allowable length of 512.';
        else if (1 !== address_text.split('@').length-1)
            error_message = 'Email address must contain only one @.';

        if (error_message) {
            if (options && options.error) {
                options.error(error_message, options.e);
            }
            else {
                if (console) console.log(error_message);
            }
            return;
        }

        // require api key
        // if (options && options.api_key == undefined) {
        //     if (console) console.log('Please pass in api_key to validation_validator.');
        // }

        // timeout incase of some kind of internal server error
        var timeoutID = setTimeout(function() {
            error_message = 'Error occurred, unable to validate address.';
            if (!success) {
                //Abort existing AJAX Request for a true timeout
                if(element.validationRequest) {
                    element.validationRequest.abort();
                    element.validationRequest = null;
                }

                if (options && options.error) {
                    options.error(error_message, options.e);
                }
                else {
                    if (console) console.log(error_message);
                }
            }
        }, 30000); //30 seconds

        // make ajax call to get validation results
        element.validationRequest = $.ajax({
            type: "GET",
            url: options.api_url || 'https://email-address-validator.herokuapp.com/address/validate' ,
            data: { address: address_text, api_key: options.api_key },
            dataType: "json",
            crossDomain: true,
            success: function(data, status_text) {
                clearTimeout(timeoutID);

                element.validationLastSuccessReturn = data;
                if (options && options.success) {
                    options.success(data, options.e);
                }
            },
            error: function(request, status_text, error) {
                clearTimeout(timeoutID);
                error_message = 'Error occurred, unable to validate address.';

                if (options && options.error) {
                    options.error(error_message, options.e);
                }
                else {
                    if (console) console.log(error_message);
                }
            }
        });
    }
})( jQuery );

// ActionKit-specific form validation
function actionkit_email_validate_init(form, api_url) {
    if (!form) { form = $('form.ak-form'); }
    if (!api_url) { api_url = 'https://email-address-validator.herokuapp.com/address/validate'; }

    $('input[name=email]', form).email_validator({
        api_url: api_url,
        in_progress: function() {
            $('input[name=email]', form).removeClass('ak-error');
            actionkit.forms.clearErrors();
        },
        success: function(data) {
            if (data.is_valid === false) {
                actionkit.forms.onValidationErrors({"email:invalid": "Email is invalid"}, "email");
            }
            if (data.did_you_mean) {
                actionkit.forms.onValidationErrors({"email:did_you_mean": "<span class='email_suggestion'>"+
                                                   "Did you mean <a style='cursor: pointer; text-decoration: underline;'>"
                                                   +data.did_you_mean+"</a>?</span>"}, "email");
                $(form).on('click', '.email_suggestion a', function() {
                    $('input[name=email]', form).val(this.text).removeClass('ak-error');
                    $('.email_suggestion').remove();
                    actionkit.forms.clearErrors();
                });
            }
        }
    });
};
