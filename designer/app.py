__all__ = ['DesignerApp', ]

from tkinter.messagebox import NO
from components.dialogs.new_project import (NEW_PROJECTS, NewProjectDialog)
from components.buildozer_spec_editor import BuildozerSpecEditor
from components.run_contextual_view import ModulesContView
from components.edit_contextual_view import EditContView
from components.designer_content import DesignerContent
from components.playground import PlaygroundDragElement
from components.dialogs.add_file import AddFileDialog
from components.dialogs.recent import RecentDialog
from components.dialogs.about import AboutDialog
from components.dialogs.help import HelpDialog

from core.project_manager import ProjectManager, ProjectWatcher
from core.profile_settings import ProfileSettings
from core.project_settings import ProjectSettings
from core.recent_manager import RecentManager
from core.settings import DesignerSettings
from core.undo_manager import UndoManager
from core.shortcuts import Shortcuts
from core.builder import Profiler

from tools.bug_reporter import BugReporterApp
from tools.tools import DesignerTools

from uix.confirmation_dialog import (ConfirmationDialog, ConfirmationDialogSave)
from uix.action_items import DesignerActionProfileCheck
from uix.xpopup.file import XFileSave, XFileOpen
from uix.input_dialog import InputDialog
from uix.sandbox import DesignerSandbox

from utils.toolbox_widgets import toolbox_widgets
import io, os, shutil, traceback
from utils import constants
import webbrowser

from utils.utils import (
    get_config_dir, get_fs_encoding, get_kd_data_dir,
    get_kd_dir, ignore_proj_watcher, show_alert,
    show_error_console, show_message, update_info,
)
from distutils.dir_util import copy_tree
from tempfile import mkdtemp

from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.carousel import Carousel
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.base import ExceptionHandler, ExceptionManager

from kivy.clock import Clock
from kivy.config import Config
from kivy.factory import Factory
from kivy.core.window import Window
from kivy.graphics import Color, Line

from kivy.properties import (
    BooleanProperty, ListProperty,
    ObjectProperty, StringProperty,
    partial,
)

