#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Pmw
import json
try:
    import Tkinter as tk
except Exception:
    import tkinter as tk
from operator import itemgetter


class GOL():
    """Status manager of GOL(Game of Life).

    Each world in game of life is a set of cells, and status of
    every cell should be alive or dead. Status changes from gen
    -eration to generation.
    """

    def __init__(self, row=0, col=0):
        """Init size and status of world."""
        self.row, self.col = row, col
        self.now = {}
        self.init_status([])

    def init_status(self, init_cells):
        """Set status of world.

        if the begining status given is not empty, then use them
        to initialize the world.

        Args:
            init_cells: begining status given. It's a a list of tuples.
                        each tuple in it is coordinate of a alive cell,
                        for example: [(10, 20), (10, 21)]
        """
        if len(init_cells) == 0:
            self.now = {}
            return

        # get bounding box of given set of cells.
        min_x = min(init_cells, key=itemgetter(0))[0]
        max_x = max(init_cells, key=itemgetter(0))[0]
        min_y = min(init_cells, key=itemgetter(1))[1]
        max_y = max(init_cells, key=itemgetter(1))[1]

        if max_x >= self.col or max_y >= self.row:
            raise Exception("Size of begining status set is too large(x:%d-%d;y:%d-%d)"
                            % (min_x, max_x, min_y, max_y))

        # compute offset in row direction and column direction
        # TODO: offset is wrong.
        row_off = (self.row - max_y - min_y) // 2
        col_off = (self.col - max_x - min_x) // 2

        # create the world
        for cell in init_cells:
            new_cell = (cell[0] + row_off, cell[1] + col_off)
            self.now[new_cell] = True

    def update(self):
        """Update status of world by status before.

        For each cell in world, do these things:
        1. look and find how many alive neighbors around,each cell
           have eight neighbors
        2. update status of cell according the number of its alive
           neighbors. The following are the rules
           + if cell is alive, and number of neighbors is too small
             (less than 2) or too too much(more than 3), this cell
             will die, or it will be keep alive
           + if cell is dead, and number of neighbors is three, then
             cell will be alive
        """
        next_generation = {}
        related_neighbors = set([])
        for cell in self.now.keys():
            # for a alive cell
            arounds = self.neighbors(cell[0], cell[1])
            around_count = sum([1 for c in arounds if c in self.now.keys()])
            if around_count in (2, 3):
                next_generation[cell] = True

            # record related neighbors
            dead_neighbors = [c for c in arounds if c not in self.now.keys()]
            related_neighbors.update(dead_neighbors)

        # update neighbors
        for cell in related_neighbors:
            arounds = self.neighbors(cell[0], cell[1])
            around_count = sum([1 for c in arounds if c in self.now.keys()])
            if around_count == 3:
                next_generation[cell] = True

        self.now = next_generation.copy()
        return self.now

    def neighbors(self, row, col):
        """Compute number of alive neighbors around a cell."""
        res = []
        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                irow = i % self.row
                icol = j % self.col
                if irow != row or icol != col:
                    res.append((irow, icol))

        return res


