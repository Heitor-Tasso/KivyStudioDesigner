__all__ = [
    'DesignerActionSubMenu', 'ActionCheckButton',
    'DesignerActionProfileCheck', 'DesignerActionGroup',
    'DesignerSubActionButton', 'DesignerActionButton',]

from uix.contextual import ContextSubMenu

from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.actionbar import ActionButton, ActionGroup, ActionItem
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty

import weakref

Builder.load_string("""

<DesignerActionButton>:
    info: info
    background_normal: 'atlas://data/images/defaulttheme/action_bar'
    size_hint_x: None
    width: designer_action_width
    canvas.before:
        Color:
            rgba: [1, 1, 1, 0.5] if self.disabled else [1, 1, 1, 1]
        Rectangle:
            pos: self.pos
            size: self.size
            source: self.background_normal
    Label:
        pos: root.pos
        text_size: (self.width - sp(24), self.size[1])
        valign: 'middle'
        size_hint_y: None
        height: '40sp'
        text: root.text
    Label:
        id: info
        text: root.hint
        pos: root.pos
        size: root.size
        opacity: 0.5
        text_size: self.size
        valign: 'bottom'
        halign: 'right'
        padding: '5dp', '5dp'

<DesignerActionSubMenu>:
    text_size: (self.width - sp(24), self.size[1])
    valign: 'middle'
    size_hint_y: None
    height: '40sp'
    width: designer_action_width

<ActionCheckButton>:
    btn_layout: btn_layout
    _label: _label
    checkbox: checkbox
    background_normal: 'atlas://data/images/defaulttheme/action_bar'
    size_hint: None, None
    height: '49sp'
    width: designer_action_width
    canvas.before:
        Color:
            rgba: [1, 1, 1, 1]
        Rectangle:
            pos: self.pos
            size: self.size
            source: self.background_normal
    BoxLayout:
        id: btn_layout
        pos: root.pos
        padding: [dp(5), 0, dp(5), 0]
        spacing: '10dp'
        CheckBox:
            id: checkbox
            size_hint_x: None
            width: '20sp'
            pos: [root.x+dp(2), root.y]
            active: root.checkbox_active
            group: root.group
            allow_no_selection: root.allow_no_selection
            on_active: root.dispatch('on_active', *args)
        Label:
            id: _label
            text_size: self.size
            valign: 'middle'
            text: root.text
    Label:
        id: info
        text: root.desc
        pos: root.pos
        size: root.size
        opacity: 0.3
        text_size: self.size
        valign: 'bottom'
        halign: 'right'
        padding: dp(5), dp(5)

<DesignerSubActionButton>:
    size_hint: 1, None
    width: designer_action_width
    height: '48sp'
    background_normal: 'atlas://data/images/defaulttheme/action_bar'
    text_size: (self.width - sp(24), self.size[1])
    valign: 'middle'

<DesignerActionGroup>:
    mode: 'spinner'
    size_hint_x: None
    dropdown_cls: ContextMenu

""")

class DesignerActionSubMenu(ContextSubMenu, ActionButton):
    pass


class ActionCheckButton(ActionItem, FloatLayout):
    '''ActionCheckButton is a check button displaying text with a checkbox
    '''

    checkbox = ObjectProperty(None)
    '''Instance of :class:`~kivy.uix.checkbox.CheckBox`.
       :data:`checkbox` is a :class:`~kivy.properties.ObjectProperty`
    '''

    _label = ObjectProperty(None)
    '''Instance of :class:`~kivy.uix.label.Label`.
       :data:`_label` is a :class:`~kivy.properties.ObjectProperty`
    '''

    text = StringProperty('Check Button')
    '''text which is displayed by ActionCheckButton.
       :data:`text` is a :class:`~kivy.properties.StringProperty`
    '''

    desc = StringProperty('')
    '''text which is displayed as description to ActionCheckButton.
       :data:`desc` is a :class:`~kivy.properties.StringProperty` and defaults
       to ''
    '''

    btn_layout = ObjectProperty(None)
    '''Instance of :class:`~kivy.uix.boxlayout.BoxLayout`.
       :data:`_label` is a :class:`~kivy.properties.ObjectProperty`
    '''

    checkbox_active = BooleanProperty(True)
    '''boolean indicating the checkbox.active state
        :data:`active` is a :class:`~kivy.properties.BooleanProperty`
    '''

    group = ObjectProperty(None)
    '''Checkbox group
    :data:`group` is a :class:`~kivy.properties.ObjectProperty`
    '''

    allow_no_selection = BooleanProperty(True)
    '''This specifies whether the checkbox in group allows
        everything to be deselected.
    :data:`allow_no_selection` is a :class:`~kivy.properties.BooleanProperty`
    '''

    cont_menu = ObjectProperty(None)

    __events__ = ('on_active', )

    def on_touch_down(self, touch):
        '''Override of its parent's on_touch_down, used to reverse the state
           of CheckBox.
        '''
        if not self.disabled and self.collide_point(*touch.pos):
            self.checkbox._toggle_active()

    def on_active(self, instance, value, *args):
        '''Default handler for 'on_active' event.
        '''
        self.checkbox_active = value


