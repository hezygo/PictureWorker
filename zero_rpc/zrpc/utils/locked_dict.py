# -*- encoding: utf-8 -*-
"""
@File        :locked_dict.py
@Desc        :带线程锁的字典
@Date        :2022-03-03 10:53
"""


import itertools
from collections import OrderedDict

from threading import Lock

# Use basestring name lookup test to adapt to python version
try:
    # noinspection PyCompatibility
    base_str = basestring
    items = 'iteritems'  # from here on we are python < v3
except NameError:  # ... below section applies to python v3+
    base_str = str, bytes, bytearray
    items = 'items'


class LockedOrderedDict(OrderedDict):
    __slots__ = ('_lock',)  # no __dict__ - that would be redundant

    @staticmethod
    def _process_args(map_or_it=(), **kwargs):
        """Custom made helper for this class."""
        if hasattr(map_or_it, items):
            map_or_it = getattr(map_or_it, items)()
        it_chain = itertools.chain
        return ((k, v)
                for k, v in it_chain(map_or_it, getattr(kwargs, items)()))

    def __init__(self, mapping=(), **kwargs):
        """Base (dict) accepts mappings or iterables as first argument."""
        super(LockedOrderedDict, self).__init__(
            self._process_args(mapping, **kwargs))
        self._lock = Lock()

    def __enter__(self):
        """Context manager enter the block, acquire the lock."""
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit the block, release the lock."""
        self._lock.release()

    def __getstate__(self):
        """Enable Pickling inside context blocks,
        through inclusion of the slot entries without the lock."""
        return dict(
            (slot, getattr(self, slot))
            for slot in self.__slots__
            if hasattr(self, slot) and slot != '_lock'
        )

    def __setstate__(self, state):
        """Restore the instance from pickle including the slot entries,
        without addition of a fresh lock.
        """
        for slot, value in getattr(state, items)():
            setattr(self, slot, value)
        self._lock = Lock()

    def __getitem__(self, k):
        """For now plain delegation of getitem method to base class."""
        return super(LockedOrderedDict, self).__getitem__(k)

    def __setitem__(self, k, v):
        """For now plain delegation of setitem method to base class."""
        return super(LockedOrderedDict, self).__setitem__(k, v)

    def __delitem__(self, k):
        """For now plain delegation of del method to base class."""
        return super(LockedOrderedDict, self).__delitem__(k)

    def get(self, k, default=None):
        """For now plain delegation of get method to base class."""
        return super(LockedOrderedDict, self).get(k, default)

    def setdefault(self, k, default=None):
        """For now plain delegation of setdefault method to base class."""
        return super(LockedOrderedDict, self).setdefault(k, default)

    def pop(self, k, d=None):
        """For now plain delegation of pop method to base class."""
        return super(LockedOrderedDict, self).pop(k, d)

    def update(self, map_or_it=(), **kwargs):
        """Ensure processing of mappings or iterables as first argument."""
        super(LockedOrderedDict, self).update(
            self._process_args(map_or_it, **kwargs))

    def __contains__(self, k):
        """For now plain delegation of contains method to base class."""
        return super(LockedOrderedDict, self).__contains__(k)

    # noinspection PyMethodOverriding
    @classmethod
    def fromkeys(cls, seq, value=None):
        """For now plain delegation of fromkeys class method to base."""
        return super(LockedOrderedDict, cls).fromkeys(seq, value)
