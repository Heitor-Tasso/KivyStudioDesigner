Kivy Studio Designer
=============

Kivy Studio Designer is Kivy's tool for designing graphical user interfaces
(GUIs) from Kivy Widgets. You can compose and customize widgets, and
test them. It is completely written in Python using Kivy.

Original project -> http://github.com/kivy/kivy-designer/

Prerequisites
-------------

- [Kivy >= 3.9.7](http://kivy.org/#download)
- The following Python modules (available via pip):
    - [watchdog](https://pythonhosted.org/watchdog/)
    - [pygments](http://pygments.org/)
    - [docutils](http://docutils.sourceforge.net/)
    - [jedi](http://jedi.jedidjah.ch/en/latest/)
    - [gitpython](http://gitpython.readthedocs.org)
    - [six](https://pythonhosted.org/six/)

Installation
------------

To install the prerequisites, enter a console (on Windows use kivy.bat in the kivy folder):

    pip install -U watchdog pygments docutils jedi gitpython six

or simple run:

    pip install -Ur requirements.txt

With the prerequisites installed, you can use the designer:

    git clone https://github.com/SrGambiarra/KivyStudioDesigner/

or download it manually from https://github.com/kivy/kivy-designer/archive/refs/heads/master.zip

On OS X you might need to use the `kivy` command instead of `python` if you are using our portable package.

If you're successful, you'll see something like this:

![ScreenShot](https://raw.github.com/kivy/kivy-designer/master/kivy_designer.png)

License
-------

Kivy Studio Designer is released under the terms of the MIT License. Please refer to the
LICENSE file.
