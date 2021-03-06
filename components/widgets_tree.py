__all__ = ['WidgetTreeElement', 'WidgetsTree']

from utils.toolbox_widgets import toolbox_widgets
from utils.utils import get_current_project

from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeViewLabel
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.properties import ObjectProperty


Builder.load_string("""

#: import hex utils.colors.hex

<WidgetTreeElement>:
    is_open: True
    text: getattr(root.node, '__class__').__name__
    font_size: '10pt'

<WidgetsTree>:
    do_scroll_x: False
    tree: tree
    canvas.before:
        Color:
            rgb: bgcolor
        Rectangle:
            pos: root.pos
            size: root.size
    
    TreeView:
        id: tree
        height: self.minimum_height
        size_hint_y: None
        hide_root: True
        on_selected_node: args[1] and app.focus_widget(args[1].node)

""")


class WidgetTreeElement(TreeViewLabel):
    '''WidgetTreeElement represents each node in WidgetsTree
    '''
    node = ObjectProperty(None)

class WidgetsTree(ScrollView):
    '''WidgetsTree class is used to display the Root Widget's Tree in a
       Tree hierarchy.
    '''
    playground = ObjectProperty(None)
    '''This property is an instance of
        :class:`~designer.components.playground.Playground`
       :data:`playground` is a :class:`~kivy.properties.ObjectProperty`
    '''
    tree = ObjectProperty(None)
    '''This property is an instance of :class:`~kivy.uix.treeview.TreeView`.
       This TreeView is responsible for showing Root Widget's Tree.
       :data:`tree` is a :class:`~kivy.properties.ObjectProperty`
    '''
    dragging = False
    '''Specifies whether a node is dragged or not.
       :data:`dragging` is a :class:`~kivy.properties.BooleanProperty`
    '''
    selected_widget = ObjectProperty(allownone=True)
    '''Current selected widget.
       :data:`dragging` is a :class:`~kivy.properties.ObjectProperty`
    '''
    def __init__(self, **kwargs):
        super(WidgetsTree, self).__init__(**kwargs)
        self.refresh = Clock.create_trigger(self._refresh)
        self._widget_cache = {}

    def recursive_insert(self, node, treenode):
        '''This function will add a node to TreeView, by recursively travelling
           through the Root Widget's Tree.
        '''
        if node is None:
            return None

        b = self._get_widget(node)
        self.tree.add_node(b, treenode)
        class_rules = get_current_project().app_widgets
        root_widget = self.playground.root

        is_child_custom = False
        for rule_name in class_rules:
            if rule_name == type(node).__name__:
                is_child_custom = True
                break

        is_child_complex = False
        for widget in toolbox_widgets:
            if widget[0] == type(node).__name__ and widget[1] == 'complex':
                is_child_complex = True
                break

        if root_widget == node or (not is_child_custom and not is_child_complex):
            if isinstance(node, TabbedPanel):
                self.insert_for_tabbed_panel(node, b)
            else:
                for child in node.children:
                    self.recursive_insert(child, b)

    def insert_for_tabbed_panel(self, node, treenode):
        '''This function will insert nodes in tree specially for TabbedPanel.
        '''
        for tab in node.tab_list:
            b = self._get_widget(tab)
            self.tree.add_node(b, treenode)
            self.recursive_insert(tab.content, b)

    def _get_widget(self, node):
        try:
            wid = self._widget_cache[node]
            if not wid:
                raise KeyError()
        except KeyError:
            wid = WidgetTreeElement(node=node)
            self._widget_cache[node] = wid.proxy_ref
        
        if wid.parent_node:
            self.tree.remove_node(wid)
        return wid

    def _clear_tree(self, tree, node):
        remove_node = tree.remove_node
        for n in node.nodes[:]:
            self._clear_tree(tree, n)
            remove_node(n)

    def _refresh(self, *l):
        '''This function will refresh the tree. It will first remove all nodes
           and then insert them using recursive_insert
        '''
        self._clear_tree(self.tree, self.tree.root)
        self.recursive_insert(self.playground.root, self.tree.root)
        self._clean_cache()

    def _clean_cache(self):
        for node, wid in list(self._widget_cache.items()):
            try:
                if node and node.parent and wid and wid.parent_node:
                    continue
            except ReferenceError:
                pass
            del self._widget_cache[node]

    def on_touch_up(self, touch):
        '''Default event handler for 'on_touch_up' event.
        '''
        self.dragging = False
        Clock.unschedule(self._start_dragging)
        return super(WidgetsTree, self).on_touch_up(touch)

    def on_touch_down(self, touch):
        '''Default event handler for 'on_touch_down' event.
        '''
        if self.collide_point(*touch.pos) and not self.dragging:
            self.dragging = True
            self.touch = touch
            Clock.schedule_once(self._start_dragging, 2)
            node = self.tree.get_node_at_pos((self.touch.x, self.touch.y))

            if node:
                self.selected_widget = node.node
                self.playground.selected_widget = self.selected_widget
            else:
                self.selected_widget = None
                self.playground.selected_widget = None

        return super(WidgetsTree, self).on_touch_down(touch)

    def _start_dragging(self, *args):
        '''This function will start dragging the widget.
        '''
        if not self.dragging or not self.selected_widget:
            return None
        
        self.playground.selected_widget = self.selected_widget
        self.playground.dragging = False
        self.playground.touch = self.touch
        self.playground.start_widget_dragging()
