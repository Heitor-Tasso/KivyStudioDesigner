from kivy.uix.floatlayout import FloatLayout
from kivy.lang.builder import Builder

Builder.load_string("""

#: import icons utils.utils.icons

<AboutDialog>:
    Image:
        source: icons('kivy-icon-512')
        pos: root.pos
        opacity: 0.2
    BoxLayout:
        orientation: 'vertical'
        pos: root.pos
        background_color: 0, 1, 0
        padding: designer_padding
        Label:
            id: title
            text: 'Kivy Designer'
            font_size: '26pt'
            halign: 'center'
            size_hint_y: None
            height: '30pt'
        Label:
            id: subtitle
            markup: True
            text: '[i]Innovative User Interfaces, Desktop, and Mobile Development Made Easy.[/i]'
            font_size: '10pt'
            halign: 'center'
            size_hint_y: None
            height: '15pt'
        Label:
            text_size: self.size
            padding: 30, 20
            text:"    Kivy Designer is Kivy\'s tool for designing Graphical User Interfaces (GUIs) from Kivy Widgets. \\nYou can compose and customize widgets, and test them. It is completely written in Python using Kivy. \\nKivy Designer is integrated with Buildozer and Hanga, so you can easily develop and publish your applications to Desktop and Mobile devices.'"
            font_size: '12pt'
            valign: 'top'
        DesignerButton:
            text: 'Close'
            on_release: root.dispatch('on_close')

""")

class AboutDialog(FloatLayout):
    '''AboutDialog, to display about information.
       It emits 'on_cancel' event when 'Cancel' button is released.
    '''

    __events__ = ('on_close',)

    def on_close(self, *args):
        '''Default handler for 'on_close' event
        '''
        pass
