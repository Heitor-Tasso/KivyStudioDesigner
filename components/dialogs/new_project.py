
__all__ = ['ProjectTemplateBox', 'NewProjectDialog']

from utils.utils import template_images

from kivy.factory import Factory
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.scrollview import ScrollView

NEW_PROJECTS = {

    'FloatLayout': ('template_floatlayout_kv', 'template_floatlayout_py'),    
    'BoxLayout': ('template_boxlayout_kv', 'template_boxlayout_py'),
    'ScreenManager': ('template_screen_manager_kv', 'template_screen_manager_py'),
    'ActionBar': ('template_actionbar_kv', 'template_actionbar_py'),
    'Carousel and ActionBar': ('template_actionbar_carousel_kv', 'template_actionbar_carousel_py'),
    'ScreenManager and ActionBar': ('template_screen_manager_actionbar_kv', 'template_screen_manager_actionbar_py'),
    'TabbedPanel': ('template_tabbed_panel_kv', 'template_tabbed_panel_py'),
    'TextInput and ScrollView': ('template_textinput_scrollview_kv', 'template_textinput_scrollview_py')
}


Builder.load_string("""

#: import hex utils.colors.hex

<ProjectTemplateBox>:
    grid: grid
    cols: 1
    padding: '2sp'
    size_hint_x: None
    bar_width: '10dp'
    scroll_type: ['bars', 'content']
    GridLayout:
        id: grid
        cols: 1
        size_hint_y: None
        height: 1

<NewProjectDialog>:
    template_preview: template_preview
    cancel_button: cancel
    select_button: select
    template_list: template_list
    app_name: app_name
    package_name: package_name
    package_version: package_version
    orientation: 'horizontal'
    padding: designer_padding
    spacing: designer_spacing
    ProjectTemplateBox:
        id: template_list
        pos_hint: {'center_x': 0.5}
        size_hint_x: 0.3
        canvas.before:
            Color:
                rgba: [1, 1, 1, 0.05]
            Rectangle:
                pos: self.pos
                size: self.size
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.7
        spacing: '20dp'
        BoxLayout:
            size_hint_y: 0.1
            orientation: 'horizontal'
            Label:
                size_hint_x: 0.2
                text_size: self.width, None
                padding_x: '10dp'
                halign: 'right'
                text: 'App Name: '
            TextInput:
                id: app_name
                size_hint_x: 0.7
                multiline: False
                padding: [dp(15), ((self.height-self.line_height)/2)]
                focus: True
        BoxLayout:
            size_hint_y: 0.1
            orientation: 'horizontal'
            Label:
                size_hint_x: 0.2
                text_size: self.width, None
                padding_x: '10dp'
                halign: 'right'
                text: 'Package Name: '
            TextInput:
                id: package_name
                size_hint_x: 0.7
                multiline: False
                padding: [dp(15), ((self.height-self.line_height)/2)]
        BoxLayout:
            size_hint_y: 0.1
            orientation: 'horizontal'
            Label:
                size_hint_x: 0.2
                text_size: self.width, None
                padding_x: '10dp'
                halign: 'right'
                text: 'Version: '
            TextInput:
                id: package_version
                size_hint_x: 0.7
                multiline: False
                padding: [dp(15), ((self.height-self.line_height)/2)]
        Image:
            id: template_preview
        GridLayout:
            rows: 1
            size_hint_y: None
            height: '48sp'
            padding: designer_padding
            spacing: designer_spacing
            DesignerButton:
                id: select
                text: 'Create New Project'
            DesignerButton:
                id: cancel
                text: 'Cancel'

""")

