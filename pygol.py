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
    def __init__(self, row = 0, col = 0):
        """Init size and status of world."""
        self.row = row
        self.col = col
        self.now = {}
        self.next = {}
        self.init_status([])

    def init_status(self, init_cells):
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
        init_row = len(init_cells)
        if (init_row == 0):
            init_col = 0
        else:
            init_col = len(init_cells[0])
        # compute offset in row direction and column direction
        row_off = (self.row - init_row) / 2
        col_off = (self.col - init_col) / 2

        # check size
        if (row_off < 0 or col_off < 0):
            raise Exception("Size of begining status set is too large")

        # create the world
        for crow in range(self.row):
            for ccol in range(self.col):
                srow = crow - row_off
                scol = ccol - col_off
                if (crow in range(row_off, row_off + init_row)
                    and
                    ccol in range(col_off, col_off + init_col)):
                    self.now[crow, ccol] = init_cells[srow][scol]
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
        self.next = self.now.copy()
        for crow in range(self.row):
            for ccol in range(self.col):
                around = self.neighbors(crow, ccol)
                if (around < 2 or around > 3):
                    self.next[crow, ccol] = False

                elif ((not self.now[crow, ccol]) and
                      around == 3):
                    self.next[crow, ccol] = True

        self.now = self.next.copy()
        return self.now

    def neighbors(self, row, col):
        """Compute number of alive neighbors around a cell."""
        alive_around = 0
        for i in range(row -1, row + 2):
            for j in range(col - 1, col + 2):
                irow = i % self.row
                icol = j % self.col
                if (not (irow == row and icol == col)):
                    if (self.now[irow, icol]):
                        alive_around = alive_around + 1

        return alive_around


