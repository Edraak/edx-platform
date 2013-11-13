from collections import OrderedDict

from . import ModuleStoreBase, ModuleStoreReadBase, ModuleStoreWriteBase


class HierarchicalModuleStore(ModuleStoreWriteBase):
    """
    An object that relies on a number of different stores and attempts to pull from them in a prescribed order
    """

    def __init__(self, hierarchy):
        """
        Hierarchy should be an ordered dict that maps human-readable strings to modulestore instances
        """
        self.hierarchy = hierarchy

    def hierarchywrapper(func):
        def wrapper(self, *args, **kwargs):
            for key, value in self.hierarchy.items():
                try:
                    result = getattr(value, func.__name__)(*args, **kwargs)
                    if result and len(result):
                        return result
                    else:
                        pass
                except:
                    pass
            return None
        return wrapper

    def __getattribute__(self, name):
        attr = super(ModuleStoreWriteBase, self).__getattribute__(name)
        if callable(attr):
            return hierarchywrapper(attr)
        else:
            return attr
