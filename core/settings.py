__all__ = ['DesignerSettings', '']

from utils.utils import get_config_dir, get_kd_data_dir, profiles_path
from uix.settings import SettingList, SettingShortcut
from kivy.properties import ObjectProperty
from kivy.uix.settings import Settings
from kivy.config import ConfigParser

import shutil
import os, sys
from pygments import styles
from distutils.spawn import find_executable


# monkey backport! (https://github.com/kivy/kivy/pull/2288)
if not hasattr(ConfigParser, 'upgrade'):
    from configparser import RawConfigParser as PythonConfigParser

    def upgrade(self, default_config_file):
        '''Upgrade the configuration based on a new default config file.
        '''
        pcp = PythonConfigParser()
        pcp.read(default_config_file)
        for section in pcp.sections():
            self.setdefaults(section, dict(pcp.items(section)))
        self.write()

    ConfigParser.upgrade = upgrade


class DesignerSettings(Settings):
    '''Subclass of :class:`kivy.uix.settings.Settings` responsible for
       showing settings of Kivy Designer.
    '''
    config_parser = ObjectProperty(None)
    '''Config Parser for this class. Instance
       of :class:`kivy.config.ConfigParser`
    '''

    def __init__(self, **kwargs):
        super(DesignerSettings, self).__init__(*kwargs)
        self.register_type('list', SettingList)
        self.register_type('shortcut', SettingShortcut)

    def load_settings(self):
        '''This function loads project settings
        '''
        self.config_parser = ConfigParser(name='DesignerSettings')
        
        DESIGNER_CONFIG = os.path.join(get_config_dir(), 'config.ini')
        DEFAULT_CONFIG = profiles_path('config')

        if not os.path.exists(DESIGNER_CONFIG):
            shutil.copyfile(DEFAULT_CONFIG, DESIGNER_CONFIG)

        self.config_parser.read(DESIGNER_CONFIG)
        self.config_parser.upgrade(DEFAULT_CONFIG)
        
        # creates a panel before insert it to update code input theme list
        path = os.path.join(get_kd_data_dir(), 'settings', 'designer_settings.json')
        panel = self.create_json_panel('Kivy Designer Settings', self.config_parser, path)

        uid = panel.uid
        if self.interface is not None:
            self.interface.add_panel(panel, 'Kivy Designer Settings', uid)

        # loads available themes
        for child in panel.children:
            if hasattr(child, 'items'):
                if len(child.items) > 0:
                    if child.items[0] == 'code_input_theme_options':
                        child.items = styles.get_all_styles()

        # tries to find python and buildozer path if it's not defined
        getdefault = self.config_parser.getdefault
        path = getdefault('global', 'python_shell_path', '')

        if path.strip() == '':
            self.config_parser.set('global', 'python_shell_path', sys.executable)
            self.config_parser.write()

        buildozer_path = getdefault('buildozer', 'buildozer_path', '')

        if buildozer_path.strip() == '':
            buildozer_path = find_executable('buildozer')
            if buildozer_path:
                self.config_parser.set('buildozer', 'buildozer_path', buildozer_path)
                self.config_parser.write()

        dir_setting = lambda file: os.path.join(get_kd_data_dir(), 'settings', file+'.json')

        self.add_json_panel('Buildozer', self.config_parser, dir_setting('buildozer_settings'))
        self.add_json_panel('Hanga', self.config_parser, dir_setting('hanga_settings'))
        self.add_json_panel('Keyboard Shortcuts', self.config_parser, dir_setting('shortcuts'))

    def on_config_change(self, *args):
        '''This function is default handler of on_config_change event.
        '''
        self.config_parser.write()
        super(DesignerSettings, self).on_config_change(*args)
