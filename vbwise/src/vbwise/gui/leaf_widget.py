# vbwise/gui/leaf_widget.py

import tkinter as tk
import tkinter.scrolledtext as scrolledtext
# Assume Node is available via import
from vbwise.node import Node
# Assume AppState is available (though LeafWidget mostly just needs Node and state info passed in)
# from vbwise.app_state import AppState # Not strictly needed if state info is passed


class LeafWidget(tk.Frame):
    """A Tkinter widget to display the content of a single Node."""
    def __init__(self, parent, app_state, node_id, **kwargs):
        # Inherit from tk.Frame. We'll use this frame to contain the node's content.
        super().__init__(parent, bd=2, relief=tk.GROOVE, **kwargs) # Add a border to see leaf boundaries

        self.app_state = app_state # Keep a reference to AppState to query state
        self.node_id = node_id     # Store the ID of the node this widget represents

        # --- Internal Widgets to display Node content ---
        # We'll use a ScrolledText for the main content area for simplicity initially.
        # Later, we might replace this with more complex rendering logic for different content types.

        # Use a Label for the title/header
        self.header_label = tk.Label(self, anchor=tk.W, font=('TkDefaultFont', 10, 'bold'))
        self.header_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)


        self.content_display = scrolledtext.ScrolledText(self, wrap=tk.WORD, state=tk.DISABLED, font=('TkDefaultFont', 9))
        self.content_display.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- State Variables for Visuals ---
        self._is_focused = False
        self._is_selected = False

        # --- Event Bindings ---
        # Bind clicks on the LeafWidget (or its content) to update focus/selection
        # Binding to <Button-1> on self (the frame) will capture clicks
        # Binding to the content_display might also be needed if clicks on text should focus
        self.bind("<Button-1>", self._on_click)
        self.header_label.bind("<Button-1>", self._on_click)
        self.content_display.bind("<Button-1>", self._on_click)


        # Initial display update will be called after creation in MainWindow


    def _on_click(self, event):
        """Handles a click event on the leaf widget."""
        print(f"LeafWidget '{self.node_id}' clicked.")
        # Inform the AppState that this node should be focused
        # The AppState will handle setting focus and notifying observers
        self.app_state.execute_command(f"goto {self.node_id}") # Using goto command to set focus and display

        # Also handle selection - maybe Ctrl+Click or Shift+Click for selection?
        # For now, a simple click sets focus via goto. Let's add simple selection toggle on click.
        # A single click could just set focus, maybe a right-click or key combo for selection?
        # Let's stick to single click setting focus (via goto) for now. Selection logic needs more thought on interaction.

        # If we want single click to SET focus, we need to tell AppState
        # Let's add a specific command/method for setting focus without necessarily changing displayed leaves?
        # Or does 'goto' always mean display AND focus? For now, yes.
        # Let's make a separate focus command for clarity later if needed.
        # For now, clicking a leaf essentially says "make this the current leaf".

        # A more direct way to set focus without 'goto' changing displayed leaves:
        # self.app_state.set_focused_leaf(self.node_id)
        # self.app_state._notify_observers(event_type="focused_leaf_changed", node_id=self.node_id) # Manually notify

        # Let's modify AppState slightly to have a `set_focus_and_select` method or similar,
        # or just use individual AppState methods directly here if execute_command is too heavy for clicks.
        # Let's use direct AppState methods for click handlers for responsiveness.

        # Directly update AppState for click:
        self.app_state.set_focused_leaf(self.node_id) # Set focus
        # Simple click toggles selection? No, let's keep selection separate.
        # Maybe right click selects? Or a modifier key + click?
        # For now, click only sets focus.

        # If you want click to also set displayed leaves (like `goto`):
        # self.app_state.set_displayed_leaves([self.node_id])
        # self.app_state.set_focused_leaf(self.node_id)
        # The on_state_changed observer will handle the update.

        # Let's make single click SET FOCUS ONLY initially. This requires `on_state_changed`
        # to handle the visual update for focused state without changing layout/displayed leaves.
        # This is simpler and aligns better with a multi-leaf layout where clicking just changes active leaf.
        pass # Keep the _on_click logic simple: it will call set_focused_leaf and notify observers.


    def update_display(self):
        """Updates the content and appearance of the LeafWidget based on AppState."""
        node = self.app_state.get_node_by_id(self.node_id)
        if not node:
            # Handle case where node is somehow missing
            self.header_label.config(text=f"Error: Node '{self.node_id}' not found")
            self.content_display.config(state=tk.NORMAL)
            self.content_display.delete(1.0, tk.END)
            self.content_display.insert(tk.END, "Node data could not be loaded.")
            self.content_display.config(state=tk.DISABLED)
            print(f"Error: LeafWidget cannot find node data for ID: {self.node_id}", file=sys.stderr)
            return

        # Get effective detail level for this specific leaf
        effective_detail = self.app_state.get_effective_detail_level(self.node_id)
        print(f"Updating display for node '{self.node_id}' with effective detail {effective_detail}")

        # --- Update Header ---
        header_text = node.id
        if node.title:
             header_text += f" - {node.title}"
        # Add visual indicator for override if needed
        if self.node_id in self.app_state.leaf_detail_overrides:
            header_text += f" (Detail Override: {self.app_state.leaf_detail_overrides[self.node_id]})"

        self.header_label.config(text=header_text)

        # --- Update Content ---
        displayable_lines = node.get_content_for_display(effective_detail)

        self.content_display.config(state=tk.NORMAL) # Enable editing temporarily
        self.content_display.delete(1.0, tk.END)     # Delete all current text

        # Insert content lines
        for line in displayable_lines:
            self.content_display.insert(tk.END, line + "\n")

        self.content_display.config(state=tk.DISABLED) # Disable editing again


        # --- Update Visual State (Focus/Selection) ---
        self.set_focused(self.node_id == self.app_state.get_focused_leaf_id())
        self.set_selected(self.node_id in self.app_state.selected_leaf_ids)


    def set_focused(self, is_focused: bool):
        """Visually indicates if the leaf has focus."""
        if self._is_focused != is_focused:
            self._is_focused = is_focused
            print(f"LeafWidget '{self.node_id}': is_focused = {is_focused}")
            if self._is_focused:
                self.config(relief=tk.SOLID, bd=2) # Bold border for focus
                # Optionally set background color for header/content
                # self.header_label.config(bg='lightblue')
            else:
                self.config(relief=tk.GROOVE, bd=2) # Normal border
                # self.header_label.config(bg=self.cget('bg')) # Reset background

    def set_selected(self, is_selected: bool):
        """Visually indicates if the leaf is selected."""
        if self._is_selected != is_selected:
            self._is_selected = is_selected
            print(f"LeafWidget '{self.node_id}': is_selected = {is_selected}")
            # Selection visual could be different from focus
            # Example: change background color of the frame slightly, or change relief
            if self._is_selected:
                 # Ensure focus visual overrides selection visual if both are true
                 if not self._is_focused:
                      self.config(relief=tk.RIDGE, bd=2) # Different border for selected
                     # self.header_label.config(bg='lightyellow') # Example selection highlight
            else:
                 # Only change relief/bg if it's not currently focused
                 if not self._is_focused:
                     self.config(relief=tk.GROOVE, bd=2) # Reset to normal if not focused
                     # self.header_label.config(bg=self.cget('bg'))

    # TODO: Add methods for editing content later
    # TODO: Add binding for right-click for context menu or selection
    # TODO: Add binding for keyboard navigation within the leaf (like vim j/k) - complex!


