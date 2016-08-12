import hashlib
import urllib
import simplejson
from httplib2 import Http
import logging


from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore

from edraak_misc.utils import validate_email, get_absolute_url_prefix

from edxmako.shortcuts import render_to_response, render_to_string
from util.json_request import JsonResponse

from .models import BaytPublishedCertificate

log = logging.getLogger(__name__)


@require_POST
@login_required
def get_student_email(request):
    user_email = request.POST['bayt_email']
    course_name = request.POST['course_name']
    course_id = request.POST['course_id']
    cert_end = request.POST['cert_end']
    user_id = request.user.id

    if not validate_email(user_email):
        return JsonResponse({'success': False, 'error': _('Invalid Email')})

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        ## close the pop-up because there is sth wrong
        return JsonResponse({'success': False, 'error': 'Invalid ID'})

    if user.email == user_email:
        h = Http()
        params = {
            'secret_key': settings.BAYT_SECRET_KEY,
            'valid_until': cert_end,
            'certificate_name': course_name.encode('UTF-8'),
            'email_address': user_email
        }

        url = 'https://api.bayt.com/api/edraak-api/post.adp?' + urllib.urlencode(params)
        resp, content = h.request(url)
        json_content = simplejson.loads(content)

        if json_content['status'] == 'NOT EXISTS':
            return JsonResponse({
                'success': True,
                'error': False,
                'redirect_to': '{bayt_base}{register}'.format(
                    bayt_base=settings.BAYT_BASE,
                    register='/en/register-j/',
                ),
                'response': content,
            })
        else:
            BaytPublishedCertificate.objects.create(user_id=int(user_id), course_id=course_id)
            return JsonResponse({'success': True, 'error': False, 'redirect_to': False, 'response': content})
    else:
        secret_key = settings.BAYT_SECRET_KEY
        my_string = user_email + course_name + secret_key
        access_token = hashlib.md5(my_string.encode('UTF-8')).hexdigest()

        params = {
            'email': user_email,
            'course_name': course_name.encode('UTF-8'),
            'access_token': access_token,
            'course_id': course_id.encode('UTF-8'),
            'cert_end': cert_end,
            'user_id': user_id,
        }

        message = render_to_string('emails/bayt_verification_email.txt', {
            'activation_url': '{base}{view}?{params}'.format(
                base=get_absolute_url_prefix(request),
                view=reverse('bayt_activation'),
                params=urllib.urlencode(params)
            ),
        })

        try:
            subject = _('Verify your email to share your Edraak certificate on Bayt.com')
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
            # here we have to send an auth email to user email that contains a link to
            # get back to here and then post the certificate
            return JsonResponse({
                'success': True,
                'error': False,
                'redirect_to': reverse('bayt_check_email', kwargs={
                    'email': user_email,
                    'course_id': course_id,
                }),
            })
        except:
            log.warning('Unable to send activation email to user', exc_info=True)
            return JsonResponse({
                'success': False,
                'error': True,
                'redirect_to': False,
            })


@login_required
def check_email(request, course_id, email):
    course_key = CourseKey.from_string(course_id)
    course = modulestore().get_course(course_key)

    return render_to_response('bayt/check_email.html', {
        'course': course,
        'email': email,
    })


@login_required
def activation(request):
    access_token = request.GET['access_token']
    user_email = request.GET['email']
    course_name = request.GET['course_name']
    course_id = request.GET['course_id']
    cert_end = request.GET['cert_end']
    user_id = request.user.id
    secret_key = settings.BAYT_SECRET_KEY
    my_string = user_email + course_name + secret_key
    current_access_token = hashlib.md5(my_string.encode('UTF-8')).hexdigest()

    if current_access_token == access_token:
        connection = Http()

        resp, content = connection.request('{base}?{params}'.format(
            base='https://api.bayt.com/api/edraak-api/post.adp',
            params=urllib.urlencode({
                'secret_key': settings.BAYT_SECRET_KEY,
                'valid_until': cert_end,
                'certificate_name': course_name.encode('UTF-8'),
                'email_address': user_email
            }),
        ))

        json_content = simplejson.loads(content)

        if json_content['status'] == 'NOT EXISTS':
            # redirect user to bayt registration
            return render_to_response('bayt/callback.html', {
                'status': False,
                'redirect_url': '{bayt_base}{register}'.format(
                    bayt_base=settings.BAYT_BASE,
                    register='/en/register-j/',
                )
            })

        BaytPublishedCertificate.objects.create(user_id=user_id, course_id=course_id)
        return render_to_response('bayt/callback.html', {
            'status': True,
            'redirect_url': '{base}{view}'.format(
                base=get_absolute_url_prefix(request),
                view=reverse('dashboard'),
            ),
        })
    else:
        log.warning(
            'Access tokens don\'t match: current=\'%s\' original=\'%s\'',
            current_access_token,
            access_token,
        )
        return JsonResponse({'success': False, 'error': True, 'redirect_to': False})