class Designer(FloatLayout):
    '''Designer is the Main Window class of Kivy Designer
       :data:`message` is a :class:`~kivy.properties.StringProperty`
    '''
    spec_editor = ObjectProperty(None)
    '''Instance of
        :class:`~designer.components.buildozer_spec_editor.BuildozerSpecEditor`
    '''
    designer_tools = ObjectProperty(None)
    '''Instance of :class:`~designer.tools.tools.DesignerTools`
    '''
    designer_git = ObjectProperty(None)
    '''Instance of :class:`~designer.tools.git_integration.DesignerGit`
    '''
    statusbar = ObjectProperty(None)
    '''Reference to the
        :class:`~designer.components.statusbar.StatusBar` instance.
       :data:`statusbar` is a :class:`~kivy.properties.ObjectProperty`
    '''
    editcontview = ObjectProperty(None)
    '''Reference to the
        :class:`~designer.components.edit_contextual_view.EditContView`
        instance. :data:`editcontview` is a
        :class:`~kivy.properties.ObjectProperty`
    '''
    modulescontview = ObjectProperty(None)
    '''Reference to the
        :class:`~designer.components.run_contextual_view.ModulesContView`.
       :data:`modulescontview` is a :class:`~kivy.properties.ObjectProperty`
    '''
    actionbar = ObjectProperty(None)
    '''Reference to the :class:`~kivy.actionbar.ActionBar` instance.
       ActionBar is used as a MenuBar to display bunch of menu items.
       :data:`actionbar` is a :class:`~kivy.properties.ObjectProperty`
    '''
    undo_manager = ObjectProperty(UndoManager())
    '''Reference to the
        :class:`~designer.core.undo_manager.UndoManager` instance.
       :data:`undo_manager` is a :class:`~kivy.properties.ObjectProperty`
    '''
    project_watcher = ObjectProperty(None)
    '''Reference to the :class:`~designer.core.project_manager.ProjectWatcher`.
       :data:`project_watcher` is a :class:`~kivy.properties.ObjectProperty`
    '''
    project_manager = ObjectProperty(None)
    '''Reference to the :class:`~designer.core.project_manager.ProjectManager`.
       :data:`project_manager` is a :class:`~kivy.properties.ObjectProperty`
    '''
    proj_settings = ObjectProperty(None)
    '''Reference of :class:`~designer.core.project_settings.ProjectSettings`.
       :data:`proj_settings` is a :class:`~kivy.properties.ObjectProperty`
    '''
    _proj_modified_outside = BooleanProperty(False)
    '''Specifies whether current project has been changed outside Kivy Designer
       :data:`_proj_modified_outside` is a
       :class:`~kivy.properties.BooleanProperty`
    '''
    ui_creator = ObjectProperty(None)
    '''Reference to :class:`~designer.components.ui_creator.UICreator` instance.
       :data:`ui_creator` is a :class:`~kivy.properties.ObjectProperty`
    '''
    designer_content = ObjectProperty(None)
    '''Reference to
       :class:`~designer.components.designer_content.DesignerContent` instance.
       :data:`designer_content` is a :class:`~kivy.properties.ObjectProperty`
    '''
    proj_tree_view = ObjectProperty(None)
    '''Reference to Project Tree instance
       :data:`proj_tree_view` is a :class:`~kivy.properties.ObjectProperty`
    '''
    designer_settings = ObjectProperty(None)
    '''Reference of :class:`~designer.core.settings.DesignerSettings`.
       :data:`designer_settings` is a :class:`~kivy.properties.ObjectProperty`
    '''
    start_page = ObjectProperty(None)
    '''Reference of :class:`~designer.start_page.DesignerStartPage`.
       :data:`start_page` is a :class:`~kivy.properties.ObjectProperty`
    '''
    select_profile_cont_menu = ObjectProperty(None)
    '''Reference of
        :class:`~designer.uix.action_items.DesignerActionSubMenu`.
       :data:`select_profile_cont_menu` is a
       :class:`~kivy.properties.ObjectProperty`
    '''
    selected_profile = StringProperty('')
    '''Selected profile settings path
    :class:`~kivy.properties.StringProperty` and defaults to ''.
    '''
    code_inputs = ListProperty([])
    '''List with all opened code inputs and kv lang area.
    This list can be used to fetch unsaved code inputs or to check code content
    '''

    @property
    def save_window_size(self):
        '''Save window size on exit.
        '''
        if Config.getboolean('kivy', 'desktop'):
            getdefault = self.designer_settings.config_parser.getdefault
            return bool(int(getdefault('desktop', 'save_window_size', 1)))
        return False

    def __init__(self, **kwargs):
        super(Designer, self).__init__(**kwargs)
        self.project_watcher = ProjectWatcher()
        self.project_watcher.bind(on_project_modified=self.project_modified)
        self.project_manager = ProjectManager()
        self.recent_manager = RecentManager()
        self.spec_editor = BuildozerSpecEditor()
        self.widget_to_paste = None

        self.designer_settings = DesignerSettings()
        self.designer_settings.bind(on_config_change=self._config_change)
        self.designer_settings.load_settings()
        self.designer_settings.bind(on_close=self.close_popup)

        self.shortcuts = Shortcuts()
        self.shortcuts.map_shortcuts(self.designer_settings.config_parser)
        self.designer_settings.config_parser.add_callback(
                self.on_designer_settings)
        self.display_shortcuts()

        self.prof_settings = ProfileSettings()
        self.prof_settings.bind(on_close=self.close_popup)
        self.prof_settings.bind(on_changed=self.on_profiles_changed)
        self.prof_settings.bind(
            on_use_this_profile=self._perform_use_this_prof)
        self.prof_settings.load_profiles()

        self.designer_content = DesignerContent(size_hint=(1, None))
        self.designer_content = self.designer_content.__self__

        self.designer_git.bind(on_branch=self.on_git_branch)
        self.statusbar.bind(on_info_press=self.on_info_press)

        getdefault = self.designer_settings.config_parser.getdefault
        Clock.schedule_interval(self.save_project,
            (int(getdefault('global', 'auto_save_time', 5)) * 60),
        )

        self.profiler = Profiler()
        self.profiler.designer = self
        self.profiler.bind(on_error=self.on_profiler_error)
        self.profiler.bind(on_message=self.on_profiler_message)
        self.profiler.bind(on_run=self.on_profiler_run)
        self.profiler.bind(on_stop=self.on_profiler_stop)

        self.designer_tools = DesignerTools(designer=self)

        Window.bind(on_resize=self._write_window_size)
        Window.bind(on_request_close=self.on_request_close)

        # variables used in the project
        self.popup = None
        self.help_dlg = None
        self._new_dialog = None

        self.temp_proj_directories = []

    def _write_window_size(self, *_):
        '''Write updated window size to config
        '''
        parser_set = self.designer_settings.config_parser.set
        parser_set('internal', 'window_width', Window.size[0])
        parser_set('internal', 'window_height', Window.size[1])
        self.designer_settings.config_parser.write()

    def load_view_settings(self, *args):
        '''Load "View" menu saved settings
        '''
        getdefault = self.designer_settings.config_parser.getdefault
        
        proj_tree = getdefault('view', 'actn_chk_proj_tree', True)
        if proj_tree == 'False':
            self.ids.actn_chk_proj_tree.checkbox.active = False

        props_events = getdefault('view', 'actn_chk_prop_event', True)
        if props_events == 'False':
            self.ids.actn_chk_prop_event.checkbox.active = False

        wid_tree = getdefault('view', 'actn_chk_widget_tree', True)
        if wid_tree == 'False':
            self.ids.actn_chk_widget_tree.checkbox.active = False

        status_bar = getdefault('view', 'actn_chk_status_bar', True)
        if status_bar == 'False':
            self.ids.actn_chk_status_bar.checkbox.active = False

        kv_lang_area = getdefault('view', 'actn_chk_kv_lang_area', True)
        if kv_lang_area == 'False':
            self.ids.actn_chk_kv_lang_area.checkbox.active = False

    def on_designer_settings(self, section, *args):
        '''Callback to designer settings modifications
        :param section: modified section name
        '''
        if section == 'shortcuts':
            # update the shortcuts
            self.shortcuts.map_shortcuts(self.designer_settings.config_parser)
            self.display_shortcuts()

    def display_shortcuts(self, *args):
        '''Reads shortcus and update shortcut hints in KD
        '''
        m = self.shortcuts.map

        def get_hint(name):
            for short in m:
                shortcut = m[short]
                # if shortcut key is the searched
                if shortcut[1] == name:
                    mod, key = short.split('+')
                    key = key.strip()
                    modifier = eval(mod)
                    short = '+'.join(modifier)
                    if short:
                        short += f'+{key}'
                    else:
                        short = key
                    return short.title()
            return ''

        self.ids.actn_btn_new_file.hint = get_hint('new_file')
        self.ids.actn_btn_new_project.hint = get_hint('new_project')
        self.ids.actn_btn_open_project.hint = get_hint('open_project')
        self.ids.actn_btn_save.hint = get_hint('save')
        self.ids.actn_btn_save_as.hint = get_hint('save_as')
        self.ids.actn_btn_close_proj.hint = get_hint('close_project')
        self.ids.actn_btn_recent.hint = get_hint('recent')
        self.ids.actn_btn_settings.hint = get_hint('settings')
        self.ids.actn_btn_quit.hint = get_hint('exit')
        self.ids.actn_btn_run_proj.hint = get_hint('run')
        self.ids.actn_btn_stop_proj.hint = get_hint('stop')
        self.ids.actn_btn_clean_proj.hint = get_hint('clean')
        self.ids.actn_btn_build_proj.hint = get_hint('build')
        self.ids.actn_btn_rebuild_proj.hint = get_hint('rebuild')
        self.ids.actn_btn_buildozer_init.hint = get_hint('buildozer_init')
        self.ids.actn_btn_export_png.hint = get_hint('export_png')
        self.ids.actn_btn_check_pep8.hint = get_hint('check_pep8')
        self.ids.actn_btn_create_setup_py.hint = get_hint('create_setup_py')
        self.ids.actn_btn_create_gitignore.hint = get_hint('create_gitignore')
        self.ids.actn_btn_help.hint = get_hint('help')
        self.ids.actn_btn_wiki.hint = get_hint('kivy_docs')
        self.ids.actn_btn_doc.hint = get_hint('kd_docs')
        self.ids.actn_btn_page.hint = get_hint('kd_repo')
        self.ids.actn_btn_about.hint = get_hint('about')

    def toggle_fullscreen(self, check, **kwargs):
        '''
        Event Handler when ActionCheckButton "Fullscreen" is changed.
        '''
        if check.checkbox.active is True:
            Window.fullscreen = "auto"
        else:
            Window.fullscreen = False

    def restore_window_size(self, *args):
        '''Restore window size from previous application run
        '''
        getdefault = self.designer_settings.config_parser.getdefault
        width = int(getdefault('internal', 'window_width', 800))
        height = int(getdefault('internal', 'window_height', 600))
        Window.size = max(width, 800), max(height, 600)

    def on_git_branch(self, instance, branch_name, *args):
        '''Bind git changes
        :param branch_name: name of the selected branch
        '''
        update_info('Git', branch_name)

    def on_info_press(self, *args):
        '''Callback to git statusbar info press
        '''
        # open switch branch if git repo
        if self.designer_git.is_repo:
            self.designer_git.do_branches()

    def show_help(self, *args):
        '''Event handler for 'on_help' event of self.start_page
        '''
        if self.popup:
            return False
        if self.help_dlg is None:
            self.help_dlg = HelpDialog()
            self.help_dlg.rst.source = os.path.join(get_kd_dir(), 'help.rst')

        self.popup = Popup(
            title='Kivy Designer Help', content=self.help_dlg,
            size_hint=(0.95, 0.95), auto_dismiss=False,
        )
        self.popup.open()
        self.help_dlg.bind(on_cancel=self.close_popup)

    def set_escape_exit(self):
        getdefault = self.designer_settings.config_parser.getdefault
        Config.set(
            'kivy', 'exit_on_escape',
            int(getdefault('desktop', 'exit_on_escape', 0))
        )

    def _config_change(self, *args):
        '''Event Handler for 'on_config_change'
           event of self.designer_settings.
        '''
        Clock.unschedule(self.save_project)
        getdefault = self.designer_settings.config_parser.getdefault
        
        Clock.schedule_interval(self.save_project,
            (int(getdefault('global', 'auto_save_time', 5)) * 60),
        )

        max_lines = int(getdefault('global', 'num_max_kivy_console', 200))
        self.ui_creator.kivy_console.cached_history = max_lines

        recent_files = int(getdefault('global', 'num_recent_files', 10))
        self.recent_manager.max_recent_files = recent_files

        if self.save_window_size:
            self._write_window_size()

        self.set_escape_exit()

    def on_profiler_error(self, instance, message):
        '''Display an alert if get an error
        '''
        show_alert('Profile error', message)

    def on_profiler_message(self, instance, message, duration=0):
        '''Display a message in the status bar
        '''
        show_message(message, duration, 'info')

    def on_profiler_run(self, *args):
        '''When a new process starts
        '''
        self.ids.actn_btn_stop_proj.disabled = False

    def on_profiler_stop(self, *args):
        '''When a process is stopped or finished
        '''
        self.ids.actn_btn_stop_proj.disabled = True

    def _add_designer_content(self):
        '''Add designer_content to Designer, when a project is loaded
        '''
        for _child in self.children[:]:
            if _child == self.designer_content:
                return None

        self.remove_widget(self.start_page)
        self.start_page.parent = None
        self.add_widget(self.designer_content, 1)

        self.ids['actn_btn_new_file'].disabled = False
        self.ids['actn_btn_save'].disabled = False
        self.ids['actn_btn_save_as'].disabled = False
        self.ids['actn_btn_close_proj'].disabled = False
        self.ids['actn_menu_view'].disabled = False
        self.ids['actn_menu_proj'].disabled = False
        self.ids['actn_menu_run'].disabled = False
        self.ids['actn_menu_tools'].disabled = False

        self.proj_settings = ProjectSettings(
            project=self.project_manager.current_project)
        self.proj_settings.load_proj_settings()

        Clock.schedule_once(self.load_view_settings, 0)

    def on_statusbar_height(self, *args):
        '''Callback for statusbar.height
        '''
        self.designer_content.y = self.statusbar.height
        self.on_height(*args)

    def on_actionbar_height(self, *args):
        '''Callback for actionbar.height
        '''
        self.on_height(*args)

    def on_height(self, *args):
        '''Callback for self.height
        '''
        if self.actionbar and self.statusbar:
            h = (self.height-self.actionbar.height-self.statusbar.height)
            self.designer_content.height = h

            self.designer_content.y = self.statusbar.height

    def project_modified(self, *args):
        '''Event Handler called when Project is modified outside Kivy Designer
        '''
        # To dispatch modified event only once for all files/folders
        # of proj_dir
        if self._proj_modified_outside:
            return None

        msg = 'Project modified outside Kivy Designer'
        Clock.schedule_once(partial(show_message, msg, 5, 'error'))
        if self.popup:
            return None

        def close(*args):
            self._proj_modified_outside = False
            self.close_popup()

        confirm_dlg = ConfirmationDialog(
            message="Current Project has been modified\n"
                    "outside the Kivy Designer.\n"
                    "Do you want to reload project?")
        confirm_dlg.bind(on_ok=self._perform_reload, on_cancel=close)
        
        self.popup = Popup(
            title='Kivy Designer', content=confirm_dlg,
            size_hint=(None, None), size=('200pt', '150pt'),
            auto_dismiss=False)
        self.popup.open()

        self._proj_modified_outside = True

    @ignore_proj_watcher
    def _perform_reload(self, *args):
        '''Perform reload of project after it is modified
        '''
        # Perform reload of project after it is modified
        self.close_popup()
        self._perform_open(self.project_manager.current_project.path)
        self._proj_modified_outside = False

        # buildozer may have changed, reload it
        proj_path = self.project_manager.current_project.path

        def reload_spec_editor(*args):
            self.spec_editor.load_settings(proj_path)
        if os.path.exists(os.path.join(proj_path, 'buildozer.spec')):
            Clock.schedule_once(reload_spec_editor, 1)

    def on_show_edit(self, *args):
        '''Event Handler of 'on_show_edit' event. This will show EditContView
           in ActionBar
        '''
        if isinstance(self.actionbar.children[0], EditContView):
            return None

        if self.editcontview is None:
            select_all_trigger = Clock.create_trigger(
                self.action_btn_select_all_pressed)
            self.editcontview = EditContView(
                on_undo=self.action_btn_undo_pressed,
                on_redo=self.action_btn_redo_pressed,
                on_cut=self.action_btn_cut_pressed,
                on_copy=self.action_btn_copy_pressed,
                on_paste=self.action_btn_paste_pressed,
                on_delete=self.action_btn_delete_pressed,
                on_selectall=select_all_trigger,
                on_next_screen=self._next_screen,
                on_prev_screen=self._prev_screen,
                on_touch_up=self.on_editcontview_release,
                on_find=partial(self.designer_content.show_findmenu, True))

        self.actionbar.add_widget(self.editcontview)

        widget = self.ui_creator.propertyviewer.widget
        show = isinstance(widget, (Carousel, ScreenManager, TabbedPanel))
        self.editcontview.show_action_btn_screen(show)

        self._edit_selected = 'Py'
        if self.ui_creator.kv_code_input.clicked:
            self._edit_selected = 'KV'
        elif self.ui_creator.playground.clicked:
            self._edit_selected = 'Play'

        show_f = self._edit_selected == 'Py'
        self.editcontview.show_find(show_f)

        self.ui_creator.playground.clicked = False
        self.ui_creator.kv_code_input.clicked = False

    def on_editcontview_release(self, instance, touch):
        if self._edit_selected != 'Py':
            return self.editcontview.on_touch_up(touch)
        
        tab_list = self.designer_content.tab_pannel.tab_list
        for tab_item in tab_list:
            clicked = tab_item.content.code_input.clicked    
            if hasattr(tab_item.content, 'code_input') and clicked:
                Clock.schedule_once(tab_item.content.code_input.do_focus)
                return True

    def _prev_screen(self, *args):
        '''Event handler for 'on_prev_screen' for self.editcontview
        '''
        widget = self.ui_creator.propertyviewer.widget
        if isinstance(widget, Carousel):
            widget.load_previous()

        elif isinstance(widget, ScreenManager):
            widget.current = widget.previous()

        elif isinstance(widget, TabbedPanel):
            index = widget.tab_list.index(widget.current_tab)
            if len(widget.tab_list) <= (index + 1):
                return None

            widget.switch_to(widget.tab_list[index + 1])

    def _next_screen(self, *args):
        '''Event handler for 'on_next_screen' for self.editcontview
        '''
        widget = self.ui_creator.propertyviewer.widget
        if isinstance(widget, Carousel):
            widget.load_next()

        elif isinstance(widget, ScreenManager):
            widget.current = widget.next()

        elif isinstance(widget, TabbedPanel):
            index = widget.tab_list.index(widget.current_tab)
            if index == 0:
                return None

            widget.switch_to(widget.tab_list[index - 1])

    def on_touch_down(self, touch):
        '''Override of FloatLayout.on_touch_down. Used to determine where
           touch is down and to call self.actionbar.on_previous
        '''
        instance = isinstance(self.actionbar.children[0], EditContView)
        collided = self.actionbar.collide_point(*touch.pos) 
        
        if instance or not collided:
            if self.actionbar._stack_cont_action_view:
                self.actionbar.on_previous(self)
            self.ui_creator.playground.clicked = False

        return super(FloatLayout, self).on_touch_down(touch)

    def action_btn_new_file_pressed(self, *args):
        '''Event Handler when ActionButton "New Project" is pressed.
        '''
        if self.popup:
            return False

        input_dialog = InputDialog("File name:")
        input_dialog.bind(on_confirm=self._perform_new_file, on_cancel=self.close_popup)
        
        self.popup = Popup(
            title="Add new File", content=input_dialog,
            size_hint=(None, None), size=('200pt', '150pt'),
            auto_dismiss=False,
        )
        self.popup.open()
        return True

    @ignore_proj_watcher
    def _perform_new_file(self, instance):
        '''
        Create a new file in the project folder
        '''
        current_project = self.project_manager.current_project
        
        file_name = instance.get_user_input()
        if file_name.find('.') == -1:
            file_name += '.py'

        new_file = os.path.join(current_project.path, file_name)
        if os.path.exists(new_file):
            instance.lbl_error.text = 'File exists'
            return None

        open(new_file, 'a').close()
        self.designer_content.update_tree_view(current_project)
        self.close_popup()

    def action_btn_new_project_pressed(self, *args):
        '''Event Handler when ActionButton "New" is pressed.
        '''
        if self.popup:
            return False

        if self.project_manager.current_project.saved:
            self._show_new_dialog()
            return True

        _confirm_dlg_save = ConfirmationDialogSave(
            'Your project is not saved.\nWhat would you like to do?'
        )
        def save_and_open(*args):
            self.action_btn_save_pressed()
            self._show_new_dialog()
        _confirm_dlg_save.bind(
            on_dont_save=self._show_new_dialog, on_save=save_and_open,
            on_cancel=self.close_popup)

        self.popup = Popup(
            title='New', content=_confirm_dlg_save,
            size_hint=(None, None), size=('300pt', '150pt'),
            auto_dismiss=False,
        )
        self.popup.open()
        return True

    def _show_new_dialog(self, *args):
        if self.popup:
            return False

        if self._new_dialog is None:
            self._new_dialog = NewProjectDialog()
            self._new_dialog.bind(on_select=self._perform_new, on_cancel=self.close_popup)
        
        self.popup = Popup(
            title='New Project', content=self._new_dialog,
            size_hint=(None, None), size=('650pt', '450pt'),
            auto_dismiss=False,
        )
        self.popup.open()

    @ignore_proj_watcher
    def _perform_new(self, *args):
        '''To load new project
        '''
        self.close_popup()

        new_proj_dir = mkdtemp(prefix=constants.NEW_PROJECT_DIR_NAME_PREFIX)
        self.temp_proj_directories.append(new_proj_dir)

        template = self._new_dialog.template_list.text
        app_name = self._new_dialog.app_name.text
        package_domain, package_name = self._new_dialog.package_name.text\
            .rsplit('.', 1)
        package_version = self._new_dialog.package_version.text

        templates_dir = os.path.join(get_kd_data_dir(), constants.DIR_NEW_TEMPLATE)
        
        kv_file = NEW_PROJECTS[template][0]
        py_file = NEW_PROJECTS[template][1]
        shutil.copy(os.path.join(templates_dir, py_file),
                    os.path.join(new_proj_dir, "main.py"))

        shutil.copy(os.path.join(templates_dir, kv_file),
                    os.path.join(new_proj_dir, "main.kv"))

        buildozer = io.open(os.path.join(new_proj_dir, 'buildozer.spec'), 'w', encoding='utf-8')

        for line in io.open(os.path.join(templates_dir, 'default.spec'), 'r', encoding='utf-8'):
            line = line.replace('$app_name', app_name)
            line = line.replace('$package_name', package_name)
            line = line.replace('$package_domain', package_domain)
            line = line.replace('$package_version', package_version)
            buildozer.write(line)
        buildozer.close()

        self._perform_open(new_proj_dir, True)
        self.project_manager.current_project.new_project = True
        self.project_manager.current_project.saved = False
        show_message('Project created successfully', 5, 'info')

    def cleanup(self):
        '''To cleanup everything loaded by the current project before loading
           another project.
        '''
        self.ui_creator.cleanup()
        self.undo_manager.cleanup()
        self.designer_content.toolbox.cleanup()
        self.designer_content.tab_pannel.cleanup()

        for node in self.proj_tree_view.root.nodes[:]:
            self.proj_tree_view.remove_node(node)

        for widget in toolbox_widgets[:]:
            if widget[1] == 'custom':
                toolbox_widgets.remove(widget)
        self.ui_creator.kv_code_input.text = ''

    def action_btn_open_pressed(self, *args):
        '''Event Handler when ActionButton "Open" is pressed.
        '''
        if self.popup:
            return False

        if self.project_manager.current_project.saved:
            self._show_open_dialog()
            return True
        
        _confirm_dlg_save = ConfirmationDialogSave(
            'Your project is not saved.\nWhat would you like to do?'
        )
        def save_and_open(*args):
            self.close_popup()
            self.action_btn_save_pressed()
            self._show_open_dialog()

        def show_open(*args):
            self.close_popup()
            self._show_open_dialog()

        _confirm_dlg_save.bind(on_dont_save=show_open,
                                on_save=save_and_open,
                                on_cancel=self.close_popup)
        self.popup = Popup(
            title='Kivy Designer', auto_dismiss=False,
            size_hint=(None, None), size=('300pt', '150pt'),
            content=_confirm_dlg_save,
        )
        self.popup.open()
        return True

    def action_btn_close_proj_pressed(self, *args):
        '''
        Event Handler when ActionButton "Close Project" is pressed.
        '''
        if self.popup:
            return False

        if self.project_manager.current_project.saved:
            self._perform_close_project()
            return True

        _confirm_dlg_save = ConfirmationDialogSave(
            'Your project is not saved.\nWhat would you like to do?'
        )
        def save_and_close(*args):
            self.close_popup()
            self.action_btn_save_pressed()
            self._perform_close_project()

        _confirm_dlg_save.bind(on_cancel=self.close_popup,
                                on_dont_save=self._perform_close_project,
                                on_save=save_and_close)
        self.popup = Popup(
            title='Kivy Designer', auto_dismiss=False,
            size_hint=(None, None), size=('300pt', '150pt'),
            content=_confirm_dlg_save,
        )
        self.popup.open()
        return True

    def _perform_close_project(self, *args):
        '''
        Close the current project and go to the start page
        '''
        self.close_popup()

        self.remove_widget(self.designer_content)
        self.designer_content.parent = None
        self.add_widget(self.start_page, 1)

        self.ids['actn_btn_new_file'].disabled = True
        self.ids['actn_btn_save'].disabled = True
        self.ids['actn_btn_save_as'].disabled = True
        self.ids['actn_btn_close_proj'].disabled = True
        self.ids['actn_menu_view'].disabled = True
        self.ids['actn_menu_proj'].disabled = True
        self.ids['actn_menu_run'].disabled = True
        self.ids['actn_menu_tools'].disabled = True
        self.project_manager.close_current_project()
        self.project_watcher.stop_watching()

    def _show_open_dialog(self, *args):
        '''To show FileBrowser to "Open" a project
        '''
        if self.popup:
            return False

        def_path = os.path.expanduser('~')
        current_project = self.project_manager.current_project
        if current_project.path and not current_project.new_project:
            def_path = self.project_manager.current_project.path

        def open_file_browser(instance):
            if instance.is_canceled():
                return None
            self._fbrowser_load(instance)

        XFileOpen(title="Open", on_dismiss=open_file_browser, path=def_path)

    def _fbrowser_load(self, instance):
        '''Event Handler for 'on_load' event of self._fbrowser
        '''
        if not instance.selection or self.popup:
            return None

        file_path = instance.selection[0]
        file_name, file_extension = os.path.splitext(instance.selection[0])

        error = None
        try:
            if file_extension in ('.py', '.kv') \
                    or (file_name.endswith('buildozer')
                        and file_extension == '.spec'):
                self._perform_open(file_path)
            else:
                error = 'Cannot load file type: .%s, Please load a .py file' % \
                        file_extension
        except:
            error = 'Cannot load empty file type'

        if error:
            show_message(error, 5, 'error')

    def _perform_open(self, file_path, new_project=False):
        '''To open a project given by file_path
        '''
        self.project_watcher.stop_watching()
        show_message('Project loaded successfully', 5, 'info')

        self.cleanup()

        if os.path.isfile(file_path):
            file_path = os.path.dirname(file_path)

        project = self.project_manager.open_project(file_path)
        if project is None:
            return None
            
        self.project_watcher.start_watching(file_path)
        self.designer_content.update_tree_view(project)

        if not new_project:
            self.recent_manager.add_path(project.path)

        for widget in toolbox_widgets[:]:
            if widget[1] == 'custom':
                toolbox_widgets.remove(widget)

        self._add_designer_content()
        app_widgets = self.project_manager.current_project.app_widgets

        if app_widgets:
            for name in app_widgets.keys():
                toolbox_widgets.append((name, 'custom'))

            self.designer_content.toolbox.update_app_widgets()

            if len(app_widgets):
                first_wdg = app_widgets[list(app_widgets.keys())[-1]]
                self.ui_creator.playground.load_widget(first_wdg.name)
            else:
                self.ui_creator.playground.no_widget()

        Clock.schedule_once(partial(self.ui_creator.kivy_console.run_command,
            'cd %s' % (file_path)
        ), 1)
        self.designer_git.load_repo(file_path)

    def close_popup(self, *args):
        '''EventHandler for all self.popup when self.popup.content
           emits 'on_cancel' or equivalent.
        '''
        if not self.popup:
            return False

        if self.popup.content:
            # remove the content from the popup
            self.popup.content.parent = None
        self.popup.dismiss()
        self.popup = None
        return True

    @ignore_proj_watcher
    def save_project(self, *args):
        '''Saves the current project.
        :param path: path to save the project.
        '''
        proj = self.project_manager.current_project
        saved = proj.save()
        if saved:
            show_message('Project saved!', 5, 'info')
        else:
            show_message('Failed to save the project!', 5, 'error')

    def action_btn_save_pressed(self, exit_on_save=False, *args):
        '''Event Handler when ActionButton "Save" is pressed.
        :param exit_on_save: if True, closes the KD after saving the project
        '''
        proj = self.project_manager.current_project
        if proj.new_project:
            self.action_btn_save_as_pressed(exit_on_save=exit_on_save)
            return None

        self.save_project()
        if exit_on_save:
            self._perform_quit()

    def action_btn_save_as_pressed(self, exit_on_save=False, *args):
        '''Event Handler when ActionButton "Save As" is pressed.
        '''
        if self.popup:
            return False
        proj = self.project_manager.current_project

        def_path = os.path.expanduser('~')
        if not proj.new_project and proj.path:
            def_path = proj.path

        def save_project(instance):
            if instance.is_canceled():
                return None

            self._perform_save_as(instance, exit_on_save=exit_on_save)

        XFileSave(title="Enter Folder Name", size_hint=(0.9, 0.9),
                  on_dismiss=save_project, path=def_path)

    def _perform_save_as(self, instance, exit_on_save=False):
        '''Event handler for 'on_success' event of self._save_as_browser
        '''
        proj_dir = instance.path + os.path.sep + instance.filename

        # save the project in the folder and then copy it to a new folder
        self.save_project()
        path = self.project_manager.current_project.path
        if os.path.isdir(path):
            copy_tree(path, proj_dir)

        if exit_on_save:
            self._perform_quit()
            return None
        self._perform_open(proj_dir)

    def action_btn_settings_pressed(self, *args):
        '''Event handler for 'on_release' event of
           DesignerActionButton "Settings"
        '''
        if self.popup:
            return False

        self.designer_settings.parent = None
        self.popup = Popup(
            title="Kivy Designer Settings",
            content=self.designer_settings,
            size_hint=(None, None),
            size=(720, 480), auto_dismiss=False,
        )
        self.popup.open()
        return True

    def action_btn_select_prof_project_pressed(self, *args):
        '''Event handler for "Select Profile" menu
        '''
        pass

    def on_profiles_changed(self, *args):
        '''Callback when there is a modification in the profile settings
        '''
        self.prof_settings.load_profiles()
        self.fill_select_profile_menu()

    def _perform_use_this_prof(self, instance, *args):
        '''Callback to "Use this Profile" button
        '''
        _config = instance.selected_config
        _config_path = _config.filename
        config_parser = self.designer_settings.config_parser

        config_parser.set('internal', 'default_profile', _config_path)
        config_parser.write()

    def fill_select_profile_menu(self, *args):
        '''Fill self.select_profile_cont_menu with available Build Profiles
        '''
        prof_menu = self.select_profile_cont_menu
        prof_menu.remove_children()
        group = 'profile'
        config_parsers = self.prof_settings.config_parsers
        
        for profile in sorted(config_parsers.keys()):
            config = config_parsers[profile]
            config_path = config.filename

            if isinstance(config_path, bytes):
                config_path = config_path.decode(get_fs_encoding())

            prof_name = config.getdefault('profile', 'name', 'PROFILE')
            if not prof_name.strip():
                prof_name = 'PROFILE'

            btn = DesignerActionProfileCheck(group=group,
                                             allow_no_selection=False)
            btn.text = prof_name
            btn.checkbox.active = False

            btn.config_key = profile
            btn.bind(on_active=self._perform_profile_selected)

            getdefault = self.designer_settings.config_parser.getdefault
            if getdefault('internal', 'default_profile', '') == config_path:
                btn.checkbox.active = True
                self.selected_profile = config_path
                self._perform_profile_selected(btn, btn.checkbox, True)

            prof_menu.add_widget(btn)

        prof_menu._add_widget()

    def _perform_profile_selected(self, instance, checkbox, value, *args):
        '''Event handler to select profile radio button.
        Save the selected config_parser path to the config
        '''
        if not value:
            return False
        
        _config = self.prof_settings.config_parsers[instance.config_key]
        _config_path = _config.filename
        config_parser = self.designer_settings.config_parser
        
        if isinstance(_config_path, bytes):
            _config_path.decode(get_fs_encoding())
        
        config_parser.set('internal', 'default_profile', _config_path)
        config_parser.write()
        self.selected_profile = _config_path

        target = _config.getdefault('profile', 'target', '')
        if target == 'Desktop':
            self.ids.actn_btn_run_module.disabled = False
        else:
            self.ids.actn_btn_run_module.disabled = True

    def action_btn_recent_files_pressed(self, *args):
        '''Event Handler when ActionButton "Recent Projects" is pressed.
        '''
        if self.popup:
            return False

        _recent_dlg = RecentDialog(self.recent_manager.list_projects)
        _recent_dlg.bind(on_cancel=self.close_popup,
                         on_select=self._recent_file_release)
        self.popup = Popup(title='Recent Projects', content=_recent_dlg,
                           size_hint=(0.5, 0.5), auto_dismiss=False)
        self.popup.open()
        return True

    def _recent_file_release(self, instance, *args):
        '''Event Handler for 'on_select' event of RecentDialog.
        '''
        self._perform_open(instance.get_selected_project())
        self.close_popup()

    def remove_temp_proj_directories(self):
        '''Before KD closes, delete temp new project directories.
        '''
        for temp_proj_dir in self.temp_proj_directories:
            if os.getcwd() == temp_proj_dir:
                os.chdir(get_config_dir())
            shutil.rmtree(temp_proj_dir)

    def check_quit(self, *args):
        '''Check if the KD can be closed.
        If the project is modified, show an alert. Otherwise closes it.
        '''
        if self.popup:
            # if there is something open, stops the propagation
            show_message(
                'You must close all popups before closing Kivy Designer',
                5, 'error')
            return True

        proj = self.project_manager.current_project
        if proj.new_project or not proj.saved:
            _confirm_dlg_save = ConfirmationDialogSave(
                'Your project is not saved.\nWhat would you like to do?',
            )
            def save(*args):
                self.close_popup()
                self.action_btn_save_pressed(exit_on_save=True)

            _confirm_dlg_save.bind(
                on_dont_save=self._perform_quit,
                on_save=save, on_cancel=self.close_popup,
            )
            self.popup = Popup(
                title='Quit', content=_confirm_dlg_save,
                size_hint=(None, None), size=('300pt', '150pt'),
                auto_dismiss=False,
            )
            self.popup.open()
            return True

        self._perform_quit()
        return False

    def on_request_close(self, *args):
        '''Event Handler for 'on_request_close' event of Window.
           Check if the project was saved before exit
        '''
        return self.check_quit()

    def action_btn_quit_pressed(self, *args):
        '''Event Handler when ActionButton "Quit" is pressed.
        '''
        return self.check_quit()

    def _perform_quit(self, *args):
        '''Perform Application qui.Application
        '''
        self.remove_temp_proj_directories()
        App.get_running_app().stop()

    def action_btn_undo_pressed(self, *args):
        '''Event Handler when ActionButton "Undo" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.undo_manager.do_undo()

        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.do_undo()

        elif self._edit_selected == 'Py':
            tab_list = self.designer_content.tab_pannel.tab_list
            for tab_item in tab_list:
                code = tab_item.content.code_input
                if hasattr(tab_item.content, 'code_input') and code.clicked:
                    code.do_undo()
                    break

    def action_btn_redo_pressed(self, *args):
        '''Event Handler when ActionButton "Redo" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.undo_manager.do_redo()

        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.do_redo()

        elif self._edit_selected == 'Py':
            tab_list = self.designer_content.tab_pannel.tab_list
            for tab_item in tab_list:
                code = tab_item.content.code_input
                if hasattr(tab_item.content, 'code_input') and code.clicked:
                    code.do_redo()
                    break

    def action_btn_cut_pressed(self, *args):
        '''Event Handler when ActionButton "Cut" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.ui_creator.playground.do_cut()

        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.cut()

        elif self._edit_selected == 'Py':
            tab_list = self.designer_content.tab_pannel.tab_list
            for tab_item in tab_list:
                code = tab_item.content.code_input
                if hasattr(tab_item.content, 'code_input') and code.clicked:
                    code.cut()
                    break

    def action_btn_copy_pressed(self, *args):
        '''Event Handler when ActionButton "Copy" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.ui_creator.playground.do_copy()

        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.copy()

        elif self._edit_selected == 'Py':
            tab_list = self.designer_content.tab_pannel.tab_list
            for tab_item in tab_list:
                code = tab_item.content.code_input
                if hasattr(tab_item.content, 'code_input') and code.clicked:
                    code.copy()
                    break

    def action_btn_paste_pressed(self, *args):
        '''Event Handler when ActionButton "Paste" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.ui_creator.playground.do_paste()

        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.paste()

        elif self._edit_selected == 'Py':
            tab_list = self.designer_content.tab_pannel.tab_list
            for tab_item in tab_list:
                code = tab_item.content.code_input
                if hasattr(tab_item.content, 'code_input') and code.clicked:
                    code.paste()
                    break

    def action_btn_delete_pressed(self, *args):
        '''Event Handler when ActionButton "Delete" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.ui_creator.playground.do_delete()

        elif self._edit_selected == 'KV':
            self.ui_creator.kv_code_input.delete_selection()

        elif self._edit_selected == 'Py':
            tab_list = self.designer_content.tab_pannel.tab_list
            for tab_item in tab_list:
                code = tab_item.content.code_input
                if hasattr(tab_item.content, 'code_input') and code.clicked:
                    code.delete_selection()
                    break

    def action_btn_select_all_pressed(self, *args):
        '''Event Handler when ActionButton "Select All" is pressed.
        '''

        if self._edit_selected == 'Play':
            self.ui_creator.playground.do_select_all()

        elif self._edit_selected == 'KV':
            Clock.schedule_once(self.ui_creator.kv_code_input.do_select_all)

        elif self._edit_selected == 'Py':
            tab_list = self.designer_content.tab_pannel.tab_list
            for tab_item in tab_list:
                code = tab_item.content.code_input
                if hasattr(tab_item.content, 'code_input') and code.clicked:
                    Clock.schedule_once(code.do_select_all)
                    break

    def action_chk_btn_toolbox_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "Toolbox" is activated.
        '''
        config_parser = self.designer_settings.config_parser
        config_parser.set('view', 'actn_chk_proj_tree', chk_btn.checkbox.active)
        config_parser.write()

        splitter_tree = self.designer_content.splitter_tree
        if chk_btn.checkbox.active:
            self._toolbox_parent.add_widget(splitter_tree)
            splitter_tree.width = self._toolbox_width
            return None
        
        self._toolbox_parent = splitter_tree.parent
        self._toolbox_parent.remove_widget(splitter_tree)
        self._toolbox_width = splitter_tree.width
        splitter_tree.width = 0

    def action_chk_btn_property_viewer_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "Property Viewer" is activated.
        '''
        config_parser = self.designer_settings.config_parser
        config_parser.set('view', 'actn_chk_prop_event', chk_btn.checkbox.active)
        config_parser.write()

        splitter = self.ui_creator.splitter_widget_tree
        splitter_prop = self.ui_creator.splitter_property
        if not chk_btn.checkbox.active:
            self._splitter_property_parent = splitter_prop.parent
            self._splitter_property_parent.remove_widget(splitter_prop)
            self._toggle_splitter_widget_tree()
            return None

        self._toggle_splitter_widget_tree()
        if splitter.parent is None:
            self._splitter_widget_tree_parent.add_widget(splitter)
            splitter.width = self._splitter_widget_tree_width

        add_tree = False
        grid = self.ui_creator.grid_widget_tree
        if grid.parent is not None:
            add_tree = True
            splitter_prop.size_hint_y = None
            splitter_prop.height = 300

        self._splitter_property_parent.clear_widgets()
        if add_tree:
            self._splitter_property_parent.add_widget(grid)

        self._splitter_property_parent.add_widget(splitter_prop)

    def action_chk_btn_widget_tree_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "Widget Tree" is activated.
        '''
        config_parser = self.designer_settings.config_parser
        config_parser.set('view', 'actn_chk_widget_tree', chk_btn.checkbox.active)
        config_parser.write()

        splitter_prop = self.ui_creator.splitter_property
        grid = self.ui_creator.grid_widget_tree
        if not chk_btn.checkbox.active:
            self._grid_widget_tree_parent = grid.parent
            self._grid_widget_tree_parent.remove_widget(grid)
            splitter_prop.size_hint_y = 1
            self._toggle_splitter_widget_tree()
            return None

        self._toggle_splitter_widget_tree()
        add_prop = False
        if splitter_prop.parent is not None:
            add_prop = True

        self._grid_widget_tree_parent.clear_widgets()
        self._grid_widget_tree_parent.add_widget(grid)
        if add_prop:
            self._grid_widget_tree_parent.add_widget(splitter_prop)
            splitter_prop.size_hint_y = None
            splitter_prop.height = 300


    def _toggle_splitter_widget_tree(self):
        '''To show/hide splitter_widget_tree
        '''
        splitter = self.ui_creator.splitter_widget_tree
        spl_p_parent = self.ui_creator.splitter_property.parent
        grid_parent = self.ui_creator.grid_widget_tree.parent

        if splitter.parent is not None and spl_p_parent is None and grid_parent is None:
            self._splitter_widget_tree_parent = splitter.parent
            self._splitter_widget_tree_parent.remove_widget(splitter)
            self._splitter_widget_tree_width = splitter.width
            splitter.width = 0

        elif splitter.parent is None:
            self._splitter_widget_tree_parent.add_widget(splitter)
            splitter.width = self._splitter_widget_tree_width

    def action_chk_btn_status_bar_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "StatusBar" is activated.
        '''
        config_parser = self.designer_settings.config_parser
        config_parser.set('view', 'actn_chk_status_bar', chk_btn.checkbox.active)
        config_parser.write()

        if chk_btn.checkbox.active:
            self._statusbar_parent.add_widget(self.statusbar)
            self.statusbar.height = self._statusbar_height
        else:
            self._statusbar_parent = self.statusbar.parent
            self._statusbar_height = self.statusbar.height
            self._statusbar_parent.remove_widget(self.statusbar)
            self.statusbar.height = 0

    def action_chk_btn_kv_area_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "KVLangArea" is activated.
        '''
        config_parser = self.designer_settings.config_parser
        config_parser.set('view', 'actn_chk_kv_lang_area', chk_btn.checkbox.active)
        config_parser.write()

        splitter_code = self.ui_creator.splitter_kv_code_input
        if chk_btn.checkbox.active:
            splitter_code.height = self._kv_area_height
            self._kv_area_parent.add_widget(splitter_code)
            return None
        
        self._kv_area_parent = splitter_code.parent
        self._kv_area_height = splitter_code.height
        splitter_code.height = 0
        self._kv_area_parent.remove_widget(splitter_code)

    def _error_adding_file(self, *args):
        '''Event Handler for 'on_error' event of self._add_file_dlg
        '''
        show_message('Error while adding file to project', 5, 'error')
        self.close_popup()

    def _added_file(self, *args):
        '''Event Handler for 'on_added' event of self._add_file_dlg
        '''
        show_message('File successfully added to project', 5, 'info')
        self.close_popup()
        project = self.project_manager.current_project
        self.designer_content.update_tree_view(project)

    def action_btn_add_file_pressed(self, *args):
        '''Event Handler when ActionButton "Add File" is pressed.
        '''
        if self.popup:
            return False
        
        project = self.project_manager.current_project
        add_file_dlg = AddFileDialog(project)
        add_file_dlg.bind(
            on_added=self._added_file,
            on_error=self._error_adding_file,
            on_cancel=self.close_popup,
        )
        self.popup = Popup(
            title="Add File", content=add_file_dlg,
            size_hint=(None, None), size=(480, 350),
            auto_dismiss=False,
        )
        self.popup.open()
        return True

    def action_btn_run_module_pressed(self, *args):

        if self.modulescontview is None:
            self.modulescontview = ModulesContView()
            self.modulescontview.bind(
                on_module=self.action_btn_run_project_pressed)

        self.actionbar.add_widget(self.modulescontview)

    def action_btn_project_settings_pressed(self, *args):
        '''Event Handler when ActionButton "Project Settings" is pressed.
        '''
        if self.popup:
            return False
        
        project = self.project_manager.current_project
        self.proj_settings = ProjectSettings(project=project)
        self.proj_settings.load_proj_settings()
        self.proj_settings.bind(on_close=self.close_popup)
        
        self.popup = Popup(
            title="Project Settings", content=self.proj_settings,
            size_hint=(None, None), size=(720, 480),
            auto_dismiss=False,
        )
        self.popup.open()
        return True

    def action_btn_edit_prof_project_pressed(self, *args):
        '''Event Handler when ActionButton "Edit Profiles" is pressed.
        '''
        if self.popup:
            return False

        self.prof_settings.load_profiles()
        self.popup = Popup(
            title="Build Profiles", content=self.prof_settings,
            size_hint=(None, None), size=(720, 480),
            auto_dismiss=False,
        )
        self.popup.open()
        return True

    def check_selected_prof(self, *args):
        '''Check if there is a selected build profile.
        :return: True if ok. Show an alert and returns false if not.
        '''
        if self.selected_profile == '' or not os.path.isfile(self.selected_profile):
            show_alert('Profiler error', "Please, select a build profile on 'Run' -> 'Select Profile' menu")
            return False

        self.profiler.load_profile(
            self.selected_profile,
            self.project_manager.current_project.path)
        return True

    def action_btn_stop_project_pressed(self, *args):
        '''Event handler when ActionButton "Stop" is pressed.
        '''
        if not self.check_selected_prof():
            return None
        self.profiler.stop()

    def action_btn_clean_project_pressed(self, *args):
        '''Event handler when ActionButton "Clean" is pressed
        '''
        if not self.check_selected_prof():
            return None
        self.profiler.clean()

    def action_btn_build_project_pressed(self, *args):
        '''Event handler when ActionButton "Build" is pressed
        '''
        if not self.check_selected_prof():
            return None
        self.profiler.build()

    def action_btn_rebuild_project_pressed(self, *args):
        '''Event handler when ActionButton "Build" is pressed
        '''
        if not self.check_selected_prof():
            return None
        self.profiler.rebuild()

    def action_btn_run_project_pressed(self, *args, **kwargs):
        '''Event Handler when ActionButton "Run" is pressed.
        '''
        if not self.check_selected_prof():
            return None

        self.profiler.run(*args, **kwargs)

    def on_sandbox_getting_exception(self, *args):
        '''Event Handler for
           :class:`~designer.uix.sandbox.DesignerSandbox`
           on_getting_exception event. This function will add exception
           string in error_console.
        '''
        show_error_console(traceback.format_exc(), append=False)
        if self.ui_creator.playground.sandbox.error_active:
            self.ui_creator.tab_pannel.switch_to(
                self.ui_creator.tab_pannel.tab_list[0])

        self.ui_creator.playground.sandbox.error_active = False

    def action_btn_about_pressed(self, *args):
        '''Event handler for 'on_release' event of DesignerActionButton
           "About Kivy Designer"
        '''
        if self.popup:
            return False

        about_dlg = AboutDialog()
        self.popup = Popup(
            title='About Kivy Designer', content=about_dlg,
            size_hint=(None, None), size=(600, 400),
            auto_dismiss=False,
        )
        self.popup.open()
        about_dlg.bind(on_close=self.close_popup)
        return True

    #### GET SITES ####
    def open_repo(self, *args):
        '''
        Open the Kivy Designer repository
        '''
        webbrowser.open("https://github.com/kivy/kivy-designer")

    def open_docs(self, *args):
        '''
        Open the Kivy docs
        '''
        webbrowser.open("http://kivy.org/docs/")

    def open_kd_docs(self, *args):
        '''
        Open the Kivy Designer documentation
        '''
        webbrowser.open("http://kivy-designer.readthedocs.org")

class DesignerException(ExceptionHandler):

    raised_exception = False
    '''Indicates if the BugReporter has already raised some exception
    '''

    def handle_exception(self, inst):
        if self.raised_exception:
            return ExceptionManager.PASS

        App.get_running_app().stop()
        if isinstance(inst, KeyboardInterrupt):
            return ExceptionManager.PASS

        for child in Window.children:
            Window.remove_widget(child)

        self.raised_exception = True
        Window.fullscreen = False
        BugReporterApp(traceback=traceback.format_exc()).run()
        return ExceptionManager.PASS


class DesignerApp(App):

    widget_focused = ObjectProperty(allownone=True)
    '''Currently focused widget
    '''

    started = BooleanProperty(False)
    '''Indicates if has finished the build()
    '''

    title = 'Kivy Designer'

    def on_stop(self, *args):
        if hasattr(self.root, 'ui_creator'):
            if hasattr(self.root.ui_creator, 'py_console'):
                self.root.ui_creator.py_console.exit()

    def build(self):
        ExceptionManager.add_handler(DesignerException())

        modules = (
            ('Playground', 'components.playground'),
            ('Toolbox', 'components.toolbox'),
            ('StatusBar', 'components.statusbar'),
            ('PropertyViewer', 'components.property_viewer'),
            ('EventViewer', 'components.event_viewer'),
            ('WidgetsTree', 'components.widgets_tree'),
            ('UICreator', 'components.ui_creator'),
            ('DesignerGit', 'tools.git_integration'),
            ('DesignerContent', 'components.designer_content'),
            ('KivyConsole', 'components.kivy_console'),
            ('KVLangAreaScroll', 'components.kv_lang_area'),
            ('PythonConsole', 'uix.py_console'),
            ('DesignerContent', 'components.designer_content'),
            ('EventDropDown', 'components.event_viewer'),
            ('DesignerActionGroup', 'uix.action_items'),
            ('DesignerActionButton', 'uix.action_items'),
            ('DesignerActionSubMenu', 'uix.action_items'),
            ('DesignerStartPage', 'components.start_page'),
            ('DesignerLinkLabel', 'components.start_page'),
            ('RecentFilesBox', 'components.start_page'),
            ('ContextMenu', 'components.edit_contextual_view'),
            ('PlaygroundSizeSelector', 'components.playground_size_selector'),
            ('CodeInputFind', 'uix.code_find'),
        )
        for file in modules:
            classname, module = file
            Factory.register(classname, module=module)

        self._widget_focused = None
        # self.root = Designer()
        Clock.schedule_once(self._setup)
        return Designer()

    def _setup(self, *args):
        '''To setup the properties of different classes
        '''
        if self.root.save_window_size:
            Clock.schedule_once(self.root.restore_window_size, 0)
        self.root.set_escape_exit()

        design = self.root.designer_content
        self.root.ui_creator = design.ui_creator
        playground = self.root.ui_creator.playground
        eventviewer = self.root.ui_creator.eventviewer
        statusbar = self.root.statusbar
        actionbar = self.root.actionbar

        self.root.proj_tree_view = design.tree_view
        statusbar.playground = playground
        playground.undo_manager = self.root.undo_manager

        eventviewer.designer_tabbed_panel = design.tab_pannel
        statusbar.bind(height=self.root.on_statusbar_height)
        actionbar.bind(height=self.root.on_actionbar_height)
        
        playground.sandbox = DesignerSandbox()
        playground.add_widget(playground.sandbox)
        playground.sandbox.pos = playground.pos
        playground.sandbox.size = playground.size

        getdefault = self.root.designer_settings.config_parser.getdefault
        max_lines = int(getdefault('global', 'num_max_kivy_console', 200))
        console = self.root.ui_creator.kivy_console
        propviewer = self.root.ui_creator.propertyviewer
        console.cached_history = max_lines

        playground.sandbox.bind(on_getting_exception=self.root.on_sandbox_getting_exception)
        self.bind(widget_focused=propviewer.setter('widget'))
        self.bind(widget_focused=eventviewer.setter('widget'))
        self.focus_widget(playground.root)

        self.create_kivy_designer_dir()
        projects = self.root.recent_manager.list_projects
        self.root.start_page.recent_files_box.add_recent(projects)

        self.root.fill_select_profile_menu()
        self.started = True

    def create_kivy_designer_dir(self):
        '''To create the ~/.kivy-designer dir
        '''
        if not os.path.exists(get_config_dir()):
            os.mkdir(get_config_dir())

    def create_draggable_element(self, instance, widget_name, touch,
                                 widget=None):
        '''Create PlagroundDragElement and make it draggable
           until the touch is released also search default args if exist
           :param widget: instance of widget.
                            If set, widget_name will be ignored
           :param touch: instance of the current touch
           :param instance: if from toolbox, ToolboxButton instance.
                    None otherwise
           :param widget_name: name of the widget that will be dragged
        '''
        container = None
        if widget:
            container = PlaygroundDragElement(
                    playground=self.root.ui_creator.playground,
                    child=Widget(),
                    widget=widget)
            touch.grab(container)
            touch.grab_current = container
            container.on_touch_move(touch)
            container.center_x = touch.x
            container.y = touch.y + 20
            return None

        default_args = {}
        extra_args = {}
        for options in toolbox_widgets:
            if widget_name == options[0]:
                if len(options) > 2:
                    default_args = options[2].copy()
                if len(options) > 3:
                    extra_args = options[3].copy()
                break
        
        creator = self.root.ui_creator
        container = creator.playground.get_playground_drag_element(
            instance, widget_name, touch,
            default_args, extra_args,
        )
        if container:
            self.root.add_widget(container)
        else:
            show_message("Cannot create %s" % widget_name, 5, 'error')

        container.widgettree = self.root.ui_creator.widgettree
        return container

    def focus_widget(self, widget, *args):
        '''Called when a widget is select in Playground. It will also draw
           lines around focussed widget.
           :param widget: widget to receive focus
        '''

        if self._widget_focused and (widget is None or self._widget_focused[0] != widget):
            fwidget = self._widget_focused[0]
            for instr in self._widget_focused[1:]:
                fwidget.canvas.after.remove(instr)
            self._widget_focused = []

        self.widget_focused = widget
        if not widget:
            return None

        x, y = widget.pos
        right, top = widget.right, widget.top
        points = [x, y, right, y, right, top, x, top]
        if self._widget_focused:
            line = self._widget_focused[2]
            line.points = points
        else:
            with widget.canvas.after:
                color = Color(0.42, 0.62, 0.65)
                line = Line(points=points, close=True, width=2.0)
            self._widget_focused = [widget, color, line]

        self.root.ui_creator.playground.clicked = True
        self.root.on_show_edit()
