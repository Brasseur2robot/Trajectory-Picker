import tkinter as tk
from tkinter import ttk

MIN_HEIGHT = 300
MIN_WIDTH = 300


def toggle_actions_panel(self, event=None) -> None:
    """Create or delete the actions_panel depending if it exist

    Args:
        self (GUI): the GUI object that is manipulated
        event (event): set to None here because not used
    """

    # Create the panel if it don't exist
    if self.actions_panel is None or not self.actions_panel.winfo_exists():
        # Panel creation
        self.actions_panel = tk.Toplevel(self.master)

        self.actions_panel.title("Actions panel")
        self.actions_panel.overrideredirect(True)
        self.actions_panel.geometry(f"{MIN_WIDTH}x{MIN_HEIGHT}")
        self.actions_panel.minsize(height=MIN_HEIGHT, width=MIN_WIDTH)

        # Main frame (everything is inside it)
        main_frame = ttk.Frame(self.actions_panel)
        main_frame.pack(fill=tk.X)

        # Titlebar
        titlebar_frame = ttk.Frame(main_frame)
        titlebar_frame.pack(fill=tk.X)

        titlebar_frame.pack_propagate(False)  # Disable resizing based on child widgets
        titlebar_frame.config(height=20)

        titlebar_label = ttk.Label(
            titlebar_frame,
            text="Actions Panel",
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
        self.actions_form_canvas = tk.Canvas(scroll_frame)
        self.actions_form_canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            scroll_frame, orient="vertical", command=self.actions_form_canvas.yview
        )
        scrollbar.pack(side="right", fill="y")

        # Linking the scrollbar to the canvas
        self.actions_form_canvas.configure(yscrollcommand=scrollbar.set)
        self.actions_form_canvas.bind(
            "<Configure>",
            lambda event: self.actions_form_canvas.configure(
                scrollregion=self.actions_form_canvas.bbox("all")
            ),
        )

        # Function and binding to use the mousewheel for scrolling
        self.actions_panel.bind(
            "<Button-4>",
            lambda event: self.actions_form_canvas.yview_scroll(-1, "units"),
        )
        self.actions_panel.bind(
            "<Button-5>",
            lambda event: self.actions_form_canvas.yview_scroll(1, "units"),
        )

        # Need to be tested for windows
        # def _on_mousewheel(event):
        #     canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        #
        # canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Content inside the canvas where the labels and entries will be displayed
        self.actions_form_frame = ttk.Frame(self.actions_form_canvas)
        self.actions_form_canvas.create_window(
            (0, 0), window=self.actions_form_frame, anchor="nw"
        )

        # Create the form for each actions that already exist + 1 that is empty
        self.actions_form = []
        for i in range(len(self.actions) + 1):
            if i == len(self.actions):
                _create_form(self)
            else:
                _create_form(self, self.actions[i], i)

        # Frame without scroll for the close button
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=1, column=0, pady=10)

        # Close button
        ttk.Button(
            button_frame,
            text="Close panel",
            command=self.actions_panel.destroy,
        ).pack()

    # Delete the panel if it exist
    else:
        self.actions_panel.destroy()


def _remove_form(self, event=None) -> None:
    """Remove the action from the cleared form and recreate all form from the actions list

    Args:
        self (GUI): the GUI object that is manipulated
        event (event): set to None here because not used
    """

    index_to_del = None

    # Search for the action to remove
    for i in range(len(self.actions_form)):
        if i != len(self.actions_form) - 1:
            if self.actions_form[i][1].get() == "":
                index_to_del = i

    # Remove the action based on the found index and recreate all forms
    if index_to_del is not None:
        self.actions.pop(index_to_del)

        for form in self.actions_form:
            form[0].destroy()
            form[1].destroy()
        self.actions_form = []

        for i in range(len(self.actions) + 1):
            if i == len(self.actions):
                _create_form(self)
            else:
                _create_form(self, self.actions[i], i)

        # Without the following the freshly created items aren't displayed inside the scrollregion if there is too much widget
        self.actions_panel.update_idletasks()  # Ensure every widget are displayed before the next command
        self.actions_form_canvas.configure(
            scrollregion=self.actions_form_canvas.bbox(
                "all"
            )  # Update the scrollregion to display all widgets
        )

        # Load the edited actions list inside the trajectory_panel
        self.update_trajectory_panel_content()


def _entry_change(self, new_action: str, action_index: int) -> None:
    """Edit an already existing action or append a new action and create a new form

    Args:
        self (GUI): the GUI object that is manipulated
        new_action (str): the new value for the new action or the action to update
        action_index (int): the index of the action that need to be updated
    """

    if new_action != "":
        # Create a new action and a new form if the last form is completed or update the existing action
        if action_index == len(self.actions_form) - 1:
            self.actions.append(new_action)

            _create_form(self)

            # Without the following the freshly created items aren't displayed inside the scrollregion if there is too much widget
            self.actions_panel.update_idletasks()  # Ensure every widget are displayed before the next command
            self.actions_form_canvas.configure(
                scrollregion=self.actions_form_canvas.bbox(
                    "all"
                )  # Update the scrollregion to display all widgets
            )

            # Load the edited actions list inside the trajectory_panel
            self.update_trajectory_panel_content()

        else:
            self.actions[action_index] = new_action

            # Load the edited actions list inside the trajectory_panel
            self.update_trajectory_panel_content()


def _create_form(self, action: str | None = None, action_index: int = -1) -> None:
    """Create a form and insert an action inside if the form previously exist

    Args:
        self (GUI): the GUI object that is manipulated
        new_action (str | None): the text to render inside the the entry widget
        action_index (int): the index that will be used for the update of the action
    """

    # Label to show the action number
    label = ttk.Label(
        self.actions_form_frame,
        text=f"Action n°{len(self.actions_form) + 1}:",
    )
    label.grid(row=len(self.actions_form) + 1, column=0, padx=5, pady=5)

    # The entry and his StringVar
    string = tk.StringVar()
    entry = ttk.Entry(self.actions_form_frame, textvariable=string)
    if action is not None:
        entry.insert(0, action)
    entry.grid(row=len(self.actions_form) + 1, column=1, padx=5, pady=5)

    # Trace to update the action
    string.trace_add(
        "write",
        lambda *args,
        new_action=string,
        action_index=action_index
        if action_index != -1
        else len(self.actions): _entry_change(
            self,
            new_action.get(),
            action_index,
        ),
    )
    # Bind to delete form when cleared
    entry.bind(
        "<FocusOut>",
        lambda event=None: _remove_form(self, event),
    )

    # Storing the object
    self.actions_form.append([label, entry])
