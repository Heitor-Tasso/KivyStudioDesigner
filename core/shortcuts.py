__all__ = ['Shortcuts', ]

from utils.open_sites import open_repo, open_docs, open_kd_docs
from utils.utils import get_designer

from kivy.core.window import Keyboard, Window

class Shortcuts(object):

    def __init__(self, **kw):
        Window.bind(on_key_down=self.parse_key_down)
        # map is the link between a shortcut and a callback
        # the key is a formatted keyboard shortcuts string
        # and the value is a method declared in this class
        self.map = {}

    def map_shortcuts(self, config_parser, *args):
        '''Read shortcuts from config_parser
        :param config_parser: config parser with all shorcut settings
        '''
        # get all defined shortcuts
        shortcuts = (
            (self.do_new_file, 'new_file'), (self.do_new_project, 'new_project'),
            (self.do_open_project, 'open_project'), (self.do_save, 'save'),
            (self.do_save_as, 'save_as'), (self.do_close_project, 'close_project'),
            (self.do_recent, 'recent'), (self.do_settings, 'settings'), (self.do_run, 'run'),
            (self.do_stop, 'stop'), (self.do_clean, 'clean'), (self.do_build, 'build'),
            (self.do_rebuild, 'rebuild'), (self.do_buildozer_init, 'buildozer_init'),
            (self.do_export_png, 'export_png'), (self.do_check_pep8, 'check_pep8'),
            (self.do_create_setup_py, 'create_setup_py'), (self.do_create_gitignore, 'create_gitignore'),
            (self.do_help, 'help'), (self.do_kivy_docs, 'kivy_docs'), (self.do_kd_docs, 'kd_docs'),
            (self.do_kd_repo, 'kd_repo'), (self.do_about, 'about'),
        )

        self.map = dict()
        getdefault = config_parser.getdefault
        for func, name in shortcuts:
            key = getdefault('shortcuts', name, '')
            self.map[key] = [func, name]

    def parse_key_down(self, keyboard, key, codepoint, text, modifier, *args):
        '''Parse keys and generate the formatted keyboard shortcut
        '''
        key_str = Keyboard.keycode_to_string(Window._system_keyboard, key)
        modifier.sort()
        value = f'{modifier} + {key_str}'
        if value in self.map:
            self.map.get(value)[0]()
            return True

    def do_new_file(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_new_file
        menu = d.ids.toll_bar_top.ids.actn_menu_file

        if not btn.disabled and not menu.disabled:
            d.ids.toll_bar_top.action_btn_new_file_pressed()

    def do_new_project(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_new_project
        menu = d.ids.toll_bar_top.ids.actn_menu_file

        if not btn.disabled and not menu.disabled:
            d.ids.toll_bar_top.action_btn_new_project_pressed()

    def do_open_project(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_open_project
        menu = d.ids.toll_bar_top.ids.actn_menu_file

        if not btn.disabled and not menu.disabled:
            d.ids.toll_bar_top.action_btn_open_pressed()

    def do_save(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_save
        menu = d.ids.toll_bar_top.ids.actn_menu_file

        if not btn.disabled and not menu.disabled:
            d.ids.toll_bar_top.action_btn_save_pressed()

    def do_save_as(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_save_as
        menu = d.ids.toll_bar_top.ids.actn_menu_file

        if not btn.disabled and not menu.disabled:
            d.ids.toll_bar_top.action_btn_save_as_pressed()

    def do_close_project(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_close_proj
        menu = d.ids.toll_bar_top.ids.actn_menu_file

        if not btn.disabled and not menu.disabled:
            d.ids.toll_bar_top.action_btn_close_proj_pressed()

    def do_recent(self, *args):
        d = get_designer()
        d.ids.toll_bar_top.action_btn_recent_files_pressed()

    def do_settings(self, *args):
        d = get_designer()
        d.ids.toll_bar_top.action_btn_settings_pressed()

    def do_run(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_run_proj
        menu = d.ids.toll_bar_top.ids.actn_menu_run

        if not btn.disabled and not menu.disabled:
            d.ids.toll_bar_top.action_btn_clean_pressed('run')

    def do_stop(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_stop_proj
        menu = d.ids.toll_bar_top.ids.actn_menu_run

        if not btn.disabled and not menu.disabled:
            d.ids.toll_bar_top.action_btn_clean_pressed('stop')

    def do_clean(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_clean_proj
        menu = d.ids.toll_bar_top.ids.actn_menu_run

        if not btn.disabled and not menu.disabled:
            d.ids.toll_bar_top.action_btn_clean_pressed('clean')

    def do_build(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_build_proj
        menu = d.ids.toll_bar_top.ids.actn_menu_run

        if not btn.disabled and not menu.disabled:
            d.ids.toll_bar_top.action_btn_clean_pressed('build')

    def do_rebuild(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_rebuild_proj
        menu = d.ids.toll_bar_top.ids.actn_menu_run

        if not btn.disabled and not menu.disabled:
            d.ids.toll_bar_top.action_btn_clean_pressed('rebuild')

    def do_buildozer_init(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_buildozer_init
        menu = d.ids.toll_bar_top.ids.actn_menu_tools

        if not btn.disabled and not menu.disabled:
            d.ids.toll_bar_top.designer_tools.buildozer_init()

    def do_export_png(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_export_png
        menu = d.ids.toll_bar_top.ids.actn_menu_tools

        if not btn.disabled and not menu.disabled:
            d.designer_tools.export_png()

    def do_check_pep8(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_check_pep8
        menu = d.ids.toll_bar_top.ids.actn_menu_tools

        if not btn.disabled and not menu.disabled:
            d.designer_tools.check_pep8()

    def do_create_setup_py(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_create_setup_py
        menu = d.ids.toll_bar_top.ids.actn_menu_tools

        if not btn.disabled and not menu.disabled:
            d.designer_tools.create_setup_py()

    def do_create_gitignore(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_create_gitignore
        menu = d.ids.toll_bar_top.ids.actn_menu_tools

        if not btn.disabled and not menu.disabled:
            d.designer_tools.create_gitignore()

    def do_help(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_help
        menu = d.ids.toll_bar_top.ids.actn_menu_help

        if not btn.disabled and not menu.disabled:
            d.ids.toll_bar_top.show_help()

    def do_kivy_docs(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_wiki
        menu = d.ids.toll_bar_top.ids.actn_menu_help

        if not btn.disabled and not menu.disabled:
            open_docs()

    def do_kd_docs(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_doc
        menu = d.ids.toll_bar_top.ids.actn_menu_help

        if not btn.disabled and not menu.disabled:
            open_kd_docs()

    def do_kd_repo(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_page
        menu = d.ids.toll_bar_top.ids.actn_menu_help

        if not btn.disabled and not menu.disabled:
            open_repo()

    def do_about(self, *args):
        d = get_designer()
        btn = d.ids.toll_bar_top.ids.actn_btn_about
        menu = d.ids.toll_bar_top.ids.actn_menu_help

        if not btn.disabled and not menu.disabled:
            d.ids.toll_bar_top.action_btn_about_pressed()
