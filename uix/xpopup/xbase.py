"""
XBase class
============

Subclass of :class:`xpopup.XPopup`.
Base class for all popup extensions. Don't use this class directly.

Examples
--------

How to create your own class based on :class:`XBase`? It's easy!

The content of the popup should be implemented in the :meth:`XBase._get_body`::

    class MyPopup(XBase):
        def _get_body(self):
            return Label(text='Hello World!')
    popup = MyPopup()

By default, popup will automatically opened when the instance was created.
If you don't want that, you can set :attr:`auto_open` to False::

    popup = MyPopup(auto_open=False)

If you want to add buttons to the popup, just use :attr:`buttons`::

    popup = MyPopup(buttons=[MyPopup.BUTTON_OK, MyPopup.BUTTON_CANCEL])

Pressing the button will trigger the 'dismiss' event. The button that was
pressed, can be obtained from the :attr:`button_pressed`. You can use it
in your callback::

    def my_callback(instance):
        print('Button "', instance.button_pressed, '" was pressed.')
    popup = MyPopup(auto_open=False, buttons=['Ok', 'Cancel'])
    popup.bind(on_dismiss=my_callback)
    popup.open()

If you include a XBase.BUTTON_CANCEL in your set of buttons, then you can
use :meth:`XBase.is_canceled` to check if it was pressed::

    def my_callback(instance):
        if instance.is_canceled():
            print('Popup was canceled.')
        else:
            print('Button "', instance.button_pressed, '" was pressed.')

"""

from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from kivy.metrics import dp

from kivy.properties import (
    ListProperty, StringProperty,
    NumericProperty, ObjectProperty,
)

from .tools import gettext_
from .xpopup import XPopup

__author__ = 'ophermit'

__all__ = ['XBase', ]

class XBase(XPopup):
    """XBase class. See module documentation for more information.
    """

    auto_open = ObjectProperty(True)
    '''This property determines if the pop-up is automatically
    opened when the instance was created. Otherwise use :meth:`XBase.open`

    :attr:`auto_open` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to True.
    '''

    buttons = ListProperty()
    '''List of button names. Can be used when using custom button sets.

    :attr:`buttons` is a :class:`~kivy.properties.ListProperty` and defaults to
    [].
    '''

    button_pressed = StringProperty('')
    '''Name of button which has been pressed.

    :attr:`button_pressed` is a :class:`~kivy.properties.StringProperty` and
    defaults to '', read-only.
    '''

    size_hint_x = NumericProperty(.6, allownone=True)
    size_hint_y = NumericProperty(.3, allownone=True)
    auto_dismiss = False
    '''Overrides properties from :class:`~kivy.uix.popup.Popup`
    '''

    min_width = NumericProperty(dp(300), allownone=True)
    min_height = NumericProperty(dp(150), allownone=True)
    fit_to_window = True
    '''Overrides properties from :class:`XPopup`
    '''

    BUTTON_OK = gettext_('Ok')
    BUTTON_CANCEL = gettext_('Cancel')
    BUTTON_YES = gettext_('Yes')
    BUTTON_NO = gettext_('No')
    BUTTON_CLOSE = gettext_('Close')
    '''Basic button names
    '''

    def __init__(self, **kwargs):
        # preventing change content of the popup
        kwargs.pop('content', None)
        self._pnl_buttons = None
        super(XBase, self).__init__(**kwargs)

        layout = BoxLayout(orientation="vertical")
        layout.add_widget(self._get_body())
        self._pnl_buttons = BoxLayout(size_hint_y=None)
        layout.add_widget(self._pnl_buttons)
        self.add_widget(layout)

        # creating buttons panel
        self.property('buttons').dispatch(self)

        if self.auto_open:
            self.open()

    def _on_click(self, instance):
        self.button_pressed = instance.text
        self.dismiss()

    def _get_body(self):
        """Returns the content of the popup. You need to implement
        this in your subclass.
        """
        raise NotImplementedError

    def on_buttons(self, instance, buttons):
        if self._pnl_buttons is None:
            return

        self._pnl_buttons.clear_widgets()
        if len(buttons) == 0:
            self._pnl_buttons.height = 0
            return

        self._pnl_buttons.height = dp(30)
        for button in buttons:
            self._pnl_buttons.add_widget(
                Factory.XButton(text=button, on_release=self._on_click)
            )

    def is_canceled(self):
        """Check the `cancel` event

        :return: True, if the button 'Cancel' has been pressed
        """
        return self.button_pressed == self.BUTTON_CANCEL
