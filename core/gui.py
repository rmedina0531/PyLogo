import os
from typing import Tuple, Union

import PySimpleGUI as sg
from math import floor
# By importing this file itself, can avoid the use of globals
# noinspection PyUnresolvedReferences
import core.gui as gui
from core.clock import Clock

# Assumes that all Blocks are square with side BLOCK_SIDE and one pixel between them.
# PATCH_SIZE should be odd so that there is a center pixel: (HALF_PATCH_SIZE(), HALF_PATCH_SIZE()).
# Assumes that the upper left corner is at (relative) (0, 0).
# If PATCH_SIZE == 3, then HALF_PATCH_SIZE() == 3//2 == 1, and center pixel == (1, 1)
PATCH_SIZE = 11


# BOARD_SHAPE is the shape of the board
PATCH_ROWS = 51
PATCH_COLS = 51

CIRCLE = 'circle'
NETLOGO_FIGURE = 'netlogo_figure'
NODE = 'node'
SQUARE = 'square'
STAR = 'star'

FPS = 'fps'
GO = 'go'
GO_ONCE = 'go once'
GOSTOP = 'GoStop'

# Since it's used as a default value, can't be a list. A tuple works just as well.

# SHAPES = {NETLOGO_FIGURE: ((1, 1), (0.5, 0), (0, 1), (0.5, 3/4)),
#           SQUARE: ((1, 1), (1, 0), (0, 0), (0, 1)),
#           STAR: ((1, 1), (0, 0), (0.5, 0.5), (0, 1), (1, 0), (0.5, 0.5), (0, 0.5), (1, 0.5), (0.5, 0.5),
#                    (0.5, 0), (0.5, 1), (0.5, 0.5)),
#           }
#redifined to make the shape around a center pixel at 0,0
#add polygon functionality to draw and shapes

SHAPES = {SQUARE: (-.5, -5, .5, .5),
          NETLOGO_FIGURE: (.5,.5,0,-.5,-.5,.5,0,.25)
          }

KNOWN_FIGURES = sorted(list(SHAPES.keys()) + [CIRCLE, NODE])


# def polygon(sides):
#     points = []
#     arc = 2*math.pi/sides
#     for i in range(sides):
#         angle = i*arc + math.pi/4
#         xy = ((math.cos(angle), math.sin(angle)) + (0.5, 0.5)).round(2)
#         points.append(xy)
#     # print(sides, points)
#     return points
#
#
def BLOCK_SPACING():
    return PATCH_SIZE + 1


def HALF_PATCH_SIZE():
    return PATCH_SIZE//2



def HOR_SEP(length=25, pad=((0, 0), (0, 0))):
    return [sg.Text('_' * length, text_color='black', pad=pad)]



def SCREEN_PIXEL_WIDTH():
    """
    Includes pixel x coordinates range(SCREEN_PIXEL_WIDTH())
    """
    return PATCH_COLS * BLOCK_SPACING() + 1


def SCREEN_PIXEL_HEIGHT():
    """
    Includes pixel y coordinates range(SCREEN_PIXEL_HEIGHT())
    """
    return PATCH_ROWS * BLOCK_SPACING() + 1


FPS_VALUES = values = [1, 3, 6, 10, 15, 25, 40, 60]


# def gui_set(key, **kwargs):
#     """
#     Widgets typically have a 'disabled' property. The following makes
#     it possible to use 'enabled' as the negation of 'disabled'.
#     """
#     if 'enabled' in kwargs:
#         value = kwargs.get('enabled')
#         kwargs['disabled'] = not bool(value)
#         kwargs.pop('enabled')
#     widget = WINDOW[key]
#     widget.update(**kwargs)
#

# def set_fps(val):
#     # Select the value in FPS_VALUES closest to val.
#     new_val = min(FPS_VALUES, key=lambda v: abs(v - val))
#     gui_set(gui.FPS, value=new_val)
#     return new_val


