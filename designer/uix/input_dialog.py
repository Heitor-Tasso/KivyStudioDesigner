__all__ = ['InputDialog', 'UserTextInput']

from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.lang.builder import Builder

Builder.load_string("""

#: import hex utils.colors.hex

<InputDialog>:
    orientation: 'vertical'
    user_input: user_input
    btn_confirm: btn_confirm
    lbl_error: lbl_error
    padding: designer_padding
    spacing: designer_spacing
    Label:
        text: root.message
        halign: 'left'
        text_size: self.size
        valign: 'middle'
    Label:
        id: lbl_error
        text: ""
        size_hint_x: None
        halign: 'left'
        color: [1, 0, 0, 1]
    UserTextInput:
        id: user_input
        focus: True
    GridLayout:
        cols: 2
        size_hint_y: None
        spacing: designer_spacing
        padding: designer_padding
        height: self.minimum_height
        DesignerButton:
            id: btn_confirm
            text: 'Confirm'
            disabled: True
            on_press: root.dispatch('on_confirm')
        DesignerButton:
            text: 'Cancel'
            on_press: root.dispatch('on_cancel')

<UserTextInput>:
    size_hint_y: None
    height: designer_text_input_height

""")

class InputDialog(BoxLayout):
    '''InputDialog is a widget with a TextInput, Cancel and Confirm button.
    '''
    message = StringProperty('')
    '''It is the message to be shown
       :data:`message` is a :class:`~kivy.properties.StringProperty`
    '''
    user_input = ObjectProperty()
    '''Is the UserTextInput
        :data:`user_input` is a
        :class:`~designer.uix.input_dialog.UserTextInput`
    '''
    btn_confirm = ObjectProperty()
    '''Is the button to confirm the input
        :data:`btn_confirm` is a :class:`~kivy.uix.button.Button`
    '''
    lbl_error = ObjectProperty()
    '''Is a Label to show errors
        :data:`lbl_error` is a :class:`~kivy.uix.label.Label`
    '''
    __events__ = ('on_confirm', 'on_cancel',)

    def __init__(self, message):
        super(InputDialog, self).__init__()
        self.message = message
        self.user_input.bind(text=self.on_text)

    def on_confirm(self, *args):
        pass

    def on_cancel(self, *args):
        pass

    def on_text(self, *args):
        self.btn_confirm.disabled = len(args[1]) == 0


class UserTextInput(TextInput):
    '''
    TextInput used by InputDialog.
    Used to filter the input and handle events
    '''

    def __init__(self, **kwargs):
        super(UserTextInput, self).__init__(**kwargs)

    def insert_text(self, substring, from_undo=False):
        '''
        Override the default insert_text to add a filter
        '''
        s = ""
        if (substring.isalnum() or substring in {'.', '-', '_'}):
            if len(self.text) < 32:
                s = substring

        return super(UserTextInput, self).insert_text(s, from_undo=from_undo)
