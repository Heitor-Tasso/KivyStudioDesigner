__all__ = ['ToolboxCategory', 'ToolboxButton', 'Toolbox']

from utils.toolbox_widgets import toolbox_widgets

from kivy.clock import Clock
from kivy.factory import Factory
from kivy.uix.button import Button
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.accordion import AccordionItem


Builder.load_string("""

<Toolbox>:
    accordion: accordion
    Accordion:
        id: accordion
        orientation: 'vertical'
        pos: root.pos
        min_space: '1dp'
        size_hint_y: None
        height: root.height

<ToolboxCategory>:
    gridlayout: gridlayout
    size_hint_y: None
    height: '22dp'
    title: self.title[0].upper() + self.title[1:]
    ScrollView:
        pos: root.pos
        bar_width: '10dp'
        scroll_type: ['bars', 'content']
        GridLayout:
            id: gridlayout
            cols: 1
            padding: '5dp'
            spacing: '3dp'
            size_hint_y: None
            height: self.minimum_height + dp(40)
            Widget:
                size_hint_y:None
                height: '40dp'

<ToolboxButton>:
    size_hint_y: None
    height: '52dp'
    font_size: '10pt'
    on_press_and_touch: app.create_draggable_element(self, self.text, args[1])

""")

class ToolboxCategory(AccordionItem):
    '''ToolboxCategory is responsible for grouping and showing
       :class:`~designer.components.toolbox.ToolboxButton`
       of same class into one category.
    '''
    gridlayout = ObjectProperty(None)
    '''An instance of :class:`~kivy.uix.gridlayout.GridLayout`.
       :data:`gridlayout` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

class ToolboxButton(Button):
    '''ToolboxButton is a subclass of :class:`~kivy.uix.button.Button`,
       to display class of Widgets in
       :class:`~designer.components.toolbox.ToolboxCategory`.
    '''
    def __init__(self, **kwargs):
        self.register_event_type('on_press_and_touch')
        super(ToolboxButton, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        '''Default handler for 'on_touch_down'
        '''
        if self.collide_point(*touch.pos):
            self.dispatch('on_press_and_touch', touch)
        
        return super(ToolboxButton, self).on_touch_down(touch)

    def on_press_and_touch(self, touch):
        '''Default handler for 'on_press_and_touch' event
        '''
        pass

class Toolbox(BoxLayout):
    '''Toolbox is used to display all the widgets in designer.common.widgets
       in their respective classes.
    '''
    accordion = ObjectProperty()
    '''An instance to :class:`~kivy.uix.accordion.Accordion`,
       used to show Widgets in their groups.
       :data:`accordion` is an
       :class:`~kivy.properties.ObjectProperty`
    '''
    app = ObjectProperty()
    '''An instance to the current running app.
       :data:`app` is an
       :class:`~kivy.properties.ObjectProperty`
    '''
    def __init__(self, **kwargs):
        super(Toolbox, self).__init__(**kwargs)
        Clock.schedule_once(self.discover_widgets)
        self.custom_category = None
        self._list = []

    def discover_widgets(self, *largs):
        '''To create and add ToolboxCategory and ToolboxButton for widgets in
           designer.common.widgets
        '''
        # for now, don't do auto detection of widgets.
        # just do manual discovery, and tagging.
        categories = list(set([x[1] for x in toolbox_widgets]))
        categories.sort()
        for category in categories:
            toolbox_category = ToolboxCategory(title=category)
            self.accordion.add_widget(toolbox_category)

            cat_widgets = []
            for widget in toolbox_widgets:
                if widget[1] == category:
                    cat_widgets.append(widget)

            cat_widgets.sort()
            for widget in cat_widgets:
                toolbox_category.gridlayout.add_widget(
                    ToolboxButton(text=widget[0]))

        self.accordion.children[-1].collapse = False

    def cleanup(self):
        '''To clean all the children in self.custom_category.
        '''
        if not self.custom_category:
            return None
        
        self.accordion.remove_widget(self.custom_category)
        Factory.register('BoxLayout', module='kivy.uix.boxlayout')
        self.custom_category = ToolboxCategory(title='App Widgets')
        self._list.append(self.custom_category)

    def update_app_widgets(self):
        '''To add/update self.custom_category with new custom classes loaded
           by project.
        '''
        if self.custom_category:
            self.accordion.remove_widget(self.custom_category)
            self._list = []
        
        self.custom_category = ToolboxCategory(title='App Widgets')
        self._list.append(self.custom_category)
        self.accordion.add_widget(self.custom_category)

        custom_widgets = []
        for widget in toolbox_widgets:
            if widget[1] == 'custom':
                custom_widgets.append(widget)

        custom_widgets.sort()
        grid = self.custom_category.gridlayout
        for widget in custom_widgets:
            grid.add_widget(ToolboxButton(text=widget[0]))
