import functools

from django.conf import settings

class prefer_alternate_db(object):
    """
    Decorator. 

    If an "replica" db is specified in django settings, 
    it is provided to the function as the the value of the
    argument `alternate_db`.

    Example:

    @prefer_alternate_db('replica')
    def count_users(alternate_db=None):
        assert alternate_db is not None
        return User.objects.using(alternate_db).filter().count()

    count_users()
    
    will provide different results depending on the dbs defined in
    settings.py.  If a database named 'replica' is defined, it will
    return the number of users in the replica database.  If no such
    db is specified, it will return the number of users in the default
    db.

    """

    def __init__(self, alternate_db):
        if alternate_db in settings.DATABASES:
            self.alternate_db = alternate_db
        else:
            self.alternate_db = 'default'

    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            kwargs['alternate_db'] = self.alternate_db
            return fn(*args, **kwargs)

        return decorated