from utils.utils import get_designer
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.lang.builder import Builder

Builder.load_string("""

<UICreator>:
    kv_code_input: code_input
    splitter_kv_code_input: splitter_kv
    grid_widget_tree: grid_widget_tree
    splitter_property: splitter_property
    splitter_widget_tree: splitter_widget_tree
    propertyviewer: propertyviewer
    playground: playground
    widgettree: widgettree
    error_console: error_console
    kivy_console: kivy_console
    tab_pannel: tab_pannel
    eventviewer: eventviewer
    py_console: py_console

    GridLayout:
        height: root.height
        pos: root.pos
        cols: 1
        splitter_widget_tree: splitter_widget_tree

        canvas.before:
            StencilPush
            Rectangle:
                pos: self.pos
                size: self.size
            StencilUse
        canvas.after:
            StencilUnUse
            Rectangle:
                pos: self.pos
                size: self.size
            StencilPop

        FloatLayout:
            size_hint: 1,1
            canvas:
                Color:
                    rgb: .21, .22, .22
                Rectangle:
                    pos: self.pos
                    size: self.size

            Playground:
                id: playground
                canvas.before:
                    Color:
                        rgb: 0, 0, 0
                    Rectangle:
                        size: self.size
                on_show_edit: root.on_show_edit()

            Splitter:
                id: splitter_kv
                sizable_from: 'top'
                size_hint_y: None
                size_hint_x: None
                height: 200
                min_size: 150
                max_size: 500
                x: root.x
                width: root.width - splitter_widget_tree.width
                y: root.y
                canvas.before:
                    Color:
                        rgb: .21, .22, .22

                    Rectangle:
                        size: splitter_kv.size
                        pos: splitter_kv.pos


                DesignerTabbedPanel:
                    id: tab_pannel
                    do_default_tab: False
                    DesignerTabbedPanelItem:
                        text: 'KV Lang Area'
                        BoxLayout:
                            orientation: 'vertical'
                            KVLangAreaScroll:
                                id: scroll
                                kv_lang_area: code_input
                                line_number: line_number
                                GridLayout:
                                    cols: 2
                                    size_hint: 1, None
                                    height: max(scroll.height, self.minimum_height)
                                    TextInput:
                                        id: line_number
                                        size_hint: None, 1
                                        readonly: True
                                        background_color: 1, 1, 1, 0
                                        foreground_color: 1, 1, 1, 1
                                    KVLangArea:
                                        id: code_input
                                        size_hint_y: None
                                        height: max(scroll.height, self.minimum_height)
                                        on_show_edit: root.on_show_edit()
                            DesignerButton:
                                size_hint_x: 0.2
                                text: 'Reload Widgets'
                                pos_hint: {'x': 0.8}
                                on_release: root.reload_btn_pressed()

                    DesignerTabbedPanelItem:
                        text: 'Kivy Console'
                        KivyConsole:
                            id: kivy_console

                    DesignerTabbedPanelItem:
                        text: 'Python Shell'
                        PythonConsole:
                            id: py_console

                    DesignerTabbedPanelItem:
                        text: 'Error Console'
                        ScrollView:
                            id: e_scroll
                            CodeInput:
                                id: error_console
                                size_hint_y: None
                                height: max(e_scroll.height, self.minimum_height)
                                text: ''

            Splitter:
                id: splitter_widget_tree
                size_hint_x: None
                min_size: 170
                width: 250
                pos_hint: {'y': 0, 'right': 1}

                BoxLayout:
                    orientation: 'vertical'

                    GridLayout:
                        id: grid_playground_settings
                        cols: 1
                        spacing: .5
                        height: self.minimum_height
                        size_hint_y: None

                        canvas:
                            Color:
                                rgb: titlecolor
                            Rectangle:
                                pos: self.pos
                                size: self.size

                        Label:
                            text: 'Playground Settings'
                            font_size: '10pt'
                            height: '20pt'
                            size_hint_y: None

                        BoxLayout:
                            size_hint_y: None
                            height: sp(48)

                            canvas.before:
                                Color:
                                    rgb: bgcolor
                                Rectangle:
                                    pos: self.pos
                                    size: self.size

                            Label:
                                text: 'Size:'
                                size_hint_x: None
                                width: sp(52)

                            PlaygroundSizeSelector:
                                playground: playground

                        BoxLayout:
                            size_hint_y: None
                            height: sp(48)

                            canvas.before:
                                Color:
                                    rgb: bgcolor
                                Rectangle:
                                    pos: self.pos
                                    size: self.size

                            Label:
                                text: 'Zoom: %d%%' % (zoom_slider.value * 100)
                                size_hint_x: None
                                width: sp(96)

                            Slider:
                                id: zoom_slider
                                min: 0.25
                                max: 1.5
                                step: 0.05
                                value: playground.scale
                                on_value: playground.scale = args[1]

                    GridLayout:
                        id: grid_playground_widget
                        cols: 1
                        spacing: .5
                        height: self.minimum_height
                        size_hint_y: None

                        canvas:
                            Color:
                                rgb: titlecolor
                            Rectangle:
                                pos: self.pos
                                size: self.size

                        Label:
                            text: 'Playground Widget'
                            font_size: '10pt'
                            height: '20pt'
                            size_hint_y: None

                        BoxLayout:
                            size_hint_y: None
                            height: sp(48)

                            canvas.before:
                                Color:
                                    rgb: bgcolor
                                Rectangle:
                                    pos: self.pos
                                    size: self.size

                            Button:
                                text: playground.root_name
                                on_press: playground.on_widget_select_pressed()

                    GridLayout:
                        cols: 1
                        spacing: .5

                        canvas:
                            Color:
                                rgb: titlecolor
                            Rectangle:
                                pos: self.pos
                                size: self.size

                        GridLayout:
                            id: grid_widget_tree
                            cols: 1
                            spacing: .5
                            Label:
                                text: 'Widget Navigator'
                                font_size: '10pt'
                                height: '20pt'
                                size_hint_y: None

                            WidgetsTree:
                                id: widgettree
                                playground: playground

                        Splitter:
                            id: splitter_property
                            sizable_from: 'top'
                            size_hint_y: None
                            height: 300
                            max_size: 500
                            canvas.before:
                                Color:
                                    rgb: bgcolor
                                Rectangle:
                                    pos: self.pos
                                    size: self.size
                            DesignerTabbedPanel:
                                do_default_tab: False
                                DesignerTabbedPanelItem:
                                    text: 'Properties'
                                    PropertyViewer:
                                        id: propertyviewer

                                DesignerTabbedPanelItem:
                                    text: 'Events'
                                    EventViewer:
                                        id: eventviewer

""")

