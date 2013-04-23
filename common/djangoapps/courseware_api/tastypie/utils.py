from xblock.core import Scope


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