# The WINDOW variable will be available to refer to the WINDOW object from elsewhere in the code.
# Neither the WINDOW nor the SCREEN can be imported directly because imports occur before they are created.
WINDOW: sg.PySimpleGUI.Window


def draw(agent, shape_name):
    if shape_name in [CIRCLE, NODE]:
        radius = round(BLOCK_SPACING()/2)*agent.scale if shape_name == 'circle' else 3
        # pg.draw.circle(gui.SCREEN, agent.color, agent.center_pixel.as_int(), int(radius), 0)
        #return the ID so the agent associated with the drawn shape has a reference to its ID on the GRAPH
        return gui.GRAPH.DrawCircle(agent.center_pixel.as_int(), int(radius), fill_color=agent.color)
    elif shape_name is SQUARE:
        return gui.GRAPH.DrawRectangle(*list(map(lambda x: x*agent.scale, SHAPES[SQUARE])), fill_color=agent.color)
    elif shape_name in SHAPES:
        #draw the polygon around the center pixel
        #make a list of the points of the polygon scaled to the desired image size
        #simple gui does not have a create polygon so the canvas inside graph was used to create it.
        return gui.GRAPH.TKCanvas.create_polygon(*list(map(lambda x: x*agent.scale, SHAPES[shape_name])), fill=agent.color)
    else:
        print(f"Don't know how to draw a {shape_name}.")

def draw_patch(agent):
    return gui.GRAPH.DrawRectangle((agent.center_pixel.x - floor(gui.PATCH_SIZE/2), agent.center_pixel.y - floor(gui.PATCH_SIZE/2)),
                                   (agent.center_pixel.x + floor(gui.PATCH_SIZE/2), agent.center_pixel.y + floor(gui.PATCH_SIZE/2)),
                                   fill_color=agent.color)


def draw_label(label, text_center, obj_center, line_color, background='white'):
    label_ID = {}
    label_ID['text_id'] = gui.GRAPH.DrawText(label, text_center)
    # line_color = Color('white') if isinstance(self, Patch) and self.color == Color('black') else self.color
    if line_color is not None:
        # gui.draw_line(start_pixel=obj_center, end_pixel=text_center, line_color=line_color)
        label_ID['line_id'] = gui.draw_line(obj_center, text_center, line_color=line_color)

    return label_ID


def draw_line(start_pixel, end_pixel, line_color='white', width=1):
    # line(gui.SCREEN, line_color, start_pixel, end_pixel, width)
    gui.GRAPH.DrawLine(start_pixel, end_pixel, color=line_color, width=width)

def set_properties(agent, **kwargs):
    gui.GRAPH.TKCanvas.itemconfig(agent.image_id, **kwargs)

