'''Version of the CA that does not implement the justification on each iteration'''

import core.gui as gui
from core.gui import HOR_SEP
from core.on_off import on_off_left_upper, OnOffPatch, OnOffWorld
from core.sim_engine import SimEngine
from core.utils import bin_str

import random

from typing import List


class CA_World(OnOffWorld):

    ca_display_size = 151

    # bin_0_to_7 is ['000' .. '111']
    bin_0_to_7 = [bin_str(n, 3) for n in range(8)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.pos_to_switch is a dictionary that maps position values in a binary number to range(8) represented
        # as 3-digit binary strings:
        #     {1: '000', 2: '001', 4: '010', 8: '011', 16: '100', 32: '101', 64: '110', 128: '111'}
        # The three digits are the rule components and the keys to the switches.
        # To see it, try: print(self.pos_to_switch) after executing the next line.
        # The function bin_str() is defined in utils.py

        self.pos_to_switch = dict(zip([2**i for i in range(8)], CA_World.bin_0_to_7))
        # print(self.pos_to_switch)

        # The rule number used for this run, initially set to 110 as the default rule.
        # (You might also try rule 165.)
        # The following sets the local variable self.rule_nbr. It doesn't change the 'Rule_nbr' slider widget.
        self.rule_nbr = 110
        # Set the switches and the binary representation of self.rule_nbr.
        # self.set_switches_from_rule_nbr()
        # self.set_binary_nbr_from_rule_nbr()
        # self.set_slider_from_rule_nbr()

        self.make_switches_and_rule_nbr_consistent()

        self.init = None

        # self.ca_lines is a list of lines, each of which is a list of 0/1. Each line represents
        # a state of the CA, i.e., all the cells in the line. self.ca_list contains the entire
        # history of the CA.
        self.ca_lines: List[List[int]] = []
        self.ca_left_lines: List[List[int]] = []
        self.ca_right_lines: List[List[int]] = []


        #For testing --- REMOVE
        self.ca_lines.append([])
        while len(self.ca_lines[0]) < 151:
            self.ca_lines[0].append(0)

        self.ca_lines[0][75] = 1
        self.ca_left_lines.append([0,0])
        self.ca_right_lines.append([0,0])
        #end of test code


        # gui.WINDOW['rows'].update(value=len(self.ca_lines))
        SimEngine.gui_set('rows', value=len(self.ca_lines))

    def build_initial_line(self):
        """
        Construct the initial CA line
        """
        self.init = SimEngine.gui_get('init')
        if self.init == 'Random':
            # Set the initial row to random 1/0.
            # You complete this line.
            line = "".join(random.choice('10') for i in range(self.ca_display_size))
        else:
            line = [0] * self.ca_display_size
            col = 0 if self.init == 'Left' else \
                  CA_World.ca_display_size // 2 if self.init == 'Center' else \
                  CA_World.ca_display_size - 1   # self.init == 'Right'
            line[col] = 1
        return line

    def get_rule_nbr_from_switches(self):
        """
        Translate the on/off of the switches to a rule number.
        This is the inverse of set_switches_from_rule_nbr(), but it doesn't set the 'Rule_nbr' Slider.
        """
        output = []

        for rule in CA_World.bin_0_to_7:
            output.append(str('1' if SimEngine.gui_get(rule) else '0'))
        output.reverse()
        self.rule_nbr = int("".join(output), 2)

    def handle_event(self, event):
        """
        This is called when a GUI widget is changed and isn't handled by the system.
        The key of the widget that changed is the event.
        If the changed widget has to do with the rule number or switches, make them all consistent.

        This is the function that will trigger all the code you write this week
        """
        # Handle color change requests.
        super().handle_event(event)


        if event in ['Rule_nbr'] + CA_World.bin_0_to_7:
            if event == 'Rule_nbr':
                self.rule_nbr = SimEngine.gui_get('Rule_nbr')

            if event in CA_World.bin_0_to_7:
                self.get_rule_nbr_from_switches()

            self.make_switches_and_rule_nbr_consistent()

    def make_switches_and_rule_nbr_consistent(self):
        """
        Make the Slider, the switches, and the bin number consistent: all should equal self.rule_nbr.
        """
        self.set_slider_from_rule_nbr()
        self.set_switches_from_rule_nbr()
        self.set_binary_nbr_from_rule_nbr()

    def set_slider_from_rule_nbr(self):
        SimEngine.gui_set('Rule_nbr', value=self.rule_nbr)

    def set_binary_nbr_from_rule_nbr(self):
        """
        Translate self.rule_nbr into a binary string and put it into the
        gui.WINDOW['bin_string'] widget. For example, if self.rule_nbr is 110,
        the string '(01101110)' is stored in gui.WINDOW['bin_string']. Include
        the parentheses around the binary number.

        Use gui.WINDOW['bin_string'].update(value=new_value) to update the value of the widget.
        Use SimEngine.gui_set('bin_string', value=new_value) to update the value of the widget.
        """
        binary = self.int_to_8_bit_binary(self.rule_nbr, False)
        binary_str = ''.join(binary)
        SimEngine.gui_set('bin_string', value=binary_str)

    def int_to_8_bit_binary(self, input, rev=True):
        output = "{0:b}".format(input)
        output2 = list(output)
        output2.reverse()
        while len(output2) < 8:
            output2.append('0')

        #reverse to alignt to rules and index
        if rev:
            return output2
        else:
            output2.reverse()
            return output2

    def set_display_from_lines(self):
        """
        Copy values from self.ca_lines to the patches. One issue is dealing with
        cases in which there are more or fewer lines than Patch row.
        """

        #does not fill up the entire screen


        y = 1
        limy = len(self.ca_lines) + 150
        for i in self.ca_lines:
            x = 1
            if limy >= 150:
                limx = len(i) + 150
                for j in range(len(i)):
                    if limx >= 150:
                        b = bool(i[j])
                        patch = self.pixel_tuple_to_patch(((150 - len(i) + x) * 4, (150 - len(self.ca_lines) + y) * 4))
                        patch.set_on_off(b)
                        x += 1
                    else:
                        limx -= 1
                    # print(limx, "x")
                y += 1
            else:
                limy -= 1
            # print(limy, "y")

    def set_switches_from_rule_nbr(self):
        """
        Update the settings of the switches based on self.rule_nbr.
        Note that the 2^i position of self.rule_nbr corresponds to self.pos_to_switch[i]. That is,
        self.pos_to_switch[i] returns the key for the switch representing position  2^i.

        Set that switch as follows: gui.WINDOW[self.pos_to_switch[pos]].update(value=new_value).
        Set that switch as follows: SimEngine.gui_set(self.pos_to_switch[pos], value=new_value).
        (new_value will be either True or False, i.e., 1 or 0.)

        This is the inverse of get_rule_nbr_from_switches().
        """
        for rule_switch, enabled in zip(CA_World.bin_0_to_7, self.int_to_8_bit_binary(self.rule_nbr)):
            SimEngine.gui_set(rule_switch, value=(True if enabled=='1' else False))

    def setup(self):
        """
        Make the slider, the switches, and the bin_string of the rule number consistent with each other.
        Give the switches priority.
        That is, if the slider and the switches are both different from self.rule_nbr,
        use the value derived from the switches as the new value of self.rule_nbr.

        Once the slider, the switches, and the bin_string of the rule number are consistent,
        set self.ca_lines[0] as directed by SimEngine.gui_get('init').

        Copy (the settings on) that line to the bottom row of patches.
        Note that the lists in self.ca_lines are lists of 0/1. They are not lists of Patches.
        """

        self.ca_lines = []
        self.ca_left_lines = []
        self.ca_right_lines = []
        self.ca_left_lines.append([0,0])
        self.ca_right_lines.append([0,0])
        self.ca_lines.append(self.build_initial_line())
        self.set_display_from_lines()

    def step(self):
        """
        Take one step in the simulation.
        o Generate an additional line in self.ca_lines.
        o Copy self.ca_lines to the display
        """
        #make a dictionary of rules and which are active
        binary = self.int_to_8_bit_binary(self.rule_nbr)
        binary_str = ''.join(binary)

        active_rules = dict(zip(CA_World.bin_0_to_7, list(binary_str)))
        # print('Active Rules: ' + str(active_rules))
        # print("is 001 active " + str(active_rules['001']))

        #move all elements one over in the history
        # self.ca_lines.insert(0,[])
        # self.ca_left_lines.insert(0,[])
        # self.ca_right_lines.insert(0,[])

        # find the indexes to isolate the visible part of the cellular automaton
        start_index = len(self.ca_left_lines[-1])
        stop_index = start_index + len(self.ca_lines[-1])

        #get the combined line of visible and not visible cells
        combined_line_to_compute = self.ca_left_lines[-1] + self.ca_lines[-1] + self.ca_right_lines[-1]

        #check to see if a zero needs to be added to either end
        #useful for the rule 001 or 100
        if combined_line_to_compute[:2] == [0,1]:
            combined_line_to_compute.insert(0,0)
            #make sure to att 1 to the indexes to account for the new element
            start_index += 1
            stop_index += 1

        if combined_line_to_compute[-2:] == [1,0]:
            combined_line_to_compute.append(0)


        #variable to store the new computed line
        #first one will always be zero as there is no rule
        #find better explanation
        new_line = [0]

        #compute the new line

        #for each ca triplet to check
        for i in range(len(combined_line_to_compute) - 2):
            #make the array of three cells together ex [1,0,0] starting at index one and ending at index 3 before the end
            #then check to see if it is active from the dictionary
            #add the new cell as a 1 if active else set it to 0
            new_line.append(1 if active_rules["".join(str(x) for x in combined_line_to_compute[i:i + 3])] == '1' else 0)


        # for i in range(len(combined_line_to_compute) - 2):
        #     to_check = "".join(str(x) for x in combined_line_to_compute[i:i+3])
        #     # print(to_check)
        #
        #     # print('from list: ' + active_rules[to_check])
        #     if (active_rules[to_check]) == '1':
        #         # print ('Active Rule')
        #         new_line.append(1)
        #     else:
        #         # print('Inactive Rule')
        #         new_line.append(0)


        #last element in the new line will also be zero
        new_line.append(0)

        #seperate the components
        #and add them to ther histories
        self.ca_left_lines.append(new_line[:start_index])
        self.ca_lines.append(new_line[start_index:stop_index])
        self.ca_right_lines.append(new_line[stop_index:])

        self.set_display_from_lines()

# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg

""" 
The following appears at the top-left of the window. 
It puts a row consisting of a Text widgit and a ComboBox above the widgets from on_off.py
"""
ca_left_upper = [[sg.Text('Initial row:'),
                  sg.Combo(values=['Left', 'Center', 'Right', 'Random'], key='init', default_value='Right')],
                 [sg.Text('Rows:'), sg.Text('     0', key='rows')],
                 HOR_SEP(30)] + \
                 on_off_left_upper

# The switches are CheckBoxes with keys from CA_World.bin_0_to_7 (in reverse).
# These are the actual GUI widgets, which we access via their keys.
# The pos_to_switch dictionary maps position values in the rule number as a binary number
# to these widgets. Each widget corresponds to a position in the rule number.
# Note how we generate the text for the chechboxes.
switches = [sg.CB(n + '\n 1', key=n, pad=((30, 0), (0, 0)), enable_events=True)
                                             for n in reversed(CA_World.bin_0_to_7)]

""" 
This  material appears above the screen: 
the rule number slider, its binary representation, and the switches.
"""
ca_right_upper = [[sg.Text('Rule number', pad=((100, 0), (20, 10))),
                   sg.Slider(key='Rule_nbr', range=(0, 255), orientation='horizontal',
                             enable_events=True, pad=((10, 20), (0, 10))),
                   sg.Text('00000000 (binary)', key='bin_string', enable_events=True, pad=((0, 0), (10, 0)))],

                  switches
                  ]


if __name__ == "__main__":
    """
    Run the CA program. PyLogo is defined at the bottom of core.agent.py.
    """
    from core.agent import PyLogo

    # Note that we are using OnOffPatch as the Patch class. We could define CA_Patch(OnOffPatch),
    # but since it doesn't add anything to OnOffPatch, there is no need for it.
    PyLogo(CA_World, '1D CA', patch_class=OnOffPatch,
           gui_left_upper=ca_left_upper, gui_right_upper=ca_right_upper,
           fps=10, patch_size=3, board_rows_cols=(CA_World.ca_display_size, CA_World.ca_display_size))
