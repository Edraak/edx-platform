import logging

from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.mail import send_mail

from .utils import get_client_ip
from edxmako.shortcuts import render_to_response, render_to_string
from util.json_request import JsonResponse

log = logging.getLogger(__name__)


@ensure_csrf_cookie
def contact(request):
    if request.method == 'POST':
        post = request.POST  # shortcut

        missing_contact_field = not all([post['firstname'], post['lastname'], post['email'], post['message']])
        missing_inquiry_type_in_help = (request.GET['form'] == 'help' and not post['inquiry-type'])

        if missing_contact_field or missing_inquiry_type_in_help:
            return render_to_response("static_templates/theme-contact.html", {'error': True})

        ##################################### We will need this #####################################
        # import urllib, urllib2                                                                    #
        #                                                                                           #
        # recaptcha_private_key = '6LfLjfMSAAAAAHPCSEZ3HvMzIYDSXrgA3AFYpQKI'                        #
        #                                                                                           #
        # recaptcha_server_name = 'http://www.google.com/recaptcha/api/verify'                      #
        # recaptcha_server_form = 'https://www.google.com/recaptcha/api/challenge'                  #
        #                                                                                           #
        # client_ip_address = get_client_ip(request)                                                #
        # recaptcha_challenge_field = post['recaptcha_challenge_field']                             #
        # recaptcha_response_field = post['recaptcha_response_field']                               #
        #                                                                                           #
        # params = urllib.urlencode(dict(privatekey=recaptcha_private_key,                          #
        #                            remoteip=client_ip_address,                                    #
        #                            challenge=recaptcha_challenge_field,                           #
        #                            response=recaptcha_response_field))                            #
        #                                                                                           #
        # try:                                                                                      #
        #     data = urllib2.urlopen(recaptcha_server_name, params)                                 #
        #     response = data.read()                                                                #
        #     data.close()                                                                          #
        #     if response:                                                                          #
        #         if response.lower().startswith('true'):                                           #
        #             result = True                                                                 #
        #         else:                                                                             #
        #             params = {'error': True, 'captcha': True}                                     #
        #             return render_to_response("static_templates/theme-contact.html", params)      #
        # except:                                                                                   #
        #     # should return a google error                                                        #
        #     return render_to_response("static_templates/theme-contact.html", {'error': True})     #
        ###################################### Do NOT Delete ########################################


        # send e-mail
        if request.GET['form'] == 'help':
            dest_addr = settings.CONTACT_EMAIL
        else:
            dest_addr = settings.COLLABORATE_EMAIL

        context = {
                'firstname': post.get('firstname', ''),
                'lastname': post.get('lastname', ''),
                'email': post.get('email', ''),
                'inquiry_type': post.get('inquiry-type', ''),
                'message': post.get('message', ''),
                'profession': post.get('profession', ''),
                'interest': post.get('interest', ''),
                'instorg': post.get('instorg', ''),
                'institution': post.get('institution', ''),
                'discipline': post.get('discipline', ''),
                'course_title': post.get('course-title'),
                'country': post.get('country', ''),
        }

        message = render_to_string('contact/email.txt', context)

        # Meaningful email subject for community manager
        subject_sliced = post['message'][:25]
        full_name = u'%s, %s' % (post['firstname'], post['lastname'])
        full_subject = u'%s: %s' % (full_name, subject_sliced)

        from_address = post['email']

        js = {}

        try:
            send_mail(full_subject, message, from_address, [dest_addr], fail_silently=False)
        except Exception:  # pylint: disable=broad-except
            log.warning('Unable to send contact email', exc_info=True)
            js['error'] = 'e-mail not sent...e-mail exception'
            # What is the correct status code to use here? I think it's 500, because
            # the problem is on the server's end -- but also, the account was created.
            # Seems like the core part of the request was successful.
            return JsonResponse(js, status=500)

        return render_to_response("static_templates/theme-contact.html", {'success': True})
    return render_to_response("static_templates/theme-contact.html", {})
