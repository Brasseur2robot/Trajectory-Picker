import tkinter as tk
from tkinter import ttk, messagebox

MIN_HEIGHT = 300
MIN_WIDTH = 300


def toggle_fbd_area_panel(self, event=None) -> None:
    """Create or delete the fbd_area_panel depending if it exist

    Args:
        self (GUI): the GUI object that is manipulated
        event (event): set to None here because not used
    """

    # Create the panel if it don't exist
    if self.fbd_area_panel is None or not self.fbd_area_panel.winfo_exists():
        # Panel creation
        self.fbd_area_panel = tk.Toplevel(self.master)

        self.fbd_area_panel.title("Forbiden area panel")
        self.fbd_area_panel.overrideredirect(True)
        self.fbd_area_panel.geometry(f"{MIN_WIDTH}x{MIN_HEIGHT}")
        self.fbd_area_panel.minsize(height=MIN_HEIGHT, width=MIN_WIDTH)

        # Main frame (everything is inside it)
        main_frame = ttk.Frame(self.fbd_area_panel)
        main_frame.pack(fill=tk.X)

        # Titlebar
        titlebar_frame = ttk.Frame(main_frame)
        titlebar_frame.pack(fill=tk.X)

        titlebar_frame.pack_propagate(False)  # Disable resizing based on child widgets
        titlebar_frame.config(height=20)

        titlebar_label = ttk.Label(
            titlebar_frame,
            text="Forbiden Area Panel",
        )
        titlebar_label.pack(side=tk.LEFT, padx=5)

        # Titlebar / content separator
        separator_frame = ttk.Frame(main_frame, style="primary.TFrame", height=2)
        separator_frame.pack(fill=tk.X)

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
        self.fbd_area_form_canvas = tk.Canvas(scroll_frame)
        self.fbd_area_form_canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            scroll_frame, orient="vertical", command=self.fbd_area_form_canvas.yview
        )
        scrollbar.pack(side="right", fill="y")

        # Linking the scrollbar to the canvas
        self.fbd_area_form_canvas.configure(yscrollcommand=scrollbar.set)
        self.fbd_area_form_canvas.bind(
            "<Configure>",
            lambda event: self.fbd_area_form_canvas.configure(
                scrollregion=self.fbd_area_form_canvas.bbox("all")
            ),
        )

        # Function and binding to use the mousewheel for scrolling
        self.fbd_area_panel.bind(
            "<Button-4>",
            lambda event: self.fbd_area_form_canvas.yview_scroll(-1, "units"),
        )
        self.fbd_area_panel.bind(
            "<Button-5>",
            lambda event: self.fbd_area_form_canvas.yview_scroll(1, "units"),
        )

        # Need to be tested for windows
        # def _on_mousewheel(event):
        #     canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        #
        # canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Content inside the canvas where the labels and entries will be displayed
        self.fbd_area_form_frame = ttk.Frame(self.fbd_area_form_canvas)
        self.fbd_area_form_canvas.create_window(
            (0, 0), window=self.fbd_area_form_frame, anchor="nw"
        )

        # Frame without scroll for the close button
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=1, column=0, pady=10)

        # Close button
        # ttk.Button(
        #     button_frame,
        #     text="Close panel",
        #     command=lambda self=self: _close_panel(self),
        # ).pack()

        # Delete fbd_area button
        ttk.Button(
            button_frame, text="Delete forbiden area(s)", command=self.fbd_area_delete
        ).pack()

        _init_fbd_area_panel_content(self)

    # Delete the panel if it exist
    else:
        _close_panel(self)


def update_fbd_area_panel_content(
    self, delete_fbd_area_idx: list[int] | None = None
) -> None:
    """Delete, add & update the fbd_area_frames depending of the context

    Args:
        self (GUI): the GUI object that is manipulated
        delete_fbd_area_idx (list[int] | None): list of index of the fbd_area_frame(s) to delete
    """

    # Add fbd_area case
    if len(self.fbd_area_frames) + 1 == len(self.fbd_area):
        _add_fbd_area_frame(self)

    # Remove fbd_area case
    if isinstance(delete_fbd_area_idx, list):
        for index in delete_fbd_area_idx:
            _delete_fbd_area_frame(self, index)

    # Clear the var to not delete non existent index based on the checkbox widgets values (see fbd_area_delete in main_panel.py)
    self.fbd_area_checkbox_del_widgets.clear()

    # Update the point_frames content
    for i in range(len(self.fbd_area)):
        fbd_area_frame = self.fbd_area_frames[i]
        _clear_frame(fbd_area_frame)
        # point_frame.grid_forget()
        _update_fbd_area_frame(self, i)

    # Without the following the freshly created items aren't displayed inside the scrollregion if there is too much widget
    self.fbd_area_panel.update_idletasks()  # Ensure every widget are displayed before the next command
    self.fbd_area_form_canvas.configure(
        scrollregion=self.fbd_area_form_canvas.bbox(
            "all"
        )  # Update the scrollregion to display all widgets
    )


