

import json
import time

from django.conf import settings
from django.http import HttpResponse
from django.utils.importlib import import_module
from django.views.generic.base import View

from sessions.middleware import patch_session_object

def sessions_report(request):

    session_key = request.GET.get('key')
    iterations = int(request.GET.get('iterations', 100))
    sleep_time = float(request.GET.get('sleep', 0.0))

    engine = import_module(settings.SESSION_ENGINE)
    session = engine.SessionStore(session_key)
    patch_session_object(session)

    if session_key is None:
        session['key'] = 'value'
        session.save()

    response = ''
    misses = 0
    for iteration in range(0, iterations):

        data = session.load()

        status = 'Found '
        if not data:
            status = 'Empty '
            misses += 1

        result = '{0}: {1} {2}\n'.format(iteration, status, json.dumps(data))
        response += result

        if sleep_time is not None:
            time.sleep(sleep_time)

    response = '-------- Key: {0} ----  Misses: {1} ----- \n'.format(session.session_key, misses) + response

    return HttpResponse(response, content_type="text/plain")
