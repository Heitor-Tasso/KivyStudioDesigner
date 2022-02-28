"""
Module file.py
==============

.. versionadded:: 0.2

This module contains the class which represents
:class:`~kivy.uix.filechooser.FileChooser` in the popup and some templates
for this class.

Classes:

* XFilePopup: represents :class:`~kivy.uix.filechooser.FileChooser` in the
  popup.

* XFolder: :class:`XFilePopup` template for folder selection.

* XFileOpen: :class:`XFilePopup` template for files selection.

* XFileSave: :class:`XFilePopup` template for save file.


XFilePopup class
================

Subclass of :class:`xpopup.XBase`.
This class represents :class:`~kivy.uix.filechooser.FileChooser` in the
popup with following features:

* label which shows current path

* buttons which allows you to select view mode (icon/list)

* button `New folder`

Usage example::

    popup = XFilePopup(title='XFilePopup demo', buttons=['Select', 'Close'])

To set path on the filesystem that this controller should refer to, you can
use :attr:`XFilePopup.path`. The same property you should use to get the
selected path in your callback.

By default it possible to select only one file. If you need to select multiple
files, set :attr:`XFilePopup.multiselect` to True.

By default it possible to select files only. If you need to select the
files and folders, set :attr:`XFilePopup.dirselect` to True.

To obtain selected files and/or folders you need just use
:attr:`XFilePopup.selection`.

You can add custom preview filters via :attr:`XFilePopup.filters`

Following example shows how to use properties::

    def my_callback(instance):
        print(u'Path: ' + instance.path)
        print(u'Selection: ' + str(instance.selection))

    from os.path import expanduser
    popup = XFilePopup(title='XFilePopup demo', buttons=['Select', 'Close'],
                       path=expanduser(u'~'), on_dismiss=my_callback,
                       multiselect=True, dirselect=True)


XFolder class
=============

Subclass of :class:`xpopup.XFilePopup`.
This class is a template with predefined property values for selecting
the folders. He also checks the validity of the selected values. In this case,
selection is allowed only folders.

By default the folder selection is disabled. It means that the folder cannot be
selected because it will be opened by one click on it. In this case the
selected folder is equal to the current path.

By the way, the folder selection is automatically enabled when you set
:attr:`XFilePopup.multiselect` to True. But in this case the root folder
cannot be selected.


XFileOpen class
===============

Subclass of :class:`xpopup.XFilePopup`.
This class is a template with predefined property values for selecting
the files. He also checks the validity of the selected values. In this case,
selection is allowed only files.


XFileSave class
===============

Subclass of :class:`xpopup.XFilePopup`.
This class is a template with predefined property values for entering name of
file which will be saved.
It contains the :class:`~kivy.uix.textinput.TextInput` widget for input
filename.

To set a default value in the TextInput widget, use :attr:`XFileSave.filename`.
Also this property can be used to get the file name entered.

To get full filename (including path), use :meth:`XFileSave.get_full_name`.

Following example shows how to use properties::

    def my_callback(instance):
        print(u'Path: ' + instance.path)
        print(u'Filename: ' + instance.filename)
        print(u'Full name: ' + instance.get_full_name())

    popup = XFileSave(filename='file_to_save.txt', on_dismiss=my_callback)

"""

