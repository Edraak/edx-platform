from xblock.core import Scope
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session


def get_xblock_metadata(module, metadata_whitelist):
    metadata = {}
    for field in module.fields + module.lms.fields:
        if field.name not in metadata_whitelist:
            continue
        # Only save metadata that wasn't inherited
        if field.scope != Scope.settings:
            continue

        try:
            metadata[field.name] = module._model_data[field.name]
        except KeyError:
            # Ignore any missing keys in _model_data
            pass

    return metadata


def get_xblock_summary(module, metadata_whitelist):
    metadata = get_xblock_metadata(module, metadata_whitelist)

    summary = {
        'category': module.location.category,
        'metadata': metadata,
        'children': getattr(module, 'children', []),
        'definition': module.location.url()
    }

    return summary


def get_user_from_token(request):
    # can pass in as query string parameter or cookie
    if 'token' in request.GET:
        token = request.GET['token']
    elif 'token' in request.COOKIES:
        token = request.COOKIES['token']
    else:
        return None

    try:
        session = Session.objects.get(session_key=token)
    except Session.DoesNotExist:
        return None

    uid = session.get_decoded().get('_auth_user_id')
    user = User.objects.get(pk=uid)
    return user
