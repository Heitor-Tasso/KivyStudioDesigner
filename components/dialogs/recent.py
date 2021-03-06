
__all__ = ['']

from utils.utils import get_fs_encoding
from components.adapters.listadapter import ListAdapter

from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from uix.listview import ListItemButton
from kivy.lang.builder import Builder

Builder.load_string("""

#: import hex utils.colors.hex

<RecentItemButton>:
    selected_color: [1, 1, 1, 0.5]
    deselected_color: [0, 0, 0, 0]
    text_size: self.size
    valign: 'middle'
    shorten: True
    padding_x: '20dp'
    canvas.after:
        Color:
            rgba: (47/255.0, 167/255.0, 212/255.0, 1.0) if self.is_selected else (0.2, 0.2, 0.2, 1)
        Rectangle:
            pos: ((self.x+dp(25)), self.y)
            size: ((self.width-dp(50)), dp(1))

<RecentDialog>:
    select_button: select
    cancel_button: cancel
    listview: listview
    orientation: 'vertical'
    padding: designer_padding

    BoxLayout:
        padding: [0, dp(15)]
        ListView:
            id: listview
            row_height: dp(40)

    GridLayout:
        cols: 2
        size_hint_y: None
        height: self.minimum_height
        spacing: designer_spacing
        DesignerButton:
            id: select
            text: 'Open Selected'
        DesignerButton:
            id: cancel
            text: 'Cancel'

""")

class RecentItemButton(ListItemButton):
    pass

class RecentDialog(BoxLayout):
    '''RecentDialog shows the list of recent files retrieved from RecentManager
       It emits, 'on_select' event when a file is selected and select_button is
       clicked and 'on_cancel' when cancel_button is pressed.
    '''
    listview = ObjectProperty(None)
    ''':class:`~kivy.uix.listview.ListView` used for showing file paths.
       :data:`listview` is a :class:`~kivy.properties.ObjectProperty`
    '''
    select_button = ObjectProperty(None)
    ''':class:`~kivy.uix.button.Button` used to select the list item.
       :data:`select_button` is a :class:`~kivy.properties.ObjectProperty`
    '''
    cancel_button = ObjectProperty(None)
    ''':class:`~kivy.uix.button.Button` to cancel the dialog.
       :data:`cancel_button` is a :class:`~kivy.properties.ObjectProperty`
    '''
    adapter = ObjectProperty(None)
    ''':class:`~kivy.uix.listview.ListAdapter` used for selecting files.
       :data:`adapter` is a :class:`~kivy.properties.ObjectProperty`
    '''
    __events__ = ('on_select', 'on_cancel')

    def __init__(self, file_list, **kwargs):
        super(RecentDialog, self).__init__(**kwargs)
        self.item_strings = []

        for item in file_list:
            if isinstance(item, bytes):
                item = item.decode(get_fs_encoding())
            self.item_strings.append(item)

        self.list_items = RecentItemButton
        self.adapter = ListAdapter(
                cls=self.list_items,
                data=self.item_strings,
                selection_mode='single',
                allow_empty_selection=False,
                args_converter=self._args_converter)

        self.listview.adapter = self.adapter

    def _args_converter(self, index, path):
        '''Convert the item to listview
        '''
        return {'text': path, 'size_hint_y': None, 'height': 40}

    def get_selected_project(self, *args):
        '''
        Get the path of the selected project
        '''
        if not self.adapter.selection:
            return ''
        return self.adapter.selection[0].text

    def on_select_button(self, *args):
        '''Event handler for 'on_release' event of select_button.
        '''
        self.select_button.bind(on_press=lambda *a: self.dispatch('on_select'))

    def on_cancel_button(self, *args):
        '''Event handler for 'on_release' event of cancel_button.
        '''
        self.cancel_button.bind(on_press=lambda *a: self.dispatch('on_cancel'))

    def on_select(self, *args):
        '''Default event handler for 'on_select' event.
        '''
        pass

    def on_cancel(self, *args):
        '''Default event handler for 'on_cancel' event.
        '''
        pass
