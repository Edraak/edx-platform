
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
import json


@require_POST
@csrf_protect
def submit_feedback(request):

    email = request.POST.get('email', None)

    if email is None and user.is_authenticated:
        email = request.user.email
    try:
        validate_email(email)
    except ValidationError:
        return HttpResponse(json.dumps({'error': 'Invalid email'}),
                                content_type="application/json")

    category = request.POST.get('category', '')
    description = request.POST.get('description', '')

    from_email = 'info@edx.org'
    recipient_list = ['jarv@edx.org']

    if category not in ['general', 'issue', 'account', 'other']:
        return HttpResponse(json.dumps({'error': 'Invalid category'}),
                                content_type="application/json")
    elif not description or len(description) > 500:
        return HttpResponse(json.dumps({'error': 'Message invalid'}),
                                content_type="application/json")

    description = strip_tags(description)

    user_info = """
    User = {user}
    User agent = {user_agent}
    IP = {ip}
    """.format(
        user=request.user,
        ip=request.META['REMOTE_ADDR'],
        user_agent = request.META['HTTP_USER_AGENT'])

    description = description + user_info
    subject = '[{0}] - User feedback'.format(category)


    try:
        send_mail(subject,
                  description, from_email, recipient_list,
                  fail_silently=False, auth_user=None,
                  auth_password=None, connection=None)
        return HttpResponse(json.dumps({'success': 'Submitted'}),
                                content_type="application/json")
    except:
        return HttpResponse(
            {'error': 'Could not send, please try again later'})


