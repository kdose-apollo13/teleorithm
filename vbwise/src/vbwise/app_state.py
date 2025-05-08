# app_state.py

# from .node import Node # Assuming node.py is in the same directory or package
import sys # Used for printing errors
import traceback # Helpful for debugging observer errors

from vbwise.node import Node


class AppState:
    """Manages the application's data (knowledge graph) and current state."""
    def __init__(self):
        # --- The Data (The loaded knowledge graph) ---
        # Dictionary of all nodes, keyed by their unique ID
        self.all_nodes = {} # type: dict[str, Node]

        # --- The State (The current state of the application) ---
        self.displayed_leaf_ids = [] # type: list[str] # List of node IDs currently visible in the layout order
        self.layout = 'single'     # type: str      # Current layout ('single', 'split_v_2', etc.)
        self.focused_leaf_id = None # type: str | None # The ID of the leaf with input focus (for editing/nav)
        self.detail_level = 1      # type: int      # Global content detail level (default)

        # Dictionary to store detail level overrides for specific leaves {node_id: level}
        self.leaf_detail_overrides = {} # type: dict[str, int]

        self.selected_leaf_ids = set() # type: set[str] # Set of node IDs currently selected

        # State related to pathway navigation
        # For simplicity initially, active pathway is defined by the *link type* being followed
        self.active_pathway_link_type = None # type: str | None # e.g., 'next', 'pathway_basic_linux'
        self.active_pathway_current_node_id = None # type: str | None # The ID of the current node within the active pathway

        self.command_buffer = "" # type: str # Text in the command input area (for internal command line)

        # Observer pattern: list of callbacks to notify on state changes
        self._observers = [] # type: list[callable]

        print("AppState initialized.")

    def add_observer(self, callback):
        """Register a callback function to be called when the state changes."""
        if callable(callback) and callback not in self._observers:
            self._observers.append(callback)
            print(f"Added observer: {callback.__name__}")

    def remove_observer(self, callback):
        """Remove a registered callback."""
        if callback in self._observers:
            self._observers.remove(callback)
            print(f"Removed observer: {callback.__name__}")


    def _notify_observers(self, event_type=None, **kwargs):
        """Notify registered observers that the state has changed."""
        print(f"Notifying observers. Event Type: {event_type}, Kwargs: {kwargs}")
        # Iterate over a copy of the list in case an observer modifies the list
        for callback in list(self._observers):
            try:
                # Pass self so observers can inspect the new state
                # Pass event_type and kwargs for targeted updates
                callback(self, event_type=event_type, **kwargs)
            except Exception as e:
                print(f"Error in observer callback {callback.__name__}: {e}", file=sys.stderr)
                traceback.print_exc() # Print traceback for debugging


    # --- Methods to Load Data ---
    def load_nodes(self, nodes: dict[str, Node]):
        """Loads a dictionary of Node objects into the AppState."""
        print(f"Attempting to load {len(nodes)} nodes.")
        self.all_nodes = nodes
        print(f"Loaded {len(self.all_nodes)} nodes into AppState.")

        # After loading, set a default display state
        if self.all_nodes:
            first_node_id = list(self.all_nodes.keys())[0]
            print(f"Setting initial display to node: {first_node_id}")
            self.set_displayed_leaves([first_node_id]) # Display the first node
            self.set_focused_leaf(first_node_id)
        else:
            self.set_displayed_leaves([])
            self.set_focused_leaf(None)

        self.clear_selection()
        self.leaf_detail_overrides = {}
        self.active_pathway_link_type = None
        self.active_pathway_current_node_id = None
        self.detail_level = 1 # Reset state to default on load

        self._notify_observers(event_type="data_loaded") # Notify GUI data is ready


    # --- Methods to Transform State (Triggered by commands/actions) ---

    def execute_command(self, command_string: str):
        """Parses and executes a command string, transforming the state."""
        print(f"Executing command: '{command_string}'")
        parts = command_string.strip().split(maxsplit=1)
        status = "error" # Default status
        message = ""     # Initialize message to an empty string

        if not parts:
            status = "ignored"
            message = "Empty command"
            self._notify_observers(event_type="command_executed", command=command_string, status=status, message=message)
            return status

        command = parts[0].lower()
        args_string = parts[1] if len(parts) > 1 else ""
        args = args_string.split()

        try:
            if command == 'goto' and len(args) == 1:
                node_id = args[0]
                self.goto_node(node_id) # This method can raise ValueError
                status = "success"
                message = f"Navigated to node: {node_id}"
            elif command == 'layout' and len(args) == 1:
                layout_type = args[0]
                self.set_layout(layout_type) # This method can raise ValueError
                status = "success"
                message = f"Set layout to: {layout_type}"
            elif command == 'verbosity' and len(args) == 1:
                level_str = args[0]
                self.set_global_detail_level(level_str) # Can raise ValueError
                status = "success"
                message = f"Set global verbosity to: {level_str}"
            elif command == 'select':
                 # Handle select commands: 'select all', 'select none', 'select <node_id>'
                 if len(args) == 1:
                     if args[0] == 'all':
                         self.select_all_displayed()
                         message = "Selected all displayed leaves."
                     elif args[0] == 'none':
                         self.clear_selection()
                         message = "Cleared selection."
                     else:
                         # Assume it's a node ID
                         self.select_leaf(args[0]) # Warning printed inside if node not found
                         message = f"Attempted to select leaf: {args[0]}" # Message could be more specific
                 # TODO: Add select range logic later
                 status = "success" # Select commands are generally successful even if node not found, it just warns

            elif command == 'set_selected_verbosity' and len(args) == 1:
                 level_str = args[0]
                 self.set_selected_leaves_detail_level(level_str) # Can raise ValueError
                 status = "success"
                 message = f"Set verbosity for selected leaves to: {level_str}"

            elif command == 'follow' and len(args) >= 1:
                 link_type = args[0]
                 start_node_id = args[1] if len(args) > 1 else None
                 self.start_pathway(link_type, start_node_id) # Can raise ValueError
                 status = "success"
                 message = f"Started pathway '{link_type}' from {start_node_id if start_node_id else 'focused node'}."

            elif command == 'next' or command == 'pathway_next':
                 self.pathway_next() # Prints messages directly
                 status = "success" # Assume success if it doesn't raise an exception
                 # Message is printed inside pathway_next

            elif command == 'prev' or command == 'pathway_previous':
                 # self.pathway_previous() # TODO: Implement
                 print("Command 'prev' not yet implemented.")
                 status = "not_implemented"
                 message = "Command 'prev' not yet implemented."

            elif command == 'stop' or command == 'pathway_stop':
                 self.stop_pathway() # Prints messages directly
                 status = "success" # Assume success
                 # Message is printed inside stop_pathway

            elif command == 'quit' or command == 'exit':
                 print("Command 'quit' received.")
                 status = "quit"
                 message = "Application shutting down."
                 # Don't notify observers for quit, the main loop handles it
                 return status

            else:
                status = "error"
                message = f"Unknown command or incorrect arguments: '{command_string}'"
                print(message, file=sys.stderr)

        except ValueError as e:
            status = "error"
            message = f"Error: {e}"
            print(f"Error executing command '{command_string}': {message}", file=sys.stderr)
        except Exception as e:
            # Catch any unexpected errors during command execution
            status = "error"
            message = f"Unexpected error: {e}"
            print(f"An unexpected error occurred during command '{command_string}': {message}", file=sys.stderr)
            traceback.print_exc()


        # Notify observers after state has potentially changed (unless quitting)
        self._notify_observers(event_type="command_executed", command=command_string, status=status, message=message)
        return status
    # --- State Transformation Methods ---

    def goto_node(self, node_id: str):
        """Sets the state to display a single specific node."""
        if node_id in self.all_nodes:
            print(f"Going to node: {node_id}")
            self.set_displayed_leaves([node_id]) # Always display single node for goto
            self.set_focused_leaf(node_id)
            self.clear_selection() # Clear selection on navigation
            self.leaf_detail_overrides = {} # Clear overrides too
            # set_displayed_leaves and set_focused_leaf will notify observers
        else:
            raise ValueError(f"Node not found: {node_id}")


    def set_displayed_leaves(self, node_ids: list[str]):
        """Sets which nodes are currently displayed in the layout."""
        # Validate that node_ids exist in all_nodes
        valid_ids = [id for id in node_ids if id in self.all_nodes]
        if self.displayed_leaf_ids != valid_ids:
            print(f"Setting displayed leaves: {valid_ids}")
            self.displayed_leaf_ids = valid_ids
            # Decide what happens to focus/selection/overrides for removed leaves later
            self._notify_observers(event_type="displayed_leaves_changed")
        else:
             print("Displayed leaves unchanged.")


    def set_layout(self, layout_type: str):
        """Sets the layout type (e.g., 'single', 'split_v_2')."""
        # TODO: Add validation for valid layout types
        valid_layouts = ['single', 'split_v_2', 'split_h_2'] # Define valid layouts
        if layout_type not in valid_layouts:
             raise ValueError(f"Invalid layout type: {layout_type}. Valid types are: {', '.join(valid_layouts)}")

        if self.layout != layout_type:
            print(f"Setting layout: {layout_type}")
            self.layout = layout_type
            # Logic might be needed here to adjust displayed_leaf_ids based on new layout
            # For now, just changing the state variable is enough. GUI reacts to it.
            self._notify_observers(event_type="layout_changed")
        else:
             print("Layout unchanged.")


    def set_focused_leaf(self, node_id: str | None):
        """Sets the leaf that currently has input focus."""
        if node_id is None or node_id in self.all_nodes:
             if self.focused_leaf_id != node_id:
                 print(f"Setting focused leaf: {node_id}")
                 self.focused_leaf_id = node_id
                 self._notify_observers(event_type="focused_leaf_changed")
             else:
                print("Focused leaf unchanged.")
        else:
            raise ValueError(f"Cannot set focus to non-existent node: {node_id}")


    def set_global_detail_level(self, level_str: str):
        """Sets the default detail level for all leaves."""
        try:
            level = int(level_str)
            if level < 0: # Example validation
                 raise ValueError("Detail level cannot be negative.")
            if self.detail_level != level:
                print(f"Setting global detail level: {level}")
                self.detail_level = level
                # When global level changes, clear overrides for consistency? Yes.
                self.leaf_detail_overrides = {}
                self._notify_observers(event_type="global_detail_level_changed")
            else:
                 print("Global detail level unchanged.")
        except ValueError as e:
            raise ValueError(f"Invalid detail level '{level_str}': {e}") from e


    def set_leaf_detail_override(self, node_id: str, level_str: str):
        """Sets a specific detail level override for a single leaf."""
        if node_id not in self.all_nodes:
             raise ValueError(f"Cannot set detail override for non-existent node: {node_id}")
        try:
            level = int(level_str)
            if level < 0: # Example validation
                 raise ValueError("Detail level cannot be negative.")

            # Only update if the override is different or didn't exist
            if self.leaf_detail_overrides.get(node_id) != level:
                 print(f"Setting detail override for node '{node_id}' to level {level}")
                 self.leaf_detail_overrides[node_id] = level
                 # Notify observers only for the specific node that changed
                 self._notify_observers(event_type="leaf_detail_override_changed", node_id=node_id)
            else:
                 print(f"Detail override for node '{node_id}' unchanged.")
        except ValueError as e:
            raise ValueError(f"Invalid detail level override '{level_str}' for node '{node_id}': {e}") from e


    def clear_leaf_detail_override(self, node_id: str):
        """Removes the detail level override for a single leaf."""
        if node_id in self.leaf_detail_overrides:
            print(f"Clearing detail override for node '{node_id}'")
            del self.leaf_detail_overrides[node_id]
            self._notify_observers(event_type="leaf_detail_override_cleared", node_id=node_id)
        else:
             print(f"No detail override to clear for node '{node_id}'.")


    def get_effective_detail_level(self, node_id: str):
        """Gets the effective detail level for a leaf (override if exists, else global)."""
        return self.leaf_detail_overrides.get(node_id, self.detail_level)


    # --- Selection Methods ---
    def select_leaf(self, node_id: str):
        """Adds a node to the selection."""
        if node_id in self.all_nodes:
            if node_id not in self.selected_leaf_ids:
                print(f"Selecting node: {node_id}")
                self.selected_leaf_ids.add(node_id)
                self._notify_observers(event_type="selection_changed")
            else:
                 print(f"Node '{node_id}' already selected.")
        else:
             print(f"Warning: Cannot select non-existent node: {node_id}") # Warning, not error for select


    def deselect_leaf(self, node_id: str):
        """Removes a node from the selection."""
        if node_id in self.selected_leaf_ids:
            print(f"Deselecting node: {node_id}")
            self.selected_leaf_ids.discard(node_id) # Use discard to avoid error if not present
            self._notify_observers(event_type="selection_changed")
        else:
             print(f"Node '{node_id}' not selected.")


    def clear_selection(self):
        """Clears the entire selection."""
        if self.selected_leaf_ids: # Only notify if selection was not empty
            print("Clearing selection.")
            self.selected_leaf_ids.clear()
            self._notify_observers(event_type="selection_changed")
        else:
             print("Selection already empty.")

    def select_all_displayed(self):
         """Selects all nodes currently being displayed."""
         if self.displayed_leaf_ids:
             print("Selecting all displayed leaves.")
             # Create a set from the displayed IDs
             new_selection = set(self.displayed_leaf_ids)
             # Only update and notify if the selection actually changes
             if new_selection != self.selected_leaf_ids:
                self.selected_leaf_ids = new_selection
                self._notify_observers(event_type="selection_changed")
             else:
                 print("All displayed leaves already selected.")
         else:
              print("No leaves displayed to select.")

    # TODO: Implement select_range(start_node_id, end_node_id) - needs context of the range (display order, pathway order?)

    def set_selected_leaves_detail_level(self, level_str: str):
        """Sets the detail level override for all currently selected leaves."""
        if not self.selected_leaf_ids:
             print("No leaves selected to apply detail level.")
             return

        try:
            level = int(level_str)
            if level < 0:
                 raise ValueError("Detail level cannot be negative.")

            print(f"Setting detail level for {len(self.selected_leaf_ids)} selected leaves to {level}")
            nodes_notified = [] # Track nodes that actually got updated overrides
            for node_id in list(self.selected_leaf_ids): # Iterate over a copy as overrides might change
                if node_id in self.all_nodes: # Ensure the selected node still exists
                     if self.leaf_detail_overrides.get(node_id) != level:
                        self.leaf_detail_overrides[node_id] = level
                        nodes_notified.append(node_id)
                else:
                    # Clean up selection if node no longer exists
                    self.selected_leaf_ids.discard(node_id)


            if nodes_notified:
                 # Notify observers specifically about the nodes whose overrides changed
                 # This allows the GUI to refresh just those leaves efficiently
                 self._notify_observers(event_type="leaf_detail_override_changed_batch", node_ids=nodes_notified)
            else:
                 print("Selected leaves already had the specified detail level override.")

        except ValueError as e:
            raise ValueError(f"Invalid detail level '{level_str}' for selected leaves: {e}") from e


    # --- Pathway Navigation Methods ---
    def start_pathway(self, link_type: str, start_node_id: str | None = None):
        """Starts following a pathway defined by a link type from a starting node."""
        # Validate link_type if necessary (e.g., must be 'next', 'prev', or start with 'pathway_')
        # For now, allow any string as link_type, validation can be added.

        effective_start_node_id = start_node_id
        if effective_start_node_id is None:
            # Default to focused node if no start node is specified
            effective_start_node_id = self.focused_leaf_id

        if effective_start_node_id is None or effective_start_node_id not in self.all_nodes:
            raise ValueError(f"Cannot start pathway '{link_type}', invalid or unspecified start node: {effective_start_node_id}")

        if link_type not in self.all_nodes[effective_start_node_id].links:
             # It's possible a pathway starts at a node but the first link isn't there
             # Decide if this is an error or just a short pathway
             print(f"Warning: Start node '{effective_start_node_id}' has no link of type '{link_type}'. Pathway may be short or invalid.")


        print(f"Starting pathway '{link_type}' from node '{effective_start_node_id}'.")
        self.active_pathway_link_type = link_type
        self.active_pathway_current_node_id = effective_start_node_id

        # Immediately display the starting node and set focus
        self.set_displayed_leaves([self.active_pathway_current_node_id])
        self.set_focused_leaf(self.active_pathway_current_node_id)
        self.clear_selection()
        self.leaf_detail_overrides = {} # Clear overrides when starting a pathway? Yes.

        self._notify_observers(event_type="pathway_started", link_type=link_type, start_node_id=effective_start_node_id)


    def pathway_next(self):
        """Moves to the next node in the active pathway."""
        if not self.active_pathway_link_type or not self.active_pathway_current_node_id:
            print("No active pathway to navigate next.")
            # Notify observers that navigation failed/did nothing
            self._notify_observers(event_type="pathway_navigation_failed", direction="next", reason="no_active_pathway")
            return

        current_node = self.all_nodes.get(self.active_pathway_current_node_id)
        if current_node and self.active_pathway_link_type in current_node.links:
            next_node_id = current_node.links[self.active_pathway_link_type]
            if next_node_id in self.all_nodes:
                 # Move to the next node
                print(f"Pathway next: Moving from '{self.active_pathway_current_node_id}' to '{next_node_id}'.")
                self.active_pathway_current_node_id = next_node_id
                self.set_displayed_leaves([self.active_pathway_current_node_id]) # Display the next node (single view for simplicity)
                self.set_focused_leaf(self.active_pathway_current_node_id)
                self.clear_selection()
                self.leaf_detail_overrides = {} # Clear overrides on pathway navigation? Yes.
                self._notify_observers(event_type="pathway_navigated", direction="next", new_node_id=next_node_id)
            else:
                print(f"End of pathway or broken link: Target node '{next_node_id}' not found.")
                # Decide how to handle broken links: stop pathway, warn, etc.
                # For now, stop the pathway.
                self.stop_pathway()
                self._notify_observers(event_type="pathway_ended", reason="broken_link")
        else:
            print(f"End of pathway '{self.active_pathway_link_type}' from node '{self.active_pathway_current_node_id}'. No next link.")
            # Decide how to handle the end of a pathway
            # For now, stop the pathway.
            self.stop_pathway()
            self._notify_observers(event_type="pathway_ended", reason="end_of_links")


    def pathway_previous(self):
         """Moves to the previous node in the active pathway."""
         # This requires knowing the *sequence* navigated, not just the current link.
         # Implementation requires storing pathway history or pre-calculating sequences.
         print("pathway_previous not yet implemented.")
         self._notify_observers(event_type="pathway_navigation_failed", direction="previous", reason="not_implemented")


    def stop_pathway(self):
         """Stops navigating the current pathway."""
         if self.active_pathway_link_type:
             print(f"Stopping pathway '{self.active_pathway_link_type}'.")
             stopped_link_type = self.active_pathway_link_type # Store before clearing
             self.active_pathway_link_type = None
             # Keep displaying the current node after stopping
             self._notify_observers(event_type="pathway_stopped", link_type=stopped_link_type)
         else:
             print("No active pathway to stop.")


    # --- Getters (Methods to query the state) ---
    # These methods allow the GUI or other parts to read the current state
    # They should generally *not* modify the state.

    def get_displayed_leaves(self) -> list[Node]:
        """Returns a list of Node objects currently displayed."""
        return [self.all_nodes[node_id] for node_id in self.displayed_leaf_ids if node_id in self.all_nodes]

    def get_selected_leaves(self) -> list[Node]:
        """Returns a list of Node objects currently selected."""
        return [self.all_nodes[node_id] for node_id in self.selected_leaf_ids if node_id in self.all_nodes]

    def get_node_by_id(self, node_id: str) -> Node | None:
        """Returns a Node object by its ID, or None if not found."""
        return self.all_nodes.get(node_id)

    def get_layout(self) -> str:
        """Returns the current layout type."""
        return self.layout

    def get_focused_leaf_id(self) -> str | None:
        """Returns the ID of the currently focused leaf."""
        return self.focused_leaf_id

    def get_global_detail_level(self) -> int:
        """Returns the global default detail level."""
        return self.detail_level

    def get_effective_detail_level(self, node_id: str) -> int:
        """Gets the effective detail level for a leaf (override if exists, else global)."""
        # This method was already defined above, keeping it here for completeness
        return self.leaf_detail_overrides.get(node_id, self.detail_level)

    def get_command_buffer(self) -> str:
        """Returns the current content of the command buffer."""
        return self.command_buffer # Note: Updating command buffer state will need a dedicated method

    def get_active_pathway_link_type(self) -> str | None:
        """Returns the link type of the active pathway, or None."""
        return self.active_pathway_link_type

    def get_active_pathway_current_node_id(self) -> str | None:
         """Returns the ID of the current node in the active pathway, or None."""
         return self.active_pathway_current_node_id

    # ... add other getter methods as needed
