from uix.sandbox import DesignerSandbox
from designer import DesignerException, Designer
from utils.toolbox_widgets import toolbox_widgets
from components.playground import PlaygroundDragElement
from utils.utils import get_config_dir, get_fs_encoding, show_message

from kivy.app import App
from kivy.factory import Factory
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.graphics import Color, Line
from kivy.base import ExceptionManager
from kivy.resources import resource_add_path
from kivy.properties import BooleanProperty, ObjectProperty

import os

Builder.load_string("""

#: import hex utils.colors.hex
#: import KivyLexer kivy.extras.highlight.KivyLexer
#: import ContextMenu uix.contextual.ContextMenu
#: import ToolBarTopDesigner screens.inicial.main_inicial.ToolBarTopDesigner

<DesignerButton@Button+Label>:
    size_hint_y: None
    height: designer_height

<DesignerListItemButton@ListItemButton>:
    size_hint: 1, None
    size: ((self.texture_size[0]+sp(32)), designer_height)
    selected_color: [1, 1, 1, 1]
    deselected_color: [0.8, 0.8, 0.8, 0.5]

<Designer>:
    statusbar: statusbar
    actionbar: actionbar
    start_page: start_page.__self__
    designer_git: toll_bar_top.ids.git_tools

    ActionBar:
        id: actionbar
        pos_hint: {'top': 1}
        on_height: root.on_height()
        ToolBarTopDesigner:
            id:toll_bar_top

    DesignerStartPage:
        id: start_page
        size_hint_y: None
        height: root.height - actionbar.height - statusbar.height
        top: root.height - actionbar.height
        on_open_down: toll_bar_top.action_btn_open_pressed()
        on_new_down: toll_bar_top.action_btn_new_project_pressed()
        on_help: toll_bar_top.show_help()

    StatusBar:
        id: statusbar
        size_hint_y: None
        on_height: root.on_statusbar_height()
        height: '20pt'
        pos_hint: {'y': 0}

""")

class ProgramDesigner(App):

    widget_focused = ObjectProperty(allownone=True)
    '''Currently focused widget
    '''
    started = BooleanProperty(False)
    '''Indicates if has finished the build()
    '''
    title = 'Kivy Designer'

    def build(self):
        data = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        if isinstance(data, bytes):
            data = data.decode(get_fs_encoding())
        resource_add_path(data)

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
        return Designer(self)

    def _setup(self, *args):
        '''To setup the properties of different classes
        '''
        self.root.ui_creator = self.root.designer_content.ui_creator
        playground = self.root.ui_creator.playground
        eventviewer = self.root.ui_creator.eventviewer
        self.root.proj_tree_view = self.root.designer_content.tree_view
        self.root.statusbar.playground = playground
        playground.undo_manager = self.root.undo_manager

        eventviewer.designer_tabbed_panel = self.root.designer_content.tab_pannel
        self.root.statusbar.bind(
            height=self.root.on_statusbar_height)
        self.root.actionbar.bind(
            height=self.root.on_height)
        
        playground.sandbox = DesignerSandbox()
        playground.add_widget(playground.sandbox)
        playground.sandbox.pos = playground.pos
        playground.sandbox.size = playground.size

        getdefault = self.root.designer_settings.config_parser.getdefault
        max_lines = int(getdefault('global', 'num_max_kivy_console', 200))
        self.root.ui_creator.kivy_console.cached_history = max_lines

        playground.sandbox.bind(
            on_getting_exception=self.root.on_sandbox_getting_exception)
        self.bind(widget_focused=self.root.ui_creator.propertyviewer.setter('widget'))
        self.bind(widget_focused=eventviewer.setter('widget'))
            
        self.focus_widget(playground.root)
        if not os.path.exists(get_config_dir()):
            os.mkdir(get_config_dir())

        projects = self.root.recent_manager.list_projects
        self.root.start_page.recent_files_box.add_recent(projects)
        self.started = True

    def create_draggable_element(self, instance, widget_name, touch, widget=None):
        """
        Create PlagroundDragElement and make it draggable until the touch is
        released also search default args if exist.

        Args:
            `instance` (_type_): if from toolbox, ToolboxButton instance, None otherwise.
            `widget_name` (_type_): name of the widget that will be dragged.
            `touch` (_type_): instance of the current touch.
            `widget` (_type_, optional): instance of widget, If set, widget_name will be ignored.

        Returns:
            _type_: container that was drawed by `playground.get_playground_drag_element`
        """
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
        
        _drag_element = self.root.ui_creator.playground.get_playground_drag_element
        container = _drag_element(instance, widget_name, touch, default_args, extra_args)
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

if __name__ == '__main__':
    app = ProgramDesigner()
    app.run()
    if hasattr(app.root, 'ui_creator'):
        if hasattr(app.root.ui_creator, 'py_console'):
            app.root.ui_creator.py_console.exit()
