from os.path import expanduser
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

# Uncomment this if you want to see a demo of localization.
# from kivy.config import Config
# from os.path import abspath, dirname, join
# Config.add_section('xpopup')
# Config.set('xpopup', 'locale_file',
#            join(dirname(abspath(__file__)), 'xpopup_ru.mo'))

try:
    from .tools import *
    from .notification import XNotification, XConfirmation, XError, XMessage,\
        XProgress, XLoading
    from .form import XSlider, XTextInput, XNotes, XAuthorization
    from .file import XFileOpen, XFileSave, XFolder
except:
    from tools import *
    from notification import XNotification, XConfirmation, XError, XMessage,\
        XProgress, XLoading
    from form import XSlider, XTextInput, XNotes, XAuthorization
    from file import XFileOpen, XFileSave, XFolder


__author__ = 'ophermit'


Builder.load_string('''
#:import metrics kivy.metrics

<XPopupDemo>:
    padding: 5
    spacing: 2
    orientation: 'vertical'

    BoxLayout:
        spacing: 2

        XButton:
            text: 'XMessage demo'
            on_release: root._on_click('msgbox')
        XButton:
            text: 'XConfirmation demo'
            on_release: root._on_click('confirm')
        XButton:
            text: 'XError demo'
            on_release: root._on_click('error')
        XButton:
            text: 'XProgress demo'
            on_release: root._on_click('progress')
        XButton:
            text: 'XLoading demo'
            on_release: root._loading_demo()

    BoxLayout:
        spacing: 2

        XButton:
            text: 'XTextInput demo'
            on_release: root._on_click('input')
        XButton:
            text: 'XNotes demo'
            on_release: root._on_click('notes')
        XButton:
            text: 'XSlider demo'
            on_release: root._on_click('slider')
        XButton:
            text: 'XAuthorization demo'
            on_release: root._on_click('login')

    BoxLayout:
        spacing: 2

        XButton:
            text:'XOpenFile demo'
            on_release: root._open_dialog_demo()
        XButton
            text: 'XSaveFile demo'
            on_release: root._save_dialog_demo()
        XButton:
            text: 'XFolder demo'
            on_release: root._folder_dialog_demo()
''')


class XPopupDemo(BoxLayout):
    def _on_click(self, sid):
        if sid == 'msgbox':
            XMessage(text='It could be your Ad', title='XMessage demo')
        elif sid == 'error':
            XError(text='Don`t panic! Its just the XError demo.')
        elif sid == 'confirm':
            XConfirmation(text='Do you see a confirmation?',
                          on_dismiss=self._callback)
        elif sid == 'progress':
            self._o_popup = XProgress(title='PopupProgress demo',
                                      text='Processing...', max=200)
            Clock.schedule_once(self._progress_test, .1)
        elif sid == 'input':
            XTextInput(title='Edit text', text='I\'m a text',
                       on_dismiss=self._callback)
        elif sid == 'notes':
            XNotes(title='Edit notes', on_dismiss=self._callback_notes,
                   lines=['Text', 'Too many text...', 'Yet another row.'])
        elif sid == 'slider':
            self._o_popup = XSlider(
                min=.4, max=.9, value=.5, size_hint=(.6, .5),
                title_template='Slider test, Value: %0.2f',
                buttons=['Horizontal', 'Vertical', 'Close'],
                on_change=self._slider_value, on_dismiss=self._slider_click)
        elif sid == 'login':
            XAuthorization(
                on_dismiss=self._callback, login='login',
                required_fields={'login': 'Login', 'password': 'Password'},
                password='password')

    @staticmethod
    def _callback(instance):
        if instance.is_canceled():
            return None

        s_message = 'Pressed button: %s\n\n' % instance.button_pressed

        try:
            values = instance.values
            for kw in values:
                s_message += ('<' + kw + '> : ' + str(values[kw]) + '\n')
        except AttributeError:
            pass

        XNotification(
            text=s_message, show_time=3, size_hint=(0.8, 0.4),
            title='Results of the popup ( will disappear after 3 seconds ):')

    @staticmethod
    def _callback_notes(instance):
        if instance.is_canceled():
            return

        s_message = 'Pressed button: %s\n\n' % instance.button_pressed
        s_message += str(instance.lines)

        XNotification(
            text=s_message, show_time=3, size_hint=(0.8, 0.4),
            title='XNotes demo ( will disappear after 3 seconds ):')

    def _progress_test(self, pdt=None):
        if self._o_popup.is_canceled():
            return

        self._o_popup.inc()
        self._o_popup.text = 'Processing (%d / %d)' %\
                             (self._o_popup.value, self._o_popup.max)
        if self._o_popup.value < self._o_popup.max:
            Clock.schedule_once(self._progress_test, .01)
        else:
            self._o_popup.complete()

    @staticmethod
    def _loading_demo():
        XLoading(buttons=['Close'])

    @staticmethod
    def _slider_value(instance, value):
        if instance.orientation == 'vertical':
            instance.size_hint_x = value
        else:
            instance.size_hint_y = value

    @staticmethod
    def _slider_click(instance):
        if instance.button_pressed == 'Horizontal':
            instance.orientation = 'horizontal'
            instance.size_hint = (.6, .5)
            instance.min = .4
            instance.max = .9
            instance.value = .5
            return True
        elif instance.button_pressed == 'Vertical':
            instance.orientation = 'vertical'
            instance.size_hint = (.5, .6)
            instance.min = .4
            instance.max = .9
            instance.value = .5
            return True

    def _filepopup_callback(self, instance):
            if instance.is_canceled():
                return
            s = 'Path: %s' % instance.path
            if instance.__class__.__name__ == 'XFileSave':
                s += ('\nFilename: %s\nFull name: %s' %
                      (instance.filename, instance.get_full_name()))
            else:
                s += ('\nSelection: %s' % instance.selection)
            XNotification(title='Pressed button: ' + instance.button_pressed,
                          text=s, show_time=5)

    def _open_dialog_demo(self):
        XFileOpen(on_dismiss=self._filepopup_callback, path=expanduser(u'~'),
                  multiselect=True)

    def _save_dialog_demo(self):
        XFileSave(on_dismiss=self._filepopup_callback, path=expanduser(u'~'))

    def _folder_dialog_demo(self):
        XFolder(on_dismiss=self._filepopup_callback, path=expanduser(u'~'))


if __name__ == '__main__':
    import kivy
    # kivy.require('1.9.1')
    from kivy.app import runTouchApp
    runTouchApp(XPopupDemo())
