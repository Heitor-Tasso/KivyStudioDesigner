"""
Module tools.py
==============

.. versionadded:: 0.3.0

This module contains configuration functions.


Localization
============

To apply custom messages you need create your own 'xpopup.mo' file using
existing template ('xpopup.pot'). Then place an 'xpopup.mo' file into the
package folder. Or place it wherever you want and add the following code BEFORE
the first occurrence of xpopup imports::

    from kivy.config import Config
    Config.add_section('xpopup')
    Config.set('xpopup', 'locale_file', '/your_path_to/xpopup.mo')


Custom objects
==============

If you want to use self-designed label or button classes, you need to set base
classes via 'configure' function::

    class MyLabel(Label):
        .....

    class MyButton(Button):
        .....

    from garden.xpopup import configure
    configure(cls_label=MyLabel, cls_button=MyButton)

"""
import gettext
from kivy.compat import PY2
from kivy.config import Config
from kivy.factory import Factory
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.label import Label

__author__ = 'ophermit'

__all__ = ('configure', )


def configure(cls_label=None, cls_button=None):
    """ Sets custom objects
    :param cls_label: class for Label
    :param cls_button: class for Button
    """
    if cls_label:
        _register_class('XLabel', cls_label)
    if cls_button:
        _register_class('XButton', cls_button)


def _register_class(cls_name, cls):
    if cls_name in Factory.classes:
        Factory.unregister(cls_name)
    Factory.register(cls_name, cls=cls)


def _setup_locale():
    """ Setting up localization
    :return: translation method
    """
    try:
        locale_file = Config.get('xpopup', 'locale_file')
    except:
        from os.path import abspath, dirname, join
        locale_file = join(dirname(abspath(__file__)), 'xpopup.mo')

    try:
        with open(locale_file, "rb") as f:
            xpopup_locale = gettext.GNUTranslations(f)
        Logger.info('Localization file loaded (%s).' % locale_file)
    except Exception as e:
        Logger.warning('%s: %s. Switch to the defaults.' %
                       (e.__class__.__name__, str(e)))
        xpopup_locale = gettext.NullTranslations()

    if PY2:
        return xpopup_locale.ugettext
    else:
        return xpopup_locale.gettext


class XLabelBehavior(object):
    """Specifies a label behavior - sets text area size to the widget's bounds.
    """

    def __init__(self, **kwargs):
        defaults = {
            'valign': 'middle',
            'halign': 'center',
            'padding': (3, 3)
        }
        defaults.update(kwargs)
        super(XLabelBehavior, self).__init__(**defaults)
        self.bind(size=self.setter('text_size'))


class XLabel(XLabelBehavior, Label):
    pass


class XButton(XLabelBehavior, Button):
    pass


gettext_ = _setup_locale()
configure(cls_label=XLabel, cls_button=XButton)
