import functools

from django.conf import settings

class prefer_secondary_db(object):
    """
    Decorator. 

    If an "replica" db is specified in django settings, 
    it is provided to the function as the the value of the
    argument `secondary_db`.

    Example:

    @prefer_secondary_db('replica')
    def count_users(secondary_db=None):
        assert secondary_db is not None
        return User.objects.using(secondary_db).filter().count()

    count_users()
    
    will provide different results depending on the dbs defined in
    settings.py.  If a database named 'replica' is defined, it will
    return the number of users in the replica database.  If no such
    db is specified, it will return the number of users in the default
    db.

    """
    def __init__(self, secondary_db):
        if secondary_db in settings.DATABASES:
            self.secondary_db = secondary_db
        else:
            self.secondary_db = 'default'

    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            kwargs['secondary_db'] = self.secondary_db
            return fn(*args, **kwargs)

        return decorated