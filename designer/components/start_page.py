import webbrowser
from utils.utils import get_designer, get_fs_encoding
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.lang.builder import Builder

Builder.load_string("""

#: import theme_atlas utils.utils.theme_atlas

<DesignerButtonFit@DesignerButton>
    size_hint_x: None
    width: self.texture_size[0] + sp(32)

<DesignerStartPage>:
    btn_open: btn_open
    btn_new: btn_new
    recent_files_box: recent_files_box
    orientation: 'vertical'
    padding: 0, 0, 0, 20
    Label:
        text: 'Kivy Designer'
        font_size: '26pt'
        size_hint_y: None
        height: '40pt'
    Label:
        markup: True
        text: '[i]Innovative User Interfaces, Desktop, and Mobile Development Made Easy.[/i]'
        font_size: '12pt'
        halign: 'center'
        size_hint_y: None
        height: '15pt'
    GridLayout:
        cols: 2
        size_hint: None, None
        height: self.minimum_height
        width: self.minimum_width
        pos_hint: {'center_x': 0.5}
        padding: 0, '15pt', 0, 0
        spacing: '4sp'
        DesignerButtonFit:
            id: btn_open
            text: 'Open Project'
            on_release: root.dispatch('on_open_down')
        DesignerButtonFit:
            id: btn_new
            text: 'New Project'
            on_release: root.dispatch('on_new_down')

    Label:
        text: 'Getting Started'
        font_size: '16pt'
        bold: True
        size_hint_y: None
        height: '30pt'

    GridLayout:
        kivy_label: kivy_label
        cols: 2
        size_hint: None, None
        height: self.minimum_height
        width: 450
        pos_hint: {'center_x': 0.5}
        row_force_default: True
        row_default_height: '40sp'
        spacing: '4sp'
        padding: '16sp', '0sp'

        DesignerLinkLabel:
            id: kivy_label
            text: ' Kivy'
            link: 'http://kivy.org'

        DesignerLinkLabel:
            text: ' Kivy Designer Help'
            on_release: root.dispatch('on_help')

        DesignerLinkLabel:
            id: kivy_label
            text: ' Kivy Documentation'
            link: 'http://kivy.org/docs'

        DesignerLinkLabel:
            text: ' Kivy Designer Documentation'
            link: 'http://kivy-designer.readthedocs.org/'

    Label:
        text: 'Recent Projects'
        font_size: '16pt'
        bold: True
        size_hint_y: None
        height: '30pt'

    RecentFilesBox:
        id: recent_files_box
        pos_hint: {'center_x': 0.5}
        size_hint_x: None
        width: 600
        canvas.before:
            Color:
                rgba: 1, 1, 1, 0.05
            Rectangle:
                pos: self.pos
                size: self.size

<DesignerLinkLabel>:
    color: 0, 0, 1, 1
    background_normal: theme_atlas('action_item')
    background_disabled_normal: theme_atlas('action_item_disabled')
    text_size: self.width, None

<RecentFilesBox>:
    grid: grid
    cols: 1
    padding: '2sp'
    size_hint_x: None
    bar_width: 10
    scroll_type: ['bars', 'content']
    GridLayout:
        id: grid
        cols: 1
        size_hint_y: None
        height: 1

<RecentItem>:
    orientation: 'vertical'
    size_hint: 1, None
    height: 40
    on_touch_down: if self.collide_point(*args[1].pos): root.dispatch('on_press')
    canvas.after:
        Color:
            rgb: .2, .2, .2
        Rectangle:
            pos: self.x + 25, self.y
            size: self.width - 50, 1
    Label:
        text: root.path
        text_size: self.size
        valign: 'middle'
        shorten: True
        padding_x: 20

""")

class DesignerLinkLabel(Button):
    '''DesignerLinkLabel displays a http link and opens it in a browser window
       when clicked.
    '''

    link = StringProperty(None)
    '''Contains the http link to be opened.
       :data:`link` is a :class:`~kivy.properties.StringProperty`
    '''

    def on_release(self, *args):
        '''Default event handler for 'on_release' event.
        '''
        if self.link:
            webbrowser.open(self.link)


class RecentItem(BoxLayout):
    path = StringProperty('')
    '''Contains the application path
       :data:`path` is a :class:`~kivy.properties.StringProperty`
    '''

    __events__ = ('on_press', )

    def on_press(self, *args):
        '''Item pressed
        '''


class RecentFilesBox(ScrollView):
    '''Container consistings of buttons, with their names specifying
       the recent files.
    '''

    grid = ObjectProperty(None)
    '''The grid layout consisting of all buttons.
       This property is an instance of :class:`~kivy.uix.gridlayout`
       :data:`grid` is a :class:`~kivy.properties.ObjectProperty`
    '''

    def __init__(self, **kwargs):
        super(RecentFilesBox, self).__init__(**kwargs)

    def add_recent(self, list_files):
        '''To add buttons representing Recent Files.
        :param list_files: array of paths
        '''
        for p in list_files:
            if isinstance(p, bytes):
                p = p.decode(get_fs_encoding())
            recent_item = RecentItem(path=p)
            self.grid.add_widget(recent_item)
            recent_item.bind(on_press=self.btn_release)
            self.grid.height += recent_item.height

        self.grid.height = max(self.grid.height, self.height)

    def btn_release(self, instance):
        '''Event Handler for 'on_release' of an event.
        '''
        d = get_designer()
        d._perform_open(instance.path)


class DesignerStartPage(BoxLayout):

    recent_files_box = ObjectProperty(None)
    '''This property is an instance
        of :class:`~designer.components.start_page.RecentFilesBox`
       :data:`recent_files_box` is a :class:`~kivy.properties.ObjectProperty`
    '''

    __events__ = ('on_open_down', 'on_new_down', 'on_help')

    def on_open_down(self, *args):
        '''Default Event Handler for 'on_open_down'
        '''
        pass

    def on_new_down(self, *args):
        '''Default Event Handler for 'on_new_down'
        '''
        pass

    def on_help(self, *args):
        '''Default Event Handler for 'on_help'
        '''
        pass
