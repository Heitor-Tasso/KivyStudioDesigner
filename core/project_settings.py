__all__ = ['ProjectSettings', ]

from kivy.config import ConfigParser
from kivy.uix.settings import Settings
from kivy.properties import ObjectProperty
from utils.utils import settings_path, ignore_proj_watcher, profiles_path

import os
from textwrap import dedent

PROJ_DESIGNER = '.designer'
PROJ_CONFIG = profiles_path('config')

class ProjectSettings(Settings):
    '''Subclass of :class:`kivy.uix.settings.Settings` responsible for
       showing settings of project.
    '''
    project = ObjectProperty(None)
    '''Reference to :class:`desginer.project_manager.Project`
    '''
    config_parser = ObjectProperty(None)
    '''Config Parser for this class. Instance
       of :class:`kivy.config.ConfigParser`
    '''
    def __init__(self, project, *args, **kargs):
        self.project = project
        super().__init__(*args, **kargs)

    def load_proj_settings(self):
        '''This function loads project settings
        '''
        self.config_parser = ConfigParser()
        
        file_path = profiles_path('config')
        if not os.path.exists(file_path):
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))

            CONFIG_TEMPLATE = dedent('''
                [proj name]
                name = Project

                [arguments]
                arg =

                [env variables]
                env =
            ''')

            f = open(file_path, 'w')
            f.write(CONFIG_TEMPLATE)
            f.close()

        self.config_parser.read(file_path)

        print("FILE -> ", file_path)
        print('FIRST -> ', settings_path('proj_settings_shell_env'))
        print("SECOND -> ", settings_path('proj_settings_proj_prop'))

        self.add_json_panel('Shell Environment', self.config_parser,
                            settings_path('proj_settings_shell_env'))       
        self.add_json_panel('Project Properties', self.config_parser,
                            settings_path('proj_settings_proj_prop'))

    @ignore_proj_watcher
    def on_config_change(self, *args):
        '''This function is default handler of on_config_change event.
        '''
        self.config_parser.write()
        super(ProjectSettings, self).on_config_change(*args)
