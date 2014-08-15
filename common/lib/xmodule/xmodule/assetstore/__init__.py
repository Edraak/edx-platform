

from opaque_keys.edx.keys import CourseKey, AssetKey


class AssetMetadata(object):
    """
    Stores the metadata associated with a particular course asset. The asset metadata gets stored
    in the modulestore.
    """

    TOP_LEVEL_ATTRS = ['filepath', 'internal_name', 'locked']
    EDIT_INFO_ATTRS = ['curr_version', 'prev_version', 'edited_by', 'edited_on']
    ALLOWED_ATTRS = TOP_LEVEL_ATTRS + EDIT_INFO_ATTRS

    def __init__(self, asset_id, upload_name,
                 filepath=None, internal_name=None, locked=None,
                 curr_version=None, prev_version=None,
                 edited_by=None, edited_on=None, **kwargs):
        """
        Construct a AssetMetadata object.
        """
        self.asset_id = asset_id
        self.upload_name = upload_name
        self.filepath = filepath  # Path w/o filename.
        self.internal_name = internal_name
        self.locked = locked
        self.curr_version = curr_version
        self.prev_version = prev_version
        self.edited_by = edited_by
        self.edited_on = edited_on

    def __eq__(self, other):
        return self.asset_id == other.asset_id and self.upload_name == other.upload_name

    def __repr__(self):
        return """asset_id: {} upload_name: {}\nfilepath: '{}' internal_name: '{}' locked: {} curr_version: {} prev_version: {} edited_by: {} edited_on: {}"""\
                .format(self.asset_id, self.upload_name,
                        self.filepath, self.internal_name, self.locked,
                        self.curr_version, self.prev_version,
                        self.edited_by, self.edited_on)

    def isLocked(self):
        return self.locked

    def set_attrs(self, attr_dict):
        """
        Set the attributes on the metadata. For now, ignore all those outside the known fields.
        """
        for attr, val in attr_dict.iteritems():
            if attr in self.ALLOWED_ATTRS:
                setattr(self, attr, val)

    def to_mongo(self):
        return {'filename': self.upload_name,
                'filepath': self.filepath,
                'internal_name': self.internal_name,
                'locked': self.locked,
                'edit_info': {'curr_version': self.curr_version,
                              'prev_version': self.prev_version,
                              'edited_by': self.edited_by,
                              'edited_on': self.edited_on}}

    def from_mongo(self, asset_doc):
        """
        Fill in all metadata fields besides asset_id and upload_name, which are initialized upon construction.
        """
        if asset_doc is None:
            return
        assert isinstance(asset_doc, dict)
        self.filepath = asset_doc['filepath']
        self.internal_name = asset_doc['internal_name']
        self.locked = asset_doc['locked']
        edit_info = asset_doc['edit_info']
        self.curr_version = edit_info['curr_version']
        self.prev_version = edit_info['prev_version']
        self.edited_by = edit_info['edited_by']
        self.edited_on = edit_info['edited_on']



