from pygame import Color

from core.agent import Agent
import core.gui as gui
from core.gui import BLOCK_SPACING, HOR_SEP, SCREEN_PIXEL_HEIGHT, SCREEN_PIXEL_WIDTH
from core.link import hash_object, Link, link_exists
from core.pairs import Pixel_xy, Velocity
from core.sim_engine import SimEngine
import core.utils as utils
from core.world_patch_block import World
from core.link import Link, link_exists
import random
from random import choice, randint, sample, uniform
from math import sqrt
from core.utils import normalize_dxdy
from pygame.draw import circle

class Network_Node(Agent):

    def __init__(self, heading=0, not_center=True, radius=100, **kwargs):
        # shape_name = SimEngine.gui_get('shape')
        # color = SimEngine.gui_get('color')
        # color = Color(color) if color != 'Random' else None
        super().__init__(**kwargs)


        #set heading angle, 0-360
        self.set_heading(heading)

        #if it is a center node keep it centered else move it out of the center at that heading
        self.forward(radius if not_center else 0)

        # If there are any (other) agents, create links to them with probability 0.25.
        # agents = World.agents - {self}
        # if agents:
        #     self.make_links(agents)
        # # Has the node been selected for shortest path?
        self.highlighted = False

    def __str__(self):
        return f'FLN-{self.id}'

    def adjust_distances(self, velocity_adjustment):
        #get from gui what the base distance units
        # dist_unit = SimEngine.gui_get(('dist_unit'))
        dist_unit = 10

        #define how many distance units exist per screen
        screen_distance_unit = sqrt(SCREEN_PIXEL_WIDTH()**2 + SCREEN_PIXEL_HEIGHT()**2)/dist_unit

        #define initial Veolocity as (0,0), forces act in the x and y directions
        repulsive_force: Velocity = Velocity((0, 0))

        #for all other agents excluding this instance
        for agent in (World.agents - {self}):
            #add their respective influence of each other element towards this element, calculate using
            #this center pixel, elements center pixel and using defined units (optional repulsove flag)
            repulsive_force += self.force_as_dxdy(self.center_pixel, agent.center_pixel, screen_distance_unit,
                                                    repulsive=True)

        # Also consider repulsive force from walls.
        repulsive_wall_force: Velocity = Velocity((0, 0))

        horizontal_walls = [Pixel_xy((0, 0)), Pixel_xy((SCREEN_PIXEL_WIDTH(), 0))]
        x_pixel = Pixel_xy((self.center_pixel.x, 0))
        for h_wall_pixel in horizontal_walls:
            repulsive_wall_force += self.force_as_dxdy(x_pixel, h_wall_pixel, screen_distance_unit, repulsive=True)

        vertical_walls = [Pixel_xy((0, 0)), Pixel_xy((0, SCREEN_PIXEL_HEIGHT()))]
        y_pixel = Pixel_xy((0, self.center_pixel.y))
        for v_wall_pixel in vertical_walls:
            repulsive_wall_force += self.force_as_dxdy(y_pixel, v_wall_pixel, screen_distance_unit, repulsive=True)

        #calculate the attractive force generated by all the nodes connected by a link
        attractive_force: Velocity = Velocity((0, 0))
        for agent in (World.agents - {self}):
            if link_exists(self, agent):
                attractive_force += self.force_as_dxdy(self.center_pixel, agent.center_pixel, screen_distance_unit,
                                                         repulsive=False)

        #find the final force, find out what velocity adjustment is
        net_force = repulsive_force + repulsive_wall_force + attractive_force
        normalized_force: Velocity = net_force/max([net_force.x, net_force.y, velocity_adjustment])
        normalized_force *= 10

        #print force values if selected
        if SimEngine.gui_get('Print force values'):
            print(f'{self}. \n'
                  f'rep-force {tuple(repulsive_force.round(2))}; \n'
                  f'rep-wall-force {tuple(repulsive_wall_force.round(2))}; \n'
                  f'att-force {tuple(attractive_force.round(2))}; \n'
                  f'net-force {tuple(net_force.round(2))}; \n'
                  f'normalized_force {tuple(normalized_force.round(2))}; \n\n'
                  )

        #set the velocity of this object
        self.set_velocity(normalized_force)
        #take a step
        self.forward()

    def delete(self):
        World.agents.remove(self)
        World.links -= {lnk for lnk in World.links if lnk.includes(self)}

    def draw(self, shape_name=None):
        super().draw(shape_name=shape_name)
        if self.highlighted:
            radius = round((BLOCK_SPACING() / 2) * self.scale * 1.5)
            circle(gui.SCREEN, Color('red'), self.rect.center, radius, 1)

    @staticmethod
    def force_as_dxdy(pixel_a: Pixel_xy, pixel_b: Pixel_xy, screen_distance_unit, repulsive):
        """
        Compute the force between pixel_a pixel and pixel_b and return it as a velocity: direction * force.
        """
        direction: Velocity = normalize_dxdy( (pixel_a - pixel_b) if repulsive else (pixel_b - pixel_a) )
        d = pixel_a.distance_to(pixel_b, wrap=False)
        if repulsive:
            dist = max(1, pixel_a.distance_to(pixel_b, wrap=False) / screen_distance_unit)
            # rep_coefficient = SimEngine.gui_get('rep_coef')
            # rep_exponent = SimEngine.gui_get('rep_exponent')
            #hard coded repulsion and attraction
            rep_coefficient = 1
            rep_exponent = -2

            force = direction * (10**rep_coefficient)/10 * dist**rep_exponent
            return force
        else:  # attraction
            dist = max(1, max(d, screen_distance_unit) / screen_distance_unit)
            # att_exponent = SimEngine.gui_get('att_exponent')
            #hard coded
            att_exponent = 2
            force = direction*dist**att_exponent
            # If the link is too short, push away instead of attracting.
            if d < screen_distance_unit:
                force = force*(-1)
            # att_coefficient = SimEngine.gui_get('att_coef')
            #hard coded
            att_coefficient = 1
            return 10**(att_coefficient-1) * force

    def neighbors(self):
        lns = [(lnk, lnk.other_side(self)) for lnk in World.links if lnk.includes(self)]
        return lns

    def make_links(self, agents):
        """
        Ceate links from self to existing nodes.
        """
        # Put agents (nodes) in random order.
        potential_partners = sample(agents, len(agents))
        # Build a generator that keeps with probability 0.25 potential partners without links to self
        gen = (agent for agent in potential_partners if uniform(0, 1) < 0.25 and not link_exists(self, agent))
        # Create a link with each of these partners.
        for partner in gen:
            Link(self, partner)

    def make_link(self, agent):
        Link(self, agent)



