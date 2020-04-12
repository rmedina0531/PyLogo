from core.gui import PATCH_COLS, PATCH_ROWS
from core.world_patch_block import World, Patch
from core.agent import Agent
from pygame.color import Color
from random import randint
from core.sim_engine import SimEngine
import time

#route definitions
TOP_ROUTE = 0
BOTTOM_ROUTE = 1
BRAESS_ROAD_ROUTE = 2

#road definitions
VARIABLE_CONGESTION = 0
CONSTANT_CONGESTION = 1
BRAESS_ROAD_ENABLED = 2
BRAESS_ROAD_DISABLED = 3

class Braess_Road_Patch(Patch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.road_type = None

    def set_road_type(self, type):
        self.road_type = type

class Commuter(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Braess_Road_World(World):


    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.reset()

    def reset(self):
        self.reset_all()

        self.latest_travel_time = None
        self.latest_top_time = None
        self.latest_middle_time = None

        self.spawn_time = 0
        self.spawn_rate = 30
        self.avg_time = None

        self.cars_spawned = 0

        self.top_prob = None
        self.bottom_prob = None
        self.middle_prob = None

        self.top_left_patch = None
        self.top_right_patch = None
        self.bottom_left_patch = None
        self.bottom_right_patch = None

        self.congestion_top_road = None
        self.congestion_bottom_road = None

        # world class might have a ticks attribute
        self.middle_on = False

    def setup(self):
        # Clear everything
        self.reset()

        # Set the corner patches
        self.top_left_patch: Patch = World.patches_array[2][2]
        self.top_right_patch: Patch = World.patches_array[2][PATCH_COLS-3]
        self.bottom_left_patch: Patch = World.patches_array[PATCH_ROWS - 3][2]
        self.bottom_right_patch: Patch = World.patches_array[PATCH_ROWS - 3][PATCH_COLS - 3]

        #grab all gui variables
        self.spawn_rate = SimEngine.gui_get(SPAWN_RATE)

        # Set up the roads
        self.setup_roads()

        #spawn commuters
        # self.spawn_commuters()

    # def test(self):
    #     self.top_left_patch: Patch = World.patches_array[2][2]
    #     self.top_right_patch: Patch = World.patches_array[2][PATCH_COLS - 3]
    #     self.bottom_left_patch: Patch = World.patches_array[PATCH_ROWS - 3][2]
    #     self.bottom_right_patch: Patch = World.patches_array[PATCH_ROWS - 3][PATCH_COLS - 3]
    #
    #     # self.color_line(self.top_right_patch, self.bottom_right_patch, Color('Blue'))
    #     # self.color_line(self.bottom_right_patch, self.top_right_patch, Color('Red'))
    #     # self.color_line(self.bottom_right_patch, self.bottom_left_patch, Color('Red'))
    #     # self.color_line(self.bottom_left_patch, self.bottom_right_patch, Color('Green'))
    #     self.color_line(self.top_right_patch, self.bottom_left_patch, Color('Pink'))
    #     self.color_line(self.top_left_patch, self.bottom_right_patch, Color('Green'))

    def step(self):
        self.spawn_commuters()
        #determine congestion
        #move commuters
        #check if any commuters have finished their commute

    def spawn_commuters(self):
        if self.spawn_time >= self.spawn_rate:
            #spawn Commuter
            center_pixel = self.top_left_patch.center_pixel
            # new_commuter = self.agent_class(center_pixel=center_pixel, birth_tick=World.ticks, ticks_here=1, route=new_route())
            # if new_commuter.route == TOP_ROUTE or new_commuter.route == BRAESS_ROAD:
            #     new_commuter.face(self.top_right_patch)
            # elif new_commuter.route == BOTTOM_ROUTE:
            #     new_commuter.face(self.bottom_left_patch)

            #todo
            #remove test code
            print(center_pixel)
            print("spawned Commuter")
            print('Cars Spawned = ' + str(self.cars_spawned))

            self.cars_spawned += 1

            self.spawn_time = 0
        else:
            #increase Spawn time
            self.spawn_time += 1

    def setup_roads(self):
        #Cover everything in random green grass (set all patches a random green color)
        for patch in self.patches:
            color = randint(0,16) + 96
            patch.set_color(Color(0, color, 0))

        #Color the Corners
        self.top_left_patch.set_color(Color('Green'))
        self.top_right_patch.set_color(Color('Blue'))
        self.bottom_right_patch.set_color(Color('Red'))
        self.bottom_left_patch.set_color(Color('Blue'))

        # fill in corners
        corner_padding = self.bottom_left_patch.neighbors_8() + self.bottom_right_patch.neighbors_8() + \
                         self.top_left_patch.neighbors_8() + self.top_right_patch.neighbors_8()
        for p in corner_padding:
            p.set_color(Color('Grey'))

        #Draw the Roads
        self.draw_road(VARIABLE_CONGESTION, self.top_left_patch, self.top_right_patch)
        self.draw_road(VARIABLE_CONGESTION, self.bottom_left_patch, self.bottom_right_patch)
        self.draw_road(CONSTANT_CONGESTION, self.top_left_patch, self.bottom_left_patch)
        self.draw_road(CONSTANT_CONGESTION, self.top_right_patch, self.bottom_right_patch)

        #Check for middle and draw it or disable it
        self.middle_on = SimEngine.gui_get(MIDDLE_ON)
        self.middle_prev = self.middle_on

        if self.middle_on:
            self.draw_road(BRAESS_ROAD_ENABLED, self.top_right_patch, self.bottom_left_patch)
        else:
            self.draw_road(BRAESS_ROAD_DISABLED, self.top_right_patch, self.bottom_left_patch)

    def determine_congestion(self):
        pass

    def check_middle(self):
        if self.middle_on != self.middle_prev:
            if self.middle_on:
                self.draw_road(BRAESS_ROAD_ENABLED, self.top_right_patch, self.bottom_left_patch)
                self.middle_prev = SimEngine.gui_get(MIDDLE_ON)
            else:
                braess_road_commuters = [x for x in self.agent_class if x.route == BRAESS_ROAD_ROUTE]
                if len(braess_road_commuters) > 0:
                    self.draw_road(BRAESS_ROAD_DISABLED, self.top_right_patch, self.bottom_left_patch)
                    self.middle_prev = SimEngine.gui_get(MIDDLE_ON)

    def select_route(self):
        algorithm = SimEngine.gui_get(SELECTION_ALGORITHM)

    def patches_line(self, a, b):
        #same column infinite slope
        # print(b.col)
        # print(a.col)
        output = []
        if b.col == a.col:
            start = a if a.row < b.row else b
            stop = a if a.row > b.row else b
            for i in range(0, stop.row - start.row + 1):
                output.append(World.patches_array[start.row + i][start.col])
            return output

        elif b.row == a.row:
            start = a if a.col < b.col else b
            stop = a if a.col > b.col else b
            for i in range(0, stop.col - start.col + 1):
                output.append(World.patches_array[start.row][start.col + i])
            return output

        start = a if a.col < b.col else b
        stop = a if a.col > b.col else b

        if stop.row - start.row > 0:
            for i in range(0, stop.col - start.col + 1):
                output.append(World.patches_array[start.row + i][start.col + i])
            return output

        if stop.row - start.row < 0:
            for i in range(0, stop.col - start.col +1):
                output.append(World.patches_array[start.row - i][start.col + i])
            return output


    def draw_road(self, road_type, start_patch, stop_patch):
        if road_type == VARIABLE_CONGESTION:
            start_patch = World.patches_array[start_patch.row][start_patch.col + 1]
            stop_patch = World.patches_array[stop_patch.row][stop_patch.col - 1]

            #draw and set the middle line
            for p in self.patches_line(start_patch, stop_patch):
                p.set_color(Color('White'))
                p.set_road_type(VARIABLE_CONGESTION)

                World.patches_array[p.row+1][p.col].set_color(Color('Grey'))
                World.patches_array[p.row-1][p.col].set_color(Color('Grey'))

        if road_type == CONSTANT_CONGESTION:
            start_patch = World.patches_array[start_patch.row+1][start_patch.col]
            stop_patch = World.patches_array[stop_patch.row-1][stop_patch.col]

            # draw and set the middle line
            for p in self.patches_line(start_patch, stop_patch):
                p.set_color(Color('Yellow'))
                p.set_road_type(VARIABLE_CONGESTION)

                World.patches_array[p.row][p.col+1].set_color(Color('Grey'))
                World.patches_array[p.row][p.col-1].set_color(Color('Grey'))

        if road_type == BRAESS_ROAD_ENABLED or road_type == BRAESS_ROAD_DISABLED:
            if road_type == BRAESS_ROAD_ENABLED:
                edge_color = Color('Grey')
                middle_color = Color('Orange')
            else:
                edge_color = Color(64,64,64)
                middle_color = Color(64,64,64)

            start_patch = World.patches_array[start_patch.row + 2][start_patch.col - 2]
            stop_patch = World.patches_array[stop_patch.row - 2][stop_patch.col + 2]

            for p in self.patches_line(start_patch, stop_patch):
                p.set_color(middle_color)
                p.set_road_type(road_type)

                if p in self.patches_line(start_patch, stop_patch)[2:]:
                    World.patches_array[p.row + 2][p.col].set_color(edge_color)
                    World.patches_array[p.row][p.col - 2].set_color(edge_color)
                if p in self.patches_line(start_patch, stop_patch)[1:]:
                    World.patches_array[p.row][p.col - 1].set_color(edge_color)
                    World.patches_array[p.row+1][p.col].set_color(edge_color)

# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
MIDDLE_ON = 'middle_on'
SPAWN_RATE = 'spawn_rate'
SELECTION_ALGORITHM = 'mode'
BEST_KNOWN = 'Best Known'
EMPIRICAL_ANALYTICAl = 'Empirical Analytical'
PROBABILISTIC_GREEDY = 'Probabilistic Greedy'
SMOOTHING = 'Smoothing'
RANDOMNESS = 'Randomness'

# switches = [sg.CB(n + '\n 1', key=n, pad=((30, 0), (0, 0)), enable_events=True)
#                                              for n in reversed(CA_World.bin_0_to_7)]
gui_left_upper = [[sg.Text('Middle On?', pad=((0,5), (20,0))), sg.CB('True', key=MIDDLE_ON, pad=((0,5), (10,0)))],
                   [sg.Text('Spawn Rate', pad=((0, 5), (20, 0))),
                    sg.Slider(key=SPAWN_RATE, default_value=10, resolution=10, range=(0, 100), pad=((0, 5), (10, 0)),
                              orientation='horizontal')],
                   [sg.Text('Smoothing', pad=((0, 5), (20, 0))),
                    sg.Slider(key=SMOOTHING, default_value=10, resolution=1, range=(1, 100), pad=((0, 5), (10, 0)),
                              orientation='horizontal')],
                  [sg.Text('mode', pad=((0, 5), (20, 0))),
                   sg.Combo([BEST_KNOWN, EMPIRICAL_ANALYTICAl, PROBABILISTIC_GREEDY], key=SELECTION_ALGORITHM,
                            default_value=BEST_KNOWN, tooltip='Selection Algorithm', pad=((0, 5), (20, 0)))],
                  [sg.Text('Randomness', pad=((0, 5), (20, 0))),
                   sg.Slider(key=RANDOMNESS, default_value=16, resolution=1, range=(0, 100), pad=((0, 5), (10, 0)),
                             orientation='horizontal')]]

# sg.Combo([PREF_ATTACHMENT, RANDOM, RING, SMALL_WORLD, STAR, WHEEL], size=(11, 20),
#                               key=GRAPH_TYPE, pad=((5, 0), (20, 0)), default_value=WHEEL, tooltip='graph type')
if __name__ == "__main__":
    from core.agent import PyLogo
    # PyLogo(Braess_Road_World, 'Braess Road Paradox', gui_left_upper, bounce=True, patch_size=9, board_rows_cols=(71, 71))
    PyLogo(world_class=Braess_Road_World, caption='Braess Road Paradox', agent_class=Commuter, gui_left_upper=gui_left_upper, patch_class=Braess_Road_Patch)