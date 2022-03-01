__all__ = [
    'StatusNavBarButton', 'StatusNavBarSeparator'
    'StatusNavbar', 'StatusMessage', 'StatusInfo',
    'StatusBar']

from utils.utils import icons

from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelContent, TabbedPanelHeader


Builder.load_string("""

#: import hex utils.colors.hex

<StatusBar>:
    app: app
    navbar: navbar
    status_message: status_message
    status_info: status_info
    canvas:
        Color:
            rgb: bordercolor
        Rectangle:
            pos: (self.x, (self.top-dp(0.5)))
            size: (self.width, dp(1))
        Color:
            rgb: bgcolor
        Rectangle:
            pos: self.pos
            size: self.size

    ScrollView:
        id: nav_scroll
        size_hint_x: None
        width: 0
        do_scroll_y: False
        StatusNavbar:
            id: navbar
            size_hint_x: None
            width: max(nav_scroll.width, self.width)
            on_children: root._update_content_width()

    StatusMessage:
        id: status_message
        img: img
        size_hint: 0.9, None
        height: '20pt'
        spacing: '10dp'
        on_message: root._update_content_width()
        on_touch_down: if self.collide_point(*args[1].pos): root.dispatch('on_message_press')
        Image:
            id: img
            size_hint: None, None
            width: '20pt'
            height: '20pt'
            opacity: 0
        Label:
            size_hint_x: 1
            text: status_message.message
            text_size: self.size
            halign: 'left'
            valign: 'middle'
            shorten: True
            shorten_from: 'left'

    StatusInfo:
        id: status_info
        size_hint_x: 0.1
        on_touch_down:
            if self.collide_point(*args[1].pos): root.dispatch('on_info_press')
        Label:
            size_hint_x: 1
            text: status_info.message
            text_size: self.size
            halign: 'center'
            valign: 'middle'
            shorten: True
            shorten_from: 'left'

<StatusNavBarButton>:
    text: getattr(root.node, '__class__').__name__
    font_size: '10pt'
    width: (self.texture_size[0]+dp(20))
    size_hint_x: None
    on_release: app.focus_widget(root.node)

<StatusNavBarSeparator>:
    text: '>'
    font_size: '10pt'
    width: (self.texture_size[0+dp(20))
    size_hint_x: None

""")

class StatusNavBarButton(Button):
    '''StatusNavBarButton is a :class:`~kivy.uix.button` representing
       the Widgets in the Widget hierarchy of currently selected widget.
    '''
    node = ObjectProperty()

class StatusNavBarSeparator(Label):
    '''StatusNavBarSeparator :class:`~kivy.uix.label.Label`
       Used to separate two Widgets by '>'
    '''
    pass

class StatusNavbar(BoxLayout):
    pass

class StatusMessage(BoxLayout):

    message = StringProperty('')
    '''Message visible on the status bar
       :data:`message` is an
       :class:`~kivy.properties.StringProperty` and defaults to ''
    '''
    icon = StringProperty('')
    '''Message icon path
       :data:`icon` is an
       :class:`~kivy.properties.StringProperty` and defaults to ''
    '''
    img = ObjectProperty(None)
    '''Instance of notification type icon
        :data:`img` is an
       :class:`~kivy.properties.ObjectProperty` and defaults to None
    '''
    def show_message(self, message, duration=5, notification_type=None):
        self.message = message
        icon = ''
        if notification_type == 'info':
            icon = icons('info')
        elif notification_type == 'error':
            icon = icons('error')
        elif notification_type == 'loading':
            icon = icons('loading', '.gif')

        if icon:
            self.img.opacity = 1
            self.img.source = icon
        else:
            self.img.opacity = 0
        
        if duration > 0:
            Clock.schedule_once(self.clear_message, duration)

    def clear_message(self, *args):
        self.img.opacity = 0
        self.message = ''

