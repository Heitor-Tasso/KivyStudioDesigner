'''
Needed to get colors and sizes of DesignerStudio
'''

from kivy.lang.builder import Builder
from kivy.utils import get_color_from_hex

def hex(he):
    return get_color_from_hex(he)


Builder.load_string("""

#:set bgcolor (0.06, 0.07, 0.08)
#:set bordercolor (0.54, 0.59, 0.60)
#:set titlecolor (0.34, 0.39, 0.40)

#
# Helper for keeping a consistency across the whole designer UI
#

# Rules:
# - rows height are 48sp
# - padding is 4sp
# - spacing is 4sp
# - button / label / widget are 40sp height
# - TextInput with a single line is 30sp height
# - modal with just one button(close, cancel, etc). The button must be in the left
# - menu item width is 250
# - in conditional modals, more positive action in the right

#:set designer_height '40sp'
#:set designer_spacing '4sp'
#:set designer_padding '4sp'
#:set designer_text_input_height '30sp'
#:set designer_action_width dp(200)

""")
