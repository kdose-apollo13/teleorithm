# vbwise/gui/main_window.py

import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import tkinter.ttk as ttk
import sys
import os
import traceback

# Assume these exist in vbwise/
from vbwise.app_state import AppState
from vbwise.node import Node # Imported for type hinting and clarity
from vbwise.source_parser import parse_source_string_to_nodes
from vbwise.gui.leaf_widget import LeafWidget


class MainWindow(tk.Tk):
    """The main application window for Vibewise."""
    def __init__(self, app_state: AppState):
        super().__init__()

        self.app_state = app_state
        # Observer will be added *after* this __init__ call in run_vibewise

        self.title("Vibewise")
        self.geometry("1000x700")

        # --- Layout Containers ---
        # We will use separate containers for different layouts and show/hide them.
        # This main_content_area frame will hold the currently active layout container.
        self.main_content_area = tk.Frame(self)
        self.main_content_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Container for 'single' layout - a simple Frame
        self.single_leaf_container = tk.Frame(self.main_content_area)

        # Container for 'split_h_2' layout (horizontal split) - a PanedWindow
        self.h_split_paned_window = ttk.PanedWindow(self.main_content_area, orient=tk.HORIZONTAL)

        # Container for 'split_v_2' layout (vertical split) - a PanedWindow
        self.v_split_paned_window = ttk.PanedWindow(self.main_content_area, orient=tk.VERTICAL)

        # Dictionary to keep track of currently managed LeafWidgets by node_id
        # These widgets are kept alive even if not currently displayed, until their node leaves displayed_leaf_ids.
        self._leaf_widgets = {} # type: dict[str, LeafWidget]


        self.command_frame = tk.Frame(self, height=30)
        self.command_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.command_frame.pack_propagate(False) # Prevent frame from shrinking vertically

        # --- Command Input ---
        self.command_label = tk.Label(self.command_frame, text=">")
        self.command_label.pack(side=tk.LEFT, padx=2)

        self.command_entry = tk.Entry(self.command_frame)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", self.on_command_enter)
        self.command_entry.focus_set() # Set focus to command entry on start

        # --- Status Bar ---
        self.status_bar = tk.Label(self, text="Initializing...", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        print("MainWindow initialized.")
        # Initial display will be handled by the observer after data is loaded and goto is called


    def on_command_enter(self, event=None):
        """Handles command entered in the command line."""
        command_string = self.command_entry.get()
        self.command_entry.delete(0, tk.END)
        if command_string:
            print(f"GUI received command: '{command_string}'")
            status = self.app_state.execute_command(command_string)
            if status == "quit":
                 self.quit()


    def on_state_changed(self, app_state: AppState, event_type=None, **kwargs):
        """Callback function registered with AppState observer."""
        print(f"GUI: Received state change notification. Event Type: {event_type}")

        # --- Update Status Bar ---
        status_text = f"Layout: {app_state.get_layout()} | Detail: {app_state.get_global_detail_level()}"
        if app_state.get_focused_leaf_id():
            status_text += f" | Focused: {app_state.get_focused_leaf_id()}"
        if app_state.selected_leaf_ids:
             status_text += f" | Selected: {len(app_state.selected_leaf_ids)}"
        if app_state.get_active_pathway_link_type():
             status_text += f" | Pathway: {app_state.get_active_pathway_link_type()}"
             if app_state.get_active_pathway_current_node_id():
                  status_text += f" ({app_state.get_active_pathway_current_node_id()})"

        if event_type == "command_executed":
             cmd_status = kwargs.get("status", "unknown")
             cmd_message = kwargs.get("message", "")
             command_prefix = kwargs.get('command', '')
             if len(command_prefix) > 30:
                 command_prefix = command_prefix[:27] + '...'
             status_text += f" | Cmd: '{command_prefix}' Status: {cmd_status}"
             if cmd_status != "success" and cmd_message:
                   status_text += f" ({cmd_message})"

        self.status_bar.config(text=status_text)


        # --- Update Displayed Leaves and Layout ---
        # This is the core logic to manage LeafWidgets
        # Trigger this update on relevant state changes
        relevant_layout_events = [
            "data_loaded", # Initial load
            "displayed_leaves_changed", # goto command changes this
            "layout_changed", # layout command changes this
            "pathway_navigated", # next/prev changes displayed leaves
            "pathway_started", # follow changes displayed leaves
            # "pathway_ended", # Decide later if these affect layout
            # "pathway_stopped", # Decide later if these affect layout
        ]

        if event_type in relevant_layout_events:
            print(f"GUI: Updating displayed leaves and layout due to {event_type}.")

            current_displayed_nodes = app_state.get_displayed_leaves()
            current_layout = app_state.get_layout()
            displayed_ids_in_order = [n.id for n in current_displayed_nodes]


            # --- Step 1: Determine which LeafWidgets need to exist ---
            # Keep track of which node IDs should *eventually* have widgets.
            # We create/destroy widgets only as nodes enter/leave the *set* of displayed nodes.
            ids_that_should_have_widgets = set(displayed_ids_in_order) # For now, only create widgets for currently displayed
            existing_widget_ids = set(self._leaf_widgets.keys())

            ids_to_destroy = list(existing_widget_ids - ids_that_should_have_widgets)
            # ids_to_create = list(ids_that_should_have_widgets - existing_widget_ids) # We create during packing loop


            # --- Step 2: Destroy LeafWidgets that are no longer needed ---
            # Remove from _leaf_widgets dictionary as they are destroyed.
            for node_id in ids_to_destroy:
                print(f"GUI: Destroying LeafWidget for node: {node_id}")
                # Ensure the widget is managed by us before destroying
                if node_id in self._leaf_widgets and self._leaf_widgets[node_id] is not None:
                     self._leaf_widgets[node_id].destroy()
                     del self._leaf_widgets[node_id]


            # --- Step 3: Unpack all layout containers ---
            # We'll pack the correct one based on the new layout state.
            # This also implicitly removes any widgets packed inside them.
            self.single_leaf_container.pack_forget()
            self.h_split_paned_window.pack_forget()
            self.v_split_paned_window.pack_forget()


            # --- Step 4: Determine the active layout container and pack it ---
            active_container = None
            # Determine which nodes will actually be packed into the active container
            nodes_to_pack_ids = []

            if current_layout == 'single' and len(displayed_ids_in_order) >= 1:
                 active_container = self.single_leaf_container
                 active_container.pack(fill=tk.BOTH, expand=True)
                 nodes_to_pack_ids = displayed_ids_in_order[:1] # Only the first node for single layout

            elif current_layout == 'split_v_2' and len(displayed_ids_in_order) >= 2:
                 active_container = self.v_split_paned_window
                 active_container.pack(fill=tk.BOTH, expand=True)
                 nodes_to_pack_ids = displayed_ids_in_order[:2] # First two nodes for split layouts

            elif current_layout == 'split_h_2' and len(displayed_ids_in_order) >= 2:
                 active_container = self.h_split_paned_window
                 active_container.pack(fill=tk.BOTH, expand=True)
                 nodes_to_pack_ids = displayed_ids_in_order[:2] # First two nodes for split layouts

            else:
                 print(f"GUI: Layout '{current_layout}' not implemented or insufficient nodes ({len(displayed_ids_in_order)}) for it. No container packed.")
                 # No active container means nothing will be displayed in the main area


            # --- Step 5: Add (Pack/Add) Existing or Create and Add LeafWidgets to the Active Container ---
            # Iterate through the node IDs that should be packed into this specific container instance
            if active_container:
                # Clear contents of the active container before adding - THIS IS DONE BY pack_forget/add/pack logic itself mostly
                # But if using Pack/Grid directly within a Frame, might need to explicitly destroy children.
                # PanedWindow.add/remove handles widget lifecycle within the pane list.
                # Frame.pack_forget just unpacks, doesn't destroy.
                # We destroy in Step 2 if a node leaves the *displayed* set.
                # When changing layouts (e.g., single to split), the widgets in the *old* container
                # might not be destroyed in Step 2 if they are still in the *new* displayed list.
                # We need to make sure we aren't trying to pack/add a widget that's still parented elsewhere
                # or is in a weird state after being managed by a different container type.

                # Let's simplify the lifecycle: LeafWidget is created when needed for display, destroyed when not needed.
                # We'll destroy ALL widgets in _leaf_widgets first if the layout/displayed list changes drastically,
                # and then recreate ONLY the ones needed for the *new* display state.
                # This is less efficient but safer for now.

                # --- Simplified and Corrected Step 2 & 5 ---
                # Combine Step 2 (Destroy) and Step 5 (Create and Pack)

                # --- Step 2 (Corrected): Destroy ALL currently managed LeafWidgets ---
                # If the layout or displayed nodes change, let's just destroy everything
                # and rebuild the necessary ones for the new state.
                if event_type in relevant_layout_events: # Only destroy on layout/displayed changes
                    print("GUI: Clearing all existing LeafWidgets due to layout/displayed nodes change.")
                    for node_id, leaf_widget in list(self._leaf_widgets.items()):
                         if leaf_widget is not None:
                              leaf_widget.destroy()
                    self._leaf_widgets = {} # Clear the dictionary


                # Now, recreate and pack ONLY the widgets needed for the current state and layout
                if active_container:
                     # Iterate through the node IDs that should be packed into this specific container instance
                     nodes_to_pack_ids = []
                     if active_container == self.single_leaf_container:
                         nodes_to_pack_ids = displayed_ids_in_order[:1]
                     elif active_container in [self.h_split_paned_window, self.v_split_paned_window]:
                          nodes_to_pack_ids = displayed_ids_in_order[:2]

                     for node_id in nodes_to_pack_ids:
                         if node_id in app_state.all_nodes:
                              # Create a NEW LeafWidget, parented to the active container
                              print(f"GUI: Creating NEW LeafWidget for node: {node_id} under {active_container.__class__.__name__}")
                              leaf_widget = LeafWidget(active_container, self.app_state, node_id)
                              self._leaf_widgets[node_id] = leaf_widget # Store reference

                              # Add/Pack the LeafWidget into the active container
                              print(f"GUI: Adding/Packing LeafWidget for node: {node_id}")
                              if isinstance(active_container, tk.Frame): # Single layout
                                   leaf_widget.pack(fill=tk.BOTH, expand=True)
                              elif isinstance(active_container, ttk.PanedWindow): # Split layouts
                                   active_container.add(leaf_widget)

                              # Update the display and visuals for the leaf that was just added/packed
                              leaf_widget.update_display()

                         else:
                              print(f"Warning: Cannot pack non-existent node '{node_id}' into layout.", file=sys.stderr)


            # --- Step 6: Update State Visuals for ALL currently displayed leaves ---
            # Update focus/selection visuals for the widgets that were just created/packed.
            print("GUI: Updating visuals for currently displayed leaves.")
            currently_displayed_ids_set = set(displayed_ids_in_order)

            # Iterate through all *known* leaf widgets (which are now only the currently displayed ones)
            for node_id, leaf_widget in list(self._leaf_widgets.items()):
                 # Since we just created them, they should be in the displayed set and not None
                 leaf_widget.set_focused(node_id == app_state.get_focused_leaf_id())
                 leaf_widget.set_selected(node_id in app_state.selected_leaf_ids)


        # --- Handle granular updates for content based on detail/override changes ---
        # These events trigger update_display on relevant leaf widgets *if* they are displayed
        elif event_type in ["leaf_detail_override_changed", "leaf_detail_override_cleared", "global_detail_level_changed", "leaf_detail_override_changed_batch"]:
             print(f"GUI: Detail/Override/Global detail level changed due to {event_type}. Checking displayed leaves for update...")
             currently_displayed_ids_set = set([n.id for n in app_state.get_displayed_leaves()])
             node_ids_to_update_content = []

             if event_type == "leaf_detail_override_changed_batch":
                  node_ids_to_update_content = kwargs.get("node_ids", [])
             elif "node_id" in kwargs: # For single leaf override changes
                  node_ids_to_update_content = [kwargs["node_id"]]
             else: # Global change affects all displayed
                  node_ids_to_update_content = list(currently_displayed_ids_set)


             for node_id in node_ids_to_update_content:
                 # Check if we have a widget for this displayed node AND it's currently managed
                 if node_id in self._leaf_widgets and self._leaf_widgets[node_id] is not None:
                       print(f"GUI: Updating display for content change: {node_id}")
                       self._leaf_widgets[node_id].update_display()

        # Any other event types could be handled here if needed


# --- Main Application Entry Point ---
# ... (rest of run_vibewise and __main__ remain the same) ...
def run_vibewise():
    """Sets up the AppState and the main window, then starts the Tkinter event loop."""
    app_state = AppState()
    main_window = None

    try:
         # --- Create MainWindow instance BEFORE loading data or setting initial state ---
         main_window = MainWindow(app_state)
         # Register the observer immediately after creating the window
         app_state.add_observer(main_window.on_state_changed)
         print("MainWindow created and observer added.")

         # --- Load Dummy Data ---
         dummy_source_data = """
### NODE: help_commands
# Vibewise Commands Help
--- metadata: tags=help,commands ---
TXT> Welcome to Vibewise! Here are the available commands:
TXT>
L1> goto <node_id> - Navigate to and display a specific node.
L1> layout <type> - Change the display layout (e.g., single, split_v_2, split_h_2).
L1> verbosity <level> - Set the global detail level (e.g., 1, 2, 3).
L1> select all|none|<node_id> - Select displayed nodes.
L1> set_selected_verbosity <level> - Set detail level for selected nodes.
L1> follow <link_type> [start_node_id] - Start navigating a pathway by link type.
L1> next | pathway_next - Move to the next node in the active pathway.
L1> prev | pathway_previous - Move to the previous node (TODO).
L1> stop | pathway_stop - Stop navigating the current pathway.
L1> quit - Exit the application.
TXT>
TXT> Data nodes available:
L1> linux_basics_001
L1> linux_basics_002
L1> linux_basics_003
L1> linux_rm_advanced
--- links: next=linux_basics_001 ---
### ENDNODE

### NODE: linux_basics_001
# Intro to Linux CLI
--- metadata: tags=linux,cli,beginner ---
TXT> This node covers basic Linux command line concepts.
L1> pwd - Print working directory
L1> ls - List directory contents
L2> 'pwd' shows your current location in the file system.
L2> 'ls' lists files and folders. Use 'ls -l' for detailed view.
CODE> pwd
CODE> ls -l /home/user/docs
--- links: next=linux_basics_002, pathway_beginner=linux_basics_001, prev=help_commands ---
### ENDNODE

### NODE: linux_basics_002
# File System Navigation
--- metadata: tags=linux,cli,beginner ---
TXT> Navigating the file system is key.
L1> cd <directory> - Change directory
L1> cd .. - Go up one directory
L2> Use 'cd' to move between folders.
L2> 'cd .' refers to the current directory.
CODE> cd /var/log
CODE> cd ..
--- links: prev=linux_basics_001, next=linux_basics_003, pathway_beginner=linux_basics_002 ---
### ENDNODE

### NODE: linux_basics_003
# Creating and Removing Files
--- metadata: tags=linux,cli,beginner ---
TXT> How to manage files and directories.
L1> touch <filename> - Create an empty file
L1> mkdir <directory> - Create a new directory
L1> rm <filename> - Remove a file
L1> rmdir <directory> - Remove an empty directory
L2> Be careful with 'rm'! It doesn't use a trash bin by default.
CODE> touch myfile.txt
CODE> mkdir mydir
CODE> rm oldfile.log
CODE> rmdir tempdir
--- links: prev=linux_basics_002, pathway_beginner=linux_basics_003, related=linux_rm_advanced ---
### ENDNODE

### NODE: linux_rm_advanced
# Advanced Removal (Caution!)
--- metadata: tags=linux,cli,advanced,caution ---
TXT> More powerful removal commands. Use with extreme care!
L1> rm -r <directory> - Remove a directory and its contents recursively
L1> rm -f <filename> - Force remove (ignore non-existent files, never prompt)
L3> Combining -r and -f is very dangerous: 'rm -rf /' can delete your entire system!
L3> Always double-check what you are deleting with 'rm -i' (interactive) first.
CODE> rm -r mydir_with_files
CODE> rm -f important_file.txt
CODE> # DANGEROUS EXAMPLE - DO NOT RUN
CODE> # rm -rf /
--- links: related=linux_basics_003 ---
### ENDNODE
    """
         nodes_data = parse_source_string_to_nodes(dummy_source_data)
         app_state.load_nodes(nodes_data)

         # --- Set initial display to the help node AFTER data is loaded ---
         help_node_id = 'help_commands'
         if help_node_id in app_state.all_nodes:
             print(f"Setting initial display to help node: {help_node_id}")
             # Use the execute_command method to set the initial state
             app_state.execute_command(f"goto {help_node_id}")
         else:
             print(f"Error: Help node '{help_node_id}' not found after parsing data. Cannot set initial display.", file=sys.stderr)


    except Exception as e:
        print(f"Error during initialization: {e}", file=sys.stderr)
        traceback.print_exc()
        if main_window is None:
             print("Creating error window due to initialization failure.", file=sys.stderr)
             error_window = tk.Tk()
             error_window.title("Fatal Error")
             error_label = tk.Label(error_window, text=f"Fatal initialization error:\n{e}", fg="red")
             error_label.pack(padx=20, pady=20)
             main_window = error_window


    # --- Start the Tkinter event loop ---
    if main_window:
         print("Starting Tkinter mainloop.")
         main_window.mainloop()
         print("Tkinter mainloop finished.")
    else:
         print("main_window is None. Cannot start mainloop.", file=sys.stderr)


# --- Entry Point for the Application ---
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    vbwise_root_dir = os.path.join(current_dir, '..')
    if vbwise_root_dir not in sys.path:
        sys.path.insert(0, vbwise_root_dir)

    run_vibewise()
