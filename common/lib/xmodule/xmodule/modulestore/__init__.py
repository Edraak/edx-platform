"""
This module provides an abstraction for working with XModuleDescriptors
that are stored in a database an accessible using their Location as an identifier
"""

import logging

from abc import ABCMeta, abstractmethod

from xmodule.errortracker import make_error_tracker
from xmodule.modulestore.locator import Location

log = logging.getLogger('edx.modulestore')

SPLIT_MONGO_MODULESTORE_TYPE = 'split'
MONGO_MODULESTORE_TYPE = 'mongo'
XML_MODULESTORE_TYPE = 'xml'

class ModuleStoreRead(object):
    """
    An abstract interface for a database backend that stores XModuleDescriptor
    instances and extends read-only functionality
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def has_item(self, course_id, location):
        """
        Returns True if location exists in this ModuleStore.
        """
        pass

    @abstractmethod
    def get_item(self, location, depth=0):
        """
        Returns an XModuleDescriptor instance for the item at location.

        If any segment of the location is None except revision, raises
            xmodule.modulestore.exceptions.InsufficientSpecificationError

        If no object is found at that location, raises
            xmodule.modulestore.exceptions.ItemNotFoundError

        location: Something that can be passed to Location

        depth (int): An argument that some module stores may use to prefetch
            descendents of the queried modules for more efficient results later
            in the request. The depth is counted in the number of calls to
            get_children() to cache. None indicates to cache all descendents
        """
        pass

    @abstractmethod
    def get_instance(self, course_id, location, depth=0):
        """
        Get an instance of this location, with policy for course_id applied.
        TODO (vshnayder): this may want to live outside the modulestore eventually
        """
        pass

    @abstractmethod
    def get_item_errors(self, location):
        """
        Return a list of (msg, exception-or-None) errors that the modulestore
        encountered when loading the item at location.

        location : something that can be passed to Location

        Raises the same exceptions as get_item if the location isn't found or
        isn't fully specified.
        """
        pass

    @abstractmethod
    def get_items(self, location, course_id=None, depth=0):
        """
        Returns a list of XModuleDescriptor instances for the items
        that match location. Any element of location that is None is treated
        as a wildcard that matches any value

        location: Something that can be passed to Location

        depth: An argument that some module stores may use to prefetch
            descendents of the queried modules for more efficient results later
            in the request. The depth is counted in the number of calls to
            get_children() to cache. None indicates to cache all descendents
        """
        pass

    @abstractmethod
    def get_courses(self):
        '''
        Returns a list containing the top level XModuleDescriptors of the courses
        in this modulestore.
        '''
        pass

    @abstractmethod
    def get_course(self, course_id):
        '''
        Look for a specific course id.  Returns the course descriptor, or None if not found.
        '''
        pass

    @abstractmethod
    def get_parent_locations(self, location, course_id):
        '''Find all locations that are the parents of this location in this
        course.  Needed for path_to_location().

        returns an iterable of things that can be passed to Location.
        '''
        pass

    @abstractmethod
    def get_errored_courses(self):
        """
        Return a dictionary of course_dir -> [(msg, exception_str)], for each
        course_dir where course loading failed.
        """
        pass

    @abstractmethod
    def get_modulestore_type(self, course_id):
        """
        Returns a type which identifies which modulestore is servicing the given
        course_id. The return can be either "xml" (for XML based courses) or "mongo" for MongoDB backed courses
        """
        pass


class ModuleStoreWrite(ModuleStoreRead):
    """
    An abstract interface for a database backend that stores XModuleDescriptor
    instances and extends both read and write functionality
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def update_item(self, location, data, allow_not_found=False):
        """
        Set the data in the item specified by the location to
        data

        location: Something that can be passed to Location
        data: A nested dictionary of problem data
        """
        pass

    @abstractmethod
    def update_children(self, location, children):
        """
        Set the children for the item specified by the location to
        children

        location: Something that can be passed to Location
        children: A list of child item identifiers
        """
        pass

    @abstractmethod
    def update_metadata(self, location, metadata):
        """
        Set the metadata for the item specified by the location to
        metadata

        location: Something that can be passed to Location
        metadata: A nested dictionary of module metadata
        """
        pass

    @abstractmethod
    def delete_item(self, location):
        """
        Delete an item from this modulestore

        location: Something that can be passed to Location
        """
        pass


class ModuleStoreReadBase(ModuleStoreRead):
    '''
    Implement interface functionality that can be shared.
    '''
    # pylint: disable=invalid-name, unused-argument
    def __init__(
        self,
        doc_store_config=None,  # ignore if passed up
        metadata_inheritance_cache_subsystem=None, request_cache=None,
        modulestore_update_signal=None, xblock_mixins=(),
        # temporary parms to enable backward compatibility. remove once all envs migrated
        db=None, collection=None, host=None, port=None, tz_aware=True, user=None, password=None
    ):
        '''
        Set up the error-tracking logic.
        '''
        self._location_errors = {}  # location -> ErrorLog
        # pylint: disable=invalid-name
        self.metadata_inheritance_cache_subsystem = metadata_inheritance_cache_subsystem
        self.modulestore_update_signal = modulestore_update_signal
        self.request_cache = request_cache
        self.xblock_mixins = xblock_mixins

    def _get_errorlog(self, location):
        """
        If we already have an errorlog for this location, return it.  Otherwise,
        create one.
        """
        location = Location(location)
        if location not in self._location_errors:
            self._location_errors[location] = make_error_tracker()
        return self._location_errors[location]

    def get_item_errors(self, location):
        """
        Return list of errors for this location, if any.  Raise the same
        errors as get_item if location isn't present.

        NOTE: For now, the only items that track errors are CourseDescriptors in
        the xml datastore.  This will return an empty list for all other items
        and datastores.
        """
        # check that item is present and raise the promised exceptions if needed
        # TODO (vshnayder): post-launch, make errors properties of items
        # self.get_item(location)

        errorlog = self._get_errorlog(location)
        return errorlog.errors

    def get_errored_courses(self):
        """
        Returns an empty dict.

        It is up to subclasses to extend this method if the concept
        of errored courses makes sense for their implementation.
        """
        return {}

    def get_course(self, course_id):
        """Default impl--linear search through course list"""
        for c in self.get_courses():
            if c.id == course_id:
                return c
        return None


class ModuleStoreWriteBase(ModuleStoreReadBase, ModuleStoreWrite):
    '''
    Implement interface functionality that can be shared.
    '''
    pass
