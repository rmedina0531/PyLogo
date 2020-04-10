from core.gui import PATCH_COLS, PATCH_ROWS
from core.world_patch_block import World, Patch
from core.agent import Agent
from pygame.color import Color
from random import randint

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

        self.latest_travel_time = None
        self.latest_top_time = None
        self.latest_middle_time = None

        self.spawn_time = None
        self.avg_time = None

        self.cars_spawned = None

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
        self.ticks = None

    def setup(self):
        # Clear everything
        self.reset_all()

        # Set the corner patches

        self.top_left_patch: Patch = World.patches_array[2][2]
        self.top_right_patch: Patch = World.patches_array[2][PATCH_COLS-3]
        self.bottom_left_patch: Patch = World.patches_array[PATCH_ROWS - 3][PATCH_COLS - 3]
        self.bottom_right_patch: Patch = World.patches_array[PATCH_ROWS-3][2]

        # Set up the roads
        self.setup_roads()

    def setup_roads(self):
        # 1. Cover everything in random green grass (set all patches a random green color)
        for patch in self.patches:
            color = randint(0,16) + 96
            patch.set_color(Color(0, color, 0))

        self.draw_roads()

    def draw_roads(self):
        # 2. Set colors and properties on all corners
        self.top_left_patch.set_color(Color('Green'))
        self.top_right_patch.set_color(Color('Blue'))
        self.bottom_right_patch.set_color(Color('Blue'))
        self.bottom_left_patch.set_color(Color('Red'))

        corner_padding = self.bottom_left_patch.neighbors_8() + self.bottom_right_patch.neighbors_8() + \
                         self.top_left_patch.neighbors_8() + self.top_right_patch.neighbors_8()
        # print(neighbors)
        for p in corner_padding:
            p.set_color(Color('Grey'))

        #set up top and bottom roads, set the road types
        for i in range(3, PATCH_COLS-3):

            #top road
            road_type = 1
            self.patches_array[1, i].set_color(Color('Grey'))
            self.patches_array[1, i].set_road_type(road_type)
            self.patches_array[3, i].set_color(Color('Grey'))
            self.patches_array[3, i].set_road_type(road_type)
            self.patches_array[2, i].set_color(Color('Yellow'))
            self.patches_array[2, i].set_road_type(road_type)
            #bottom road
            self.patches_array[PATCH_ROWS - 2, i].set_color(Color('Grey'))
            self.patches_array[PATCH_ROWS - 2, i].set_road_type(road_type)
            self.patches_array[PATCH_ROWS - 4, i].set_color(Color('Grey'))
            self.patches_array[PATCH_ROWS - 4, i].set_road_type(road_type)
            self.patches_array[PATCH_ROWS - 3, i].set_color(Color('Yellow'))
            self.patches_array[PATCH_ROWS - 3, i].set_road_type(road_type)

            #left road
            self.patches_array[i, 1].set_color(Color('Grey'))
            self.patches_array[i, 1].set_road_type(road_type)
            self.patches_array[i, 3].set_color(Color('Grey'))
            self.patches_array[i, 3].set_road_type(road_type)
            self.patches_array[i, 2].set_color(Color('Yellow'))
            self.patches_array[i, 2].set_road_type(road_type)

            # Right Road
            self.patches_array[i, PATCH_ROWS - 2].set_color(Color('Grey'))
            self.patches_array[i, PATCH_ROWS - 2].set_road_type(road_type)
            self.patches_array[i, PATCH_ROWS - 4].set_color(Color('Grey'))
            self.patches_array[i, PATCH_ROWS - 4].set_road_type(road_type)
            self.patches_array[i, PATCH_ROWS - 3].set_color(Color('Yellow'))
            self.patches_array[i, PATCH_ROWS - 3].set_road_type(road_type)

        if self.middle_on:
            pass

# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
gui_left_upper = [ [sg.Text('nbr agents', pad=((0, 5), (20, 0))),
                    sg.Slider(key='nbr_agents', range=(1, 101), resolution=25, default_value=25,
                              orientation='horizontal', size=(10, 20))] ]


if __name__ == "__main__":
    from core.agent import PyLogo
    # PyLogo(Braess_Road_World, 'Braess Road Paradox', gui_left_upper, bounce=True, patch_size=9, board_rows_cols=(71, 71))
    PyLogo(world_class=Braess_Road_World, caption='Braess Road Paradox', agent_class=Commuter, patch_class=Braess_Road_Patch)