class Network_World(World):
    def __init__(self, patch_class, agent_class):
        self.velocity_adjustment = 1
        super().__init__(patch_class, agent_class)
        # self.shortest_path_links = None
        # self.selected_nodes = set()
        # self.disable_enable_buttons()


    def setup(self):
        self.clear_all()

    def handle_event(self, event):
        events = {RING:self.ring, STAR:self.star, SMALL_WORLD:self.small_world}
        if event in events:
            events[event]()

    def star(self):
        self.setup()
        nodes = self.circle_of_nodes(center=True)

        for n in nodes[1:]:
            nodes[0].make_link(n)

    def ring(self):
        self.setup()
        nodes = self.circle_of_nodes()
        for i in range(len(nodes)):
            if i > len(nodes) -1:
                nodes[i].make_link(nodes[0])
            else:
                nodes[i].make_link(nodes[i+1])

    def circle_of_nodes(self, center=False):
        #TODO
        #number of nodes created is still being shifty
        #create a list of angles for number of nodes
        nbr_nodes = SimEngine.gui_get(NUMBER_NODES)
        nodes = []
        if nbr_nodes == 1:
            nodes.append(self.agent_class())
            return nodes
        if center:
            angles = list(range(0,360, int(360/(nbr_nodes - 1))))
            if len(angles) > (int(nbr_nodes) - 1):
                angles.pop()
            nodes.append(self.agent_class(not_center=False))

        else:
            angles = list(range(0,360, int(360/nbr_nodes)))

        for a in angles:
            nodes.append(self.agent_class(heading=a))

        return nodes

    def small_world(self):
        #clears all the previous stuff
        self.setup()
        #generate a list of nodes arranged by neighbors in a circle
        circle_nodes = self.circle_of_nodes()
        #create the initial connections depending on neighborhood size
        for i in range(len(circle_nodes)):
            for j in range(1, int(SimEngine.gui_get(NEIGHBORHOOD_SIZE)) + 1):
                #makes sure to loop back if over list size
                #only taking into account undirected links
                #make sure to not connect nodes to themselves
                if not link_exists(circle_nodes[i], circle_nodes[(i+j)%len(circle_nodes)]) and \
                        circle_nodes[i] is not circle_nodes[(i+j)%len(circle_nodes)]:
                    Link(circle_nodes[i], circle_nodes[(i+j)%len(circle_nodes)])

        #rewire chance for each link
        #get rewire chance
        rewire_chance = SimEngine.gui_get(REWIRE_PROB)

        old_links = []
        #copy the links
        for l in self.links:
            print(l)
            old_links.append(l)
        for l in old_links:
            # generate random number to see if it gets rewired
            if random.random() < rewire_chance:
                #pick the first node in the link
                # print(str(l.agent_1)+str(l.agent_2))
                # print(len(l.agent_1.all_links()))

                #make random later
                # pick the first node in the link
                # find all the nodes neigbors
                #cosider yourself as a neighbor
                neighbors = [l.agent_1]
                for n_link in l.agent_1.all_links():
                    neighbors.append(n_link.other_side(l.agent_1))

                # print('neighbors of agent' + str(l.agent_1))
                # for i in neighbors:
                #     print(i)
                #for all nodes minus the neighbors
                #show all non neighbors
                # for i in list(self.agents - set(neighbors)):
                #     print(i)

                #check to see if there exists any agent not considered a neighbor
                if len(neighbors) < len(self.agents):
                    new_neighbor = choice(list(self.agents - set(neighbors)))
                    # print(new_neighbor)
                    #remove the current link
                    self.links.remove(l)
                    #create the new link add it to the list of links to ignore
                    Link(l.agent_1, new_neighbor)

    def step(self):
        #enable forces only on spring setup
        if SimEngine.gui_get(LAYOUT_TYPE) == 'spring':
            for node in self.agents:
                node.adjust_distances(self.velocity_adjustment)
        # # Set all the links back to normal.
        # for lnk in World.links:
        #     lnk.color = lnk.default_color
        #     lnk.width = 1
        #
        # self.selected_nodes = [node for node in self.agents if node.highlighted]
        # # If there are exactly two selected nodes, find the shortest path between them.
        # if len(self.selected_nodes) == 2:
        #     self.shortest_path_links = self.shortest_path()
        #     # self.shortest_path_links will be either a list of links or None
        #     # If there is a path, highlight it.
        #     if self.shortest_path_links:
        #         for lnk in self.shortest_path_links:
        #             lnk.color = Color('red')
        #             lnk.width = 2
        #
        # # Update which buttons are enabled.
        # self.disable_enable_buttons()


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
SMALL_WORLD = 'small world'
REWIRE_PROB = 'rewire_prob'
NUMBER_NODES = 'number_of_nodes'
#ca _left_upper will need
#setup button and Clear button (use undirected links on set up)
#Layout:spring "sould be continual as in the forces and effects example
#generators  (make sure to clear before generating, No need for user input
#number_nodes 1-20
#style (preferential, attachment, ring, star)
#wheel "find out what a wheel model is and generate one"
#random
ca_left_upper = [[sg.Text('Links to Use'), sg.Combo(values=['directed', 'undirected'],
                                                   key=LINKS_TO_USE, default_value='undirected')],
                 [sg.Text('Layout'), sg.Combo(values=['spring', 'circle', 'radial', 'tutte'],
                                              key=LAYOUT_TYPE, default_value='spring')],
                 HOR_SEP(30, pad=((0, 0), (0, 0))),
                 [sg.Text(NUMBER_NODES), sg.Slider(key=NUMBER_NODES, resolution=1, default_value=5,
                                                   orientation='horizontal', range=(0,20))],
                 [sg.Button(PREFERENTIAL_ATTACHMENT), sg.Button(RING), sg.Button(STAR)],
                 [sg.Button(WHEEL), sg.Text('Spokes Direction'),
                  sg.Combo(values=['outward', 'inward'], key=SPOKES_DIRECTION, default_value='outward')],
                 [sg.Button(RANDOM), sg.Text('Connection Probability'),
                  sg.Slider(key=CONNECTION_PROB, resolution=1, default_value= 5, orientation='horizontal')],
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
    PyLogo(Network_World, 'Networks', gui_left_upper=ca_left_upper, agent_class=Network_Node, bounce=True)