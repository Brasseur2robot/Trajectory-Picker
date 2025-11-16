import enum
import tkinter as tk
from tkinter import image_names, ttk, messagebox
import numpy as np

from trajectory_manager import update_trajectory

MIN_HEIGHT = 320
MIN_WIDTH = 300


def toggle_trajectory_panel(self, event=None) -> None:
    """Create the trajectory panel or remove it

    Args:
        self (GUI): the GUI object that is manipulated
        event (tkinter.Event): set to None here because not used
    """

    # Create the panel if it don't exist
    if self.trajectory_panel is None or not self.trajectory_panel.winfo_exists():
        # Panel creation
        self.trajectory_panel = tk.Toplevel(self.master)

        self.trajectory_panel.title("Trajectory panel")
        self.trajectory_panel.overrideredirect(True)
        self.trajectory_panel.geometry(f"{MIN_WIDTH}x{MIN_HEIGHT}")
        self.trajectory_panel.minsize(height=MIN_HEIGHT, width=MIN_WIDTH)

        # Main frame (everything is inside it)
        main_frame = ttk.Frame(self.trajectory_panel)
        main_frame.pack(fill=tk.X)

        # Title bar
        titlebar_frame = ttk.Frame(main_frame)
        titlebar_frame.pack(fill=tk.X)

        titlebar_frame.pack_propagate(False)  # Disable resizing based on child widgets
        titlebar_frame.config(
            height=20
        )  # Set the height of the titlebar, can't do it if pack is not desactivate

        titlebar_label = ttk.Label(
            titlebar_frame,
            text="Floating Panel",
        )
        titlebar_label.pack(side=tk.LEFT, padx=5)

        # Titlebar / content separator
        separator_frame = ttk.Frame(main_frame, style="primary.TFrame", height="2")
        separator_frame.pack(fill="x")

        # Content inside the panel
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(expand=True, fill=tk.BOTH)

        # A grid is used here to separate the scrollable zone (row 0 - scroll_frame) from the button zone (row 1 - button_frame)
        content_frame.rowconfigure(0, weight=1)
        content_frame.columnconfigure(0, weight=1)

        # Defining the frame where scrollable content will be displayed
        scroll_frame = ttk.Frame(content_frame)
        scroll_frame.grid(row=0, column=0, sticky="nsew")

        # Creating a canvas to use ttk.Scrollbar inside
        self.trajectory_form_canvas = tk.Canvas(scroll_frame)
        self.trajectory_form_canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            scroll_frame, orient="vertical", command=self.trajectory_form_canvas.yview
        )
        scrollbar.pack(side="right", fill="y")

        # Linking the scrollbar to the canvas
        self.trajectory_form_canvas.configure(yscrollcommand=scrollbar.set)
        self.trajectory_form_canvas.bind(
            "<Configure>",
            lambda event: self.trajectory_form_canvas.configure(
                scrollregion=self.trajectory_form_canvas.bbox("all")
            ),
        )

        # Function and binding to use the mousewheel for scrolling
        self.trajectory_panel.bind(
            "<Button-4>",
            lambda event: self.trajectory_form_canvas.yview_scroll(-1, "units"),
        )
        self.trajectory_panel.bind(
            "<Button-5>",
            lambda event: self.trajectory_form_canvas.yview_scroll(1, "units"),
        )

        # Need to be tested for Windows
        # def _on_mousewheel(event):
        #     canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        #
        # canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Content inside the canvas where the content will be displayed
        self.trajectory_form_frame = ttk.Frame(self.trajectory_form_canvas)
        self.trajectory_form_canvas.create_window(
            (0, 0), window=self.trajectory_form_frame, anchor="nw"
        )

        # Frame without scroll for the close button
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=1, column=0, pady=10)

        # Delete points button
        ttk.Button(
            button_frame,
            text="Delete point(s)",
            command=self.delete_point,
        ).pack()

        # self.trajectory_panel_text_widget = tk.Text(
        #     self.trajectory_panel_content,
        #     bg="#262626",
        #     fg="#ffffff",
        #     bd=0,
        #     highlightthickness=0,
        #     height=13,
        #     width=40,
        # )
        # self.trajectory_panel_text_widget.pack(padx=10, pady=10)

        # Enable dragging the panel
        # TODO: Need to be tested on Windows to see if it's working without
        """
        for widget in (self.panel_title_label, self.panel_titlebar):
            widget.bind("<Button-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.do_drag)"""

        _create_trajectory_panel_content(self)

    # Delete the panel if it exist
    else:
        self.trajectory_panel.destroy()


