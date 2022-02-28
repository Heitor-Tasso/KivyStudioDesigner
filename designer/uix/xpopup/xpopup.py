"""
https://github.com/kivy-garden/garden.xpopup.git

XPopup class
============

 The :class:`XPopup` is the extension for the :class:`~kivy.uix.popup.Popup`
class. Implements methods for limiting minimum size of the popup and fit popup
to the app's window.

 By default, the minimum size is not set. It can be changed via setting value
of an appropriate properties (see documentation below).

.. warning::
    * Normalization is applied once (when using the :meth:`XPopup.open`)

    * The first normalization is performed on the minimum size, and then - fit
      to app's window. In this case, if the specified minimum size is greater
      than the size of the app's window - it will be ignored.


Examples
--------
This example creates a simple popup with specified minimum size::

    popup = XPopup(size_hint=(.4, .3), min_width=400, min_height=300)
    popup.open()

If actual size of popup less than minimum size, :attr:`size_hint` will be
normalized. For example: assume the size of app window is 500x500, in this case
popup will had size 200x150. But we set a minimum size, so :attr:`size_hint`
for this popup will be recalculated and set to (.8, .6)

 By default, if you set the popup size in pixels, which will exceed the size
of the app window, the popup will go out of app's window bounds.
If you don't want that, you can set :attr:`fit_to_window` to True (popup will
be normalized to the size of the app window)::

    popup = XPopup(size=(1000, 1000), size_hint=(None, None),
                   fit_to_window=True)
    popup.open()
"""

from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.popup import Popup

__author__ = 'ophermit'

__all__ = ['XPopup', ]

class XPopup(Popup):
    """XPopup class. See module documentation for more information.
    """

    min_width = NumericProperty(None, allownone=True)
    '''Minimum width of the popup.

    :attr:`min_width` is a :class:`~kivy.properties.NumericProperty` and
    defaults to None.
    '''
    min_height = NumericProperty(None, allownone=True)
    '''Minimum height of the popup.

    :attr:`min_height` is a :class:`~kivy.properties.NumericProperty` and
    defaults to None.
    '''
    fit_to_window = BooleanProperty(False)
    '''This property determines if the pop-up larger than app window is
    automatically fit to app window.

    :attr:`fit_to_window` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False.
    '''

    def _norm_value(self, pn_value, pn_hint, pn_min, pn_max):
        """Normalizes one value

        :param pn_value: original value (width or height)
        :param pn_hint: original `size hint` (x or y)
        :param pn_min: minimum limit for the value
        :param pn_max: maximum limit for the value
        :return: tuple of normalized parameters (value, `size hint`)
        """
        norm_hint = pn_hint
        norm_value = pn_value

        if pn_min is not None and norm_value < pn_min:
            norm_value = pn_min
            norm_hint = (pn_min/float(pn_max))

        if self.fit_to_window:
            if norm_value > pn_max:
                norm_value = pn_max
            if norm_hint is not None and norm_hint > 1:
                norm_hint = 1.0

        return (norm_value, norm_hint)

    def _norm_size(self):
        """Applies the specified parameters
        """
        win_size = self.get_root_window().size[:]
        popup_size = self.size[:]

        norm_x = self._norm_value(
            popup_size[0], self.size_hint_x,
            self.min_width, win_size[0])

        norm_y = self._norm_value(
            popup_size[1], self.size_hint_y,
            self.min_height, win_size[1])
        
        self.width = norm_x[0]
        self.height = norm_y[0]
        self.size_hint = (norm_x[1], norm_y[1])

        # DON`T REMOVE OR FOUND AND FIX THE ISSUE
        # if `size_hint` is not specified we need to recalculate position
        # of the popup
        if (norm_x[1], norm_y[1]) == (None, None) and self.size != popup_size:
            self.property('size').dispatch(self)

    def open(self, *largs):
        super(XPopup, self).open(*largs)
        self._norm_size()
