__all__ = ['ReportWarning', 'BugReporter', 'BugReporterApp']

from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup

import os, sys, platform
from textwrap import dedent
import webbrowser
import urllib

try: # for pip >= 10
    from pip._internal.req import parse_requirements
    from pip._internal.network.download import PipSession
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements
    from pip.download import PipSession

Builder.load_string('''

<BugReporter>:
    txt_traceback: txt_traceback
    Image:
        source: 'data/logo/kivy-icon-256.png'
        opacity: 0.2
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        Label:
            id: title
            text: 'Sorry, Kivy Designer has experienced an internal error :('
            font_size: '16pt'
            halign: 'center'
            size_hint_y: None
            height: '30pt'
        Label:
            id: subtitle
            text: 'You can report this bug using the button bellow, ' \
                    'helping us to fix it.'
            text_size: self.size
            font_size: '11pt'
            halign: 'center'
            valign: 'top'
            size_hint_y: None
            height: '30pt'
        ScrollView:
            id: e_scroll
            bar_width: 10
            scroll_y: 0
            TextInput:
                id: txt_traceback
                size_hint_y: None
                height: max(e_scroll.height, self.minimum_height)
                background_color: 1, 1, 1, 0.05
                text: ''
                foreground_color: 1, 1, 1, 1
                readonly: True
        BoxLayout:
            size_hint: 0.6, None
            padding: 10, 10
            height: 70
            pos_hint: {'x':0.2}
            spacing: 5
            Button:
                text: 'Copy to clipboard'
                on_press: root.on_clipboard()
            Button:
                text: 'Report Bug'
                on_press: root.on_report()
            Button:
                text: 'Close'
                on_press: root.on_close()

<ReportWarning>:
    size_hint: .5, .5
    auto_dismiss: False
    title: 'Warning'
    BoxLayout:
        orientation: 'vertical'
        Label:
            text_size: self.size
            text: root.text
            padding: '4sp', '4sp'
            valign: 'middle'
        BoxLayout:
            Button:
                size_hint_y: None
                height: '40sp'
                on_release: root.dispatch('on_release')
                text: 'Report'
            Button:
                size_hint_y: None
                height: '40sp'
                on_release: root.dismiss()
                text: 'Close'
''')


class ReportWarning(Popup):
    text = StringProperty('')
    '''Warning Message
    '''
    __events__ = ('on_release',)

    def on_release(self, *args):
        pass

class BugReporter(FloatLayout):
    txt_traceback = ObjectProperty(None)
    '''TextView to show the traceback message
    '''

    def __init__(self, **kw):
        super(BugReporter, self).__init__(**kw)
        self.warning = None

    def on_clipboard(self, *args):
        '''Event handler to "Copy to Clipboard" button
        '''
        Clipboard.copy(self.txt_traceback.text)

    def on_report(self, *args):
        '''Event handler to "Report Bug" button
        '''
        warning = ReportWarning()
        warning.text = ('Warning. Some web browsers doesn\'t post the full'
                        ' traceback error. \n\nPlease, check if the last line'
                        ' of your report is "End of Traceback". \n\n'
                        'If not, use the "Copy to clipboard" button the get'
                        'the full report and post it manually."')
        warning.bind(on_release=self._do_report)
        warning.open()
        self.warning = warning

    def _do_report(self, *args):
        txt = urllib.parse.quote(
            self.txt_traceback.text.encode('utf-8'))
        url = 'https://github.com/kivy/kivy-designer/issues/new?body=' + txt
        webbrowser.open(url)

    def on_close(self, *args):
        '''Event handler to "Close" button
        '''
        App.get_running_app().stop()


class BugReporterApp(App):
    title = "Kivy Designer - Bug reporter"
    traceback = StringProperty('')

    def __init__(self, **kw):
        # self.traceback = traceback
        super(BugReporterApp, self).__init__(**kw)

    def build(self):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'requirements.txt')
        requirements = parse_requirements(path, session=PipSession())
        env_info = '\n'
        space = ' ' * 16
        
        for req in requirements:
            try:
                version = req.installed_version
            except AttributeError:
                version = req.requirement

            if version is None:
                version = 'Not installed'

            try:
                env_info +=  f'{space}{req.name}: {version}\n'
            except AttributeError:
                env_info += f'{space}{version}\n'

        env_info += f'\n{space}Platform: {platform.platform()}'
        env_info += f'\n{space}Python: {platform.python_version()}'

        if isinstance(self.traceback, bytes):
            encoding = sys.getfilesystemencoding()
            if not encoding:
                encoding = sys.stdin.encoding
            if encoding:
                self.traceback = self.traceback.decode(encoding)

        template = dedent(f'''
            ## Environment Info
            {env_info}

            ## Traceback

            ```
            {self.traceback}
            ```

            End of Traceback
        ''')

        rep = BugReporter()
        rep.txt_traceback.text = template
        return rep


if __name__ == '__main__':
    BugReporterApp(traceback='Bug example').run()
