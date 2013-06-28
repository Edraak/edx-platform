import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.envs.aws")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.
from django.core.wsgi import WSGIHandler


class ForceDataReadHandler(WSGIHandler):
    def get_response(self, request):
        """
        GET and POST are lazy evaluated.
        Force read them before passing them to django
        """
        query = request.GET
        data = request.POST

        return super(ForceDataReadHandler, self).get_response(request)

application = ForceDataReadHandler()

from django.conf import settings
from xmodule.modulestore.django import modulestore

for store_name in settings.MODULESTORE:
    modulestore(store_name)
