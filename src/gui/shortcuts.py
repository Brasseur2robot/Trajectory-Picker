import tkinter as tk


def create_default_shortcuts(self):
    """Create all shortcuts for master and menu bar

    Args:
        self (GUI): the GUI object that is manipulated
    """

    #############
    #   Mouse   #
    #############

    # Master

    #
    # Select a point / left click
    #
    self.bind_select_point()

    #
    # Delete last point / mousewheel click
    #
    self.master.bind("<Button-2>", self.delete_point)

    #
    # Set the current coordinates to move the image / right click
    #
    self.master.bind("<Button-3>", self.set_move_image)

    #
    # Move the image / right click with movement
    #
    self.master.bind("<B3-Motion>", self.move_image)

    #
    # Change coordinates in the info bar / mouse movement
    #
    self.master.bind("<Motion>", self.change_coordinates)

    #
    # Recenter the image / double right click
    #
    self.master.bind("<Double-Button-3>", self.recenter_image)

    #
    # Zoom / mouse wheel
    #
    self.master.bind("<MouseWheel>", self.zoom)

    ##############
    #  Keyboard  #
    ##############

    # Master

    #
    # Create a point / control + p
    #
    self.create_preview_bind = self.master.bind("<Control-p>", self.create_preview)

    #
    # Zoom-in / control + +
    #
    self.master.bind("<Control-equal>", lambda event: self.zoom(event, 1))

    #
    # Zoom-out / control + -
    #
    self.master.bind("<Control-minus>", lambda event: self.zoom(event, 0))

    #
    # Rotate image clockwise / control + m
    #
    # The following bind didn't worked with leftarrow and rightarrow :(
    self.master.bind(
        "<Control-m>",
        lambda event: self.rotate_image(5.0),
    )

    #
    # Rotate image counterclockwise / control + l
    #
    self.master.bind("<Control-l>", lambda event: self.rotate_image(-5.0))

    #
    # Delete selected point
    #
    self.master.bind(
        "<Delete>",
        lambda event, selection_mode=True: self.delete_point(event, selection_mode),
    )

    # Menu bar

    #
    # Open image to load/ control + o
    #
    self.menu_bar.bind_all("<Control-o>", self.load_image)

    #
    # Open trajectory file / control + j
    #
    self.menu_bar.bind_all("<Control-j>", self.load_file)

    #
    # Save current trajectory to a file / control + s
    #
    self.menu_bar.bind_all(
        "<Control-s>",
        lambda event, data_type="trajectory": self.save_file(data_type),
    )

    #
    # Close the app / control + q
    #
    self.menu_bar.bind_all("<Control-q>", self.menu_quit_clicked)

    #
    # Close or open the actions_panel / control + a
    #
    self.menu_bar.bind_all("<Control-a>", lambda event: self.toggle_action_panel())

    #
    # Close or open the trajectory_panel / control + e
    #
    self.menu_bar.bind_all("<Control-e>", self.toggle_trajectory_panel)


def bind_select_point(self) -> None:
    """Create the bind to select a point

    Args:
        self (GUI): the GUI object that is manipulated
    """

    self.select_point_bind = self.master.bind("<Button-1>", self.select_point)


def unbind_select_point(self) -> None:
    """Unbind the previous created bind to select a point

    Args:
        self (GUI): the GUI object that is manipulated
    """

    self.master.unbind("<Button-1>", self.select_point_bind)


def binds_preview(self) -> None:
    """Create the binds for the preview point

    Args:
        self (GUI): the GUI object that is manipulated
    """

    self.preview_motion_bind = self.canvas.bind("<Motion>", self.move_preview)
    self.preview_button_bind = self.canvas.bind("<Button-1>", self.create_point)
    self.preview_escape_bind = self.master.bind("<Escape>", self.leave_preview)


def unbinds_preview(self) -> None:
    """Unbind the previous created bind for the preview point

    Args:
        self (GUI): the GUI object that is manipulated
    """

    self.canvas.unbind("<Motion>", self.preview_motion_bind)
    self.canvas.unbind("<Button-1>", self.preview_button_bind)
    self.master.unbind("<Escape>", self.preview_escape_bind)


def bind_forbiden_area_mode(self) -> None:
    """Create the bind to swap to the fbd_area_mode

    Args:
        self (GUI): the GUI object that is manipulated
    """

    self.fbd_area_mode_bind = self.menu_bar.bind_all(
        "<Control-f>", self.toggle_fbd_area_mode
    )


def unbind_forbiden_area_mode(self) -> None:
    """Undind the previous created bind to swap to the fbd_area_mode

    Args:
        self (GUI): the GUI object that is manipulated
    """

    self.menu_bar.unbind("<Button-f>", self.fbd_area_mode_bind)


def binds_forbiden_area(self) -> None:
    """Create the binds to draw a forbiden area

    Args:
        self (GUI): the GUI object that is manipulated
    """

    self.fbd_area_start_bind = self.canvas.bind("<Button-1>", self.fbd_area_start)
    self.fbd_area_update_bind = self.canvas.bind("<B1-Motion>", self.fbd_area_update)
    self.fbd_area_end_bind = self.canvas.bind("<ButtonRelease-1>", self.fbd_area_end)
    self.fbd_area_escape_bind = self.master.bind("<Escape>", self.fbd_area_escape)


def unbinds_forbiden_area(self) -> None:
    """Unbind the previous created bind for the drawing of a forbiden area

    Args:
        self (GUI): the GUI object that is manipulated
    """

    self.canvas.unbind("<Button-1>", self.fbd_area_start_bind)
    self.canvas.unbind("<B1-Motion>", self.fbd_area_update_bind)
    self.canvas.unbind("<ButtonRelease-1>", self.fbd_area_end_bind)
    self.canvas.unbind("<Escape>", self.fbd_area_escape_bind)
