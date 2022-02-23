# xpopup
Kivy (http://kivy.org) extensions

Usefull extensions of the `kivy.uix.popup.Popup` class.


Features
========

* `XPopup` - extension for the :class:`~kivy.uix.popup.Popup`. Implements methods
  for limiting minimum size of the popup and fit popup to the app's window.
  For more information, see `xpopup.py`.

* `XBase` - subclass of `XPopup`, the base class for all popup extensions.
  Supports an easy way to add a set of buttons to the popup. Use it to create
  your own popup extensions. For more information, see `xbase.py`.

* `XNotifyBase` - the base class for notifications. Implements the popup with a
  label. Use it to create your own notifications. For more information, see
  `notification.py`. Subclasses: 

    - `XNotification` - a popup that closes automatically after a time limit.

    - `XMessage`, `XError`, `XConfirmation` - templates for often used notifications.

    - `XProgress` - a popup with progress bar.
    
    - `XLoading` - a popup with a gif image.

* `XForm` - a simple basis for the UI-forms creation. For more information,
  see `form.py`. Subclasses:

    - `XSlider` - a popup with a slider.

    - `XTextInput` - a popup for editing singleline text.
    
    - `XNotes` - a popup for editing multiline text.

    - `XAuthorization` - a simple authorization form.

* `XFilePopup` - a popup for file system browsing. For more information,
  see `file.py`. Subclasses:

    - `XFileOpen` - a popup for selecting the files.
    
    - `XFileSave` - a popup for saving file. 
    
    - `XFolder` - a popup for selecting the folders.


Demo
====

To see a demonstration, you need to perform one of the following: 

* Install `Kivy` library (https://kivy.org/#download) and execute `demo_app.py`

* Install `Kivy Launcher` on your Android device and copy this package by following these instructions:
  https://kivy.org/docs/guide/packaging-android.html#packaging-your-application-for-the-kivy-launcher
  (files `main.py` and `android.txt` already in package)
  
* Just watch the video: https://youtu.be/UX8gCyEg2J8


Version history
===============

* 0.3.1

    **XFilePopup.filters** - new property, binded to `kivy.uix.filechooser.FileChooser.filters`
    
    XFolder now shows only folders

* 0.3.0

    Added support for localization. For more information, see `tools.py`.
    
    Added support for custom labels and buttons. For more information, see `tools.py`.

    Added <b>XLoading</b> - shows a 'loading.gif' in the popup

* 0.2.3

    <b>XForm.required_fields</b> - new property, list of required fields

    <b>XNotes.lines</b> - new property, default text for the TextInput as list
    of strings
        
    <b>XSlider.title_template</b> - new property, formatted string for display
    the slider's value in the title.
        
    XAuthorization.autologin - now supports 'None' (to hide checkbox)
    
    XForm.get_value() - fixed bug (exception in Python 3.x)

* 0.2.2
    
    Added support for python 3.x

* 0.2.1
    
    XNotifyBase - added checkbox 'Do not show this message again'
    
    XProgress.complete() now takes optional parameters: text (for custom
    message) and show_time (for custom time-to-close)
    
    <b>XProgress.autoprogress()</b> - new method which starting infinite progress
    increase in the separate thread

* 0.2
    
    Added <b>XFilePopup, XFileOpen, XFileSave, XFolder</b> (classes of the popup for
    file system browsing).
    
    Some minor changes.

* 0.1
    
    Initial release
