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
    self.select_point_bind = self.master.bind("<Button-1>", self.select_point)

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
    self.master.bind("<Control-p>", self.create_preview)

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
    # Open trajectory file / control + t
    #
    self.menu_bar.bind_all("<Control-t>", self.load_file)

    #
    # Save current trajectory to a file / control + s
    #
    self.menu_bar.bind_all(
        "<Control-s>",
        lambda event=None, data_type="trajectory": self.save_file(event, data_type),
    )

    #
    # Close the app / control + q
    #
    self.menu_bar.bind_all("<Control-q>", self.menu_quit_clicked)

    #
    # Close or open the actions_panel / control + a
    #
    self.menu_bar.bind_all("<Control-a>", self.toggle_actions_panel)

    #
    # Close or open the actions_panel / control + a
    #
    self.menu_bar.bind_all("<Control-e>", self.toggle_trajectory_panel)