class ProjectTemplateBox(ScrollView):
    '''Container consistings of buttons, with their names specifying
       the recent files.
    '''
    grid = ObjectProperty(None)
    '''The grid layout consisting of all buttons.
       This property is an instance of :class:`~kivy.uix.gridlayout`
       :data:`grid` is a :class:`~kivy.properties.ObjectProperty`
    '''
    text = ObjectProperty(None)
    '''The grid layout consisting of all buttons.
       This property is an instance of :class:`~kivy.uix.gridlayout`
       :data:`grid` is a :class:`~kivy.properties.ObjectProperty`
    '''
    def __init__(self, **kwargs):
        super(ProjectTemplateBox, self).__init__(**kwargs)

    def add_template(self):
        '''To add buttons representing Recent Files.
        :param list_files: array of paths
        '''
        item_strings = list(NEW_PROJECTS.keys())
        item_strings.sort()

        for p in item_strings:
            recent_item = Factory.DesignerListItemButton(text=p)
            self.grid.add_widget(recent_item)
            recent_item.bind(on_press=self.btn_release)
            self.grid.height += recent_item.height

        self.grid.height = max(self.grid.height, self.height)
        self.grid.children[-1].trigger_action()

    def btn_release(self, instance):
        '''Event Handler for 'on_release' of an event.
        '''
        self.text = instance.text
        self.parent.update_template_preview(instance)


class NewProjectDialog(BoxLayout):
    select_button = ObjectProperty(None)
    ''':class:`~kivy.uix.button.Button` used to select the list item.
       :data:`select_button` is a :class:`~kivy.properties.ObjectProperty`
    '''
    cancel_button = ObjectProperty(None)
    ''':class:`~kivy.uix.button.Button` to cancel the dialog.
       :data:`cancel_button` is a :class:`~kivy.properties.ObjectProperty`
    '''
    template_preview = ObjectProperty(None)
    '''Type of :class:`~kivy.uix.image.Image` to display preview of selected
       new template.
       :data:`template_preview` is a :class:`~kivy.properties.ObjectProperty`
    '''
    template_list = ObjectProperty(None)
    '''Type of :class:`ProjectTemplateBox` used for showing template available.
       :data:`template_list` is a :class:`~kivy.properties.ObjectProperty`
    '''
    app_name = ObjectProperty(None)
    '''Type of :class:`ProjectTemplateBox` used for showing template available.
       :data:`template_list` is a :class:`~kivy.properties.ObjectProperty`
    '''
    package_name = ObjectProperty(None)
    '''Type of :class:`ProjectTemplateBox` used for showing template available.
       :data:`template_list` is a :class:`~kivy.properties.ObjectProperty`
    '''
    package_version = ObjectProperty(None)
    '''Type of :class:`ProjectTemplateBox` used for showing template available.
       :data:`template_list` is a :class:`~kivy.properties.ObjectProperty`
    '''
    __events__ = ('on_select', 'on_cancel')

    def __init__(self, **kwargs):
        super(NewProjectDialog, self).__init__(**kwargs)
        self.template_list.add_template()
        self.app_name.bind(text=self.on_app_name_text)
        self.app_name.text = "My Application"
        self.package_version.text = "0.1.dev0"

    def update_template_preview(self, instance):
        '''Event handler for 'on_selection_change' event of adapter.
        '''
        name = instance.text.lower()
        name = name.replace(' and ', '_')
        image_source = template_images(name)
        self.template_preview.source = image_source

    def on_app_name_text(self, instance, value):
        self.package_name.text = 'org.test.' + value.lower().replace(' ', '_')

    def on_select(self, *args):
        '''Default Event Handler for 'on_select' event
        '''
        pass

    def on_cancel(self, *args):
        '''Default Event Handler for 'on_cancel' event
        '''
        pass

    def on_select_button(self, *args):
        '''Event Handler for 'on_release' of select button.
        '''
        self.select_button.bind(on_press=lambda *a: self.dispatch('on_select'))

    def on_cancel_button(self, *args):
        '''Event Handler for 'on_release' of cancel button.
        '''
        self.cancel_button.bind(on_press=lambda *a: self.dispatch('on_cancel'))
