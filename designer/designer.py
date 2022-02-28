__all__ = ['DesignerApp', ]

from utils.utils import (
    get_config_dir, show_alert,
    ignore_proj_watcher, update_info,
    show_error_console, show_message,
)

from uix.confirmation_dialog import ConfirmationDialog, ConfirmationDialogSave
from components.buildozer_spec_editor import BuildozerSpecEditor
from core.project_manager import ProjectManager, ProjectWatcher
from components.run_contextual_view import ModulesContView
from components.edit_contextual_view import EditContView
from components.designer_content import DesignerContent
from core.profile_settings import ProfileSettings
from core.project_settings import ProjectSettings
from utils.toolbox_widgets import toolbox_widgets
from core.recent_manager import RecentManager
from core.settings import DesignerSettings
from tools.bug_reporter import BugReporterApp
from core.undo_manager import UndoManager
from tools.tools import DesignerTools
from core.shortcuts import Shortcuts
from core.builder import Profiler

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.carousel import Carousel
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.base import ExceptionHandler, ExceptionManager
from kivy.properties import (
    BooleanProperty, ListProperty,
    ObjectProperty, StringProperty,
)

import os, shutil, traceback
from functools import partial


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

    selected_profile = StringProperty('')
    '''Selected profile settings path
    :class:`~kivy.properties.StringProperty` and defaults to ''.
    '''
    code_inputs = ListProperty([])
    '''List with all opened code inputs and kv lang area.
    This list can be used to fetch unsaved code inputs or to check code content
    '''

    def __init__(self, program_designer, **kwargs):
        super(Designer, self).__init__(**kwargs)
        Clock.schedule_once(self.config)
        Clock.schedule_once(program_designer._setup)

    def config(self, *args):
        self.project_watcher = ProjectWatcher()
        self.project_watcher.bind(on_project_modified=self.project_modified)
        self.project_manager = ProjectManager()
        self.recent_manager = RecentManager()
        self.spec_editor = BuildozerSpecEditor()
        self.widget_to_paste = None

        self.designer_settings = DesignerSettings()
        self.designer_settings.bind(on_config_change=self._config_change)
        self.designer_settings.load_settings()
        self.designer_settings.bind(on_close=self.ids.toll_bar_top.close_popup)

        self.shortcuts = Shortcuts()
        self.shortcuts.map_shortcuts(self.designer_settings.config_parser)
        self.designer_settings.config_parser.add_callback(
                self.on_designer_settings)
        self.display_shortcuts()

        self.prof_settings = ProfileSettings()
        self.prof_settings.bind(on_close=self.ids.toll_bar_top.close_popup)
        self.prof_settings.load_profiles()

        self.designer_content = DesignerContent(size_hint=(1, None))
        self.designer_content = self.designer_content.__self__

        self.designer_git.bind(on_branch=lambda i, name, *a: update_info('Git', name))
        self.statusbar.bind(on_info_press=self.on_info_press)

        getdefault = self.designer_settings.config_parser.getdefault
        Clock.schedule_interval(self.save_project,
            (int(getdefault('global', 'auto_save_time', 5)) * 60),
        )

        self.profiler = Profiler()
        self.profiler.designer = self
        self.profiler.bind(
            on_error=lambda i, msg: show_alert('Profile error', msg),
            on_message=lambda i, msg, dt=0: show_message(msg, dt, 'info'),
            on_run=lambda *a: setattr(self.ids.actn_btn_stop_proj, 'disabled', False),
            on_stop=lambda *a: setattr(self.ids.actn_btn_stop_proj, 'disabled', True),
        )

        self.designer_tools = DesignerTools(designer=self)
        # variables used in the project
        self.help_dlg = None

        self.temp_proj_directories = []

    def load_view_settings(self, *args):
        '''Load "View" menu saved settings
        '''
        options = (
            'proj_tree', 'prop_event',  'widget_tree',
            'status_bar', 'kv_lang_area',
        )
        getdefault = self.designer_settings.config_parser.getdefault

        for option in options:
            name = f'actn_chk_{option}'

            if getdefault('view', name, True) == 'False':
                self.ids.get(name).checkbox.active = False

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
                # if shortcut key is the searched
                if m[short][1] != name:
                    continue

                mod, key = short.split('+')
                key = key.strip()
                short = f'+{key}' + '+'.join(eval(mod))
                if not short:
                    short = key
                return short.title()
            return ''
        
        contents = (
            ('check_pep8', 'check_pep8'), ('create_setup_py', 'create_setup_py'),
            ('buildozer_init', 'buildozer_init'), ('export_png', 'export_png'),
            ('wiki', 'kivy_docs'), ('doc', 'kd_docs'), ('page', 'kd_repo'),
            ('quit', 'exit'), ('run_proj', 'run'), ('about', 'about'),
            ('create_gitignore', 'create_gitignore'), ('help', 'help'),
            ('new_file', 'new_file'), ('new_project', 'new_project'),
            ('save_as', 'save_as'), ('close_proj', 'close_project'),
            ('build_proj', 'build'), ('rebuild_proj', 'rebuild'),
            ('open_project', 'open_project'), ('save', 'save'),
            ('recent', 'recent'), ('settings', 'settings'),
            ('stop_proj', 'stop'), ('clean_proj', 'clean'),
        )
        for content in contents:
            actn_id, name = content
            btn = self.ids.toll_bar_top.ids.get(f'actn_btn_{actn_id}')
            if btn is None:
                print(f'Dont work -> {content} !! def display_shortcuts !!')
            else:
                btn.hint = get_hint(name)

    def on_info_press(self, *args):
        '''Callback to git statusbar info press
        '''
        # open switch branch if git repo
        if self.designer_git.is_repo:
            self.designer_git.do_branches()

    def _config_change(self, *args):
        '''Event Handler for 'on_config_change'
           event of self.designer_settings.
        '''
        #return None
        Clock.unschedule(self.save_project)
        getdefault = self.designer_settings.config_parser.getdefault
        
        Clock.schedule_interval(self.save_project,
            (int(getdefault('global', 'auto_save_time', 5)) * 60),
        )

        max_lines = int(getdefault('global', 'num_max_kivy_console', 200))
        self.ui_creator.kivy_console.cached_history = max_lines

        recent_files = int(getdefault('global', 'num_recent_files', 10))
        self.recent_manager.max_recent_files = recent_files

    def _add_designer_content(self):
        '''Add designer_content to Designer, when a project is loaded
        '''
        for _child in self.children[:]:
            if _child == self.designer_content:
                return None

        self.remove_widget(self.start_page)
        self.start_page.parent = None
        self.add_widget(self.designer_content, 1)
        self.disable_actn('disable', False)
        self.proj_settings = ProjectSettings(
            project=self.project_manager.current_project)
        self.proj_settings.load_proj_settings()

        Clock.schedule_once(self.load_view_settings)

    def disable_actn(self, varible, value):
        error = lambda x: print(f'Dont work -> {x} !! def _add_designer_content !!')
        btns = ('new_file', 'save', 'save_as', 'close_proj')
        menus = ('view', 'proj', 'run', 'tools')

        for btn, menu in zip(btns, menus):
            actn_btn = self.ids.get(f'actn_btn_{btn}')
            setattr(actn_btn, varible, value) if actn_btn is not None else error(btn)

            actn_menu = self.ids.get(f'actn_menu_{menu}')
            setattr(actn_menu, varible, value) if actn_menu is not None else error(menu)

    def on_statusbar_height(self, *args):
        '''Callback for statusbar.height
        '''
        self.designer_content.y = self.statusbar.height
        self.on_height(*args)

    def on_height(self, *args):
        '''Callback for self.height
        '''
        if self.actionbar is None or self.statusbar is None:
            return None
        if self.designer_content is None:
            return None

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
        if self.ids.toll_bar_top.popup:
            return None

        def close(*args):
            self._proj_modified_outside = False
            self.ids.toll_bar_top.close_popup()

        confirm_dlg = ConfirmationDialog(
            message="Current Project has been modified\n"
                    "outside the Kivy Designer.\n"
                    "Do you want to reload project?")
        confirm_dlg.bind(on_ok=self._perform_reload, on_cancel=close)
        
        self.ids.toll_bar_top.popup = Popup(
            title='Kivy Designer', content=confirm_dlg,
            size_hint=(None, None), size=('200pt', '150pt'),
            auto_dismiss=False)
        self.ids.toll_bar_top.popup.open()

        self._proj_modified_outside = True

    @ignore_proj_watcher
    def _perform_reload(self, *args):
        '''Perform reload of project after it is modified
        '''
        # Perform reload of project after it is modified
        self.ids.toll_bar_top.close_popup()
        self.ids.toll_bar_top._perform_open(self.project_manager.current_project.path)
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
                lambda *a: self.action_btn_pressed('select_all'))
            self.editcontview = EditContView(
                on_undo=lambda *a: self.action_btn_pressed('do_undo'),
                on_redo=lambda *a: self.action_btn_pressed('do_redo'),
                on_cut=lambda *a: self.action_btn_pressed('cut'),
                on_copy=lambda *a: self.action_btn_pressed('copy'),
                on_paste=lambda *a: self.action_btn_pressed('paste'),
                on_delete=lambda *a: self.action_btn_pressed('delete'),
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
        
        for tab_item in self.designer_content.tab_pannel.tab_list:
            code_input = tab_item.content.code_input
            if hasattr(tab_item.content, 'code_input'):
                if not code_input.clicked:
                    continue
                Clock.schedule_once(code_input.do_focus)
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
        if not isinstance(self.actionbar.children[0], EditContView):
            return super(FloatLayout, self).on_touch_down(touch)    
        if self.actionbar.collide_point(*touch.pos):
            return super(FloatLayout, self).on_touch_down(touch) 
        
        if self.actionbar._stack_cont_action_view:
            self.actionbar.on_previous(self)
        self.ui_creator.playground.clicked = False
        return super(FloatLayout, self).on_touch_down(touch)

    
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

    def _fbrowser_load(self, instance):
        '''Event Handler for 'on_load' event of self._fbrowser
        '''
        if not instance.selection or self.ids.toll_bar_top.popup:
            return None

        file_path = instance.selection[0]
        file_name, file_extension = os.path.splitext(instance.selection[0])
        error = ''
        try:
            buildozer_file = (file_name.endswith('buildozer') and file_extension == '.spec')
            if file_extension in ('.py', '.kv') or buildozer_file:
                self.ids.toll_bar_top._perform_open(file_path)
                return None
            error = f'Cannot load file type: .{file_extension}, Please load a .py file'
        except Exception:
            error = 'Cannot load empty file type'
        show_message(error, 5, 'error')

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

    def _recent_file_release(self, instance, *args):
        '''Event Handler for 'on_select' event of RecentDialog.
        '''
        self.ids.toll_bar_top._perform_open(instance.get_selected_project())
        self.ids.toll_bar_top.close_popup()

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
        if self.ids.toll_bar_top.popup:
            # if there is something open, stops the propagation
            msg = 'You must close all popups before closing Kivy Designer'
            show_message(msg, 5, 'error')
            return True

        proj = self.project_manager.current_project
        if proj.new_project or not proj.saved:
            msg = 'Your project is not saved.\nWhat would you like to do?'
            _confirm_dlg_save = ConfirmationDialogSave(msg)

            def save(*args):
                self.ids.toll_bar_top.close_popup()
                self.ids.toll_bar_top.action_btn_save_pressed(exit_on_save=True)

            _confirm_dlg_save.bind(
                on_dont_save=self._perform_quit,
                on_save=save, on_cancel=self.ids.toll_bar_top.close_popup)
            
            self.ids.toll_bar_top.popup = Popup(
                title='Quit', content=_confirm_dlg_save,
                size_hint=(None, None), size=('300pt', '150pt'),
                auto_dismiss=False)
            self.ids.toll_bar_top.popup.open()
            return True

        self._perform_quit()
        return False

    def _perform_quit(self, *args):
        '''Perform Application qui.Application
        '''
        self.remove_temp_proj_directories()
        App.get_running_app().stop()

    def action_btn_pressed(self, action, *args):
        """Event Handler when ActionButton "Redo" is pressed.

        Args:
            action (str): 
                one of then -> {
                    'do_redo', 'do_undo', 'cut',
                    'copy', 'paste', 'delete',
                    'select_all',
        """
        do_set = {'cut', 'copy',' paste', 'delete', 'select_all'}
        schedule_set = {'select_all'}

        if self._edit_selected == 'Play':
            if action in do_set:
                getattr(self.ui_creator.playground, f'do_{action}')()
            else:
                getattr(self.undo_manager, action)()

        elif self._edit_selected == 'KV':
            do_set.remove('select_all')
            if action in do_set:
                getattr(self.ui_creator.playground, f'do_{action}')()
                action = 'delete_selection' if action == 'delete' else action
            elif action in schedule_set:
                Clock.schedule_once(getattr(self.ui_creator.kv_code_input, action))
            else:
                getattr(self.ui_creator.kv_code_input, action)()

        elif self._edit_selected == 'Py':
            tab_list = self.designer_content.tab_pannel.tab_list
            for tab_item in tab_list:
                code = tab_item.content.code_input
                if hasattr(tab_item.content, 'code_input') and code.clicked:
                    if action in schedule_set:
                        Clock.schedule_once(getattr(code, action))
                    else:
                        getattr(code, action)()
                    break

    def do_config_actn(self, name, chk_btn):
        config_parser = self.designer_settings.config_parser
        config_parser.set('view', f'actn_chk_{name}', chk_btn.checkbox.active)
        config_parser.write()

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

    def _error_adding_file(self, *args):
        '''Event Handler for 'on_error' event of self._add_file_dlg
        '''
        show_message('Error while adding file to project', 5, 'error')
        self.ids.toll_bar_top.close_popup()

    def _added_file(self, *args):
        '''Event Handler for 'on_added' event of self._add_file_dlg
        '''
        show_message('File successfully added to project', 5, 'info')
        self.ids.toll_bar_top.close_popup()
        project = self.project_manager.current_project
        self.designer_content.update_tree_view(project)

    def action_btn_run_module_pressed(self, *args):
        if self.modulescontview is None:
            self.modulescontview = ModulesContView()
            self.modulescontview.bind(
                on_module=lambda *a, **w: self.ids.toll_bar_top.action_btn_clean_pressed('run', *a, **w))

        self.actionbar.add_widget(self.modulescontview)

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

    def on_sandbox_getting_exception(self, *args):
        '''Event Handler for
           :class:`~designer.uix.sandbox.DesignerSandbox`
           on_getting_exception event. This function will add exception
           string in error_console.
        '''
        show_error_console(traceback.format_exc(), append=False)
        if self.ui_creator.playground.sandbox.error_active:
            tab = self.ui_creator.tab_pannel.tab_list[0]
            self.ui_creator.tab_pannel.switch_to(tab)

        self.ui_creator.playground.sandbox.error_active = False

class DesignerException(ExceptionHandler):

    raised_exception = False
    '''Indicates if the BugReporter has already raised some exception
    '''

    def handle_exception(self, inst):
        if self.raised_exception:
            return ExceptionManager.PASS

        # App.get_running_app().stop()
        if isinstance(inst, KeyboardInterrupt):
            return ExceptionManager.PASS

        for child in Window.children:
            Window.remove_widget(child)

        self.raised_exception = True
        Window.fullscreen = False
        print(traceback.format_exc())
        BugReporterApp(traceback=traceback.format_exc()).run()
        return ExceptionManager.PASS