class ShowGOL(tk.Tk):
    """Diasplay the Game of Life

    Use Tkinter to draw the world of cells and the changes in
    the world.
    """

    def __init__(self, *args, **kwargs):
        """Init resource and world"""
        # init resource
        tk.Tk.__init__(self, *args, **kwargs)
        # init world
        self.setup_members()    # initialize class members
        self.setup_window()     # root window
        self.setup_canvas()     # canvas to draw world
        self.create_world()

        self.setup_toolbar()    # tool bar

        # make world alive
        self.after(5, lambda: self.life(5))

    def setup_members(self):
        """Initialize class members

        These members are main information of class.They are information
        of status, widget, resource and so on
        """
        # cell
        self.cell_size = 8
        self.cell_row = 80
        self.cell_col = 100
        self.color_alive = "black"
        self.color_dead = "white"

        # world
        self.init_modes = {}    # read modes from json file
        self.init_world = {}    # begining status
        self.world = {}         # world's map
        # current status of world
        self.world_status = GOL(self.cell_row, self.cell_col)
        self.world_setable = True
        self.world_alive = False

        # widgets
        self.toolbar_height = 40
        self.world_size = [self.cell_size * self.cell_row,
                           self.cell_size * self.cell_col]
        self.window_size = self.world_size
        self.window_size[0] += self.toolbar_height

        # resource
        self.modes_file = "gol.json"
        self.modes_names = []

    def setup_window(self):
        """Create root window"""
        # make window in the center of screen
        scrn_width, scrn_height = self.maxsize()
        win_height, win_width = self.window_size
        location = '%dx%d+%d+%d' % (win_width, win_height,
                                    (scrn_width - win_width) // 2,
                                    (scrn_height - win_height) // 2)
        self.geometry(location)

        # set title
        self.title("Game of life")

    def setup_toolbar(self):
        """Create tool bar"""
        # create frame to contain buttons
        self.toolbar = tk.Frame(self, height=self.toolbar_height)
        self.toolbar.grid(row=0, column=0,
                          sticky=tk.N + tk.S + tk.W + tk.E)

        # set tools
        self.setup_mode_selector()
        self.setup_mode_saver()
        self.setup_button_run()
        self.setup_button_pause()
        self.setup_button_stop()
        self.setup_button_step()

    def setup_mode_selector(self):
        """Mode selector

        User can select begining status of the world already exists,
        these status are called 'modes' here, and modes are save in
        file with json format
        """
        # read modes from json file
        # TODO use more simple ways to read
        try:
            modes_reader = open(self.modes_file, 'r')
            self.init_modes = json.load(modes_reader)
        except Exception:
            pass

        # set selector
        self.modes_names = list(self.init_modes.keys())
        self.modes_names.insert(0, "Set by hand")
        self.modes_selector = Pmw.ComboBox(
            self.toolbar,
            label_text='Modes selector',
            labelpos='nw',
            selectioncommand=self.prepare_world,
            scrolledlist_items=self.modes_names,
        )
        self.modes_selector.grid(row=0, column=0, sticky=tk.W)
        first = self.modes_names[0]
        self.modes_selector.selectitem(first)
        self.prepare_world(first)

    def setup_mode_saver(self):
        """Mode saver

        User can save begining status set by hand to json file.
        Sharing this json file with friends is also a good idea.
        """
        self.saver_button = tk.Button(
            self.toolbar,
            text='Save',
            command=self.save_mode)
        self.saver_button.grid(row=0, column=1, sticky=tk.W)

    def setup_button_run(self):
        """Button to run the Game of Life"""
        self.button_run = tk.Button(
            self.toolbar,
            text='Run',
            command=self.run_world)
        self.button_run.grid(row=0, column=2, sticky=tk.W)

    def setup_button_pause(self):
        """Button to pause the Game of Life"""
        self.button_pause = tk.Button(
            self.toolbar,
            text='Pause',
            command=self.pause_world)
        self.button_pause.grid(row=0, column=3, sticky=tk.W)

    def setup_button_stop(self):
        """Button to stop the Game of Life

        stopping will set the world to a status initialized using
        the current item in modes selector
        """
        self.button_stop = tk.Button(
            self.toolbar,
            text='Stop',
            command=self.reset_world)
        self.button_stop.grid(row=0, column=4, sticky=tk.W)

    def setup_button_step(self):
        """Button to step the Game of Life"""
        self.button_run = tk.Button(
            self.toolbar,
            text='step',
            command=self.step_world)
        self.button_run.grid(row=0, column=5, sticky=tk.W)

    def setup_canvas(self):
        """Add canvas to root window"""
        # create frame to contain canvas
        self.world_container = tk.Frame(self,
                                        width=self.world_size[1],
                                        height=self.world_size[0])
        self.world_container.grid(row=1, column=0, sticky=tk.W + tk.N)

        # create canvas
        self.canvas = tk.Canvas(
            self.world_container,
            width=self.world_size[1],
            height=self.world_size[0],
            borderwidth=1,
            highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky=tk.W)
        self.canvas.bind('<Button-1>', self.click_cell)

    def create_world(self):
        """Create world of cells"""
        for row in range(self.cell_row):
            for col in range(self.cell_col):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if (row, col) in self.world_status.now.keys():
                    self.world[row, col] = self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=self.color_alive,
                        outline="gray",
                        tags="rect")
                else:
                    self.world[row, col] = self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=self.color_dead,
                        outline="gray",
                        tags="rect")

    def life(self, delay):
        """Loop of the Game of Life"""
        # if world is not alive, then do nothing
        if self.world_alive:
            self.world_status.update()
            for cell in [(x, y) for x in range(self.cell_row) for y in range(self.cell_col)]:
                item_id = self.world[cell]
                if cell in self.world_status.now.keys():
                    self.canvas.itemconfig(item_id, fill=self.color_alive)
                else:
                    self.canvas.itemconfig(item_id, fill=self.color_dead)

        self.after(delay, lambda: self.life(delay))

    def prepare_world(self, mode_name):
        """Init status of world with mode selected"""
        self.world_alive = False
        self.world_setable = True
        if mode_name in self.init_modes:
            mode = self.init_modes[mode_name]
            self.world_status.init_status(mode)

        self.init_world = self.world_status.now.copy()
        for cell in [(x, y) for x in range(self.cell_row) for y in range(self.cell_col)]:
            item_id = self.world[cell]
            if cell in self.init_world.keys():
                self.canvas.itemconfig(item_id, fill=self.color_alive)
            else:
                self.canvas.itemconfig(item_id, fill=self.color_dead)

    def save_mode(self):
        """Save init mode to json file"""
        def save_mode_file():
            name = dialog.entry.get()
            self.init_modes[name] = self.init_world.keys()
            with open(self.modes_file, 'wb') as fp:
                json.dump(self.init_modes, fp)
            self.world_alive = old_world_status[0]
            self.world_setable = old_world_status[1]
            self.modes_names.insert(1, name)
            self.modes_selector._list.setlist(self.modes_names)
            self.modes_selector.selectitem(name)
            dialog.destroy()

        old_world_status = [self.world_alive, self.world_setable]
        self.world_alive = False
        self.world_setable = False

        # show a dialog window to get name or new mode
        dialog = tk.Toplevel(self)
        dialog.label = tk.Label(dialog, text="Please enter the name of new mode")
        dialog.label.grid(row=0, column=0, sticky=tk.N)
        dialog.entry = tk.Entry(dialog)
        dialog.entry.grid(row=1, column=0, sticky=tk.N)
        dialog.ok_button = tk.Button(dialog, text="OK", command=save_mode_file)
        dialog.ok_button.grid(row=2, column=0, sticky=tk.N)
        self.wait_window(dialog)

    def run_world(self):
        """Make the world alive"""
        self.world_alive = True
        self.world_setable = False

    def pause_world(self):
        """Pause the world"""
        self.world_alive = False
        self.world_setable = True

    def reset_world(self):
        """Reset world"""
        self.world_alive = False
        self.world_setable = True
        self.world_status.now = self.init_world.copy()
        for cell in [(x, y) for x in range(self.cell_row) for y in range(self.cell_col)]:
            item_id = self.world[cell]
            if cell in self.world_status.now.keys():
                self.canvas.itemconfig(item_id, fill=self.color_alive)
            else:
                self.canvas.itemconfig(item_id, fill=self.color_dead)

    def step_world(self):
        self.world_alive = True
        self.world_setable = False

        self.world_status.update()
        for cell in [(x, y) for x in range(self.cell_row) for y in range(self.cell_col)]:
            item_id = self.world[cell]
            if cell in self.world_status.now.keys():
                self.canvas.itemconfig(item_id, fill=self.color_alive)
            else:
                self.canvas.itemconfig(item_id, fill=self.color_dead)

        self.world_alive = False
        self.world_setable = True

    def click_cell(self, event):
        """Set the cell mouse clicked"""
        if (self.world_setable):
            x, y = event.x, event.y
            row = y // self.cell_size
            col = x // self.cell_size
            if ((row in range(self.cell_row)) and
                    (col in range(self.cell_col))):
                if (row, col) in self.world_status.now.keys():
                    color = self.color_dead
                    self.world_status.now.pop((row, col))
                else:
                    color = self.color_alive
                    self.world_status.now[(row, col)] = True
                item_id = self.world[row, col]
                self.canvas.itemconfig(item_id, fill=color)
                self.init_world = self.world_status.now.copy()


if __name__ == "__main__":
    app = ShowGOL()
    app.mainloop()