def _init_fbd_area_panel_content(self) -> None:
    """Reset precedent content, init layout & add content

    Args:
        self (GUI): the GUI object that is manipulated
    """

    # Clear precedent content
    self.fbd_area_frames = []

    # Init the point_frames layout
    for i in range(len(self.fbd_area)):
        fbd_area_frame = ttk.Frame(self.fbd_area_form_frame)
        fbd_area_frame.grid(row=i, column=0, pady=10)
        self.fbd_area_frames.append(fbd_area_frame)

    # Add content to the point_frames
    update_fbd_area_panel_content(self)


def _add_fbd_area_frame(self) -> None:
    """Create a new fbd_area_frame at the end of the others

    Args:
        self (GUI): the GUI object that is manipulated
    """

    fbd_area_frame = ttk.Frame(self.fbd_area_form_frame)
    fbd_area_frame.grid(row=len(self.fbd_area) - 1, column=0, pady=10)
    self.fbd_area_frames.append(fbd_area_frame)


def _delete_fbd_area_frame(self, delete_fbd_area_idx: int) -> None:
    """Delete a specific fbd_area_frame based on the delete_point_idx

    Args:
        self (GUI): the GUI object that is manipulated
        delete_fbd_area_idx (int): index of the fbd_area_frame to delete
    """

    point_frame_to_delete = self.fbd_area_frames[delete_fbd_area_idx]
    self.fbd_area_frames.pop(delete_fbd_area_idx)
    point_frame_to_delete.destroy()

    for i, frame in enumerate(self.fbd_area_frames):
        frame.grid_forget()
        frame.grid(row=i, column=0, pady=10)


def _clear_frame(frame: tk.Frame) -> None:
    """Remove all widgets from a tk.Frame object

    Args:
        frame: tk.Frame object that need all his widgets to be destroyed
    """

    for widget in frame.winfo_children():
        widget.destroy()