class UICreator(FloatLayout):
    '''UICreator is the Wigdet responsible for editing/creating UI of project
    '''

    toolbox = ObjectProperty(None)
    '''Reference to the :class:`~designer.components.toolbox.Toolbox` instance.
       :data:`toolbox` is an :class:`~kivy.properties.ObjectProperty`
    '''

    propertyviewer = ObjectProperty(None)
    '''Reference to the
        :class:`~designer.components.property_viewer.PropertyViewer`
       instance. :data:`propertyviewer` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    playground = ObjectProperty(None)
    '''Reference to the :class:`~designer.components.playground.Playground`
     instance.:data:`playground` is an :class:`~kivy.properties.ObjectProperty`
    '''

    widgettree = ObjectProperty(None)
    '''Reference to the :class:`~designer.components.widgets_tree.WidgetsTree`
     instance.:data:`widgettree` is an :class:`~kivy.properties.ObjectProperty`
    '''

    kv_code_input = ObjectProperty(None)
    '''Reference to the :class:`~designer.uix.KVLangArea` instance.
       :data:`kv_code_input` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    splitter_kv_code_input = ObjectProperty(None)
    '''Reference to the splitter parent of kv_code_input.
       :data:`splitter_kv_code_input` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    grid_widget_tree = ObjectProperty(None)
    '''Reference to the grid parent of widgettree.
       :data:`grid_widget_tree` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    splitter_property = ObjectProperty(None)
    '''Reference to the splitter parent of propertyviewer.
       :data:`splitter_property` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    splitter_widget_tree = ObjectProperty(None)
    '''Reference to the splitter parent of widgettree.
       :data:`splitter_widget_tree` is an
       :class:`~kivy.properties.ObjectProperty`
    '''

    error_console = ObjectProperty(None)
    '''Instance of :class:`~kivy.uix.codeinput.CodeInput` used for displaying
       exceptions.
    '''

    kivy_console = ObjectProperty(None)
    '''Instance of :class:`~designer.components.kivy_console.KivyConsole`.
    '''

    python_console = ObjectProperty(None)
    '''Instance of :class:`~designer.uix.py_console.PythonConsole`
    '''

    tab_pannel = ObjectProperty(None)
    '''Instance of
        :class:`~designer.components.designer_content.DesignerTabbedPanel`
       containing error_console, kivy_console and kv_lang_area
    '''

    eventviewer = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(UICreator, self).__init__(**kwargs)
        Clock.schedule_once(self._setup_everything)

    def reload_btn_pressed(self, *args):
        '''Default handler for 'on_release' event of "Reload" button.
        '''
        self.kv_code_input.func_reload_kv(force=True)

    def on_touch_down(self, *args):
        '''Default handler for 'on_touch_down' event.
        '''
        if self.playground and self.playground.keyboard:
            self.playground.keyboard.release()

        return super(UICreator, self).on_touch_down(*args)

    def on_show_edit(self, *args):
        '''Event handler for 'on_show_edit' event.
        '''
        App.get_running_app().root.on_show_edit(*args)

    def cleanup(self):
        '''To clean up everything before loading new project.
        '''
        self.playground.cleanup()
        self.kv_code_input.text = ''

    def _setup_everything(self, *args):
        '''To setup all the references in between widget
        '''

        self.kv_code_input.playground = self.playground
        self.playground.kv_code_input = self.kv_code_input
        self.playground.kv_code_input.bind(
            on_reload_kv=self.playground.on_reload_kv)
        self.playground.widgettree = self.widgettree
        self.propertyviewer.kv_code_input = self.kv_code_input
        self.eventviewer.kv_code_input = self.kv_code_input
        self.py_console.remove_widget(self.py_console.children[1])
        d = get_designer()
        if self.kv_code_input not in d.code_inputs:
            d.code_inputs.append(self.kv_code_input)
