import tkinter as tk


def create_menu_bar(self):
    """Create all Menu and Sub-menu with their shortcuts

    Args:
        self (GUI): the GUI object that is manipulated
    """

    #
    # Menu bar
    #
    self.menu_bar = tk.Menu(
        self,
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

    # Open json file
    self.file_menu.add_command(
        label="Open json",
        command=self.load_file,
        accelerator="Ctrl + J",
    )

    # Save trajectory
    self.file_menu.add_command(
        label="Save trajectory",
        command=lambda data_type="trajectory": self.save_file(data_type),
        accelerator="Ctrl + S",
    )

    self.file_menu.add_separator()

    # Quit app
    self.file_menu.add_command(
        label="Exit", command=self.menu_quit_clicked, accelerator="Ctrl + Q"
    )

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
        command=lambda option_name="coordinate_system",
        option_tk_var=self.coordinate_system: self.wrapper_options(
            option_name, option_tk_var
        ),
    )

    self.cs_sub_menu.add_radiobutton(
        label="Bottom left",
        variable=self.coordinate_system,
        value="bottom-left",
        command=lambda option_name="coordinate_system",
        option_tk_var=self.coordinate_system: self.wrapper_options(
            option_name, option_tk_var
        ),
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
        command=lambda option_name="angle",
        option_tk_var=self.angle: self.wrapper_options(option_name, option_tk_var),
    )

    #
    # Orientation checkbutton
    #
    self.trajectory_menu.add_checkbutton(
        label="Orientation",
        variable=self.orientation,
        onvalue=1,
        offvalue=0,
        command=lambda option_name="orientation",
        option_tk_var=self.orientation: self.wrapper_options(
            option_name, option_tk_var
        ),
    )

    #
    # Direction checkbutton
    #
    self.trajectory_menu.add_checkbutton(
        label="Direction",
        variable=self.direction,
        onvalue=1,
        offvalue=0,
        command=lambda option_name="direction",
        option_tk_var=self.direction: self.wrapper_options(option_name, option_tk_var),
    )

    #
    # Actions checkbutton sub-menu
    #
    self.action_sub_menu = tk.Menu(
        self.trajectory_menu,
    )
    self.trajectory_menu.add_cascade(label="Action", menu=self.action_sub_menu)

    # Action checkbutton
    self.action_sub_menu.add_checkbutton(
        label="Action",
        variable=self.config_action,
        onvalue=1,
        offvalue=0,
        command=lambda option_name="action",
        option_tk_var=self.config_action: self.wrapper_options(
            option_name, option_tk_var
        ),
    )

    if self.config_action.get():
        self.toggle_action_shortcut(True)
        self.toggle_wea_checkbutton(True)
        self.toggle_export_action_checkbutton(True)

        if self.config_export_action.get():
            self.toggle_export_action_command(True)

    #
    # Fbd_area checkbutton sub-menu
    #
    self.fbd_area_sub_menu = tk.Menu(
        self.trajectory_menu,
    )
    self.trajectory_menu.add_cascade(label="Forbiden area", menu=self.fbd_area_sub_menu)

    # Fbd_area checkbutton
    self.fbd_area_sub_menu.add_checkbutton(
        label="Forbiden area",
        variable=self.config_fbd_area,
        onvalue=1,
        offvalue=0,
        command=lambda option_name="fbd_area",
        option_tk_var=self.config_fbd_area: self.wrapper_options(
            option_name, option_tk_var
        ),
    )

    if self.config_fbd_area.get():
        self.toggle_fbd_area_shortcut(True)
        self.toggle_export_fbd_area_checkbutton(True)

        if self.config_export_fbd_area.get():
            self.toggle_export_fbd_area_command(True)

    #
    # Other commands
    #

    # # Edit the actions
    # self.trajectory_menu.add_command(
    #     label="Edit actions",
    #     command=self.toggle_actions_panel,
    #     accelerator="Control + A",
    # )

    # Edit the trajectory
    self.trajectory_menu.add_command(
        label="Edit trajectory",
        command=self.toggle_trajectory_panel,
        accelerator="Control + E",
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

    # Add the menu bar to the main window
    self.master.config(menu=self.menu_bar)


def toggle_action_shortcut(self, toggle_int: int) -> None:
    """Create/bind the fbd_area_shortcut or delete/unbind it, this shortcut can toggle the fbd_area_mode to edit forbiden area

    Args:
        self (GUI): the GUI object that is manipulated
        toggle_int (int): value to know if the shortcut should be displayed or not
    """

    if toggle_int:
        self.action_sub_menu.add_command(
            label="Edit actions",
            command=lambda event: self.toggle_action_panel(),
            accelerator="Control + A",
        )

    else:
        self.action_sub_menu.delete(1)


def toggle_wea_checkbutton(self, toggle_int: int) -> None:
    """Create the wea_checkbutton or delete it

    Args:
        self (GUI): the GUI object that is manipulated
        toggle_int (int): value to know if the checkbutton should be displayed or not
    """

    if toggle_int:
        self.action_sub_menu.add_checkbutton(
            label="Wait end of action",
            variable=self.wea,
            onvalue=1,
            offvalue=0,
            command=lambda option_name="wea",
            option_tk_var=self.wea: self.wrapper_options(option_name, option_tk_var),
        )

    else:
        self.action_sub_menu.delete(1)


def toggle_export_action_checkbutton(self, toggle_int: int) -> None:
    """Create the export_action_checkbutton or delete it

    Args:
        self (GUI): the GUI object that is manipulated
        toggle_int (int): value to know if the checkbutton should be displayed or not
    """

    if toggle_int:
        self.action_sub_menu.add_checkbutton(
            label="Export action in json",
            variable=self.config_export_action,
            onvalue=1,
            offvalue=0,
            command=lambda option_name="export_action",
            option_tk_var=self.config_export_action: self.wrapper_options(
                option_name, option_tk_var
            ),
        )

    else:
        self.action_sub_menu.delete(1)


def toggle_export_action_command(self, toggle_int: int) -> None:
    """Create the save actions command or delete it

    Args:
        self (GUI): the GUI object that is manipulated
        toggle_int (int): value to know if action command should be displayed or not
    """

    if toggle_int:
        self.file_menu.insert_command(
            3,
            label="Save actions",
            command=lambda data_type="action": self.save_file(data_type),
        )

    else:
        _remove_file_menu_command(self, "Save actions")


def toggle_fbd_area_shortcut(self, toggle_int: int) -> None:
    """Create/bind the fbd_area_shortcut or delete/unbind it, this shortcut can toggle the fbd_area_mode to edit forbiden area

    Args:
        self (GUI): the GUI object that is manipulated
        toggle_int (int): value to know if the shortcut should be displayed or not
    """

    if toggle_int:
        self.fbd_area_sub_menu.add_command(
            label="Edit forbiden area",
            command=self.toggle_fbd_area_mode,
            accelerator="Control + F",
        )
        self.bind_forbiden_area_mode()

    else:
        self.fbd_area_sub_menu.delete(1)
        self.unbind_forbiden_area_mode()


def toggle_export_fbd_area_checkbutton(self, toggle_int: int) -> None:
    """Create the export_fbd_area_checkbutton or delete it

    Args:
        self (GUI): the GUI object that is manipulated
        toggle_int (int): value to know if the checkbutton should be displayed or not
    """

    if toggle_int:
        self.fbd_area_sub_menu.add_checkbutton(
            label="Export forbiden area in json",
            variable=self.config_export_fbd_area,
            onvalue=1,
            offvalue=0,
            command=lambda option_name="export_fbd_area",
            option_tk_var=self.config_export_fbd_area: self.wrapper_options(
                option_name, option_tk_var
            ),
        )

    else:
        self.fbd_area_sub_menu.delete(1)


def toggle_export_fbd_area_command(self, toggle_int: int) -> None:
    """Create the save forbiden area command or delete it

    Args:
        self (GUI): the GUI object that is manipulated
        toggle_int (int): value to know if action command should be displayed or not
    """

    if toggle_int:
        self.file_menu.insert_command(
            3,
            label="Save forbiden area",
            command=lambda data_type="fbd_area": self.save_file(data_type),
        )

    else:
        _remove_file_menu_command(self, "Save forbiden area")


def _remove_file_menu_command(self, label: str) -> None:
    """Remove a command from the file_menu based on its label

    Args:
        self (GUI): the GUI object that is manipulated
        label (str): the label that represent the command tha will be deleted
    """

    for i in range(self.file_menu.index("end") + 1):
        if self.file_menu.entrycget(i, "label") == label:
            self.file_menu.delete(i)
            break
