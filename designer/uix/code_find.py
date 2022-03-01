__all__ = ['CodeInputFind', ]

from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder

Builder.load_string("""

#: import theme_atlas utils.utils.theme_atlas
#: import hex utils.colors.hex

<CodeInputFind>:
    txt_query: txt_query
    size_hint_y: None
    height: designer_height
    canvas.before:
        Color:
            rgb: bgcolor
        Rectangle:
            size: self.size
            pos: self.pos
    CheckBox:
        group: 'find_mode'
        size_hint_x: None
        width: '20dp'
        active: True
    Label:
        text: 'Text'
        size_hint_x: None
        padding_x: '10dp'
        size: self.texture_size
    CheckBox:
        group: 'find_mode'
        size_hint_x: None
        width: '20dp'
        on_active: root.use_regex = args[1]
    Label:
        text: 'Regex'
        size_hint_x: None
        padding_x: '10dp'
        size: self.texture_size
    CheckBox:
        group: 'find_mode'
        size_hint_x: None
        width: '20dp'
        on_active: root.case_sensitive = args[1]
    Label:
        text: 'Case sensitive'
        size_hint_x: None
        padding_x: '10dp'
        size: self.texture_size
    TextInput:
        id: txt_query
        text: ''
        on_text: root.query = args[1]
        multiline: False
        on_text_validate: root.dispatch('on_next')
    Button:
        text: 'Find'
        on_release: root.dispatch('on_next')
        size_hint_x: None
        width: '100dp'
    Button:
        text: 'Find Prev'
        on_release: root.dispatch('on_prev')
        size_hint_x: None
        width: '100dp'
    Image:
        source: theme_atlas('close')
        size_hint: None, None
        size: designer_height, designer_height
        on_touch_down: if self.collide_point(*args[1].pos): root.dispatch('on_close')

""")

class CodeInputFind(BoxLayout):
    '''Widget responsible for searches in the Python Code Input
    '''

    query = StringProperty('')
    '''Search query
    :data:`query` is a :class:`~kivy.properties.StringProperty`
    '''

    txt_query = ObjectProperty(None)
    '''Search query TextInput
    :data:`txt_query` is a :class:`~kivy.properties.ObjectProperty`
    '''

    use_regex = BooleanProperty(False)
    '''Filter search with regex
        :data:`use_regex` is a :class:`~kivy.properties.BooleanProperty`
    '''

    case_sensitive = BooleanProperty(False)
    '''Filter search with case sensitive text
        :data:`case_sensitive` is a :class:`~kivy.properties.BooleanProperty`
    '''

    __events__ = ('on_close', 'on_next', 'on_prev', )

    def on_touch_down(self, touch):
        '''Enable touche
        '''
        if self.collide_point(*touch.pos):
            super(CodeInputFind, self).on_touch_down(touch)
            return True

    def find_next(self, *args):
        '''Search in the opened source code for the search string and updates
        the cursor if text is found
        '''
        pass

    def find_prev(self, *args):
        '''Search in the opened source code for the search string and updates
        the cursor if text is found
        '''
        pass

    def on_close(self, *args):
        pass

    def on_next(self, *args):
        pass

    def on_prev(self, *args):
        pass
