"""
Module notification.py
======================

This module contains the base class for all notifications. Also
subclasses which implement some the base notifications functionality.

Classes:

* XNotifyBase: Base class for all notifications.

* XMessage: Notification with predefined button set (['Ok'])

* XError: XMessage with predefined title

* XConfirmation: Notification with predefined button set (['Yes', 'No'])

* XNotification: Notification without buttons. Can autoclose after few
  seconds.

* XProgress: Notification with ProgressBar


XNotifyBase class
=================

Subclass of :class:`xpopup.XBase`.
The base class for all notifications. Also you can use this class to create
your own notifications::

    XNotifyBase(title='You have a new message!', text='What can i do for you?',
                buttons=['Open it', 'Mark as read', 'Remind me later'])

Or that way::

    class MyNotification(XNotifyBase):
        buttons = ListProperty(['Open it', 'Mark as read', 'Remind me later'])
        title = StringProperty('You have a new message!')
        text = StringProperty('What can i do for you?')
    popup = MyNotification()

.. note:: :class:`XMessage` and :class:`XError` classes were created in a
    similar manner. Actually, it is just a subclasses with predefined default
    values.

Similarly for the :class:`XConfirmation` class. The difference - it has
:meth:`XConfirmation.is_confirmed` which checks which button has been
pressed::

    def my_callback(instance):
        if instance.is_confirmed():
            print('You are agree')
        else:
            print('You are disagree')
    popup = XConfirmation(text='Do you agree?', on_dismiss=my_callback)

.. versionadded:: 0.2.1
    :attr:`XNotifyBase.dont_show_value`
    :attr:`XNotifyBase.dont_show_text`
    See documentation below.


XNotification class
===================

Subclass of :class:`xpopup.XNotifyBase`.
This is an extension of :class:`XNotifBase`. It has no buttons and can
be closed automatically::

    XNotification(text='This popup will disappear after 3 seconds',
                  show_time=3)

If you don't want that, you can ommit :attr:`XNotification.show_time` and
use :meth:`XNotification.dismiss`::

    popup = XNotification(text='To close it, use the Force, Luke!')
    def close_popup():
        popup.dismiss()


XProgress class
===============

Subclass of :class:`xpopup.XNotifyBase`.
Represents :class:`~kivy.uix.progressbar.ProgressBar` in a popup. Properties
:attr:`XProgress.value` and :attr:`XProgress.max` is binded to an
appropriate properties of the :class:`~kivy.uix.progressbar.ProgressBar`.

How to use it? Following example will create a `XProgress` object which has
a title, a text message, and it displays 50% of progress::

    popup = XProgress(value=50, text='Request is being processed',
                      title='Please wait')

There are two ways to update the progress line.
First way: simply assign a value to indicate the current progress::

    # update progress to 80%
    popup.value = 80

Second way: use :meth:`XProgress.inc`. This method will increase current
progress by specified number of units::

    # reset progress
    popup.value = 0
    # increase by 10 units
    popup.inc(10)
    # increase by 1 unit
    popup.inc()

By the way, if the result value exceeds the maximum value, this method is
"looping" the progress. For example::

    # init progress
    popup = XProgress(value=50)
    # increase by 60 units - will display 10% of the progress
    popup.inc(60)

This feature is useful when it is not known the total number of iterations.
Also in this case, a useful method is :meth:`XProgress.complete`. It sets the
progress to 100%, hides the button(s) and automatically closes the popup
after 2 seconds::

    # init progress
    popup = XProgress(value=50)
    # complete the progress
    popup.complete()

.. versionadded:: 0.2.1
    You can change the text and time-to-close using following parameters::

        popup.complete(text='', show_time=0)

    In that case, the popup will be closed immediately.

.. versionadded:: 0.2.1
    :meth:`XProgress.autoprogress` starts infinite progress increase in the
    separate thread i.e. you don't need to increase it manually. Will be
    stopped automatically when the :meth:`XProgress.complete` or
    :meth:`XProgress.dismiss` is called.


XLoading class
===============

.. versionadded:: 0.3.0

Subclass of :class:`xpopup.XBase`.
Shows a 'loading.gif' in the popup.

Following example will create a `XLoading` object using custom title and
image::

    popup = XLoading(title='Your_title', gif='/your_path_to/loading.gif')

"""

from os.path import join
from kivy import metrics, kivy_data_dir
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import ListProperty, StringProperty, NumericProperty,\
    BoundedNumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
try:
    from .tools import gettext_ as _
    from .xbase import XBase
except:
    from tools import gettext_ as _
    from xbase import XBase

__author__ = 'ophermit'


