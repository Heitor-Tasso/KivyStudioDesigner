__all__ = ['ModulesContView', 'ModScreenContView']

from uix.action_items import DesignerActionProfileCheck

from kivy.app import App
from kivy.clock import Clock
from kivy.modules import screen
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty
from kivy.uix.actionbar import ContextualActionView

import webbrowser

Builder.load_string("""

<ModulesContView>:
    ActionPrevious:
        title: "Modules"
        width: '100dp'
        with_previous: True

    ActionOverflow:

    ActionButton:
        text: 'Screen Emulation'
        on_release: root.on_screen()
    ActionButton:
        text: 'Touch Ring'
        on_release:
            root.dispatch('on_module', mod='touchring', data=[])
    ActionButton:
        text: 'Monitor'
        on_release:
            root.dispatch('on_module', mod='monitor', data=[])
    ActionButton:
        text: 'Inspector'
        on_release:
            root.dispatch('on_module', mod='inspector', data=[])
    ActionButton:
        text: 'Web Debugger'
        on_release: root.on_webdebugger(self)
    
<ModScreenContView>:
    ActionPrevious:
        title: "Screen"
        width: '100dp'
        with_previous: True

    ActionOverflow:

    ActionButton:
        text: 'Run'
        on_release: root.on_run_press()
    DesignerActionGroup:
        id: module_screen_device
        text: 'Device'
    DesignerActionGroup:
        id: module_screen_orientation
        text: 'Orientation'
        DesignerActionProfileCheck:
            text: 'Portrait'
            group: 'mod_screen_orientation'
            allow_no_selection: False
            checkbox_active: False
            config_key: 'portrait'
            on_active: root.on_module_settings(self)
        DesignerActionProfileCheck:
            text: 'Landscape'
            group: 'mod_screen_orientation'
            allow_no_selection: False
            checkbox_active: False
            config_key: 'landscape'
            on_active: root.on_module_settings(self)
    DesignerActionGroup:
        id: module_screen_scale
        text: 'Scale'
        DesignerActionProfileCheck:
            id: module_screen_25
            text: '25%'
            group: 'mod_screen_scale'
            allow_no_selection: False
            checkbox_active: False
            config_key: '0.25'
            on_active: root.on_module_settings(self)
        DesignerActionProfileCheck:
            id: module_screen_50
            text: '50%'
            group: 'mod_screen_scale'
            allow_no_selection: False
            checkbox_active: False
            config_key: '0.50'
            on_active: root.on_module_settings(self)
        DesignerActionProfileCheck:
            id: module_screen_100
            text: '100%'
            group: 'mod_screen_scale'
            allow_no_selection: False
            checkbox_active: False
            config_key: '1.0'
            on_active: root.on_module_settings(self)
        DesignerActionProfileCheck:
            id: module_screen_150
            text: '150%'
            group: 'mod_screen_scale'
            allow_no_selection: False
            checkbox_active: False
            config_key: '1.5'
            on_active: root.on_module_settings(self)
        DesignerActionProfileCheck:
            id: module_screen_200
            text: '200%'
            group: 'mod_screen_scale'
            allow_no_selection: False
            checkbox_active: False
            config_key: '2.0'
            on_active: root.on_module_settings(self)

""")

class ModulesContView(ContextualActionView):

    mod_screen = ObjectProperty(None)

    __events__ = ('on_module', )

    def on_module(self, *args, **kwargs):
        '''Dispatch the selected module
        '''
        self.parent.on_previous(self)

    def on_screen(self, *args):
        '''Screen module selected, shows ModScreenContView menu
        '''
        if self.mod_screen is None:
            self.mod_screen = ModScreenContView()
            self.mod_screen.bind(on_run=self.on_screen_module)
        
        self.parent.add_widget(self.mod_screen)

    def on_screen_module(self, *args, **kwargs):
        '''when running from screen module
        '''
        self.mod_screen.parent.on_previous(self.mod_screen)
        self.dispatch('on_module', *args, **kwargs)

    def on_webdebugger(self, *args):
        '''when running from webdebugger'''
        self.dispatch('on_module', mod='webdebugger', data=[])
        Clock.schedule_once(lambda *a: webbrowser.open('http://localhost:5000/'), 5)

class ModScreenContView(ContextualActionView):

    __events__ = ('on_run', )

    designer = ObjectProperty(None)
    '''Instance of Desiger
    '''

    def __init__(self, **kwargs):
        super(ModScreenContView, self).__init__(**kwargs)
        # populate emulation devices
        devices = self.ids.module_screen_device

        self.designer = App.get_running_app().root
        config = self.designer.designer_settings.config_parser

        # load the default values
        saved_device = config.getdefault('internal', 'mod_screen_device', '')
        saved_orientation = config.getdefault('internal', 'mod_screen_orientation', '')
        saved_scale = config.getdefault('internal', 'mod_screen_scale', '')

        first = True
        first_btn = None
        for device in sorted(screen.devices):
            btn = DesignerActionProfileCheck(
                group='mod_screen_device',
                allow_no_selection=False, config_key=device)
            
            btn.text = screen.devices[device][0]
            btn.bind(on_active=self.on_module_settings)

            if first:
                btn.checkbox_active = True
                first_btn = btn
                first = False
            else:
                if device == saved_device:
                    first_btn.checkbox.active = False
                    btn.checkbox_active = True
                else:
                    btn.checkbox_active = False
            devices.add_widget(btn)
        
        for orientation in self.ids.module_screen_orientation.list_action_item:
            if orientation.config_key == saved_orientation:
                orientation.checkbox_active = True

        for scale in self.ids.module_screen_scale.list_action_item:
            if scale.config_key == saved_scale:
                scale.checkbox_active = True

    def on_run_press(self, *args):
        '''Run button pressed. Analyze settings and dispatch ModulesContView
                on run
        '''
        device = None
        orientation = None
        scale = None

        for d in self.ids.module_screen_device.list_action_item:
            if d.checkbox.active:
                device = d.config_key
                break

        for o in self.ids.module_screen_orientation.list_action_item:
            if o.checkbox.active:
                orientation = o.config_key
                break

        for s in self.ids.module_screen_scale.list_action_item:
            if s.checkbox.active:
                scale = s.config_key
                break

        parameter = f'{device},{orientation},scale={scale}'
        self.dispatch('on_run', mod='screen', data=parameter)

    def on_run(self, *args, **kwargs):
        '''Event handler for on_run
        '''
        pass

    def on_module_settings(self, instance, *args):
        '''Event handle to save Screen Module settings when a different
        option is selected
        '''
        if not instance.checkbox.active:
            return None

        config_parser = self.designer.designer_settings.config_parser
        config_parser.set('internal', instance.group, instance.config_key)
        config_parser.write()