def update_trajectory_panel_content(
    self, delete_point_idx: list[int] | int | None = None
) -> None:
    """Delete, add & update the point_frames depending of the context

    Args:
        self (GUI): the GUI object that is manipulated
        delete_point_idx (list[int] | int | None): index (list or only one) of the point_frame(s) to delete
    """

    # Delete point cases
    if isinstance(delete_point_idx, int):
        _delete_point_frame(self, delete_point_idx)

    elif isinstance(delete_point_idx, list):
        for index in delete_point_idx:
            _delete_point_frame(self, index)

    # Add point case
    if len(self.trajectory_point_frames) + 1 == len(self.image_points):
        _add_point_frame(self)

    # Clear the var to not delete non existent index based on the checkbox widgets values (see delete_point in main_panel.py)
    self.checkbox_del_widgets.clear()

    # Update the point_frames content
    for i in range(len(self.image_points)):
        point_frame = self.trajectory_point_frames[i]
        _clear_frame(point_frame)
        # point_frame.grid_forget()
        _update_point_frame(self, i)

    # Without the following the freshly created items aren't displayed inside the scrollregion if there is too much widget
    self.trajectory_panel.update_idletasks()  # Ensure every widget are displayed before the next command
    self.trajectory_form_canvas.configure(
        scrollregion=self.trajectory_form_canvas.bbox(
            "all"
        )  # Update the scrollregion to display all widgets
    )


def _delete_point_frame(self, delete_point_idx: int) -> None:
    """Delete a specific point_frame based on the delete_point_idx

    Args:
        self (GUI): the GUI object that is manipulated
        delete_point_idx (int): index of the point_frame to delete
    """

    point_frame_to_delete = self.trajectory_point_frames[delete_point_idx]
    self.trajectory_point_frames.pop(delete_point_idx)
    point_frame_to_delete.destroy()

    for i, frame in enumerate(self.trajectory_point_frames):
        frame.grid_forget()
        frame.grid(row=i, column=0, pady=10)


def _add_point_frame(self) -> None:
    """Create a new point_frame at the end of the others

    Args:
        self (GUI): the GUI object that is manipulated
    """

    point_frame = ttk.Frame(self.trajectory_form_frame)
    point_frame.grid(row=len(self.image_points) - 1, column=0, pady=10)
    self.trajectory_point_frames.append(point_frame)


def _clear_frame(frame: tk.Frame) -> None:
    """Remove all widgets from a tk.Frame object

    Args:
        frame: tk.Frame object that need all his widgets to be destroyed
    """

    for widget in frame.winfo_children():
        widget.destroy()


def _create_trajectory_panel_content(self) -> None:
    """Reset precedent content, init layout & add content

    Args:
        self (GUI): the GUI object that is manipulated
    """

    # Clear precedent content
    self.checkbox_del_widgets.clear()
    self.trajectory_point_frames = []

    # Init the point_frames layout
    for i in range(len(self.image_points)):
        point_frame = ttk.Frame(self.trajectory_form_frame)
        point_frame.grid(row=i, column=0, pady=10)
        self.trajectory_point_frames.append(point_frame)

    # Add content to the point_frames
    update_trajectory_panel_content(self)


