'''
DictAdapter
===========

.. versionadded:: 1.5

.. warning::

    This code is still experimental, and its API is subject to change in a
    future version.

:class:`~kivy.adapters.dictadapter.DictAdapter` is an adapter around a python
dictionary of records. It extends the list-like capabilities of
:class:`~kivy.adapters.listadapter.ListAdapter`.

If you wish to have a bare-bones list adapter, without selection, use
:class:`~kivy.adapters.simplelistadapter.SimpleListAdapter`.

'''

__all__ = ('DictAdapter', )

from kivy.properties import ListProperty, DictProperty
from components.adapters.listadapter import ListAdapter


class DictAdapter(ListAdapter):
    ''':class:`~kivy.adapters.dictadapter.DictAdapter` is an adapter around a
    python dictionary of records. It extends the list-like capabilities of
    :class:`~kivy.adapters.listadapter.ListAdapter`.
    '''
    sorted_keys = ListProperty([])
    '''The sorted_keys list property contains a list of hashable objects (can
    be strings) that will be used directly if no args_converter function is
    provided. If there is an args_converter, the record received from a
    lookup in the data, using key from sorted_keys, will be passed
    to it, for instantiation of list item view class instances.

    :data:`sorted_keys` is a :class:`~kivy.properties.ListProperty`, default
    to [].
    '''
    data = DictProperty(None)
    '''A dict that indexes records by keys that are equivalent to the keys in
    sorted_keys, or they are a superset of the keys in sorted_keys.

    The values can be strings, class instances, dicts, etc.

    :data:`data` is a :class:`~kivy.properties.DictProperty`, default
    to None.
    '''
    def __init__(self, **kwargs):
        if 'sorted_keys' in kwargs:
            if type(kwargs['sorted_keys']) not in (tuple, list):
                msg = 'DictAdapter: sorted_keys must be tuple or list'
                raise Exception(msg)
        else:
            self.sorted_keys = sorted(kwargs['data'].keys())

        super(DictAdapter, self).__init__(**kwargs)

        self.bind(sorted_keys=self.initialize_sorted_keys)

    def bind_triggers_to_view(self, func):
        self.bind(sorted_keys=func)
        self.bind(data=func)

    # self.data is paramount to self.sorted_keys. If sorted_keys is reset to
    # mismatch data, force a reset of sorted_keys to data.keys(). So, in order
    # to do a complete reset of data and sorted_keys, data must be reset
    # first, followed by a reset of sorted_keys, if needed.
    def initialize_sorted_keys(self, *args):
        stale_sorted_keys = False
        for key in self.sorted_keys:
            if not key in self.data:
                stale_sorted_keys = True
                break
        
        if stale_sorted_keys:
            self.sorted_keys = sorted(self.data.keys())
        self.delete_cache()
        self.initialize_selection()

    # Override ListAdapter.update_for_new_data().
    def update_for_new_data(self, *args):
        self.initialize_sorted_keys()

    # Note: this is not len(self.data).
    def get_count(self):
        return len(self.sorted_keys)

    def get_data_item(self, index):
        if index < 0 or index >= len(self.sorted_keys):
            return None
        return self.data[self.sorted_keys[index]]

    # [TODO] Also make methods for scroll_to_sel_start, scroll_to_sel_end,
    #        scroll_to_sel_middle.

    def trim_left_of_sel(self, *args):
        '''Cut list items with indices in sorted_keys that are less than the
        index of the first selected item, if there is selection.

        sorted_keys will be updated by update_for_new_data().
        '''
        if len(self.selection) < 1:
            return None

        selected_keys = [sel.text for sel in self.selection]
        first_sel_index = self.sorted_keys.index(selected_keys[0])
        desired_keys = self.sorted_keys[first_sel_index:]
        self.data = dict(map(lambda k: (k, self.data[k]), desired_keys))

    def trim_right_of_sel(self, *args):
        '''Cut list items with indices in sorted_keys that are greater than
        the index of the last selected item, if there is selection.

        sorted_keys will be updated by update_for_new_data().
        '''
        if len(self.selection) < 1:
            return None

        selected_keys = [sel.text for sel in self.selection]
        last_sel_index = self.sorted_keys.index(selected_keys[-1])
        desired_keys = self.sorted_keys[:last_sel_index + 1]
        self.data = dict(map(lambda k: (k, self.data[k]), desired_keys))

    def trim_to_sel(self, *args):
        '''Cut list items with indices in sorted_keys that are les than or
        greater than the index of the last selected item, if there is
        selection. This preserves intervening list items within the selected
        range.

        sorted_keys will be updated by update_for_new_data().
        '''
        if len(self.selection) < 1:
            return None

        selected_keys = [sel.text for sel in self.selection]
        first_sel_index = self.sorted_keys.index(selected_keys[0])
        last_sel_index = self.sorted_keys.index(selected_keys[-1])
        desired_keys = self.sorted_keys[first_sel_index:last_sel_index + 1]
        self.data = dict(map(lambda k: (k, self.data[k]), desired_keys))

    def cut_to_sel(self, *args):
        '''Same as trim_to_sel, but intervening list items within the selected
        range are cut also, leaving only list items that are selected.

        sorted_keys will be updated by update_for_new_data().
        '''
        if len(self.selection) < 1:
            return None

        selected_keys = [sel.text for sel in self.selection]
        self.data = dict(map(lambda k: (k, self.data[k]), selected_keys))
