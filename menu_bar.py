import tkinter as tk


def create_menu_bar(self):
    """Create all Menu and Sub-menu with their shortcuts"""

    #############
    #   Menus   #
    #############

    #
    # Menu bar
    #
    self.menu_bar = tk.Menu(
        self,
        # Old config  for all tk.Manu (not useful with ttkbootstrap):
        # bg="#1d1d1d",
        # fg="#ffffff",
        # activebackground="#eeb604",
        # bd=0,
        # relief=tk.FLAT,
    )  # Create menu_bar instance from Menu class

    #
    # File menu
    #
    self.file_menu = tk.Menu(
        self.menu_bar,
    )
    self.menu_bar.add_cascade(label="File", menu=self.file_menu)

    # Open image
    self.file_menu.add_command(
        label="Open image", command=self.load_image, accelerator="Ctrl + O"
    )

    # Open trajectory
    self.file_menu.add_command(
        label="Open trajectory", command=self.load_file, accelerator="Ctrl + T"
    )

    # Save trajectory
    self.file_menu.add_command(
        label="Save trajectory", command=self.save_file, accelerator="Ctrl + S"
    )

    self.file_menu.add_separator()

    # Quit app
    self.file_menu.add_command(
        label="Exit", command=self.menu_quit_clicked, accelerator="Ctrl + Q"
    )

    #
    # Floating panel menu
    #
    self.fp_menu = tk.Menu(
        self.menu_bar,
    )
    self.menu_bar.add_cascade(label="Floating panel", menu=self.fp_menu)

    self.fp_menu.add_command(label="Open", command=self.toggle_panel_open)
    # Old config:
    # self.fp_menu.add_command(label="Resize", command=self.toggle_panel_size)
    self.fp_menu.add_command(label="Close", command=self.toggle_panel_close)

    #
    # Image menu
    #
    self.image_menu = tk.Menu(
        self.menu_bar,
    )
    self.menu_bar.add_cascade(label="Image", menu=self.image_menu)

    # Zoom-in
    self.image_menu.add_command(
        label="Zoom-in", command=lambda: self.zoom(None, 1), accelerator="Ctrl + +"
    )

    # Zoom-out
    self.image_menu.add_command(
        label="Zoom-out", command=lambda: self.zoom(None, 0), accelerator="Ctrl + -"
    )

    # Recenter
    self.image_menu.add_command(
        label="Recenter",
        command=lambda: self.recenter_image(None),
        accelerator="Double right click",
    )

    # Rotate clockwise
    self.image_menu.add_command(
        label="Rotate clockwise",
        command=lambda: self.rotate_image(5),
        accelerator="Ctrl + M",
    )

    # Rotate counterclockwise
    self.image_menu.add_command(
        label="Rotate counterclockwise",
        command=lambda: self.rotate_image(-5),
        accelerator="Ctrl + L",
    )

    #
    # Trajectory menu
    #
    self.trajectory_menu = tk.Menu(
        self.menu_bar,
    )
    self.menu_bar.add_cascade(label="Trajectory", menu=self.trajectory_menu)

    #
    # Coordinate system sub-menu (cs means coordinate system here)
    #
    self.cs_sub_menu = tk.Menu(
        self.trajectory_menu,
    )
    self.trajectory_menu.add_cascade(label="Coordinate system", menu=self.cs_sub_menu)

    # Coordinate system value
    self.cs_sub_menu.add_radiobutton(
        label="Top left",
        variable=self.coordinate_system,
        value="top-left",
        command=lambda: self.wrapper_coordinate_system(),
    )

    self.cs_sub_menu.add_radiobutton(
        label="Bottom left",
        variable=self.coordinate_system,
        value="bottom-left",
        command=lambda: self.wrapper_coordinate_system(),
    )

    #
    # Symmetry checkbutton
    #
    self.trajectory_menu.add_command(
        label="Change symmetry", command=self.toggle_symmetry
    )

    #
    # Angle checkbutton
    #
    self.trajectory_menu.add_checkbutton(
        label="Angle",
        variable=self.angle,
        onvalue=1,
        offvalue=0,
        command=lambda: self.wrapper_angle(),
    )
    # Old config:
    # self.angle_sub_menu = tk.Menu(
    #     self.trajectory_menu,
    # )
    # self.trajectory_menu.add_cascade(label="Angle", menu=self.angle_sub_menu)
    #
    # # Use angle or not
    # self.angle_sub_menu.add_radiobutton(
    #     label="False",
    #     variable=self.angle,
    #     value="false",
    #     command=lambda: self.wrapper_angle(),
    # )
    #
    # self.angle_sub_menu.add_radiobutton(
    #     label="True",
    #     variable=self.angle,
    #     value="true",
    #     command=lambda: self.wrapper_angle(),
    # )

    #
    # Orientation checkbutton
    #
    self.trajectory_menu.add_checkbutton(
        label="Orientation",
        variable=self.orientation,
        onvalue=1,
        offvalue=0,
        command=lambda: self.wrapper_orientation(),
    )

    #
    # Direction checkbutton
    #
    self.trajectory_menu.add_checkbutton(
        label="Direction",
        variable=self.direction,
        onvalue=1,
        offvalue=0,
        command=lambda: self.wrapper_direction(),
    )

    #
    # Action checkbutton
    #
    self.trajectory_menu.add_checkbutton(
        label="Action",
        variable=self.action,
        onvalue=1,
        offvalue=0,
        command=lambda: self.wrapper_action(),
    )

    #
    # Other commands
    #

    # Edit the actions
    self.trajectory_menu.add_command(
        label="Edit actions",
        command=self.toggle_actions_panel,
        accelerator="Control + A",
    )

    # Add a new point
    self.trajectory_menu.add_command(
        label="Add a new point",
        command=self.create_preview,
        accelerator="Control + P",
    )

    # Delete last point
    self.trajectory_menu.add_command(
        label="Delete last point",
        command=lambda: self.delete_point(event=not None),
        accelerator="Middle click",
    )

    # TODO: Option & help menu
    """self.options_menu = tk.Menu(
        self.menu_bar,
        tearoff=tk.OFF,
        bg="#1d1d1d",
        fg="#ffffff",
        activebackground="#eeb604",
        relief=tk.FLAT,
        bd=0,
    )
    self.menu_bar.add_cascade(label="Options & help", menu=self.options_menu)"""

    ###############
    # Arrangement #
    ###############

    self.master.config(menu=self.menu_bar)
