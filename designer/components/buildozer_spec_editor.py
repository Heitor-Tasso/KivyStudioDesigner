import json
import os
import tempfile
import webbrowser
from io import open

from uix.settings import SettingDict, SettingList
from utils.utils import get_kd_data_dir, ignore_proj_watcher
from kivy.properties import ConfigParser, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.settings import (
    ContentPanel, InterfaceWithSidebar,
    MenuSidebar, Settings,
    SettingsPanel,
)
from pygments.lexers.configs import IniLexer
from kivy.lang.builder import Builder

Builder.load_string("""

#: import theme_atlas utils.utils.theme_atlas
#: import hex utils.colors.hex

<SpecContentPanel>:
    do_scroll_x: False
    container: content
    GridLayout:
        id: content
        cols: 1
        size_hint_y: None
        height: max(self.minimum_height, root.height)

<-SpecMenuSidebar>:
    size_hint_x: None
    width: '200dp'
    buttons_layout: menu
    close_button: button
    GridLayout:
        pos: root.pos
        cols: 1
        id: menu
        # orientation: 'vertical'
        padding: 5
        canvas.after:
            Color:
                rgb: .2, .2, .2
            Rectangle:
                pos: self.right - 1, self.y
                size: 1, self.height
    Button:
        id: button

<-SpecEditorInterface>:
    orientation: 'horizontal'
    menu: menu
    content: content
    button_bar: button_bar
    SpecMenuSidebar:
        id: menu
    GridLayout:
        id: button_bar
        cols: 1
        Label:
            text: 'Buildozer Spec Editor'
            font_size: '16pt'
            halign: 'center'
            size_hint_y: None
            height: '25pt'
        Button:
            background_normal: theme_atlas('action_item')
            background_down: theme_atlas('action_item')
            text: 'GUI editor to buildozer.spec.z\\nRead more at http://buildozer.readthedocs.org'
            text_size: self.size
            font_size: '11pt'
            halign: 'center'
            valign: 'top'
            size_hint_y: None
            height: '30pt'
            on_press: root.open_buildozer_docs()
        SpecContentPanel:
            id: content
            current_uid: menu.selected_uid

<BuildozerSpecEditor>:
    interface_cls: 'SpecEditorInterface'

<SpecCodeInput>:
    text_input: text_input
    lbl_error: lbl_error
    orientation: 'vertical'
    spacing: designer_spacing
    padding: designer_padding
    Label:
        text: "Edit the buildozer.spec file"
        size_hint_y: None
        text_size: self.size
        font_size: '11pt'
        height: '20pt'
    Label:
        id: lbl_error
        text: 'There is something wrong with your .spec file...'
        size_hint_y: None
        text_size: self.size
        font_size: '11pt'
        halign: 'center'
        height: '0pt'
    ScrollView:
        id: spec_scroll
        bar_width: 10
        scroll_type: ['bars', 'content']
        CodeInput:
            id: text_input
            size_hint_y: None
            height: max(spec_scroll.height, self.minimum_height)
    GridLayout:
        cols: 2
        size_hint_y: None
        height: self.minimum_height
        DesignerButton:
            text: 'Apply Modifications'
            on_press: root._save_spec()
        DesignerButton:
            text: 'Cancel Modifications'
            on_press: root.load_spec()

""")

class SpecContentPanel(ContentPanel):

    def on_current_uid(self, *args):
        result = super(SpecContentPanel, self).on_current_uid(*args)
        if isinstance(self.current_panel, SpecCodeInput):
            self.current_panel.load_spec()
        return result


class SpecMenuSidebar(MenuSidebar):

    def on_selected_uid(self, *args):
        '''(internal) unselects any currently selected menu buttons, unless
        they represent the current panel.

        '''
        for button in self.buttons_layout.children:
            button.selected = button.uid == self.selected_uid


class SpecEditorInterface(InterfaceWithSidebar):

    def open_buildozer_docs(self, *args):
        webbrowser.open('http://buildozer.readthedocs.org')


class SpecSettingsPanel(SettingsPanel):

    def get_value(self, section, key):
        '''Return the value of the section/key from the :attr:`config`
        ConfigParser instance. This function is used by :class:`SettingItem` to
        get the value for a given section/key.

        If you don't want to use a ConfigParser instance, you might want to
        override this function.
        '''
        config = self.config
        if not config:
            return
        if config.has_option(section, key):
            return config.get(section, key)
        else:
            return ''

    def set_value(self, section, key, value):
        # some keys are not enabled by default on .spec. If the value is empty
        # and this key is not on .spec, so we don't need to save it
        if not value and not self.config.has_option(section, key):
            return False
        super(SpecSettingsPanel, self).set_value(section, key, value)