def _update_point_frame(self, idx: int) -> None:
    """(Re)create every widget inside the point_frame and update their content
    A better way to do it is to update only their content and not to recreate them each time

    Args:
        self (GUI): the GUI object that is manipulated
        idx (int): index of frame content that is updated
    """

    point_frame = self.trajectory_point_frames[idx]
    x, y, angle, orientation, direction, wea, action = self.image_points[idx]
    options_number = 2

    #
    # Checkbox
    #
    check_var = tk.IntVar()
    checkbox = ttk.Checkbutton(
        point_frame,
        variable=check_var,
    )
    self.checkbox_del_widgets.insert(idx, check_var)
    checkbox.grid(row=0, column=0, padx=(10, 0))

    #
    # Point name
    #
    label = ttk.Label(
        point_frame,
        text=f"Point n°{idx + 1}:",
    )
    label.grid(row=0, column=1)

    #
    # X label
    #
    label = ttk.Label(point_frame, text="x:")
    label.grid(row=1, column=1, padx=(58, 0))

    #
    # X entry
    #
    x_string = tk.StringVar()
    x_entry = ttk.Entry(
        point_frame,
        width=8,
        textvariable=x_string,
    )
    x_entry.insert(
        0, format(x, ".0f") if x else ""
    )  # Set the initial value to the current x rounded
    x_string.trace_add(
        "write",
        lambda *args, new_x=x_string, idx=idx: _coordinate_entry_change(
            self, new_x=new_x.get(), idx=idx
        ),
    )
    x_entry.grid(row=1, column=2, padx=(0, 75))

    #
    # Y label
    #
    label = ttk.Label(point_frame, text="y:")
    label.grid(row=2, column=1, padx=(58, 0))

    #
    # Y entry
    #
    y_string = tk.StringVar()
    y_entry = ttk.Entry(
        point_frame,
        width=8,
        textvariable=y_string,
    )
    y_entry.insert(
        0, format(y, ".0f") if y else ""
    )  # Set the initial value to the current x rounded
    y_string.trace_add(
        "write",
        lambda *args, new_y=y_string, idx=idx: _coordinate_entry_change(
            self, new_y=new_y.get(), idx=idx
        ),
    )
    y_entry.grid(row=2, column=2, padx=(0, 75))

    #
    # Angle
    #
    if self.angle.get():
        options_number += 1

        #
        # Angle labels
        #
        label = ttk.Label(point_frame, text="angle:")
        label.grid(row=options_number, column=1, padx=(32, 0))
        angle_output = f"{format(angle, '.0f')}°" if angle is not None else ""
        label = ttk.Label(point_frame, text=angle_output)
        label.grid(row=options_number, column=2, padx=(0, 75))

    #
    # Orientation
    #
    if self.orientation.get():
        options_number += 1

        #
        # Orientation label
        #
        label = ttk.Label(point_frame, text="orientation:")
        label.grid(row=options_number, column=1)

        #
        # Orientation entry
        #
        orientation_string = tk.StringVar()
        orientation_entry = ttk.Entry(
            point_frame,
            width=8,
            textvariable=orientation_string,
        )
        orientation_string.trace_add(
            "write",
            lambda *args,
            new_orientation=orientation_string,
            idx=idx: _orientation_entry_change(self, new_orientation.get(), idx),
        )
        orientation_entry.insert(
            0, format(orientation, ".0f") if orientation else ""
        )  # Set the initial orientation, empty if not set
        orientation_entry.grid(row=options_number, column=2, padx=(0, 75))

    #
    # Direction
    #
    if self.direction.get():
        options_number += 1
        #
        # Direction label
        #
        label = ttk.Label(point_frame, text="direction:")
        label.grid(row=options_number, column=1, padx=(12, 0))

        #
        # Direction entry
        #
        direction_string = tk.StringVar()
        direction_entry = ttk.Entry(
            point_frame,
            width=8,
            textvariable=direction_string,
        )
        direction_string.trace_add(
            "write",
            lambda *args,
            new_direction=direction_string,
            idx=idx: _direction_entry_change(self, new_direction.get(), idx),
        )
        direction_entry.insert(
            0, direction if direction else ""
        )  # Set the initial direction, empty if not set
        direction_entry.grid(row=options_number, column=2, padx=(0, 75))

    #
    # Action
    #
    if self.action.get():
        options_number += 1

        #
        # Action label
        #
        label = ttk.Label(point_frame, text="action(s):")
        label.grid(row=options_number, column=1, padx=(12, 0))

        #
        # Action menubutton
        #
        action_menubutton = ttk.Menubutton(point_frame, text="Choose action(s)")
        action_menu = tk.Menu(
            action_menubutton,
        )
        action_menubutton.configure(menu=action_menu)

        choices = {}

        for action in self.actions:
            if self.image_points is None:
                return

            if (
                self.image_points[idx][5] is not None
                and action in self.image_points[idx][5]
            ):
                choices[action] = tk.IntVar(value=1)
                label = f"({self.image_points[idx][5].index(action) + 1}): {action}"

            else:
                choices[action] = tk.IntVar(value=0)
                label = action

            action_menu.add_checkbutton(
                label=label,
                variable=choices[action],
                onvalue=1,
                offvalue=0,
                command=lambda new_choices=choices, idx=idx: _action_checkbutton_change(
                    self, new_choices, idx
                ),
            )

        if self.wea.get():
            action_menu.add_separator()

            if self.image_points[idx][6] is not None:
                choice = tk.IntVar(value=1)

            else:
                choice = tk.IntVar(value=0)

            action_menu.add_checkbutton(
                label="Wait end of action",
                variable=choice,
                command=lambda new_wea=choice, idx=idx: _wea_checkbutton_change(
                    self, new_wea, idx
                ),
            )

        action_menubutton.grid(row=options_number, column=2)


