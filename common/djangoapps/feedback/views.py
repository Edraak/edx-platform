
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.html import strip_tags
from django.core.mail import send_mail

import json


#@require_POST
@csrf_exempt
def submit_feedback(request):

    email = request.POST.get('email', None)

    if email is None and user.is_authenticated:
        email = request.user.email

    category = request.POST.get('category', None)
    msg = request.POST.get('msg', None)

    from_email = 'info@edx.org'
    recipient_list = ['jarv@edx.org']

    if category not in ['general', 'issue', 'account']:
        return HttpResponse(json.dumps({'error': 'Invalid category'}))
    elif msg is None or len(msg) > 500:
        return HttpResponse(json.dumps({'error': 'Message invalid'}))

    msg = strip_tags(msg)

    try:
        validate_email(email)
    except ValidateError:
        return HttpResponse(json.dump({'error': 'Invalid email'}))

    user_info = """
    User = {user}
    User agent = {user_agent}
    IP = {ip}
    """.format(
        user=request.user,
        ip=request.META['REMOTE_ADDR'],
        user_agent = request.META['HTTP_USER_AGENT'])

    msg = msg + user_info
    subject = '[{0}] - User feedback'.format(category)


    try:
        send_mail(subject,
                  msg, from_email, recipient_list,
                  fail_silently=False, auth_user=None,
                  auth_password=None, connection=None)
    except:
        log.exception(sys.exc_info())
        return HttpResponse(
            {'error': 'Could not send, please try again later'})

    return HttpResponse(json.dumps({'msg': 'Submitted'}))