class SpecCodeInput(BoxLayout):

    text_input = ObjectProperty(None)
    '''CodeInput with buildozer.spec text.
     Instance of :class:`kivy.config.ObjectProperty` and defaults to None
    '''

    lbl_error = ObjectProperty(None)
    '''(internal) Label to display errors.
     Instance of :class:`kivy.config.ObjectProperty` and defaults to None
    '''

    spec_path = StringProperty('')
    '''buildozer.spec path.
    Instance of :class:`kivy.config.StringProperty` and defaults to ''
    '''

    __events__ = ('on_change', )

    def __init__(self, **kwargs):
        super(SpecCodeInput, self).__init__(**kwargs)
        self.text_input.lexer = IniLexer()

    def load_spec(self, *args):
        '''Read the buildozer.spec and update the CodeInput
        '''
        self.lbl_error.color = [0, 0, 0, 0]
        self.text_input.text = open(self.spec_path, 'r',
                                    encoding='utf-8').read()

    @ignore_proj_watcher
    def _save_spec(self, *args):
        '''Try to save the spec file. If there is a error, show the label.
        If not, save the file and dispatch on_change
        '''
        f = tempfile.NamedTemporaryFile()
        f.write(self.text_input.text)
        try:
            cfg = ConfigParser()
            cfg.read(f.name)
        except Exception:
            self.lbl_error.color = [1, 0, 0, 1]
        else:
            spec = open(self.spec_path, 'w')
            spec.write(self.text_input.text)
            spec.close()
            self.dispatch('on_change')
        f.close()

    def on_change(self, *args):
        '''Event handler to dispatch a .spec modification
        '''
        pass


class BuildozerSpecEditor(Settings):
    '''Subclass of :class:`kivy.uix.settings.Settings` responsible for
       the UI editor of buildozer spec
    '''

    config_parser = ObjectProperty(None)
    '''Config Parser for this class. Instance
       of :class:`kivy.config.ConfigParser`
    '''

    def __init__(self, **kwargs):
        super(BuildozerSpecEditor, self).__init__(**kwargs)
        self.register_type('dict', SettingDict)
        self.register_type('list', SettingList)
        self.SPEC_PATH = ''
        self.proj_dir = ''
        self.config_parser = ConfigParser.get_configparser("buildozer_spec")
        if self.config_parser is None:
            self.config_parser = ConfigParser(name="buildozer_spec")

    def load_settings(self, proj_dir):
        '''This function loads project settings
        :param proj_dir: project directory with buildozer.spec
        '''
        self.interface.menu.buttons_layout.clear_widgets()
        self.proj_dir = proj_dir
        self.SPEC_PATH = os.path.join(proj_dir, 'buildozer.spec')

        self.config_parser.read(self.SPEC_PATH)
        self.add_json_panel('Application', self.config_parser,
                            os.path.join(get_kd_data_dir(),
                            'settings', 'buildozer_spec_app.json'))
        self.add_json_panel('Android', self.config_parser,
                            os.path.join(get_kd_data_dir(),
                            'settings', 'buildozer_spec_android.json'))
        self.add_json_panel('iOS', self.config_parser,
                            os.path.join(get_kd_data_dir(),
                            'settings', 'buildozer_spec_ios.json'))
        self.add_json_panel('Buildozer', self.config_parser,
                            os.path.join(get_kd_data_dir(),
                            'settings', 'buildozer_spec_buildozer.json'))

        raw_spec = SpecCodeInput(spec_path=self.SPEC_PATH)
        raw_spec.bind(on_change=self.on_spec_changed)
        self.interface.add_panel(raw_spec, "buildozer.spec", raw_spec.uid)

        menu = self.interface.menu
        menu.selected_uid = menu.buttons_layout.children[-1].uid

    def on_spec_changed(self, *args):
        self.load_settings(self.proj_dir)

        # force to show the last panel
        menu = self.interface.menu
        menu.selected_uid = menu.buttons_layout.children[0].uid

    def create_json_panel(self, title, config, filename=None, data=None):
        '''Override the original method to use the custom SpecSettingsPanel
        '''
        if filename is None and data is None:
            raise Exception('You must specify either the filename or data')

        if filename is not None:
            with open(filename, 'r', encoding='utf-8') as fd:
                data = json.loads(fd.read())
        else:
            data = json.loads(data)

        if type(data) != list:
            raise ValueError('The first element must be a list')
        
        panel = SpecSettingsPanel(title=title, settings=self, config=config)

        for setting in data:
            # determine the type and the class to use
            if not 'type' in setting:
                raise ValueError('One setting are missing the "type" element')
            ttype = setting['type']
            cls = self._types.get(ttype)
            if cls is None:
                raise ValueError(
                    'No class registered to handle the <%s> type' %
                    setting['type'])

            # create a instance of the class, without the type attribute
            del setting['type']
            str_settings = {}
            for key, item in setting.items():
                str_settings[str(key)] = item

            instance = cls(panel=panel, **str_settings)

            # instance created, add to the panel
            panel.add_widget(instance)

        return panel

    @ignore_proj_watcher
    def on_config_change(self, *args):
        super(BuildozerSpecEditor, self).on_config_change(*args)