class DesignerActionProfileCheck(ActionCheckButton):
    '''DesignerActionSubMenuCheck a
    :class `~designer.uix.actioncheckbutton.ActionCheckButton`
    It's used to create radio buttons to action menu
    '''
    config_key = StringProperty('')
    '''Dict key to the profile config_parser
       :data:`config_key` is a :class:`~kivy.properties.StringProperty`,
       default to ''.
    '''

class DesignerActionGroup(ActionGroup):

    to_open = BooleanProperty(False)
    '''To keep check of whether to open the dropdown list or not.
    :attr:`to_open` is a :class:`~kivy.properties.BooleanProperty`,
    defaults to False.
    '''
    hovered = BooleanProperty(False)
    '''To keep check of hover over each instance of DesignerActionGroup.
    :attr:`hovered` is a :class:`~kivy.properties.BooleanProperty`,
    defaults to False.
    '''
    instances = []
    '''List to keep the instances of DesignerActionGroup.
    '''

    def __init__(self, **kwargs):
        super(DesignerActionGroup, self).__init__(**kwargs)
        self.__class__.instances.append(weakref.proxy(self))
        self.register_event_type('on_enter')  # Registering the event
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        try:
            pos = args[1]
            inside_actionbutton = self.collide_point(*pos)
            if self.hovered == inside_actionbutton:
                # If mouse is hovering inside the group then return.
                return None
            self.hovered = inside_actionbutton
            if inside_actionbutton:
                self.dispatch('on_enter')
        except:
            return None

    def on_touch_down(self, touch):
        '''Used to determine where touch is down and to change values
        of to_open.
        '''
        if self.collide_point(touch.x, touch.y):
            DesignerActionGroup.to_open = True
            return super(DesignerActionGroup, self).on_touch_down(touch)

        if not self.is_open:
            DesignerActionGroup.to_open = False

    def on_enter(self):
        '''Event handler for on_enter event
        '''
        if not self.disabled:
            if all(instance.is_open is False for instance in
                    DesignerActionGroup.instances):
                DesignerActionGroup.to_open = False
            for instance in DesignerActionGroup.instances:
                if instance.is_open:
                    instance._dropdown.dismiss()
            if DesignerActionGroup.to_open is True:
                self.is_open = True
                self._toggle_dropdown()

class DesignerSubActionButton(ActionButton):

    def __init__(self, **kwargs):
        super(DesignerSubActionButton, self).__init__(**kwargs)

    def on_press(self):
        if self.cont_menu:
            self.cont_menu.dismiss()

class DesignerActionButton(ActionItem, ButtonBehavior, FloatLayout):
    '''DesignerActionButton is a ActionButton to the ActionBar menu
    '''

    text = StringProperty('Button')
    '''text which is displayed in the DesignerActionButton.
       :data:`text` is a :class:`~kivy.properties.StringProperty` and defaults
       to 'Button'
    '''

    hint = StringProperty('')
    '''text which is displayed as description to DesignerActionButton.
       :data:`hint` is a :class:`~kivy.properties.StringProperty` and defaults
       to ''
    '''
    cont_menu = ObjectProperty(None)

    def on_press(self, *args):
        '''
        Event to hide the ContextualMenu when a ActionButton is pressed
        '''
        if self.cont_menu is not None:
            self.cont_menu.dismiss()