class SimpleGUI:

    def __init__(self, gui_left_upper, gui_right_upper=None, caption="Basic Model",
                 patch_size=15, board_rows_cols=(51, 51), clear=None, bounce=None, fps=None):

        gui.PATCH_SIZE = patch_size if patch_size % 2 == 1 else patch_size + 1
        gui.PATCH_ROWS = board_rows_cols[0] if board_rows_cols[0] % 2 == 1 else board_rows_cols[0] + 1
        gui.PATCH_COLS = board_rows_cols[1] if board_rows_cols[1] % 2 == 1 else board_rows_cols[1] + 1

        self.EXIT = 'Exit'

        #check to see if this was being used anywhere
        self.GRAPH = '-GRAPH-'
        self.SETUP = 'setup'
        self.STOP = 'Stop'

        self.clock = Clock()

        self.caption = caption

        self.screen_shape_width_height = (SCREEN_PIXEL_WIDTH(), SCREEN_PIXEL_HEIGHT())

        # All these gui.<variable> elements are globals in this file.
        gui.WINDOW = self.make_window(caption, gui_left_upper, gui_right_upper=gui_right_upper,
                                      clear=clear, bounce=bounce, fps=fps)
        # pg.init()
        # gui.FONT = SysFont(None, int(1.5 * gui.BLOCK_SPACING()))

        # All graphics are drawn to gui.SCREEN, which is a global variable.
        # gui.SCREEN = pg.display.set_mode(self.screen_shape_width_height)

    # @staticmethod
    # def fill_screen():
        # gui.SCREEN.fill(pg.Color(gui.SCREEN_COLOR))
        # gui.SCREEN.fill(pg.Color('green'))

    def make_window(self, caption, gui_left_upper, gui_right_upper=None, clear=None, bounce=True, fps=None):
        """
        Create the window, including sg.Graph, the drawing surface.
        """
        # --------------------- PySimpleGUI window layout and creation --------------------
        clear_line = [] if clear is None else \
                     [sg.Checkbox('Clear before setup?', key='Clear?', default=clear, pad=((0, 0), (10, 0)),
                                  tooltip='Bounce back from the edges of the screen?')]

        bounce_checkbox_line = [] if bounce is None else \
                               [sg.Checkbox('Bounce?', key='Bounce?', default=bounce, pad=((20, 0), (10, 0)),
                                            tooltip='Bounce back from the edges of the screen?')]

        clear_line += bounce_checkbox_line

        # Always an fps combo box, but make it visible only if the user specifies such a box.
        # The box is necessary to allow the program to set fps even if the end user doesn't
        fps_combo_line = [sg.Text('Frames/second', tooltip='The maximum frames/second.', visible=bool(fps),
                                  pad=((0, 10), (17, 0))),
                          sg.Combo(key=gui.FPS, values=FPS_VALUES, tooltip='The maximum frames/second.',
                                   default_value=fps, visible=bool(fps), pad=((0, 0), (17, 0)), enable_events=True)
                          ]

        setup_go_line = [
            sg.Button(self.SETUP, pad=((0, 10), (10, 0))),
            sg.Button(gui.GO_ONCE, disabled=True, button_color=('white', 'green'), pad=((0, 10), (10, 0))),
            sg.Button(gui.GO, disabled=True, button_color=('white', 'green'), pad=((0, 30), (10, 0)),
                      key=gui.GOSTOP)   ]


        exit_button_line = [sg.Exit(button_color=('white', 'firebrick4'), key=self.EXIT, pad=((0, 0), (10, 0))),
                            sg.Checkbox('Grab anywhere', key='Grab', default=False, pad=((40, 0), (10, 0)))]

        col1 = [ *gui_left_upper,
                 gui.HOR_SEP(),
                 setup_go_line,
                 clear_line,
                 fps_combo_line,
                 gui.HOR_SEP(),
                 exit_button_line
                 ]

        lower_left_pixel_xy = (0, self.screen_shape_width_height[1]-1)
        upper_right_pixel_xy = (self.screen_shape_width_height[0]-1, 0)

        if gui_right_upper is None:
            gui_right_upper = [[]]

        # graph is a drawing area, a screen on which the model is portrayed, i.e., the patches and the agents.
        # It consists mainly of a TKCanvas.
        gui.GRAPH = sg.Graph(self.screen_shape_width_height, lower_left_pixel_xy, upper_right_pixel_xy,
                         background_color='grey', key='-GRAPH-', enable_events=True, drag_submits=True)
        col2 = gui_right_upper + [[gui.GRAPH]]

        # layout is the actual layout of the window. The stuff above organizes it into component parts.
        # col1 is the control buttons, sliders, etc.
        # col2 is the graph plus whatever the user wants to put above it.
        # layout is a single "GUI line" with these two components in sequence.
        layout = [[sg.Column(col1), sg.Column(col2)]]

        # window is a window with that layout.
        window = sg.Window(caption, layout, margins=(5, 20), use_default_focus=False, grab_anywhere=False,
                           return_keyboard_events=True, finalize=True)


        return window