from kivy import metrics
from kivy.factory import Factory
from kivy.lang.builder import Builder
from textwrap import dedent
from kivy.properties import (
    StringProperty, NumericProperty,
    ListProperty, OptionProperty,
    BooleanProperty, ObjectProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

from os import path, makedirs

try:
    from .tools import gettext_ as _
    from .xbase import XBase
    from .notification import XError
    from .form import XTextInput
except:
    from tools import gettext_ as _
    from xbase import XBase
    from notification import XError
    from form import XTextInput

__author__ = 'ophermit'

__all__ = ('XFileSave', 'XFileOpen', 'XFolder')


class XFilePopup(XBase):
    """XFilePopup class. See module documentation for more information.
    """

    size_hint_x = NumericProperty(1., allownone=True)
    size_hint_y = NumericProperty(1., allownone=True)
    '''Default size properties for the popup
    '''

    browser = ObjectProperty(None)
    '''This property represents the FileChooser object. The property contains
    an object after creation :class:`xpopup.XFilePopup` object.
    '''

    path = StringProperty(u'/')
    '''Initial path for the browser.

    Binded to :attr:`~kivy.uix.filechooser.FileChooser.path`
    '''

    selection = ListProperty()
    '''Contains the selection in the browser.

    Binded to :attr:`~kivy.uix.filechooser.FileChooser.selection`
    '''

    multiselect = BooleanProperty(False)
    '''Binded to :attr:`~kivy.uix.filechooser.FileChooser.multiselect`
    '''

    dirselect = BooleanProperty(False)
    '''Binded to :attr:`~kivy.uix.filechooser.FileChooser.dirselect`
    '''

    filters = ListProperty()
    '''Binded to :attr:`~kivy.uix.filechooser.FileChooser.filters`
    '''

    CTRL_VIEW_ICON = 'icon'
    CTRL_VIEW_LIST = 'list'
    CTRL_NEW_FOLDER = 'new_folder'

    view_mode = OptionProperty(
        CTRL_VIEW_ICON, options=(CTRL_VIEW_ICON, CTRL_VIEW_LIST))
    '''Binded to :attr:`~kivy.uix.filechooser.FileChooser.view_mode`
    '''

    def _get_body(self):
        from kivy.lang import Builder
        import textwrap
        self.browser = Builder.load_string(textwrap.dedent('''\
        FileChooser:
            FileChooserIconLayout
            FileChooserListLayout
        '''))

        self.browser.path = self.path
        self.browser.multiselect = self.multiselect
        self.browser.dirselect = self.dirselect
        self.browser.filters = self.filters
        self.browser.bind(path=self.setter('path'),
                          selection=self.setter('selection'))
        self.bind(view_mode=self.browser.setter('view_mode'),
                  multiselect=self.browser.setter('multiselect'),
                  dirselect=self.browser.setter('dirselect'),
                  filters=self.browser.setter('filters'))

        lbl_path = Factory.XLabel(
            text=self.browser.path, valign='top', halign='left',
            size_hint_y=None, height=metrics.dp(25))
        self.browser.bind(path=lbl_path.setter('text'))

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self._ctrls_init())
        layout.add_widget(lbl_path)
        layout.add_widget(self.browser)
        return layout

    def _ctrls_init(self):
        btn = Factory.XButton
        pnl_controls = BoxLayout(size_hint_y=None, height=metrics.dp(25))
        pnl_controls.add_widget(btn(text=_('Icons'),on_release=self._ctrls_click))
        pnl_controls.add_widget(btn(text=_('List'), on_release=self._ctrls_click))
        pnl_controls.add_widget(btn(text=_('New folder'), on_release=self._ctrls_click))
        return pnl_controls

    def _ctrls_click(self, instance):
        try:
            value = instance.id
        except Exception:
            value = instance.text
        
        if value in self.property('view_mode').options:
            self.view_mode = value
        elif value == self.CTRL_NEW_FOLDER:
            XTextInput(title=_('Input folder name'),
                       text=_('New folder'),
                       on_dismiss=self._create_dir)

    def _create_dir(self, instance):
        """Callback for create a new folder.
        """
        if instance.is_canceled():
            return
        new_folder = self.path + path.sep + instance.get_value()
        if path.exists(new_folder):
            XError(text=_('Folder "%s" is already exist. Maybe you should '
                          'enter another name?') % instance.get_value())
            return True
        makedirs(new_folder)
        self.browser.property('path').dispatch(self.browser)

    def _filter_selection(self, folders=True, files=True):
        """Filter the list of selected objects

        :param folders: if True - folders will be included in selection
        :param files: if True - files will be included in selection
        """
        if folders and files:
            return

        t = []
        for entry in self.selection:
            if entry == '..' + path.sep:
                pass
            elif folders and self.browser.file_system.is_dir(entry):
                t.append(entry)
            elif files and not self.browser.file_system.is_dir(entry):
                t.append(entry)
        self.selection = t


