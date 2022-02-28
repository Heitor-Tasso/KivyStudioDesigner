import os
import os.path
import shutil

from uix.confirmation_dialog import ConfirmationDialog
from utils import constants
from utils.utils import get_config_dir, get_kd_data_dir
from kivy.config import ConfigParser
from kivy.properties import DictProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.lang.builder import Builder
from kivy.uix.settings import (
    ContentPanel, InterfaceWithSidebar,
    MenuSidebar, Settings,
)

Builder.load_string("""

<ProfileSettings>:
    interface_cls: 'ProfileSettingsInterface'

<-ProfileSettingsInterface>:
    orientation: 'horizontal'
    menu: menu
    content: content
    button_bar: button_bar
    ProfileMenuSidebar:
        id: menu
    GridLayout:
        id: button_bar
        btn_delete_prof: btn_delete_prof
        btn_select_prof: btn_select_prof
        cols: 1
        GridLayout:
            cols: 2
            size_hint_y: None
            height: 50
            spacing: 5
            padding: 5
            DesignerButton:
                id: btn_select_prof
                text: 'Use this Profile'
                size_hint_x: 0.5
            DesignerButton:
                id: btn_delete_prof
                disabled: True
                text: 'Delete this Profile'
                size_hint_x: 0.5
        ProfileContentPanel:
            id: content
            current_uid: menu.selected_uid

<-ProfileMenuSidebar>:
    size_hint_x: None
    width: '200dp'
    buttons_layout: menu
    close_button: button_close
    new_button: button_new
    ScrollView:
        id: e_scroll
        y: root.y + 70
        x: root.x
        width: root.width
        size_hint_y: None
        height: root.height - 75
        GridLayout:
            size_hint_y: None
            height: max(e_scroll.height, self.minimum_height)
            cols: 1
            id: menu
            # orientation: 'vertical'
            padding: 5
            spacing: 5
            canvas.after:
                Color:
                    rgb: .2, .2, .2
                Rectangle:
                    pos: self.right - 1, self.y
                    size: 1, self.height
    DesignerButton:
        text: 'New'
        id: button_new
        size_hint_x: None
        width: root.width - dp(20)
        pos: root.x + dp(10), root.y + sp(49)
        font_size: '15sp'
    DesignerButton:
        text: 'Close'
        id: button_close
        size_hint_x: None
        width: root.width - dp(20)
        pos: root.x + dp(10), root.y + 5
        font_size: '15sp'

<ProfileContentPanel>:
    current_uid: 0
""")

class ProfileContentPanel(ContentPanel):
    ''' ContentPanel with a custom design and custom events
    '''

    __events__ = ('on_current_panel', )

    def __int__(self, **kwargs):
        super(ProfileContentPanel, self).__init__(**kwargs)

    def on_current_uid(self, *args):
        ''' Override the on_current_uid to to bind panel_change event
        '''
        super(ProfileContentPanel, self).on_current_uid(args)
        self.dispatch('on_current_panel')

    def on_current_panel(self, *args):
        ''' Event handler for panel_change
        '''
        pass


class ProfileMenuSidebar(MenuSidebar):
    pass


class ProfileSettingsInterface(InterfaceWithSidebar):
    ''' InterfaceWithSidebar with a custom style and custom events
    '''

    button_bar = ObjectProperty(None)
    ''' Reference to the widget's GridLayout with buttons
    :class:`~kivy.properties.ObjectProperty` and defaults to None.
    '''

    new_button = ObjectProperty(None)
    ''' Reference to the widget's New button.
    :class:`~kivy.properties.ObjectProperty` and defaults to None.
    '''

    select_prof_button = ObjectProperty(None)
    ''' Reference to the widget's Use this Profile button.
    :class:`~kivy.properties.ObjectProperty` and defaults to None.
    '''

    __events__ = ('on_delete', 'on_new', 'on_use_this_profile')

    def __init__(self, **kwargs):
        super(ProfileSettingsInterface, self).__init__(**kwargs)
        self.button_bar.btn_delete_prof.bind(
            on_press=lambda j: self.dispatch('on_delete'))
        self.button_bar.btn_select_prof.bind(
            on_press=lambda j: self.dispatch('on_use_this_profile'))
        self.menu.new_button.bind(on_press=lambda j: self.dispatch('on_new'))
        self.content.bind(on_current_panel=self.on_current_panel)

    def on_delete(self, *args):
        '''Event handler for button "Delete" press
        '''
        pass

    def on_new(self, *args):
        '''Event handler for button "New" press
        '''
        pass

    def on_use_this_profile(self, *args):
        '''Event handler for button "Use this Profile" press
        '''
        pass

    def on_current_panel(self, *args):
        ''' Event handler to panel change
        The default profile cannot be deleted, so we watch this event to
        prevent the user to delete desktop.ini
        '''
        _file = self.content.current_panel.config.filename
        filename = os.path.basename(_file)
        self.button_bar.btn_delete_prof.disabled = filename == 'desktop.ini'