def _update_fbd_area_frame(self, frame_idx: int) -> None:
    """(Re)create widget inside the fbd_area_frame and update its content
    TODO: A better way to do it is to update only their content and not to recreate them each time

    Args:
        self (GUI): the GUI object that is manipulated
        frame_idx (int): index of frame content that is updated
    """

    fbd_area_frame = self.fbd_area_frames[frame_idx]
    fbd_area = self.fbd_area[frame_idx]
    # x1, y1, x2, y2 = fbd_area[0][0], fbd_area[0][1], fbd_area[1][0], fbd_area[1][1]
    x1, y1, x2, y2 = fbd_area[0], fbd_area[1], fbd_area[2], fbd_area[3]

    #
    # Checkbox
    #
    check_var = tk.IntVar()
    checkbox = ttk.Checkbutton(
        fbd_area_frame,
        variable=check_var,
    )
    self.fbd_area_checkbox_del_widgets.insert(frame_idx, check_var)
    checkbox.grid(row=0, column=0, padx=(10, 0))

    #
    # Fbd_area name
    #
    label = ttk.Label(
        fbd_area_frame,
        text=f"Fordiden area n°{frame_idx + 1}:",
    )
    label.grid(row=0, column=1)

    #
    # Point_1
    #

    # X1 label
    x1_label = ttk.Label(fbd_area_frame, text="x1:")
    x1_label.grid(row=1, column=1, padx=(100, 0))

    # X1 entry
    x1_string = tk.StringVar()
    x1_entry = ttk.Entry(
        fbd_area_frame,
        width=8,
        textvariable=x1_string,
    )
    x1_entry.insert(0, format(x1, ".0f") if x1 else "")
    x1_string.trace_add(
        "write",
        lambda *args, new_value=x1_string, idx=frame_idx: _coordinate_entry_change(
            self, new_value=new_value.get(), coordinate_idx=0, idx=idx
        ),
    )
    x1_entry.grid(row=1, column=2, padx=(0, 75))

    # Y1 label
    y1_label = ttk.Label(fbd_area_frame, text=" y1:")
    y1_label.grid(row=2, column=1, padx=(96, 0))

    # Y1 entry
    y1_string = tk.StringVar()
    y1_entry = ttk.Entry(
        fbd_area_frame,
        width=8,
        textvariable=y1_string,
    )
    y1_entry.insert(0, format(y1, ".0f") if y1 else "")
    y1_string.trace_add(
        "write",
        lambda *args, new_value=y1_string, idx=frame_idx: _coordinate_entry_change(
            self, new_value=new_value.get(), coordinate_idx=1, idx=idx
        ),
    )
    y1_entry.grid(row=2, column=2, padx=(0, 75))

    #
    # Point_2
    #

    # X2 label
    x2_label = ttk.Label(fbd_area_frame, text="x2:")
    x2_label.grid(row=3, column=1, padx=(100, 0))

    # X2 entry
    x2_string = tk.StringVar()
    x2_entry = ttk.Entry(
        fbd_area_frame,
        width=8,
        textvariable=x2_string,
    )
    x2_entry.insert(0, format(x2, ".0f") if x2 else "")
    x2_string.trace_add(
        "write",
        lambda *args, new_value=x2_string, idx=frame_idx: _coordinate_entry_change(
            self, new_value=new_value.get(), coordinate_idx=2, idx=idx
        ),
    )
    x2_entry.grid(row=3, column=2, padx=(0, 75))

    # Y2 label
    y2_label = ttk.Label(fbd_area_frame, text=" y2:")
    y2_label.grid(row=4, column=1, padx=(96, 0))

    # Y2 entry
    y2_string = tk.StringVar()
    y2_entry = ttk.Entry(
        fbd_area_frame,
        width=8,
        textvariable=y2_string,
    )
    y2_entry.insert(0, format(y2, ".0f") if y2 else "")
    y2_string.trace_add(
        "write",
        lambda *args, new_value=y2_string, idx=frame_idx: _coordinate_entry_change(
            self, new_value=new_value.get(), coordinate_idx=3, idx=idx
        ),
    )
    y2_entry.grid(row=4, column=2, padx=(0, 75))


def _coordinate_entry_change(
    self,
    new_value: str | None = None,
    coordinate_idx: int = -1,
    idx: int = -1,
):
    """Edit a specific entry & fbd_area based on the value of new_value and the coordinate_idx to change

    Args:
        self (GUI): the GUI object that is manipulated
        new_value (str): the new value that will replace the old one
        coordinate_idx (int): the index of the coordinate that will be replaced (0, 1, 2, 3) for (x1, y1, x2, y2)
        idx (int): index of the fbd_area and the entry to edit
    """

    if new_value is None or coordinate_idx == -1 or idx == -1:
        return

    if new_value == "":
        new_value = 0

    try:
        new_value = int(new_value)

    except Exception as e:
        messagebox.showerror("Error", "New coordinate must be number")
        _update_fbd_area_frame(self, idx)
        return

    if not 0 <= new_value <= self.pil_image.width and (
        coordinate_idx == 0 or coordinate_idx == 2
    ):
        print("troubles")
        messagebox.showerror(
            "Error",
            f"X coordinate cannot be outside the dimensions of the image ({self.pil_image.width})",
        )
        _update_fbd_area_frame(self, idx)
        return

    if not 0 <= new_value <= self.pil_image.height and (
        coordinate_idx == 1 or coordinate_idx == 3
    ):
        print("troubles2")
        messagebox.showerror(
            "Error",
            f"Y coordinate cannot be outside the dimensions of the image ({self.pil_image.height})",
        )
        _update_fbd_area_frame(self, idx)
        return

    self.fbd_area[idx][coordinate_idx] = new_value
    start_point = self.to_canvas_point(
        self.fbd_area[idx][0], self.fbd_area[idx][1], True
    )
    end_point = self.to_canvas_point(self.fbd_area[idx][2], self.fbd_area[idx][3], True)
    self.canvas.coords(
        self.fbd_area[idx][4],
        start_point[0],
        start_point[1],
        end_point[0],
        end_point[1],
    )


def _close_panel(self) -> None:
    """Destroy the fbd_area_panel and quit fbd_area_mode

    Args:
        self (GUI): the GUI object that is manipulated
    """

    self.fbd_area_panel.destroy()
    self.fbd_area_escape(event=None)