# Example Usage (for testing the widget in isolation)
if __name__ == "__main__":
    # This part requires a dummy AppState and Node
    class DummyAppState:
        def __init__(self):
            self.all_nodes = {
                "test_node_1": Node(
                    id="test_node_1",
                    title="Dummy Node 1",
                    content_lines=[("L1", "Line 1"), ("L2", "Line 2"), ("TXT", "Some text")]
                ),
                 "test_node_2": Node(
                    id="test_node_2",
                    title="Dummy Node 2",
                    content_lines=[("L1", "Another L1"), ("CODE", "print('hello')"), ("L3", "More detail")]
                ),
            }
            self.detail_level = 1
            self.leaf_detail_overrides = {"test_node_2": 3} # Override for node 2
            self.focused_leaf_id = "test_node_1"
            self.selected_leaf_ids = {"test_node_1"}

        def get_node_by_id(self, node_id):
            return self.all_nodes.get(node_id)

        def get_effective_detail_level(self, node_id):
            return self.leaf_detail_overrides.get(node_id, self.detail_level)

        def get_focused_leaf_id(self):
            return self.focused_leaf_id

        def get_selected_leaf_ids(self):
            return self.selected_leaf_ids

        # Need dummy methods that the click handler might call
        def set_focused_leaf(self, node_id):
             print(f"DummyAppState: Set focused leaf to {node_id}")
             self.focused_leaf_id = node_id
             # In real AppState, this would notify observers
             # self._notify_observers(event_type="focused_leaf_changed", node_id=node_id)
             # For isolated test, manually update visuals (or run a dummy mainloop)
             # This highlights why the observer pattern is needed - state changes automatically trigger GUI update

        # Need dummy execute_command if _on_click uses it
        def execute_command(self, command_string):
             print(f"DummyAppState: Executing command: {command_string}")
             if command_string.startswith("goto "):
                  node_id = command_string.split()[-1]
                  self.set_focused_leaf(node_id) # Simulate goto effect on focus


    root = tk.Tk()
    root.title("LeafWidget Test")

    dummy_app_state = DummyAppState()

    # Create some leaf widgets
    leaf1 = LeafWidget(root, app_state=dummy_app_state, node_id="test_node_1")
    leaf1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5) # Use pack for test

    leaf2 = LeafWidget(root, app_state=dummy_app_state, node_id="test_node_2")
    leaf2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5) # Use pack for test

    # Manually update display for test (real app uses observer)
    leaf1.update_display()
    leaf2.update_display()


    # Simulate state changes and manually update widgets
    def simulate_focus_change():
         print("\nSimulating focus change to node 2")
         dummy_app_state.set_focused_leaf("test_node_2")
         leaf1.set_focused(False) # Manually update leaf 1
         leaf2.set_focused(True)  # Manually update leaf 2

    def simulate_selection_change():
         print("\nSimulating selection change: node 2 selected, node 1 deselected")
         dummy_app_state.selected_leaf_ids = {"test_node_2"}
         leaf1.set_selected(False)
         leaf2.set_selected(True)

    def simulate_detail_change():
         print("\nSimulating global detail change to 3")
         dummy_app_state.detail_level = 3
         # Need to manually call update_display on affected leaves
         leaf1.update_display() # Node 1 will use new global level
         leaf2.update_display() # Node 2 will still use override (level 3)

    tk.Button(root, text="Simulate Focus Node 2", command=simulate_focus_change).pack(side=tk.BOTTOM)
    tk.Button(root, text="Simulate Selection Node 2", command=simulate_selection_change).pack(side=tk.BOTTOM)
    tk.Button(root, text="Simulate Detail Level 3", command=simulate_detail_change).pack(side=tk.BOTTOM)


    root.mainloop()

