from components.dialogs.new_project import NEW_PROJECTS, NewProjectDialog
from components.dialogs.recent import RecentDialog
from components.dialogs.add_file import AddFileDialog
from components.dialogs.about import AboutDialog
from uix.xpopup.file import XFileSave, XFileOpen
from uix.confirmation_dialog import ConfirmationDialogSave
from utils.toolbox_widgets import toolbox_widgets
from core.project_settings import ProjectSettings
from kivy.clock import Clock
from functools import partial
from uix.contextual import DesignerActionView
from components.dialogs.help import HelpDialog
from uix.input_dialog import InputDialog
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.lang.builder import Builder
from utils.utils import constants
from utils.utils import (
    ignore_proj_watcher, get_kd_data_dir,
    show_message, get_kd_dir, get_path,
    utils_source_rst,
)
from tempfile import mkdtemp
from distutils.dir_util import copy_tree
from kivy.clock import Clock
from kivy.metrics import dp
import os, shutil, io

Builder.load_file(get_path('screens/inicial/tool_bar_first_screen.kv'))

class ToolBarTopDesigner(DesignerActionView):
    
    designer = ObjectProperty(None)
    popup = None
    _new_dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.config)

    def config(self, *args):
        self.designer = App.get_running_app().root

    def action_btn_about_pressed(self, *args):
        '''Event handler for 'on_release' event of DesignerActionButton
           "About Kivy Designer"
        '''
        if self.popup:
            return False

        about_dlg = AboutDialog()
        self.popup = Popup(
            title='About Kivy Designer', content=about_dlg,
            size_hint=(None, None), size=(dp(600), dp(400)),
            auto_dismiss=False)
        
        self.popup.open()
        about_dlg.bind(on_close=self.close_popup)
        return True

    def show_help(self, *args):
        '''Event handler for 'on_help' event of self.start_page
        '''
        if self.popup:
            return False
        if self.designer.help_dlg is None:
            self.designer.help_dlg = HelpDialog()
            self.designer.help_dlg.rst.source = utils_source_rst('help')

        self.popup = Popup(
            title='Kivy Designer Help', content=self.designer.help_dlg,
            size_hint=(0.95, 0.95), auto_dismiss=False,
        )
        self.popup.open()
        self.designer.help_dlg.bind(on_cancel=self.close_popup)

    def action_btn_edit_prof_project_pressed(self, *args):
        '''Event Handler when ActionButton "Edit Profiles" is pressed.
        '''
        if self.popup:
            return False

        self.designer.prof_settings.load_profiles()
        self.popup = Popup(
            title="Build Profiles", content=self.designer.prof_settings,
            size_hint=(None, None), size=(dp(720), dp(480)),
            auto_dismiss=False)
        self.popup.open()
        return True

    def action_btn_clean_pressed(self, action, *args, **kwargs):
        """Event handler when ActionButton function is pressed.

        Args:
            action (str): 
                one of then -> {
                    'stop', 'clean', 'build',
                    'rebuild'
        """
        if not self.designer.check_selected_prof():
            return None

        func = getattr(self.designer.profiler, action)
        if args or kwargs:
            func(*args, **kwargs)
        else:
            func()

    def action_btn_project_settings_pressed(self, *args):
        '''Event Handler when ActionButton "Project Settings" is pressed.
        '''
        if self.popup:
            return False
        
        project = self.designer.project_manager.current_project
        self.designer.proj_settings = ProjectSettings(project=project)
        self.designer.proj_settings.load_proj_settings()
        self.designer.proj_settings.bind(on_close=self.close_popup)
        
        self.popup = Popup(
            title="Project Settings", content=self.designer.proj_settings,
            size_hint=(None, None), size=(dp(720), dp(480)),
            auto_dismiss=False)
        self.popup.open()
        return True

    def action_btn_add_file_pressed(self, *args):
        '''Event Handler when ActionButton "Add File" is pressed.
        '''
        if self.popup:
            return False
        
        project = self.designer.project_manager.current_project
        add_file_dlg = AddFileDialog(project)
        add_file_dlg.bind(
            on_added=self.designer._added_file,
            on_error=self.designer._error_adding_file,
            on_cancel=self.close_popup)

        self.popup = Popup(
            title="Add File", content=add_file_dlg,
            size_hint=(None, None), size=(dp(480), dp(350)),
            auto_dismiss=False)
        self.popup.open()
        return True

    def action_chk_btn_kv_area_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "KVLangArea" is activated.
        '''
        self.designer.do_config_actn('chk_kv_lang_area', chk_btn)

        splitter_code = self.designer.ui_creator.splitter_kv_code_input
        if chk_btn.checkbox.active:
            splitter_code.height = self.designer._kv_area_height
            self.designer._kv_area_parent.add_widget(splitter_code)
            return None
        
        self.designer._kv_area_parent = splitter_code.parent
        self.designer._kv_area_height = splitter_code.height
        splitter_code.height = 0
        self.designer._kv_area_parent.remove_widget(splitter_code)

    def action_chk_btn_status_bar_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "StatusBar" is activated.
        '''
        self.designer.do_config_actn('status_bar', chk_btn)

        if chk_btn.checkbox.active:
            self.designer._statusbar_parent.add_widget(self.designer.statusbar)
            self.designer.statusbar.height = self.designer._statusbar_height
            return None

        self.designer._statusbar_parent = self.designer.statusbar.parent
        self.designer._statusbar_height = self.designer.statusbar.height
        self.designer._statusbar_parent.remove_widget(self.designer.statusbar)
        self.designer.statusbar.height = 0

    def action_chk_btn_widget_tree_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "Widget Tree" is activated.
        '''
        self.designer.do_config_actn('widget_tree', chk_btn)

        splitter_prop = self.designer.ui_creator.splitter_property
        grid = self.designer.ui_creator.grid_widget_tree
        if not chk_btn.checkbox.active:
            self.designer._grid_widget_tree_parent = grid.parent
            self.designer._grid_widget_tree_parent.remove_widget(grid)
            splitter_prop.size_hint_y = 1
            self.designer._toggle_splitter_widget_tree()
            return None

        self.designer._toggle_splitter_widget_tree()
        add_prop = False
        if splitter_prop.parent is not None:
            add_prop = True

        self.designer._grid_widget_tree_parent.clear_widgets()
        self.designer._grid_widget_tree_parent.add_widget(grid)
        if add_prop:
            self.designer._grid_widget_tree_parent.add_widget(splitter_prop)
            splitter_prop.size_hint_y = None
            splitter_prop.height = 300

    def action_chk_btn_property_viewer_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "Property Viewer" is activated.
        '''
        self.designer.do_config_actn('prop_event', chk_btn)

        splitter = self.designer.ui_creator.splitter_widget_tree
        splitter_prop = self.designer.ui_creator.splitter_property
        if not chk_btn.checkbox.active:
            self.designer._splitter_property_parent = splitter_prop.parent
            self.designer._splitter_property_parent.remove_widget(splitter_prop)
            self.designer._toggle_splitter_widget_tree()
            return None

        self.designer._toggle_splitter_widget_tree()
        if splitter.parent is None:
            self.designer._splitter_widget_tree_parent.add_widget(splitter)
            splitter.width = self._splitter_widget_tree_width

        add_tree = False
        grid = self.designer.ui_creator.grid_widget_tree
        if grid.parent is not None:
            add_tree = True
            splitter_prop.size_hint_y = None
            splitter_prop.height = 300

        self.designer._splitter_property_parent.clear_widgets()
        if add_tree:
            self.designer._splitter_property_parent.add_widget(grid)

        self.designer._splitter_property_parent.add_widget(splitter_prop)

    def action_chk_btn_toolbox_active(self, chk_btn):
        '''Event Handler when ActionCheckButton "Toolbox" is activated.
        '''
        self.designer.do_config_actn('proj_tree', chk_btn)

        splitter_tree = self.designer.designer_content.splitter_tree
        if chk_btn.checkbox.active:
            self.designer._toolbox_parent.add_widget(splitter_tree)
            splitter_tree.width = self.designer._toolbox_width
            return None
        
        self.designer._toolbox_parent = splitter_tree.parent
        self.designer._toolbox_parent.remove_widget(splitter_tree)
        self.designer._toolbox_width = splitter_tree.width
        splitter_tree.width = 0


    

    def _perform_close_project(self, *args):
        '''
        Close the current project and go to the start page
        '''
        self.close_popup()
        self.designer.remove_widget(self.designer_content)
        self.designer.designer_content.parent = None
        self.designer.add_widget(self.start_page, 1)

        self.disable_actn('disable', True)
        self.project_manager.close_current_project()
        self.project_watcher.stop_watching()

    def _perform_save_as(self, instance, exit_on_save=False):
        '''Event handler for 'on_success' event of self._save_as_browser
        '''
        proj_dir = f'{instance.path}{os.path.sep}{instance.filename}'
        # save the project in the folder and then copy it to a new folder
        self.designer.save_project()
        path = self.designer.project_manager.current_project.path
        if os.path.isdir(path):
            copy_tree(path, proj_dir)

        if exit_on_save:
            self.designer._perform_quit()
            return None
        self._perform_open(proj_dir)

    def action_btn_settings_pressed(self, *args):
        '''Event handler for 'on_release' event of
           DesignerActionButton "Settings"
        '''
        if self.popup:
            return False

        self.designer.designer_settings.parent = None
        self.popup = Popup(
            title="Kivy Designer Settings",
            content=self.designer.designer_settings,
            size_hint=(None, None),
            size=(dp(720), dp(480)), auto_dismiss=False)
        self.popup.open()
        return True

    def action_btn_recent_files_pressed(self, *args):
        '''Event Handler when ActionButton "Recent Projects" is pressed.
        '''
        if self.popup:
            return False

        _recent_dlg = RecentDialog(self.recent_manager.list_projects)
        _recent_dlg.bind(
            on_cancel=self.close_popup,
            on_select=self.designer._recent_file_release)

        self.popup = Popup(
            title='Recent Projects', content=_recent_dlg,
            size_hint=(0.5, 0.5), auto_dismiss=False)
        self.popup.open()
        return True

    def action_btn_close_proj_pressed(self, *args):
        '''
        Event Handler when ActionButton "Close Project" is pressed.
        '''
        if self.popup:
            return False

        if self.designer.project_manager.current_project.saved:
            self._perform_close_project()
            return True

        _confirm_dlg_save = ConfirmationDialogSave(
            'Your project is not saved.\nWhat would you like to do?'
        )
        def save_and_close(*args):
            self.close_popup()
            self.action_btn_save_pressed()
            self._perform_close_project()

        _confirm_dlg_save.bind(
            on_cancel=self.close_popup,
            on_dont_save=self._perform_close_project,
            on_save=save_and_close)
        
        self.popup = Popup(
            title='Kivy Designer', auto_dismiss=False,
            size_hint=(None, None), size=('300pt', '150pt'),
            content=_confirm_dlg_save)
        self.popup.open()
        return True

    def action_btn_save_as_pressed(self, exit_on_save=False, *args):
        '''Event Handler when ActionButton "Save As" is pressed.
        '''
        if self.popup:
            return False
        
        proj = self.designer.project_manager.current_project
        def_path = os.path.expanduser('~')
        if not proj.new_project and proj.path:
            def_path = proj.path

        def save_project(instance):
            if instance.is_canceled():
                return None

            self._perform_save_as(instance, exit_on_save=exit_on_save)

        XFileSave(
            title="Enter Folder Name", size_hint=(0.9, 0.9),
            on_dismiss=save_project, path=def_path)

    def action_btn_save_pressed(self, exit_on_save=False, *args):
        '''Event Handler when ActionButton "Save" is pressed.
        :param exit_on_save: if True, closes the KD after saving the project
        '''
        proj = self.designer.project_manager.current_project
        if proj.new_project:
            self.action_btn_save_as_pressed(exit_on_save=exit_on_save)
            return None

        self.designer.save_project()
        if exit_on_save:
            self.designer._perform_quit()

    def _show_open_dialog(self, *args):
        '''To show FileBrowser to "Open" a project
        '''
        if self.popup:
            return False

        def_path = os.path.expanduser('~')
        current_project = self.designer.project_manager.current_project
        if current_project.path and not current_project.new_project:
            def_path = self.designer.project_manager.current_project.path

        def open_file_browser(instance):
            if instance.is_canceled():
                return None
            self.designer._fbrowser_load(instance)

        XFileOpen(title="Open", on_dismiss=open_file_browser, path=def_path)


    def action_btn_open_pressed(self, *args):
        '''Event Handler when ActionButton "Open" is pressed.
        '''
        if self.popup:
            return False

        if self.designer.project_manager.current_project.saved:
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

        _confirm_dlg_save.bind(
            on_dont_save=show_open,
            on_save=save_and_open,
            on_cancel=self.close_popup)
        
        self.popup = Popup(
            title='Kivy Designer', auto_dismiss=False,
            size_hint=(None, None), size=('300pt', '150pt'),
            content=_confirm_dlg_save)
        self.popup.open()
        return True

    def action_btn_new_file_pressed(self, *args):
        '''Event Handler when ActionButton "New Project" is pressed.
        '''
        if self.popup:
            return False

        input_dialog = InputDialog("File name:")
        input_dialog.bind(
            on_confirm=self.designer._perform_new_file,
            on_cancel=self.close_popup)

        self.popup = Popup(
            title="Add new File", content=input_dialog,
            size_hint=(None, None), size=('200pt', '150pt'),
            auto_dismiss=False)
        self.popup.open()
        return True

    def action_btn_new_project_pressed(self, *args):
        '''Event Handler when ActionButton "New" is pressed.
        '''
        if self.popup:
            return False

        if self.designer.project_manager.current_project.saved:
            self._show_new_dialog()
            return True

        _confirm_dlg_save = ConfirmationDialogSave(
            'Your project is not saved.\nWhat would you like to do?'
        )
        def save_and_open(*args):
            self.action_btn_save_pressed()
            self._show_new_dialog()
        _confirm_dlg_save.bind(
            on_save=save_and_open,
            on_cancel=self.close_popup,
            on_dont_save=self._show_new_dialog)

        self.popup = Popup(
            title='New', content=_confirm_dlg_save,
            size_hint=(None, None), size=('300pt', '150pt'),
            auto_dismiss=False)
        self.popup.open()
        return True
    
    def _show_new_dialog(self, *args):
        if self.popup:
            return False

        if self._new_dialog is None:
            self._new_dialog = NewProjectDialog()
            self._new_dialog.bind(
                on_select=self._perform_new,
                on_cancel=self.close_popup)

        self.popup = Popup(
            title='New Project', content=self._new_dialog,
            size_hint=(None, None), size=('650pt', '450pt'),
            auto_dismiss=False)
        self.popup.open()

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
    def _perform_new_file(self, instance):
        '''
        Create a new file in the project folder
        '''
        current_project = self.designer.project_manager.current_project
        
        file_name = instance.user_input.text
        if file_name.find('.') == -1:
            file_name += '.py'

        new_file = os.path.join(current_project.path, file_name)
        if os.path.exists(new_file):
            instance.lbl_error.text = 'File exists'
            return None

        open(new_file, 'a').close()
        self.designer.designer_content.update_tree_view(current_project)
        self.close_popup()
    
    @ignore_proj_watcher
    def _perform_new(self, *args):
        '''To load new project
        '''
        self.close_popup()
        new_proj_dir = mkdtemp(prefix=constants.NEW_PROJECT_DIR_NAME_PREFIX)
        self.designer.temp_proj_directories.append(new_proj_dir)

        template = self._new_dialog.template_list.text
        app_name = self._new_dialog.app_name.text
        package_domain, package_name = self._new_dialog.package_name.text.rsplit('.', 1)
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
        self.designer.project_manager.current_project.new_project = True
        self.designer.project_manager.current_project.saved = False
        show_message('Project created successfully', 5, 'info')
    
    def _perform_open(self, file_path, new_project=False):
        '''To open a project given by file_path
        '''
        self.designer.project_watcher.stop_watching()
        show_message('Project loaded successfully', 5, 'info')
        self.designer.cleanup()
        if os.path.isfile(file_path):
            file_path = os.path.dirname(file_path)

        project = self.designer.project_manager.open_project(file_path)
        if project is None:
            return None
            
        self.designer.project_watcher.start_watching(file_path)
        self.designer.designer_content.update_tree_view(project)
        if not new_project:
            self.designer.recent_manager.add_path(project.path)

        for widget in toolbox_widgets[:]:
            if widget[1] == 'custom':
                toolbox_widgets.remove(widget)

        self.designer._add_designer_content()
        app_widgets = self.designer.project_manager.current_project.app_widgets
        if app_widgets:
            for name in app_widgets.keys():
                toolbox_widgets.append((name, 'custom'))

            self.designer.designer_content.toolbox.update_app_widgets()
            if len(app_widgets):
                first_wdg = app_widgets[list(app_widgets.keys())[-1]]
                self.designer.ui_creator.playground.load_widget(first_wdg.name)
            else:
                self.designer.ui_creator.playground.no_widget()

        run_command = self.designer.ui_creator.kivy_console.run_command
        Clock.schedule_once(partial(run_command, f'cd {file_path}'), 1)
        self.designer.designer_git.load_repo(file_path)

