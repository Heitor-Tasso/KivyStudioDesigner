
__all__ = ['HelpDialog', ]

from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder


Builder.load_string("""

#: import hex utils.colors.hex

<HelpDialog>:
    orientation: 'vertical'
    rst: rst
    padding: designer_padding
    spacing: designer_spacing
    RstDocument:
        id: rst
    DesignerButton:
        text: 'Close'
        size_hint: None, None
        size: '60pt', '30pt'
        pos_hint: {'right': 1}
        on_release: root.dispatch('on_cancel')

""")

class HelpDialog(BoxLayout):
    '''HelpDialog, in which help will be displayed from help.rst.
       It emits 'on_cancel' event when 'Cancel' button is released.
    '''
    rst = ObjectProperty(None)
    '''rst is reference to `kivy.uix.rst.RstDocument` to display help from
       help.rst
    '''
    __events__ = ('on_cancel', )

    def on_cancel(self, *args):
        '''Default handler for 'on_cancel' event
        '''
        pass
