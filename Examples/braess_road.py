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

CONSTANT_CONGESTION_DELAY = 10
#variable congestion delay is # of vehicles * the constant below
VARIABLE_CONGESTION_DELAY = 2

class Braess_Road_Patch(Patch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.road_type = None
        self.delay = 1

class Commuter(Agent):
    def __init__(self, birth_tick=None, route=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ticks_here = 1
        self.birth_tick=birth_tick
        self.route = route
        self.commute_complete = False
        #Face the agent in the appropriate direction
        if route == TOP_ROUTE or route == BRAESS_ROAD_ROUTE:
            self.face(Braess_Road_World.top_right_patch)
        else:
            self.face(Braess_Road_World.bottom_left_patch)

    def face(self, patch: Patch):
        #face should also set the new delay based on the road the will face
        self.face_xy(patch.center_pixel)

    def move(self):
        if self.commute_complete == False:
            if self.ticks_here < self.current_patch().delay:
                self.ticks_here += 1
            else:
                SOUTH = 180
                EAST = 90
                SOUTH_WEST = None
                if self.heading == EAST:
                    self.move_to_patch(World.patches_array[self.current_patch().row][self.current_patch().col + 1])
                elif self.heading == SOUTH:
                    self.move_to_patch(World.patches_array[self.current_patch().row + 1][self.current_patch().col])
                #braess road segment move
                else:
                    self.move_to_patch(World.patches_array[self.current_patch().row + 1][self.current_patch().col - 1])


                if self.current_patch() == Braess_Road_World.top_right_patch and self.route == TOP_ROUTE:
                    self.face(Braess_Road_World.bottom_right_patch)
                if self.current_patch() == Braess_Road_World.top_right_patch and self.route == BRAESS_ROAD_ROUTE:
                    self.face(Braess_Road_World.bottom_left_patch)
                if self.current_patch() == Braess_Road_World.bottom_left_patch:
                    self.face(Braess_Road_World.bottom_right_patch)
                if self.current_patch() == Braess_Road_World.bottom_right_patch:

                    #there is an extra number of ticks equal to delay so we remove them here
                    if self.route == BRAESS_ROAD_ROUTE:
                        self.birth_tick = self.birth_tick + 5
                    self.commute_complete = True
                self.ticks_here = 1

        # increase the birth ticks by one for each tick that the commuter is on braess road
        # this removes the extra time that the commuter is on the road
        if self.current_patch().road_type == BRAESS_ROAD_ENABLED or ():
            # print('braess road branch')
            self.birth_tick += 1

class Braess_Road_World(World):
    top_left_patch: Patch = None
    top_right_patch: Patch = None
    bottom_left_patch: Patch = None
    bottom_right_patch: Patch = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset()

        Braess_Road_World.top_left_patch: Patch = World.patches_array[2][2]
        Braess_Road_World.top_right_patch: Patch = World.patches_array[2][PATCH_COLS - 3]
        Braess_Road_World.bottom_left_patch: Patch = World.patches_array[PATCH_ROWS - 3][2]
        Braess_Road_World.bottom_right_patch: Patch = World.patches_array[PATCH_ROWS - 3][PATCH_COLS - 3]

    def reset(self):
        self.reset_all()

        self.latest_travel_time = 0
        self.latest_top_time = 0
        self.latest_middle_time = 0
        self.latest_bottom_time = 0

        self.spawn_time = 0
        self.spawn_rate = 30
        self.avg_time = 0

        self.cars_spawned = 0

        self.top_prob = None
        self.bottom_prob = None
        self.middle_prob = None

        self.congestion_top_road = None
        self.congestion_bottom_road = None

        # world class might have a ticks attribute
        self.middle_on = False

    def setup(self):
        # Clear everything
        self.reset()

        # Set the corner patches
        # self.top_left_patch: Patch = World.patches_array[2][2]
        # self.top_right_patch: Patch = World.patches_array[2][PATCH_COLS-3]
        # self.bottom_left_patch: Patch = World.patches_array[PATCH_ROWS - 3][2]
        # self.bottom_right_patch: Patch = World.patches_array[PATCH_ROWS - 3][PATCH_COLS - 3]

        #grab all gui variables
        self.spawn_rate = SimEngine.gui_get(SPAWN_RATE)

        # Set up the roads
        self.setup_roads()

    def step(self):
        self.spawn_commuters()
        #determine congestion
        self.determine_congestion()
        #move commuters
        to_remove = []
        for commuter in World.agents:
            #list of commuters to remove at the end of this method
            commuter.move()
            #check if any commuters have finished their commute
            if commuter.commute_complete:
                self.commuter_stats(commuter)
                to_remove.append(commuter)
        for commuter in to_remove:
            World.agents.remove(commuter)

    def commuter_stats(self, commuter):
        # calculates travel times and adds them to the appropurate route tracker
        # kills commuter

        # rate is the frame rate at wchich the sim is running
        travel_time = (World.ticks - commuter.birth_tick)
        # print(travel_time)
        # return
        smoothing = SimEngine.gui_get(SMOOTHING)
        # calculate avge traveltime across completed commutes
        if self.avg_time == 0:
            self.avg_time = travel_time
            print(self.avg_time)
        else:
            # based on number of 20 agents
            self.avg_time = ((19 * self.avg_time + travel_time) / 20)
            print(self.avg_time)

        # if the route is a _______
        if commuter.route == TOP_ROUTE:
            # top ; travel time of last turtle to complete top route
            if self.latest_top_time == 0:
                self.latest_top_time = travel_time
            else:
                self.latest_top_time = ((travel_time) + ((smoothing - 1) * self.latest_top_time)) / smoothing
        else:
            if commuter.route == BOTTOM_ROUTE:
                if self.latest_bottom_time == 0:
                    self.latest_bottom_time = travel_time
                else:
                    self.latest_bottom_time = ((travel_time) + ((smoothing - 1) * self.latest_bottom_time)) / smoothing
            #triggers on route with braess road
            else:
                if self.latest_middle_time == 0:
                    self.latest_middle_time = travel_time
                else:
                    self.latest_middle_time = ((travel_time) + ((smoothing - 1) * self.latest_middle_time)) / smoothing
        self.update_gui_data()

    def spawn_commuters(self):
        # #testing
        # center_pixel = self.top_left_patch.center_pixel
        # if self.cars_spawned == 0:
        #     self.agent_class(center_pixel=center_pixel, birth_tick=World.ticks, route=TOP_ROUTE)
        # if self.cars_spawned == 1:
        #     self.agent_class(center_pixel=center_pixel, birth_tick=World.ticks, route=BOTTOM_ROUTE)
        # if self.cars_spawned == 2:
        #     self.agent_class(center_pixel=center_pixel, birth_tick=World.ticks, route=BRAESS_ROAD_ROUTE)
        # self.cars_spawned += 1
        # return
        # #end of test code

        if self.spawn_time >= self.spawn_rate:
            #spawn Commuter
            center_pixel = self.top_left_patch.center_pixel
            self.agent_class(center_pixel=center_pixel, birth_tick=World.ticks, route=self.select_route())
            # if self.middle_on:
            #     self.agent_class(center_pixel=center_pixel, birth_tick=World.ticks, route=randint(0,2))
            # else:
            #     self.agent_class(center_pixel=center_pixel, birth_tick=World.ticks, route=randint(0,1))
            # if new_commuter.route == TOP_ROUTE or new_commuter.route == BRAESS_ROAD:
            #     new_commuter.face(self.top_right_patch)
            # elif new_commuter.route == BOTTOM_ROUTE:
            #     new_commuter.face(self.bottom_left_patch)

            #todo
            #remove test code
            # print(center_pixel)
            # print("spawned Commuter")
            # print('Cars Spawned = ' + str(self.cars_spawned))

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

        # set the delay in Constant congestion road
        for patch in self.patches_line(self.top_right_patch, self.bottom_right_patch)[1:-1]:
            patch.delay = CONSTANT_CONGESTION_DELAY
        for patch in self.patches_line(self.top_left_patch, self.bottom_left_patch)[1:-1]:
            patch.delay = CONSTANT_CONGESTION_DELAY

        #set the delay in braess road to 1 tick
        for patch in self.patches_line(self.top_right_patch, self.bottom_left_patch):
            patch.set_delay = 1

    def determine_congestion(self):
        #calculate congestion for the top road
        #patches in the top road
        top_road = self.patches_line(self.top_left_patch, self.top_right_patch)[1:-1]
        top_road_commuters = [x for x in World.agents if x.current_patch() in top_road]

        delay = len(top_road_commuters) * VARIABLE_CONGESTION_DELAY
        # print(len(top_road_commuters))
        for patch in top_road:
            patch.delay = delay

        delay = 1
        bottom_road = self.patches_line(self.bottom_left_patch, self.bottom_right_patch)[1:-1]
        bottom_road_commuters = [x for x in World.agents if x.current_patch() in bottom_road]

        # print(len(bottom_road))
        # print(len(bottom_road_commuters))
        delay = len(bottom_road_commuters) * VARIABLE_CONGESTION_DELAY
        for patch in bottom_road:
            patch.delay = delay

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
        return self.probabilistic_greedy()


        algorithm = SimEngine.gui_get(SELECTION_ALGORITHM)
    def probabilistic_greedy(self):
        if self.middle_on:
            return randint(0,2)
        else:
            if randint(0,100) <= int(SimEngine.gui_get(RANDOMNESS)):
                return randint(0,1)
            else:
                top_route_count = len([x for x in World.agents if x.route == TOP_ROUTE])
                bottom_route_count = len([x for x in World.agents if x.route == BOTTOM_ROUTE])
                return TOP_ROUTE if top_route_count < bottom_route_count else BOTTOM_ROUTE

    def patches_line(self, a: Patch, b: Patch) -> [Patch]:
        #returns all the patches between a and b
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

    def draw_road(self, road_type, start_patch: Patch, stop_patch: Patch):
        if road_type == VARIABLE_CONGESTION:
            start_patch = World.patches_array[start_patch.row][start_patch.col + 1]
            stop_patch = World.patches_array[stop_patch.row][stop_patch.col - 1]

            #draw and set the middle line
            for p in self.patches_line(start_patch, stop_patch):
                p.set_color(Color('White'))
                p.road_type = VARIABLE_CONGESTION

                World.patches_array[p.row+1][p.col].set_color(Color('Grey'))
                World.patches_array[p.row-1][p.col].set_color(Color('Grey'))

        if road_type == CONSTANT_CONGESTION:
            start_patch = World.patches_array[start_patch.row+1][start_patch.col]
            stop_patch = World.patches_array[stop_patch.row-1][stop_patch.col]

            # draw and set the middle line
            for p in self.patches_line(start_patch, stop_patch):
                p.set_color(Color('Yellow'))
                p.road_type = VARIABLE_CONGESTION

                World.patches_array[p.row][p.col+1].set_color(Color('Grey'))
                World.patches_array[p.row][p.col-1].set_color(Color('Grey'))

        if road_type == BRAESS_ROAD_ENABLED or road_type == BRAESS_ROAD_DISABLED:
            if road_type == BRAESS_ROAD_ENABLED:
                edge_color = Color('Grey')
                middle_color = Color('Orange')
            else:
                edge_color = Color(64,64,64)
                middle_color = Color(64,64,64)

            start_patch = World.patches_array[start_patch.row + 1][start_patch.col - 1]
            stop_patch = World.patches_array[stop_patch.row - 1][stop_patch.col + 1]

            for p in self.patches_line(start_patch, stop_patch):
                p.road_type = road_type

            for p in self.patches_line(start_patch, stop_patch)[1:-1]:
                p.set_color(middle_color)
                if p in self.patches_line(start_patch, stop_patch)[3:-1]:
                    World.patches_array[p.row + 2][p.col].set_color(edge_color)
                    World.patches_array[p.row][p.col - 2].set_color(edge_color)
                if p in self.patches_line(start_patch, stop_patch)[2:-1]:
                    World.patches_array[p.row][p.col - 1].set_color(edge_color)
                    World.patches_array[p.row+1][p.col].set_color(edge_color)

    def update_gui_data(self):
        SimEngine.gui_set(AVERAGE, value=str(self.avg_time))
        SimEngine.gui_set(FASTEST_TOP, value=str(self.latest_top_time))
        SimEngine.gui_set(FASTEST_MIDDLE, value=str(self.latest_middle_time))
        SimEngine.gui_set(FASTEST_BOTTOM, value=str(self.latest_bottom_time))
        # SimEngine.gui_set(AVERAGE, value=str(self.avg_time))
        # SimEngine.gui_set(AVERAGE, value=str(self.avg_time))
        # SimEngine.gui_set(AVERAGE, value=str(self.avg_time))
        # SimEngine.gui_set(AVERAGE, value=str(self.avg_time))
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
AVERAGE = 'average'
FASTEST_TOP = 'fastest top'
FASTEST_MIDDLE = 'fastest middle'
FASTEST_BOTTOM = 'fastest bottom'

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
                             orientation='horizontal')],
                  [sg.Text('Average = '), sg.Text('         0', key=AVERAGE)],
                  [sg.Text('Fastest Top Time = '), sg.Text('         0', key=FASTEST_TOP)],
                  [sg.Text('Fastest Middle Time = '), sg.Text('         0', key=FASTEST_MIDDLE)],
                  [sg.Text('Fastest Bottom Time = '), sg.Text('         0', key=FASTEST_BOTTOM)]]
                  # [sg.Text('Average= '), sg.Text('         0', key=AVERAGE)],
                  # [sg.Text('Average= '), sg.Text('         0', key=AVERAGE)],
                  # [sg.Text('Average= '), sg.Text('         0', key=AVERAGE)],
                  # [sg.Text('Average= '), sg.Text('         0', key=AVERAGE)],]

# sg.Combo([PREF_ATTACHMENT, RANDOM, RING, SMALL_WORLD, STAR, WHEEL], size=(11, 20),
#                               key=GRAPH_TYPE, pad=((5, 0), (20, 0)), default_value=WHEEL, tooltip='graph type')
if __name__ == "__main__":
    from core.agent import PyLogo
    # PyLogo(Braess_Road_World, 'Braess Road Paradox', gui_left_upper, bounce=True, patch_size=9, board_rows_cols=(71, 71))
    PyLogo(world_class=Braess_Road_World, caption='Braess Road Paradox', agent_class=Commuter,
           gui_left_upper=gui_left_upper, patch_class=Braess_Road_Patch, fps=5)