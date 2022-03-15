__all__ = ['DesignerCodeInput', ]

from utils.utils import get_current_project, get_designer, show_alert

from kivy import Config
from kivy.uix.codeinput import CodeInput
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty, ObjectProperty

import re
from pygments import styles

class DesignerCodeInput(CodeInput):
    '''A subclass of CodeInput to be used for KivyDesigner.
       It has copy, cut and paste functions, which otherwise are accessible
       only using Keyboard.
       It emits on_show_edit event whenever clicked, this is catched
       to show EditContView;
    '''
    __events__ = ('on_show_edit',)

    saved = ObjectProperty(True)
    '''Indicates if the current file is saved or not
        :data:`saved` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to True
    '''
    error = ObjectProperty(False)
    '''Indicates if the current file contains any type of error
        :data:`error` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to False
    '''
    path = StringProperty('')
    '''Path of the current file
        :data:`path` is a :class:`~kivy.properties.StringProperty`
    and defaults to ''
    '''
    clicked = ObjectProperty(False)
    '''If clicked is True, then it confirms that this widget has been clicked.
       The one checking this property, should set it to False.
       :data:`clicked` is a :class:`~kivy.properties.BooleanProperty`
    '''

    def __init__(self, name='', **kwargs):
        super(DesignerCodeInput, self).__init__(**kwargs)
        parser = Config.get_configparser('DesignerSettings')
        if parser:
            cal_names = ('global', 'code_input_theme')
            parser.add_callback(self.on_codeinput_theme, *cal_names)
            self.style_name = parser.getdefault(*cal_names, 'emacs')

    def on_codeinput_theme(self, section, key, value, *args):
        if not value in styles.get_all_styles():
            show_alert("Error", "This theme is not available")
        else:
            self.style_name = value

    def on_style_name(self, *args):
        super(DesignerCodeInput, self).on_style_name(*args)
        self.background_color = get_color_from_hex(self.style.background_color)
        self._trigger_refresh_text()

    def on_show_edit(self, *args):
        pass

    def on_touch_down(self, touch):
        '''Override of CodeInput's on_touch_down event.
           Used to emit on_show_edit
        '''
        if self.collide_point(*touch.pos):
            self.clicked = True
            self.dispatch('on_show_edit')

        return super(DesignerCodeInput, self).on_touch_down(touch)

    def do_focus(self, *args):
        '''Force the focus on this widget
        '''
        self.focus = True

    def on_text(self, *args):
        '''Listen text changes
        '''
        if not self.focus:
            return None
        
        self.saved = False
        get_current_project().saved = False

    def find_next(self, search, use_regex=False, case=False):
        '''Find the next occurrence of the string according to the cursor
        position
        '''
        text = self.text
        if not case:
            text = text.upper()
            search = search.upper()
        
        lines = text.splitlines()
        col = self.cursor_col
        row = self.cursor_row

        found = -1
        size = 0  # size of string before selection
        line = None
        search_size = len(search)

        for i, line in enumerate(lines):
            size += len(line)
            if i < row:
                continue
            
            if use_regex:
                line_find = line[col + 1:] if i == row else line[:]
                found = re.search(search, line_find)
                if found:
                    search_size = len(found.group(0))
                    found = found.start()
                else:
                    found = -1
            else:
                # if on current line, consider col
                if i == row:
                    found = line.find(search, col + 1)
                else:
                    found = line.find(search)
            # has found the string. found variable indicates the initial po
            if found != -1:
                self.cursor = (found, i)
                break

        if found != -1:
            pos = (text.find(line)+found)
            self.select_text(pos, (pos+search_size))

    def find_prev(self, search, use_regex=False, case=False):
        '''Find the previous occurrence of the string according to the cursor
        position
        '''
        text = self.text
        if not case:
            text = text.upper()
            search = search.upper()

        lines = text.splitlines()
        col = self.cursor_col
        row = self.cursor_row
        lines = lines[:row + 1]
        lines.reverse()
        line_number = len(lines)

        found = -1
        line = None
        search_size = len(search)

        for i, line in enumerate(lines):
            i = (line_number-i-1)
            if use_regex:
                line_find = line[:col] if i == row else line[:]
                found = re.search(search, line_find)
                if found:
                    search_size = len(found.group(0))
                    found = found.start()
                else:
                    found = -1
            else:
                # if on current line, consider col
                if i == row:
                    found = line[:col].find(search)
                else:
                    found = line.find(search)
            # has found the string. found variable indicates the initial po
            if found != -1:
                self.cursor = (found, i)
                break

        if found != -1:
            pos = text.find(line) + found
            self.select_text(pos, pos + search_size)
