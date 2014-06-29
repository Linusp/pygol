#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tkinter as tk
import Pmw
import json


class GOL():
    """Status manager of GOL(Game of Life).

    Each world in game of life is a set of cells, and status of
    every cell should be alive or dead. Status changes from gen
    -eration to generation.
    """
    def __init__(self, row = 0, col = 0, init_cells={}):
        """Init size and status of world."""
        self.row = row
        self.col = col
        self.now = {}
        self.next = {}
        self.set_status(init_cells)

    def set_status(self, init_cells):
        """Set status of world.

        if the begining status given is not empty, then use them
        to initialize the world.

        Args:
            init_cells: begining status given. It's a tow-dimensional
                        array. Becase its size maybe smaller than the
                        world, we should be map each coordinate to the
                        center area of world.
        """

        # get size of begining status set
        init_row, init_col = len(init_cells), len(init_cells[0])
        # compute offset in row direction and column direction
        row_off = (self.row - row_off) / 2
        col_off = (self.col - col_off) / 2

        # check size
        if (row_off < 0 or col_off < 0):
            raise Exception("Size of begining status set is beyond
            size of world")

        # create the world
        for crow in range(self.row):
            for ccol in range(self.col):
                if (crow in range(row_off, row_off + init_row)
                    and
                    ccol in range(col_off, col_off + init_col)):
                    self.now[crow, ccol] = status[crow][ccol]
                else:
                    self.now[crow, ccol] = False;
                self.next[crow, ccol] = False;

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
        for crow in range(self.row):
            for ccol in range(self.col):
                alive_around = neighbors(crow, ccol)
                if (alive_around < 2 or alive_around > 3):
                    self.next[row, col] = False
                elif ((not self.now[row, col]) and
                      alive_around == 3):
                    self.next[row, col] = True

        self.now = self.next
        return self.now

    def neighbors(self, row, col):
        """Compute number of alive neighbors around a cell."""
        alive_around = 0
        for i in range(row -1, row + 2):
            for j in range(col - 1, col + 2):
                irow = i % CELL_ROW
                icol = j % CELL_COL
                if (not (irow == row and icol == col)):
                    if (self.now[irow, icol]):
                        alive_around = alive_around + 1

        return alive_around


class ShowGOL(tk.Tk):
    """Diasplay the Game of Life

    Use Tkinter to draw the world of cells and the changes in
    the world.
    """
    def __init__(self, **args, **kwargs):
        """Init resource and world"""
        # init resource
        tk.Tk.__init__(self, *args, **kwargs)
        self.setup_members()    # initialize class members
        self.setup_window()     # root window
        self.setup_toolbar()    # tool bar
        self.setup_canvas()     # canvas to draw world

        # init world
        self.create_world()

        # make world alive
        self.after(10, lambda: self.life(10))

    def setup_members(self):
        """Initialize class members

        These members are main information of class.They are information
        of status, widget, resource and so on
        """
        ### cell
        self.cell_size = 10
        self.cell_row = 60
        self.cell_col = 80
        self.color_alive = "black"
        self.color_dead = "white"

        ### world
        self.init_modes = {}    # read modes from json file
        self.init_world = {}    # begining status
        self.world = {}         # world's map
        # current status of world
        self.world_status = GOL(self.cell_row, self.cell_col)
        self.world_setable = True

        # widgets
        self.toolbar_height = 40
        self.world_size = [self.cell_size * self.cell_row,
                           self.cell_size * self.cell_col]
        self.window_size = self.world_size
        self.window_size[1] += self.toolbar_height

        # resource
        self.saver_icon = "save.gif"
        self.run_icon = "run.gif"
        self.pause_icon = "pause.gif"
        self.stop_icon = "stop.gif"
        self.modes_file = "gol.json"

    def setup_window(self):
        """Create root window"""
        # make window in the center of screen
        scrn_width, scrn_height = self.maxsize()
        win_width, win_height = self.window_size
        location = '%dx%d+%d+%d'%(win_width, win_width,
                                  (scrn_width - win_width) / 2,
                                  (scrn_height - win_height) / 2)
        self.geometry(location)

        # set title
        self.title("Game of life")

    def setup_toolbar(self):
        """Create tool bar"""
        # create frame to contain buttons
        self.toolbar = tk.Frame(self, height=self.toolbar_height)
        self.toolbar.grid(row = 0, column = 0,
                          sticky = tk.N+tk.S+tk.W+tk.E)

        # set tools
        self.setup_mode_selector()
        self.setup_mode_saver()
        self.setup_button_run()
        self.setup_button_pause()
        self.setup_button_stop()

    def setup_mode_selector(self):
        """Mode selector

        User can select begining status of the world already exists,
        these status are called 'modes' here, and modes are save in
        file with json format
        """
        # read modes from json file
        # TODO use more simple ways to read
        modes_reader = file(self.modes_file)
        modes_json = modes_reader()
        self.init_modes = JSONDecoder().decode(modes_json)

        # set selector
        modes_names = self.init_modes.keys()
        modes_names.insert(0, "Set by hand")
        self.modes_selector = Pmw.ComboBox(
            self.toolbar,
            label_text = 'Modes selector',
            labelpos = 'nw',
            selectioncommand = self.set_world, # TODO method self.set_world
            scrolledlist_items = modes_names,
            )
        self.modes_selector.grid(row = 0, column = 0, sticky = tk.W)
        first = modes_names[0]
        self.modes_selector.selectitem(first)
        self.set_world(first)

    def setup_mode_saver(self):
        """Mode saver

        User can save begining status set by hand to json file.
        Sharing this json file with friends is also a good idea.
        """
        saver_icon = PhotoImage(file = self.saver_icon)
        self.saver_button = tk.Button(
            self.toolbar,
            width = 30,
            height = 30,
            image = saver_icon,
            command = self.save_mode) # TODO method self.save_mode
        self.saver_button.image = saver_icon
        self.saver_button.grid(row = 0, column = 1, sticky = tk.W)

    def setup_button_run(self):
        """Button to run the Game of Life"""
        run_icon = PhotoImage(file = self.run_icon)
        self.button_run = tk.Button(
            self.toolbar,
            width = 30,
            height = 30,
            image = run_icon,
            command = self.run_world) # TODO method self.run_world
        self.button_run.image = run_icon
        self.button_run.grid(row = 0, column = 2, sticky = tk.W)

    def setaup_button_pause(self):
        """Button to pause the Game of Life"""
        pause_icon = PhotoImage(file = self.pause_icon)
        self.button_pause = tk.Button(
            self.toolbar,
            width = 30,
            height = 30,
            image = pause_icon,
            command = self.pause_world) # TODO method self.pause_world
        self.button_pause.image = pause_icon
        self.button_pause.grid(row = 0, column = 3, sticky = tk.W)

    def setup_button_stop():
        """Button to stop the Game of Life

        stopping will set the world to a status initialized using
        the current item in modes selector
        """
        stop_icon = tk.PhotoImage(file = self.stop_icon)
        self.button_stop = tk.Button(
            self.toolbar,
            width = 30,
            height = 30,
            image = stop_icon,
            command=self.reset_world) # TODO method self.reset_world
        self.button_stop.image = stop_icon
        self.button_stop.grid(row = 0, column = 4, sticky=tk.W)


    def setup_canvas(self):
        """Add canvas to root window"""
        # create frame to contain canvas
        self.world = tk.Frame(self, height = self.world_size[1])
        self.world.grid(row = 1, column = 0, sticky = tk.W+tk.N)

        # create canvas
        self.canvas = tk.Canvas(
            self.world,
            width = self.world_size[0]
            height = self.world_size[1]
            borderwidth = 1,
            highlightthickness = 0)
        self.canvas.grid(row = 0, column = 0, sticky = tk.W)
        self.canvas.bind('<Button-1>', self.set_cell) # TODO method self.set_cell


    def create_world(self):
        """Create world of cells"""
        for row in range(self.cell_row):
            for col in range(self.cell_col):
                x1 = col * self.cellwidth
                y1 = row * self.cellheight
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellheight

                # TODO method GOL.get
                if (self.world_status.get(row, col)):
                    self.rect[row, col] =
                    self.canvas.create_rectangle(x1, y1, x2, y2,
                                                 fill = self.color_alive,
                                                 tags = "rect")
                else:
                    self.rect[row, col] =
                    self.canvas.create_rectangle(x1, y1, x2, y2,
                                                 fill = self.color_dead
                                                 tags="rect")

    def life(self, delay):
        """Loop of the Game of Life"""
        # if world still be setable, then should
        # not make world alive
        if (not self.world_setable):
            self.world_status.update()
            for row in range(self.cell_row):
                for col in range(self.cell_col):
                    item_id = self.rect[row, col]
                    if (self.world_status.get(row, col)):
                        self.canvas.itemconfig(item_id,
                                               fill = self.color_alive)
                    else:
                        self.canvas.itemconfig(item_id,
                                               fill = self.color_dead)

            self.after(delay, lambda: self.life(delay))


if __name__ == "__main__":
    app = ShowGOL()
    app.mainloop()
