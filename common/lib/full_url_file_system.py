from django.core.files.storage import FileSystemStorage
from django.conf import settings

class FullUrlFileSystem(FileSystemStorage):
    """
    Just like the default filesystem, except it returns full
    urls for all its objects.

    For dev purposes only.  (We use s3 in prod.)
    """
    def url(self, name):
        partial_url = super(FullUrlFileSystem, self).url(name)
        return settings.BASE_URL + partial_url