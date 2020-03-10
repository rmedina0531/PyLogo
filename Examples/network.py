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
    def nothing(self):
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
SETUP_CLEAR = 'setup_clear'
LINKS_TO_USE = 'links_to_use'
LAYOUT = 'layout'
LAYOUT_ONCE = 'layout_once'
LAYOUT_TYPE = 'layout_type'
CLEAR_BEFORE_GENERATION = 'clear_before_generation'
PREFERENTIAL_ATTACHMENT = 'preferential_attachment'
RING = 'ring'
STAR = 'star'
WHEEL = 'wheel'
SPOKES_DIRECTION = 'spokes_direction'
RANDOM = 'random'
CONNECTION_PROB = 'connection_prob'
NEIGHBORHOOD_SIZE = 'neighborhood_size'
SMALL_WORLD = 'small_world'
REWIRE_PROB = 'rewire_prob'
#ca _left_upper will need
#setup button and Clear button (use undirected links on set up)
#Layout:spring "sould be continual as in the forces and effects example
#generators  (make sure to clear before generating, No need for user input
#number_nodes 1-20
#style (preferential, attachment, ring, star)
#wheel "find out what a wheel model is and generate one"
#random
ca_left_upper = [[sg.Button(SETUP_CLEAR), sg.Text('Links to Use'), sg.Combo(values=['directed', 'undirected'],
                                                   key=LINKS_TO_USE, default_value='undirected')],
                 [sg.Button(LAYOUT), sg.Button(LAYOUT_ONCE), sg.Text('Layout'),
                  sg.Combo(values=['spring', 'circle', 'radial', 'tutte'], key=LAYOUT_TYPE, default_value='spring')],
                 [sg.Text('Generators'), sg.CB(CLEAR_BEFORE_GENERATION, default=True)],
                 HOR_SEP(30, pad=((0, 0), (0, 0))),
                 [sg.Button(PREFERENTIAL_ATTACHMENT), sg.Button(RING), sg.Button(STAR)],
                 [sg.Button(WHEEL), sg.Text('Spokes Direction'),
                  sg.Combo(values=['outward', 'inward'], key=SPOKES_DIRECTION, default_value='outward')],
                 [sg.Button(RANDOM), sg.Text('# Nodes'),
                  sg.Slider(key=CONNECTION_PROB, resolution=.01, default_value= .2, orientation='horizontal')],
                 HOR_SEP(30, pad=((0, 0), (0, 0))),
                 [sg.Text('Neighborhood Size'),
                  sg.Slider(key=NEIGHBORHOOD_SIZE, resolution=1, default_value=3, orientation='horizontal', range=(0,20))],
                 [sg.Button(SMALL_WORLD)],
                 [sg.Text('Rewire Prob'),
                  sg.Slider(key=REWIRE_PROB, resolution=.01, default_value=.1, orientation='horizontal', range=(0,1))]]


""" 
This  material appears above the screen: 
the rule number slider, its binary representation, and the switches.
"""


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
    PyLogo(Network_World, 'Networks', gui_left_upper=ca_left_upper, agent_class=Network_Agent, patch_size=9,
           board_rows_cols=(65, 71), bounce=True)