class XNotifyBase(XBase):
    """XNotifyBase class. See module documentation for more information.
    """

    text = StringProperty('')
    '''This property represents text on the popup.

    :attr:`text` is a :class:`~kivy.properties.StringProperty` and defaults to
    ''.
    '''

    dont_show_text = StringProperty(_('Do not show this message again'))
    '''Use this property if you want to use custom text instead of
    'Do not show this message'.

    :attr:`text` is a :class:`~kivy.properties.StringProperty`.
    '''

    dont_show_value = BooleanProperty(None, allownone=True)
    '''This property represents a state of checkbox 'Do not show this message'.
    To enable checkbox, set this property to True or False.

    .. versionadded:: 0.2.1

    :attr:`dont_show_value` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to None.
    '''

    def __init__(self, **kwargs):
        self._message = Factory.XLabel(text=self.text)
        self.bind(text=self._message.setter('text'))
        super(XNotifyBase, self).__init__(**kwargs)

    def _get_body(self):
        if self.dont_show_value is None:
            return self._message
        else:
            pnl = BoxLayout(orientation='vertical')
            pnl.add_widget(self._message)

            pnl_cbx = BoxLayout(
                size_hint_y=None, height=metrics.dp(35), spacing=5)
            cbx = CheckBox(
                active=self.dont_show_value, size_hint_x=None,
                width=metrics.dp(50))
            cbx.bind(active=self.setter('dont_show_value'))
            pnl_cbx.add_widget(cbx)
            pnl_cbx.add_widget(
                Factory.XLabel(text=self.dont_show_text, halign='left'))

            pnl.add_widget(pnl_cbx)
            return pnl


class XNotification(XNotifyBase):
    """XNotification class. See module documentation for more information.
    """

    show_time = BoundedNumericProperty(0, min=0, max=100, errorvalue=0)
    '''This property determines if the pop-up is automatically closed
    after `show_time` seconds. Otherwise use :meth:`XNotification.dismiss`

    :attr:`show_time` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 0.
    '''

    def open(self, *largs):
        super(XNotification, self).open(*largs)
        if self.show_time > 0:
            Clock.schedule_once(self.dismiss, self.show_time)


class XMessage(XNotifyBase):
    """XMessageBox class. See module documentation for more information.
    """

    buttons = ListProperty([XNotifyBase.BUTTON_OK])
    '''Default button set for class
    '''


class XError(XMessage):
    """XErrorBox class. See module documentation for more information.
    """

    title = StringProperty(_('Something went wrong...'))
    '''Default title for class
    '''


class XConfirmation(XNotifyBase):
    """XConfirmation class. See module documentation for more information.
    """

    buttons = ListProperty([XNotifyBase.BUTTON_YES, XNotifyBase.BUTTON_NO])
    '''Default button set for class
    '''

    title = StringProperty(_('Confirmation'))
    '''Default title for class
    '''

    def is_confirmed(self):
        """Check the `Yes` event

        :return: True, if the button 'Yes' has been pressed
        """
        return self.button_pressed == self.BUTTON_YES


class XProgress(XNotifyBase):
    """XProgress class. See module documentation for more information.
    """

    buttons = ListProperty([XNotifyBase.BUTTON_CANCEL])
    '''Default button set for class
    '''

    max = NumericProperty(100.)
    value = NumericProperty(0.)
    '''Properties that are binded to the same ProgressBar properties.
    '''

    def __init__(self, **kwargs):
        self._complete = False
        self._progress = ProgressBar(max=self.max, value=self.value)
        self.bind(max=self._progress.setter('max'))
        self.bind(value=self._progress.setter('value'))
        super(XProgress, self).__init__(**kwargs)

    def _get_body(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(super(XProgress, self)._get_body())
        layout.add_widget(self._progress)
        return layout

    def complete(self, text=_('Complete'), show_time=2):
        """
        Sets the progress to 100%, hides the button(s) and automatically
        closes the popup.

        .. versionchanged:: 0.2.1
        Added parameters 'text' and 'show_time'

        :param text: text instead of 'Complete', optional
        :param show_time: time-to-close (in seconds), optional
        """
        self._complete = True
        n = self.max
        self.value = n
        self.text = text
        self.buttons = []
        Clock.schedule_once(self.dismiss, show_time)

    def inc(self, pn_delta=1):
        """
        Increase current progress by specified number of units.
         If the result value exceeds the maximum value, this method is
         "looping" the progress

        :param pn_delta: number of units
        """
        self.value += pn_delta
        if self.value > self.max:
            # create "loop"
            self.value = self.value % self.max

    def autoprogress(self, pdt=None):
        """
        .. versionadded:: 0.2.1

        Starts infinite progress increase in the separate thread
        """
        if self._window and not self._complete:
            self.inc()
            Clock.schedule_once(self.autoprogress, .01)


class XLoading(XBase):
    """XLoading class. See module documentation for more information.

    .. versionadded:: 0.3.0
    """
    gif = StringProperty(join(kivy_data_dir, 'images', 'image-loading.gif'))
    '''Represents a path to an image.
    '''

    title = StringProperty(_('Loading...'))
    '''Default title for class
    '''

    size_hint_x = NumericProperty(None, allownone=True)
    size_hint_y = NumericProperty(None, allownone=True)
    width = NumericProperty(metrics.dp(350))
    height = NumericProperty(metrics.dp(200))
    '''Default size properties for the popup
    '''

    def _get_body(self):
        return Image(source=self.gif, anim_delay=.1)