class XFileSave(XFilePopup):
    """XFileSave class. See module documentation for more information.
    """

    BUTTON_SAVE = _('Save')
    TXT_ERROR_FILENAME = _('Maybe you should enter a filename?')

    filename = StringProperty(u'')
    '''Represents entered file name. Can be used for setting default value.
    '''

    title = StringProperty(_('Save file'))
    '''Default title for the popup
    '''

    buttons = ListProperty([BUTTON_SAVE, XFilePopup.BUTTON_CANCEL])
    '''Default button set for the popup
    '''

    def _get_body(self):
        txt = TextInput(
            text=self.filename, multiline=False,
            size_hint_y=None, height=metrics.dp(30)
        )
        txt.bind(text=self.setter('filename'))
        self.bind(filename=txt.setter('text'))

        layout = super(XFileSave, self)._get_body()
        layout.add_widget(txt)
        return layout

    def on_selection(self, *largs):
        if len(self.selection) == 0:
            return

        if not self.browser.file_system.is_dir(self.selection[0]):
            self.filename = self.selection[0].split(path.sep)[-1]

    def dismiss(self, *largs, **kwargs):
        """Pre-validation before closing.
        """
        if self.button_pressed == self.BUTTON_SAVE:
            if self.filename == '':
                # must be entered filename
                XError(text=self.TXT_ERROR_FILENAME)
                return self

        return super(XFileSave, self).dismiss(*largs, **kwargs)

    def get_full_name(self):
        """Returns full filename (including path)
        """
        return self.path + path.sep + self.filename


class XFileOpen(XFilePopup):
    """XFileOpen class. See module documentation for more information.
    """

    BUTTON_OPEN = _('Open')
    TXT_ERROR_SELECTION = _('Maybe you should select a file?')

    title = StringProperty(_('Open file'))
    '''Default title for the popup
    '''

    buttons = ListProperty([BUTTON_OPEN, XFilePopup.BUTTON_CANCEL])
    '''Default button set for the popup
    '''

    def dismiss(self, *largs, **kwargs):
        """Pre-validation before closing.
        """
        if self.button_pressed == self.BUTTON_OPEN:
            self._filter_selection(folders=False)
            if len(self.selection) == 0:
                # files must be selected
                XError(text=self.TXT_ERROR_SELECTION)
                return self
        return super(XFileOpen, self).dismiss(*largs, **kwargs)


class XFolder(XFilePopup):
    """XFolder class. See module documentation for more information.
    """

    BUTTON_SELECT = _('Select')
    TXT_ERROR_SELECTION = _('Maybe you should select a folders?')

    title = StringProperty(_('Choose folder'))
    '''Default title for the popup
    '''

    buttons = ListProperty([BUTTON_SELECT, XFilePopup.BUTTON_CANCEL])
    '''Default button set for the popup
    '''

    def __init__(self, **kwargs):
        super(XFolder, self).__init__(**kwargs)
        # enabling the folder selection if multiselect is allowed
        self.filters.append(self._is_dir)
        if self.multiselect:
            self.dirselect = True

    def _is_dir(self, directory, filename):
        return self.browser.file_system.is_dir(path.join(directory, filename))

    def dismiss(self, *largs, **kwargs):
        """Pre-validation before closing.
        """
        if self.button_pressed == self.BUTTON_SELECT:
            if not self.multiselect:
                # setting current path as a selection
                self.selection = [self.path]

            self._filter_selection(files=False)
            if len(self.selection) == 0:
                # folders must be selected
                XError(text=self.TXT_ERROR_SELECTION)
                return self
        return super(XFolder, self).dismiss(*largs, **kwargs)