class StatusInfo(BoxLayout):

    message = StringProperty('')
    '''Message visible on the status bar
       :data:`message` is an
       :class:`~kivy.properties.StringProperty` and defaults to ''
    '''
    info = StringProperty('')
    '''Info visible on the status bar
       :data:`info` is an
       :class:`~kivy.properties.StringProperty` and defaults to ''
    '''
    branch = StringProperty('')
    '''Branch name visible on the status bar
       :data:`branch` is an
       :class:`~kivy.properties.StringProperty` and defaults to ''
    '''
    def update_info(self, info, branch_name=None):
        template = info
        if branch_name is not None:
            self.branch = branch_name

        if self.branch:
            template += f' | {self.branch}'
        self.message = template

class StatusBar(BoxLayout):
    '''StatusBar used to display Widget hierarchy of currently selected
       widget and to display messages.
    '''
    app = ObjectProperty()
    '''Reference to current app instance.
       :data:`app` is an
       :class:`~kivy.properties.ObjectProperty`
    '''
    navbar = ObjectProperty()
    '''To be used as parent of
        :class:`~designer.components.statusbar.StatusNavBarButton`
       and :class:`~designer.components.statusbar.StatusNavBarSeparator`.
       :data:`navbar` is an
       :class:`~kivy.properties.ObjectProperty`
    '''
    status_message = ObjectProperty()
    '''Instance of :class:`~designer.components.statusbar.StatusMessage`
       :class:`~kivy.properties.ObjectProperty`
    '''
    status_info = ObjectProperty()
    '''Instance of :class:`~designer.components.statusbar.StatusInfo`
       :class:`~kivy.properties.ObjectProperty`
    '''
    playground = ObjectProperty()
    '''Instance of
       :data:`playground` is an
       :class:`~kivy.properties.ObjectProperty`
    '''
    __events__ = ('on_message_press', 'on_info_press', )

    def __init__(self, **kwargs):
        super(StatusBar, self).__init__(**kwargs)
        self.update_navbar = Clock.create_trigger(self._update_navbar)
        self.update_nav_size = Clock.create_trigger(self._update_content_width)

    def _update_navbar(self, *args):
        '''To update navbar with the parents of currently selected Widget.
        '''
        self.navbar.clear_widgets()
        wid = self.app.widget_focused
        if not wid:
            self.update_nav_size()
            return None

        # get parent list, until app.root.playground.root
        children = []
        while wid:
            if wid in {self.playground.sandbox, self.playground.sandbox.children[0]}:
                break

            if isinstance(wid, TabbedPanelContent):
                _wid = wid
                wid = wid.parent.current_tab
                children.append(StatusNavBarButton(node=wid))
                wid = _wid.parent

            elif isinstance(wid, TabbedPanelHeader):
                children.append(StatusNavBarButton(node=wid))
                _wid = wid
                while _wid and not isinstance(_wid, TabbedPanel):
                    _wid = _wid.parent
                wid = _wid

            children.append(StatusNavBarButton(node=wid))
            wid = wid.parent

        count = len(children)
        for index, child in enumerate(reversed(children)):
            self.navbar.add_widget(child)
            if index < count - 1:
                self.navbar.add_widget(StatusNavBarSeparator())
            else:
                child.state = 'down'

    def on_app(self, instance, app, *args):
        app.bind(widget_focused=self._update_navbar)

    def _update_content_width(self, *args):
        '''Updates the statusbar's children sizes to save space
        '''
        nav = self.navbar.parent
        nav_c = self.navbar.children
        mes = self.status_message
        if nav_c == 0:
            mes.size_hint_x = 0.9
            nav.size_hint_x = None
            nav.width = 0
        elif mes.message:
            mes.size_hint_x = 0.4
            nav.size_hint_x = 0.5
        elif not mes.message:
            mes.size_hint_x = None
            mes.width = 0
            nav.size_hint_x = 0.9

    def show_message(self, message, duration=5, notification_type=None, *args):
        '''Shows a message. Use type to change the icon and the duration
        in seconds. Set duration = -1 to undefined time
        :param notification_type: types: info, error, loading
        :param duration: notification duration in seconds
        :param message: message to display
        '''
        self.status_message.show_message(message, duration, notification_type)

    def update_info(self, info, branch_name=None):
        '''Updates the info message
        '''
        self.status_info.update_info(info, branch_name)

    def on_message_press(self, *args):
        '''Event handler to message widget touch down
        '''
        pass

    def on_info_press(self, *args):
        '''Event handler to info widget touch down
        '''
        pass