class ShowGOL(tk.Tk):
    """Diasplay the Game of Life

    Use Tkinter to draw the world of cells and the changes in
    the world.
    """
    def __init__(self, *args, **kwargs):
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
        self.after(5, lambda: self.life(5))

    def setup_members(self):
        """Initialize class members

        These members are main information of class.They are information
        of status, widget, resource and so on
        """
        ### cell
        self.cell_size = 8
        self.cell_row = 80
        self.cell_col = 100
        self.color_alive = "black"
        self.color_dead = "white"

        ### world
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
        self.saver_icon = "save.gif"
        self.run_icon = "run.gif"
        self.pause_icon = "pause.gif"
        self.stop_icon = "stop.gif"
        self.modes_file = "gol.json"
        self.modes_names = []

    def setup_window(self):
        """Create root window"""
        # make window in the center of screen
        scrn_width, scrn_height = self.maxsize()
        win_height, win_width = self.window_size
        location = '%dx%d+%d+%d'%(win_width, win_height,
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
        self.init_modes = json.load(modes_reader)

        # set selector
        self.modes_names = self.init_modes.keys()
        self.modes_names.insert(0, "Set by hand")
        self.modes_selector = Pmw.ComboBox(
            self.toolbar,
            label_text = 'Modes selector',
            labelpos = 'nw',
            selectioncommand = self.prepare_world,
            scrolledlist_items = self.modes_names,
            )
        self.modes_selector.grid(row = 0, column = 0, sticky = tk.W)
        first = self.modes_names[0]
        self.modes_selector.selectitem(first)
        self.prepare_world(first)

    def setup_mode_saver(self):
        """Mode saver

        User can save begining status set by hand to json file.
        Sharing this json file with friends is also a good idea.
        """
        saver_icon = tk.PhotoImage(file = self.saver_icon)
        self.saver_button = tk.Button(
            self.toolbar,
            width = 24,
            height = 24,
            image = saver_icon,
            command = self.save_mode)
        self.saver_button.image = saver_icon
        self.saver_button.grid(row = 0, column = 1, sticky = tk.W)

    def setup_button_run(self):
        """Button to run the Game of Life"""
        run_icon = tk.PhotoImage(file = self.run_icon)
        self.button_run = tk.Button(
            self.toolbar,
            width = 24,
            height = 24,
            image = run_icon,
            command = self.run_world)
        self.button_run.image = run_icon
        self.button_run.grid(row = 0, column = 2, sticky = tk.W)

    def setup_button_pause(self):
        """Button to pause the Game of Life"""
        pause_icon = tk.PhotoImage(file = self.pause_icon)
        self.button_pause = tk.Button(
            self.toolbar,
            width = 24,
            height = 24,
            image = pause_icon,
            command = self.pause_world)
        self.button_pause.image = pause_icon
        self.button_pause.grid(row = 0, column = 3, sticky = tk.W)

    def setup_button_stop(self):
        """Button to stop the Game of Life

        stopping will set the world to a status initialized using
        the current item in modes selector
        """
        stop_icon = tk.PhotoImage(file = self.stop_icon)
        self.button_stop = tk.Button(
            self.toolbar,
            width = 24,
            height = 24,
            image = stop_icon,
            command=self.reset_world)
        self.button_stop.image = stop_icon
        self.button_stop.grid(row = 0, column = 4, sticky=tk.W)

    def setup_canvas(self):
        """Add canvas to root window"""
        # create frame to contain canvas
        self.world_container = tk.Frame(self,
                                        width = self.world_size[1],
                                        height = self.world_size[0])
        self.world_container.grid(row = 1, column = 0, sticky = tk.W+tk.N)

        # create canvas
        self.canvas = tk.Canvas(
            self.world_container,
            width = self.world_size[1],
            height = self.world_size[0],
            borderwidth = 1,
            highlightthickness = 0)
        self.canvas.grid(row = 0, column = 0, sticky = tk.W)
        self.canvas.bind('<Button-1>', self.click_cell)

    def create_world(self):
        """Create world of cells"""
        for row in range(self.cell_row):
            for col in range(self.cell_col):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if (self.world_status.now[row, col]):
                    self.world[row, col] = self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill = self.color_alive,
                        outline = "gray",
                        tags = "rect")
                else:
                    self.world[row, col] = self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill = self.color_dead,
                        outline = "gray",
                        tags = "rect")

    def life(self, delay):
        """Loop of the Game of Life"""
        # if world is not alive, then do nothing
        if (self.world_alive):
            self.world_status.update()
            for row in range(self.cell_row):
                for col in range(self.cell_col):
                    item_id = self.world[row, col]
                    if (self.world_status.now[row, col]):
                        self.canvas.itemconfig(item_id,
                                               fill = self.color_alive)
                    else:
                        self.canvas.itemconfig(item_id,
                                               fill = self.color_dead)

        self.after(delay, lambda: self.life(delay))

    def prepare_world(self, mode_name):
        """Init status of world with mode selected"""
        self.world_alive = False
        self.world_setable = True
        if (self.init_modes.has_key(mode_name)):
            mode = self.init_modes[mode_name]
            self.world_status.init_status(mode)

        self.init_world = self.world_status.now.copy()
        if (not (len(self.world) == 0)):
            for row in range(self.cell_row):
                for col in range(self.cell_col):
                    item_id = self.world[row, col]
                    if (self.world_status.now[row, col]):
                        self.canvas.itemconfig(item_id,
                                               fill = self.color_alive)
                    else:
                        self.canvas.itemconfig(item_id,
                                               fill = self.color_dead)

    def save_mode(self):
        """Save init mode to json file"""
        def save_mode_file():
            name = dialog.entry.get()
            self.init_modes[name] = self.save_list
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
        lu_row = 0
        lu_col = 0
        rb_row = self.cell_row - 1
        rb_col = self.cell_col - 1
        for row in range(self.cell_row):
            for col in range(self.cell_col):
                if (self.init_world[row, col]):
                    lu_row = row
                    break

        for col in range(self.cell_col):
            for row in range(self.cell_row):
                if (self.init_world[row, col]):
                    lu_col = col
                    break

        for row in range(self.cell_row - 1, -1, -1):
            for col in range(self.cell_col - 1, -1 , -1):
                if (self.init_world[row, col]):
                    rb_row = row
                    break

        for col in range(self.cell_col - 1, -1, -1):
            for row in range(self.cell_row -1, -1, -1):
                if (self.init_world[row, col]):
                    rb_col = col
                    break

        self.save_list = [[False for col in range(rb_col, lu_col + 1)]
                          for row in range(rb_row, lu_row + 1)]

        for row in range(rb_row, lu_row + 1):
            for col in range(rb_col, lu_col + 1):
                self.save_list[row - rb_row][col - rb_col] = self.init_world[
                                              row, col]

        # show a dialog window to get name or new mode
        dialog = tk.Toplevel(self)
        dialog.label = tk.Label(dialog, text="Please enter the name of new mode")
        dialog.label.grid(row = 0, column = 0, sticky = tk.N)
        dialog.entry = tk.Entry(dialog)
        dialog.entry.grid(row = 1, column = 0, sticky = tk.N)
        dialog.ok_button = tk.Button(dialog, text = "OK", command = save_mode_file)
        dialog.ok_button.grid(row = 2, column = 0, sticky = tk.N)
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
        for row in range(self.cell_row):
            for col in range(self.cell_col):
                item_id = self.world[row, col]
                if (self.world_status.now[row, col]):
                    self.canvas.itemconfig(item_id,
                                           fill = self.color_alive)
                else:
                    self.canvas.itemconfig(item_id,
                                           fill = self.color_dead)

    def click_cell(self, event):
        """Set the cell mouse clicked"""
        if (self.world_setable):
            x, y = event.x, event.y
            row = y / self.cell_size
            col = x / self.cell_size
            if ((row in range(self.cell_row)) and
                (col in range(self.cell_col))):
                status_now = not self.world_status.now[row, col]
                if (status_now):
                    color = self.color_alive
                else:
                    color = self.color_dead
                item_id = self.world[row, col]
                self.canvas.itemconfig(item_id, fill=color)
                self.world_status.now[row, col] = status_now
                self.world_status.next = self.world_status.now.copy()
                self.init_world = self.world_status.now.copy()


if __name__ == "__main__":
    app = ShowGOL()
    app.mainloop()