def _coordinate_entry_change(
    self, new_x: str | None = None, new_y: str | None = None, idx: int = -1
):
    """Update the x or y coordinate based on the content of the x_entry and the y_entry widgets

    Args:
        self (GUI): the GUI object that is manipulated
        new_x (str | None): the new x value that will be saved for the point. If None, x won't be changed
        new_y (str | None): the new y value that will be saved for the point. If None, y won't be changed
        idx (int):  index of the updated point
    """

    new_coordinate = (
        [0, new_x] if new_x is not None else ([1, new_y] if new_y is not None else None)
    )

    if idx == -1 or new_coordinate is None:
        return

    if new_coordinate[1] == "":
        self.image_points = update_trajectory(
            self.image_points, idx, new_coordinate[0], new_coordinate[1]
        )
        return

    try:
        new_coordinate[1] = np.float64(new_coordinate[1])
    except Exception as e:
        messagebox.showerror("Error", "New coordinate must be number")
        _update_point_frame(self, idx)
        return

    if (
        new_coordinate[0] == 0 and not (0 <= new_coordinate[1] <= self.pil_image.width)
    ) or (
        new_coordinate[0] == 1 and not (0 <= new_coordinate[1] <= self.pil_image.height)
    ):
        messagebox.showerror(
            "Error", "Coordinates cannot be outside the dimensions of the image"
        )
        _update_point_frame(self, idx)
        return

    if not isinstance(new_coordinate[1], np.float64):
        return

    self.image_points = update_trajectory(
        self.image_points, idx, new_coordinate[0], new_coordinate[1]
    )

    self.redraw_image()


def _orientation_entry_change(self, new_orientation: str, idx: int) -> None:
    """Update the orientation of the image_points[idx] based on the orientation entry value

    Args:
        self (GUI): the GUI object that is manipulated
        new_orientation (str): new orientation value
        idx (int): index of the updated point
    """

    if new_orientation == "" or new_orientation == "-":
        self.image_points = update_trajectory(self.image_points, idx, 3, None)
        return

    try:
        new_orientation = float(new_orientation)
    except Exception as e:
        messagebox.showerror("Error", "Orientation must be number")
        _update_point_frame(self, idx)
        return

    if not (-180 <= new_orientation <= 180):
        messagebox.showerror(
            "Error", "Orientation must be a value between -180 and 180"
        )
        _update_point_frame(self, idx)
        return

    self.image_points = update_trajectory(self.image_points, idx, 3, new_orientation)
    # self.redraw_image()


def _direction_entry_change(self, new_direction: str, idx: int) -> None:
    """Update the direction of the image_points[idx] based on the direction entry value

    Args:
        self (GUI): the GUI object that is manipulated
        new_direction (str): new direction value
        idx (int): index of the updated point
    """

    self.image_points = update_trajectory(self.image_points, idx, 4, new_direction)
    # self.redraw_image()


def _action_checkbutton_change(
    self, choices: dict[str, tk.IntVar], idx: int = -1
) -> None:
    """Update the actions(s) of the image_points[idx] based on the checkbutton widget content

    Args:
        self (GUI): the GUI object that is manipulated
        choices (dict[str, tk.IntVar): represent the actions and their tk.IntVar to know if they are choosed
        idx (int): index of the updated point
    """

    if self.image_points is None:
        return

    current_actions = self.image_points[idx][5]

    for name, var in choices.items():
        if current_actions is None:
            current_actions = []

        if var.get() == 1:
            if name not in current_actions:
                current_actions.append(name)
                new_actions = current_actions
                self.image_points = update_trajectory(
                    self.image_points, idx, 5, new_actions
                )
                _update_point_frame(self, idx)

        elif var.get() == 0:
            if name in current_actions:
                current_actions.remove(name)
                new_actions = current_actions
                if len(new_actions) == 0:
                    new_actions = None
                self.image_points = update_trajectory(
                    self.image_points, idx, 5, new_actions
                )
                _update_point_frame(self, idx)


def _wea_checkbutton_change(self, new_wea: tk.IntVar, idx: int) -> None:
    """Save the wea value

    Args:
        self (GUI): the GUI object that is manipulated
        new_wea (tk.IntVar): new wait end of action value
        idx (int): index of the updated point
    """

    # Save None and not 0 because it's easier to read when not set
    if not new_wea.get():
        self.image_points = update_trajectory(self.image_points, idx, 6, None)
    else:
        if self.image_points[idx][5] is None:
            messagebox.showwarning(
                "No actions set",
                "You don't have any actions set for this point. The wait for end of point option is useless",
            )
        self.image_points = update_trajectory(self.image_points, idx, 6, new_wea.get())
    # self.redraw_image()