class ProfileSettings(Settings):
    '''Subclass of :class:`kivy.uix.settings.Settings` responsible for
       showing build profile settings of Kivy Designer.
    '''

    config_parsers = DictProperty({})
    '''List of config parsers
    :class:`~kivy.properties.DictProperty` and defaults to {}.
    '''

    selected_config = ObjectProperty(None)
    '''ConfigParser of the selected config
    :class `~kivy.properties.ObjectProperty` and defaults to None.
    '''

    __events__ = ('on_use_this_profile', 'on_changed')

    def __init__(self, **kwargs):
        super(ProfileSettings, self).__init__(**kwargs)
        # list of ConfigParsers. Each file has one to handle the settings
        self.PROFILES_PATH = ''
        self.DEFAULT_PROFILES = ''
        self.interface.bind(on_new=self.on_new)
        self.interface.bind(on_delete=self.on_delete)
        self.interface.bind(
            on_use_this_profile=lambda j: self.dispatch('on_use_this_profile'))
        self.interface.content.bind(on_current_panel=self.on_current_config)
        self.settings_changed = False  # changes in name, new or delete

    def load_profiles(self):
        '''This function loads project settings
        '''
        self.settings_changed = False
        self.PROFILES_PATH = os.path.join(get_config_dir(),
                                          constants.DIR_PROFILES)

        self.DEFAULT_PROFILES = os.path.join(get_kd_data_dir(),
                                             constants.DIR_PROFILES)

        if not os.path.exists(self.PROFILES_PATH):
            shutil.copytree(self.DEFAULT_PROFILES, self.PROFILES_PATH)

        self.update_panel()

    def update_panel(self):
        '''Update the MenuSidebar
        '''
        self.config_parsers = {}
        self.interface.menu.buttons_layout.clear_widgets()
        for _file in os.listdir(self.PROFILES_PATH):
            _file_path = os.path.join(self.PROFILES_PATH, _file)
            config_parser = ConfigParser()
            config_parser.read(_file_path)
            prof_name = config_parser.getdefault('profile', 'name', 'PROFILE')
            if not prof_name.strip():
                prof_name = 'PROFILE'
            self.config_parsers[
                str(prof_name) + '_' + _file_path] = config_parser

        for _file in sorted(self.config_parsers):
            prof_name = self.config_parsers[_file].getdefault('profile',
                                                              'name',
                                                              'PROFILE')
            if not prof_name.strip():
                prof_name = 'PROFILE'
            self.add_json_panel(prof_name,
                                self.config_parsers[_file],
                                os.path.join(
                                    get_kd_data_dir(),
                                    'settings',
                                    'build_profile.json')
                                )

        # force to show the first profile
        first_panel = self.interface.menu.buttons_layout.children[-1].uid
        self.interface.content.current_uid = first_panel

    def on_config_change(self, instance, section, key, value, *args):
        '''This function is default handler of on_config_change event.
        '''
        super(ProfileSettings, self).on_config_change(
            instance, section, key, value
        )
        if key == 'name':
            self.update_panel()
            self.settings_changed = True

    def on_new(self, *args):
        '''Handler for "New Profile" button
        '''
        new_name = 'new_profile'
        i = 1
        while os.path.exists(os.path.join(
                self.PROFILES_PATH, new_name + str(i) + '.ini')):
            i += 1
        new_name += str(i)
        new_prof_path = os.path.join(
            self.PROFILES_PATH, new_name + '.ini')

        shutil.copy2(os.path.join(self.DEFAULT_PROFILES, 'desktop.ini'),
                     new_prof_path)
        config_parser = ConfigParser()
        config_parser.read(new_prof_path)
        config_parser.set('profile', 'name', new_name.upper())
        config_parser.write()

        self.update_panel()
        self.settings_changed = True

    def on_delete(self, *args):
        '''Handler to "Delete profile" button
        '''
        confirm_dlg = ConfirmationDialog(
            message="Do you want to delete this profile?")
        self._popup = Popup(title='Delete Profile',
                            content=confirm_dlg,
                            size_hint=(None, None),
                            size=('200pt', '150pt'),
                            auto_dismiss=False)
        confirm_dlg.bind(on_ok=self._perform_delete_prof,
                         on_cancel=self._popup.dismiss)
        self._popup.open()

    def _perform_delete_prof(self, *args):
        '''Delete the selected profile
        '''
        self.selected_config = self.interface.content.current_panel.config
        os.remove(self.selected_config.filename)
        self.update_panel()
        self._popup.dismiss()
        self.settings_changed = True

    def on_use_this_profile(self, *args):
        '''Event handler for button "Use this Profile" press
        '''
        self.selected_config = self.interface.content.current_panel.config
        self.settings_changed = True

    def on_current_config(self, *args):
        ''' Event handler to panel change
        The default profile cannot be deleted, so we watch this event to
        prevent the user to delete desktop.ini
        '''
        self.selected_config = self.interface.content.current_panel.config

    def on_changed(self, *args):
        '''Event handler to Settings changes.
        Will be called when the user delete,
        create or change a name of a profile.
        '''
        pass

    def on_close(self, *args):
        '''Event handler when the settings is closed
        '''
        if self.settings_changed:
            self.dispatch('on_changed')
        self.settings_changed = False
