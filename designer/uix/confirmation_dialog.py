__all__ = ['ConfirmationDialog', 'ConfirmationDialogSave']

from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder

Builder.load_string("""

<ConfirmationDialog>:
    orientation: 'vertical'
    padding: designer_padding
    spacing: designer_spacing
    Label:
        text: root.message
    GridLayout:
        cols: 2
        size_hint_y: None
        height: self.minimum_height
        DesignerButton:
            text: 'Yes'
            on_release: root.dispatch('on_ok')
        DesignerButton:
            text: 'No'
            on_release: root.dispatch('on_cancel')

<ConfirmationDialogSave>:
    orientation: 'vertical'
    padding: designer_padding
    spacing: designer_spacing
    Label:
        text: root.message
    GridLayout:
        cols: 3
        size_hint_y: None
        height: self.minimum_height
        DesignerButton:
            text: 'Save'
            on_release: root.dispatch('on_save')
        DesignerButton:
            text: "Don\'t Save"
            on_release: root.dispatch('on_dont_save')
        DesignerButton:
            text: 'Cancel'
            on_release: root.dispatch('on_cancel')

""")

class ConfirmationDialog(BoxLayout):
    '''ConfirmationDialog shows a confirmation message with two buttons
       "Yes" and "No". It may be used for confirming user about an operation.
       It emits 'on_ok' when "Yes" is pressed and 'on_cancel' when "No" is
       pressed.
    '''

    message = StringProperty('')
    '''It is the message to be shown
       :data:`message` is a :class:`~kivy.properties.StringProperty`
    '''

    __events__ = ('on_ok', 'on_cancel')

    def __init__(self, message):
        super(ConfirmationDialog, self).__init__()
        self.message = message

    def on_ok(self, *args):
        pass

    def on_cancel(self, *args):
        pass


class ConfirmationDialogSave(BoxLayout):
    '''ConfirmationDialogSave shows a confirmation message with three buttons
       "Save", "Don't Save" and "Cancel". It may be used for confirming user
       about an operation. It emits 'on_save' when "Save" is pressed,
       'on_dont_save' when "Don't Save" is pressed and 'on_cancel'
       when "No" is pressed.
    '''

    message = StringProperty('')
    '''It is the message to be shown
       :data:`message` is a :class:`~kivy.properties.StringProperty`
    '''

    __events__ = ('on_save', 'on_dont_save', 'on_cancel')

    def __init__(self, message):
        super(ConfirmationDialogSave, self).__init__()
        self.message = message

    def on_save(self, *args):
        pass

    def on_dont_save(self, *args):
        pass

    def on_cancel(self, *args):
        pass
