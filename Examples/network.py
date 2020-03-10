from pygame import Color

from core.agent import Agent
from core.gui import BLOCK_SPACING, HOR_SEP, SCREEN_PIXEL_HEIGHT, SCREEN_PIXEL_WIDTH
from core.link import hash_object, Link, link_exists
from core.pairs import Pixel_xy
from core.sim_engine import SimEngine
import core.utils as utils
from core.world_patch_block import World

from random import choice, uniform

class Network_Agent(Agent):
    def __init__(self):
        pass

class Network_World(World):
    def __init__(self):
        pass

    def setup_clear(self):
        pass
        #clear_all
        #set_current_plot
        #set_default_shape
        #reset_ticks

# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

""" 
The following appears at the top-left of the window. 
It puts a row consisting of a Text widgit and a ComboBox above the widgets from on_off.py
"""
#ca _left_upper will need
#setup button and Clear button (use undirected links on set up)
#Layout:spring "sould be continual as in the forces and effects example
#generators  (make sure to clear before generating, No need for user input
#number_nodes 1-20
#style (preferential, attachment, ring, star)
#wheel "find out what a wheel model is and generate one"
#random
ca_left_upper = [[sg.Text('stuff')]]


###example###
# ca_left_upper = [[sg.Text('Initial row:'),
#                   sg.Combo(values=['Left', 'Center', 'Right', 'Random'], key='init', default_value='Right')],
#                  [sg.Text('Rows:'), sg.Text('     0', key='rows')],
#                  HOR_SEP(30)] + \
#                  on_off_left_upper

# The switches are CheckBoxes with keys from CA_World.bin_0_to_7 (in reverse).
# These are the actual GUI widgets, which we access via their keys.
# The pos_to_switch dictionary maps position values in the rule number as a binary number
# to these widgets. Each widget corresponds to a position in the rule number.
# Note how we generate the text for the chechboxes.
# switches = [sg.CB(n + '\n 1', key=n, pad=((30, 0), (0, 0)), enable_events=True)
#                                              for n in reversed(CA_World.bin_0_to_7)]

""" 
This  material appears above the screen: 
the rule number slider, its binary representation, and the switches.
"""
# ca_right_upper = [[sg.Text('Rule number', pad=((100, 0), (20, 10))),
#                    sg.Slider(key='Rule_nbr', range=(0, 255), orientation='horizontal',
#                              enable_events=True, pad=((10, 20), (0, 10))),
#                    sg.Text('00000000 (binary)', key='bin_string', enable_events=True, pad=((0, 0), (10, 0)))],
#
#                   switches
#                   ]


if __name__ == "__main__":
    """
    Run the CA program. PyLogo is defined at the bottom of core.agent.py.
    """
    from core.agent import PyLogo

    # Note that we are using OnOffPatch as the Patch class. We could define CA_Patch(OnOffPatch),
    # but since it doesn't add anything to OnOffPatch, there is no need for it.
    # PyLogo(Network_World, '1D CA', patch_class=OnOffPatch,
    #        gui_left_upper=ca_left_upper, gui_right_upper=ca_right_upper,
    #        fps=10, patch_size=3, board_rows_cols=(CA_World.ca_display_size, CA_World.ca_display_size))
    # PyLogo(Flocking_World, 'Flocking', gui_left_upper, agent_class=Flocking_Agent,
    #        patch_size=9, board_rows_cols=(65, 71), bounce=True)

    #find out if patch size and board rows cols are needed, as well as bounce=true (i think its the thing that lets
    #the world not wrap around
    PyLogo(Network_World, 'Networks', gui_left_upper=None, agent_class=Node_Agent)