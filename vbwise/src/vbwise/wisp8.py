import tkinter as tk
from tkinter import scrolledtext, ttk
import json
import os
import re

# Import refactored components
from data import comp_tkml, style_toml, nodes_gnml
from app_state import AppState
from commands import Command, GotoCommand, SetVerbosityCommand # Ensure this import is correct

# --- Attempt to import vbwise or use dummy loaders ---
try:
    from vbwise import load
    print("vbwise.load imported successfully.")
except ImportError:
    print("Warning: vbwise.load not found. Using dummy loaders for standalone execution.")
    class DummyLoad:
        def tkml_string(self, s):
            print(f"DummyTKML: Processing TKML...")
            # Updated dummy to reflect the new layout structure
            return {"type": "RootApp", "props": {}, "parts": [
                 {"type": "LeftPanel", "props": {}, "parts": [
                    {"type": "ScrollableNodeDetailList", "props": {}, "parts": []}
                ]},
                {"type": "RightPanel", "props": {}, "parts": [
                    {"type": "NodeListScrollable", "props": {}, "parts": [
                        {"type": "LeafList", "props": {}, "parts": []}
                    ]}
                ]},
                {"type": "BottomPanel", "props": {}, "parts": [
                    {"type": "PrevButton", "props": {"text": "<< Prev"}, "parts": []},
                    {"type": "NextButton", "props": {"text": "Next >>"}, "parts": []},
                    {"type": "CommandEntry", "props": {}, "parts": []},
                    {"type": "StatusBar", "props": {"text": "Status: OK"}, "parts": []}
                ]}
            ]}
        def toml_string(self, s):
            print(f"DummyTOML: Processing TOML...")
            # Updated dummy to reflect the new style section name
            return { "default": {
                    "NodeListScrollable": {"leaf_width": 10, "leaf_side": "left", "indicator_height": 20},
                    "LeafList": {"default_text_levels": ["T1"], "default_code_levels": ["C1"]},
                    "ScrollableNodeDetailList": {"font_family": "Arial", "font_size": 10, "node_separator": "\\n---\\n"},
                    "CommandEntry": {"placeholder": "Cmd: goto <id> | t12 c3 | default"},
                    "StatusBar": {"relief": "sunken", "anchor": "w"}
            }}
        def gnml_string(self, s):
            print(f"DummyGNML: Processing GNML...")
            return [
                {'id': 'dummy_node1', 'text_lines': [{'level': 'T1', 'content': 'Dummy T1 Content'}], 'code_lines': [{'level': 'C1', 'content': 'dummy_c1_code()'}], 'next': ['dummy_node2'], 'prev': []},
                {'id': 'dummy_node2', 'text_lines': [{'level': 'T1', 'content': 'Another Dummy T1'}], 'next': [], 'prev': ['dummy_node1']}
            ]
    load = DummyLoad()


# --- UI Application (View and Controller) ---
class NodeNavigatorApp:
    def __init__(self, root_tk, app_state, layout_config, style_config):
        self.root = root_tk
        self.state = app_state
        self.layout_config = layout_config
        self.style_config = style_config
        self.ui_elements = {}
        self._node_detail_text_widget = None # Keep a direct ref for easier access

        # *** Ensure self.commands is initialized here ***
        self.commands = {
            "goto": GotoCommand(),
            "select": GotoCommand(),
        }
        self.verbosity_command_regex = re.compile(r"^(t[1-3a-z]*|c[1-3a-z]*|default)\b", re.IGNORECASE)
        # **********************************************


        self.root.title("Wisp6 Navigator")
        self.root.geometry("1000x700") # Slightly larger window for new layout
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)


        # Updated component factories for the new layout and widget types
        self.component_factories = {
            "LeftPanel": self._create_panel_frame,
            "RightPanel": self._create_panel_frame,
            "BottomPanel": self._create_panel_frame,
            "ScrollableNodeDetailList": self._create_scrollable_node_detail_list_widget, # New factory
            "NodeListScrollable": self._create_node_tree_widget,  # Factory for the Treeview (now on the right)
            "DetailView": lambda parent, cfg: None, # Old DetailView is replaced
            "PrevButton": self._create_button_widget,
            "NextButton": self._create_button_widget,
            "CommandEntry": self._create_command_entry_widget,
            "StatusBar": self._create_status_bar_widget,
            "LeafList": lambda parent, cfg: None, # LeafList is part of the Treeview concept
            "RootApp": lambda parent, cfg: self.root
        }

        # Call the new grid-based layout builder
        self._build_grid_layout(self.root, self.layout_config)

        # Add tag configuration for highlighting
        if self._node_detail_text_widget:
             self._node_detail_text_widget.tag_configure("highlight", background="yellow", foreground="black")


        self.state.on_selection_change(self._handle_node_selection_change)
        self.state.on_verbosity_change(self._handle_verbosity_change)
        self.state.on_status_update(self._update_status_bar)

        self._populate_node_tree()  # Populate the Treeview
        self._render_all_node_details() # Render all details initially

        if self.state.get_node_count() > 0:
            # Select the initial node after rendering all details
            self._handle_node_selection_change(self.state.current_node_index)
        else:
             self._update_nav_buttons_state()
             self.state.update_status("No nodes loaded.", "info")


    def _on_closing(self):
        self.state.save_persistent_state()
        self.root.destroy()

    def _get_style_props(self, component_type, tkml_props=None):
        style = self.style_config.get('default', {}).get(component_type, {}).copy()
        if tkml_props: style.update(tkml_props)
        return style

    # Panel creation remains the same, packing/gridding is handled by the caller
    def _create_panel_frame(self, parent_tk, tkml_config):
        props = self._get_style_props(tkml_config.get("type"), tkml_config.get("props"))
        frame = tk.Frame(parent_tk, bd=props.get("bd",1), relief=props.get("relief",tk.SUNKEN))
        return frame

    # New method to build the main grid layout
    def _build_grid_layout(self, parent_tk_widget, tkml_config_node):
        if tkml_config_node.get("type") != "RootApp":
             print(f"Warning: _build_grid_layout called with non-RootApp type: {tkml_config_node.get('type')}")
             return

        # Configure the root grid (2 rows, 2 columns)
        parent_tk_widget.grid_rowconfigure(0, weight=1) # Top row (panels) expands vertically
        parent_tk_widget.grid_rowconfigure(1, weight=0) # Bottom row (status bar etc) does not expand vertically
        parent_tk_widget.grid_columnconfigure(0, weight=1) # Left column expands horizontally
        parent_tk_widget.grid_columnconfigure(1, weight=1) # Right column expands horizontally

        panel_widgets = {}
        panel_configs = {}

        # Create panel widgets based on TKML config
        for part_config in tkml_config_node.get("parts", []):
             component_type = part_config.get("type")
             if component_type in ["LeftPanel", "RightPanel", "BottomPanel"]:
                 # Create panel frames using the factory
                 panel_widgets[component_type] = self._create_panel_frame(parent_tk_widget, part_config)
                 panel_configs[component_type] = part_config
                 self.ui_elements[component_type] = panel_widgets[component_type] # Store panel widgets

        # Place panels in the grid
        if "LeftPanel" in panel_widgets:
             props = self._get_style_props("LeftPanel")
             panel_widgets["LeftPanel"].grid(row=0, column=0, sticky="nsew",
                                             padx=props.get("padx", 5), pady=props.get("pady", 5))
             # Recursively build children inside the LeftPanel
             if "LeftPanel" in panel_configs:
                  for part_config in panel_configs["LeftPanel"].get("parts", []):
                       self._build_ui_recursive(panel_widgets["LeftPanel"], part_config)


        if "RightPanel" in panel_widgets:
             props = self._get_style_props("RightPanel")
             panel_widgets["RightPanel"].grid(row=0, column=1, sticky="nsew",
                                              padx=props.get("padx", 5), pady=props.get("pady", 5))
             # Recursively build children inside the RightPanel
             if "RightPanel" in panel_configs:
                  for part_config in panel_configs["RightPanel"].get("parts", []):
                       self._build_ui_recursive(panel_widgets["RightPanel"], part_config)


        if "BottomPanel" in panel_widgets:
             props = self._get_style_props("BottomPanel")
             panel_widgets["BottomPanel"].grid(row=1, column=0, columnspan=2, sticky="nsew",
                                               padx=props.get("padx", 5), pady=props.get("pady", 2))
             # Recursively build children inside the BottomPanel
             if "BottomPanel" in panel_configs:
                  for part_config in panel_configs["BottomPanel"].get("parts", []):
                       self._build_ui_recursive(panel_widgets["BottomPanel"], part_config)

        # Note: Any other direct children of RootApp not explicitly handled as panels
        # in the loop above would need separate grid placement logic here if they existed.


    # Recursive build method for components *within* panels or other containers (using pack)
    def _build_ui_recursive(self, parent_tk_widget, tkml_config_node):
        component_type = tkml_config_node.get("type")
        tkml_props = tkml_config_node.get("props", {})
        factory_method = self.component_factories.get(component_type)
        current_widget = None

        # Main panels and RootApp are handled by _build_grid_layout, so skip them here
        if component_type in ["LeftPanel", "RightPanel", "BottomPanel", "RootApp"]:
             return


        if factory_method:
            # Factories for ScrollableNodeDetailList and NodeListScrollable create a container frame
            # and pack the actual widget inside. Their children in TKML (like LeafList)
            # don't create separate widgets we need to pack here.
            if component_type in ["ScrollableNodeDetailList", "NodeListScrollable"]:
                 current_widget = factory_method(parent_tk_widget, tkml_config_node)
                 if component_type == "ScrollableNodeDetailList":
                      self.ui_elements['node_detail_list_widget'] = current_widget
                      self._node_detail_text_widget = current_widget
                 elif component_type == "NodeListScrollable":
                      self.ui_elements['node_tree_widget'] = current_widget

                 # Recursively build children - for these, the children are logically contained
                 # but might not be distinct Tkinter widgets to pack recursively based on TKML.
                 # However, the factory method for these *returns the main widget* (ScrolledText/Treeview),
                 # but packs it inside a container frame *created within the factory*.
                 # So, if there were nested elements to pack within the container, we'd pass the container.
                 # Given LeafList is the child and its factory returns None, this loop might be unnecessary
                 # for these specific component types with the current TKML structure, but leaving it
                 # for generality if TKML structure changes. Pass the parent_tk_widget (the panel frame).
                 if tkml_config_node.get("parts"):
                     for part_config in tkml_config_node.get("parts", []):
                          self._build_ui_recursive(parent_tk_widget, part_config) # Pass the panel frame


            elif component_type not in ["RootApp", "LeafList"]: # Skip RootApp and LeafList here
                 current_widget = factory_method(parent_tk_widget, tkml_config_node)
                 widget_name = tkml_props.get("id", component_type)
                 self.ui_elements[widget_name] = current_widget
                 # For other widgets, recursively build their children within them using pack
                 if current_widget and tkml_config_node.get("parts"):
                     for part_config in tkml_config_node.get("parts", []):
                         self._build_ui_recursive(current_widget, part_config)

        else:
            print(f"Warning: No factory for TKML type: {component_type}")
            # Create a default frame if no factory exists but it has children
            if tkml_config_node.get("parts"):
                current_widget = tk.Frame(parent_tk_widget)
                current_widget.pack(fill=tk.BOTH, expand=True)
                for part_config in tkml_config_node.get("parts", []):
                    self._build_ui_recursive(current_widget, part_config)

        # Note: Widgets created and packed here are packed into parent_tk_widget.
        # This is correct for components *within* the main panels.


        return current_widget


    def _create_scrollable_node_detail_list_widget(self, parent_tk, tkml_config):
        """Create a ScrolledText widget to display all node details, packed into a container."""
        props = self._get_style_props("ScrollableNodeDetailList", tkml_config.get("props"))
        # Create a frame to hold the label and the scrolled text, packing it into the parent_tk (LeftPanel)
        container_frame = tk.Frame(parent_tk)
        container_frame.pack(fill=tk.BOTH, expand=True) # Make container fill the parent panel

        tk.Label(container_frame, text="Node Details", font=('Arial',10,'bold')).pack(pady=(5,2), anchor=tk.W)
        detail_text = scrolledtext.ScrolledText(container_frame, wrap=tk.WORD, height=props.get("height",10),
                                                relief=props.get("relief",tk.FLAT), font=(props.get("font_family","Courier New"), props.get("font_size",10)))
        detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5)) # Make text widget fill the container
        detail_text.config(state=tk.DISABLED)
        # Bind click event to detect which node was clicked
        detail_text.bind("<Button-1>", self._on_detail_list_click)
        return detail_text # Return the scrolledtext widget


    def _on_detail_list_click(self, event):
        """Handle click events in the scrollable detail list."""
        widget = event.widget
        # Get the index of the clicked character
        index = widget.index(f"@{event.x},{event.y}")
        # Find the tag associated with the node ID at this index
        tags = widget.tag_names(index)
        for tag in tags:
            if tag.startswith("node_"):
                node_id = tag[len("node_"):]
                # print(f"Clicked on node ID: {node_id}") # Debugging print
                # Select the node in the state, which will trigger UI updates
                self.state.select_node_by_id(node_id)
                return # Process only the first node tag found

    def _create_node_tree_widget(self, parent_tk, tkml_config):
        """Create a Treeview widget to display nodes hierarchically, packed into a container."""
        props = self._get_style_props("NodeListScrollable", tkml_config.get("props"))
        # Create a frame to hold the label and the treeview, packing it into the parent_tk (RightPanel)
        container_frame = tk.Frame(parent_tk)
        container_frame.pack(fill=tk.BOTH, expand=True) # Fill the RightPanel

        tk.Label(container_frame, text="Nodes", font=('Arial',10,'bold')).pack(pady=(5,2), anchor=tk.W)
        tree = ttk.Treeview(container_frame, show='tree')  # 'tree' mode hides headers
        tree.pack(fill=tk.BOTH, expand=True) # Make Treeview fill its container frame fully
        tree.bind('<<TreeviewSelect>>', self._on_tree_select)
        # Store the Treeview widget itself
        return tree # Return the tree widget


    def _on_tree_select(self, event):
        """Handle node selection in the Treeview."""
        tree = event.widget
        selected_items = tree.selection()
        if selected_items:
            selected_id = selected_items[0]  # Single selection assumed
            # Select the node in the state, which will trigger UI updates
            self.state.select_node_by_id(selected_id)


    def _create_button_widget(self, parent_tk, tkml_config):
        component_type = tkml_config.get("type")
        props = self._get_style_props(component_type, tkml_config.get("props"))
        command_action = None
        if component_type == "PrevButton": 
            command_action = self._show_prev_node
        elif component_type == "NextButton":
            command_action = self._show_next_node
        button = tk.Button(parent_tk, text=props.get("text",component_type), command=command_action)
        button.pack(side=props.get("side",tk.LEFT), padx=props.get("padx",5))
        return button

    def _create_command_entry_widget(self, parent_tk, tkml_config):
        props = self._get_style_props("CommandEntry", tkml_config.get("props"))
        placeholder = props.get("placeholder","Cmd: goto <id> | t1 c123 | default | quit")
        self.ui_elements['command_entry_placeholder'] = placeholder
        cmd_entry = tk.Entry(parent_tk, relief=props.get("relief",tk.SUNKEN), bd=props.get("bd",1), fg='grey')
        cmd_entry.insert(0, placeholder)
        cmd_entry.pack(fill=tk.X, expand=True, padx=5)
        cmd_entry.bind('<Return>', self._on_command_submit)
        cmd_entry.bind("<FocusIn>", self._on_command_focus_in)
        cmd_entry.bind("<FocusOut>", self._on_command_focus_out)
        return cmd_entry

    def _create_status_bar_widget(self, parent_tk, tkml_config):
        props = self._get_style_props("StatusBar", tkml_config.get("props"))
        status_bar = tk.Label(parent_tk, text=props.get("text","Status: OK"), relief=props.get("relief",tk.SUNKEN),
                              anchor=props.get("anchor","w"), height=props.get("height",1))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(2,0), padx=5)
        return status_bar


    def _populate_node_tree(self):
        """Populate the Treeview with nodes in a hierarchical structure."""
        tree = self.ui_elements.get('node_tree_widget')
        if not tree:
            return
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        inserted_set = set()
        # Find root nodes (no 'prev' links) - simplified for tree view
        roots = [node_id for node_id, node_data in self.state.nodes_map.items() if not node_data.get('prev', [])]
        for root_id in roots:
            self._insert_node_tree(tree, root_id, '', inserted_set)
        # Add any nodes not reachable from roots
        for node_id in self.state.nodes_map:
            if node_id not in inserted_set:
                tree.insert('', 'end', iid=node_id, text=node_id)
                inserted_set.add(node_id)


    def _insert_node_tree(self, tree, node_id, parent_iid, inserted_set):
        """Recursively insert nodes into the Treeview based on 'next' links."""
        if node_id in inserted_set:
            return
        tree.insert(parent_iid, 'end', iid=node_id, text=node_id)
        inserted_set.add(node_id)
        node_data = self.state.nodes_map.get(node_id, {})
        for next_id in node_data.get('next', []):
            self._insert_node_tree(tree, next_id, node_id, inserted_set)

    def _render_all_node_details(self):
        """Render details for all nodes in the scrollable list."""
        text_widget = self._node_detail_text_widget
        if not text_widget:
            return

        text_widget.config(state=tk.NORMAL)
        text_widget.delete('1.0', tk.END)

        separator = self._get_style_props("ScrollableNodeDetailList").get("node_separator", "\\n---\\n").replace("\\n", "\n")

        for i, node in enumerate(self.state.node_list):
            node_id = node.get('id', f'Unnamed_{i}')
            # Start index for the entire node's content block (header + content)
            start_index_node_block = text_widget.index(tk.END)

            # Add a header for the node
            header = f"--- NODE: {node_id} ---\n"
            text_widget.insert(tk.END, header)

            content_lines = []
            for tl in node.get('text_lines', []):
                if tl.get('level', '').upper() in self.state.active_text_levels:
                    content_lines.append(f"{tl['level']}> {tl.get('content', '')}")
            for cl in node.get('code_lines', []):
                if cl.get('level', '').upper() in self.state.active_code_levels:
                    content_lines.append(f"{cl['level']}> {cl.get('content', '')}")

            if content_lines:
                content_text = "\n".join(content_lines) + "\n"
                text_widget.insert(tk.END, content_text)
            else:
                no_content_msg = f"(No content for T=[{','.join(self.state.active_text_levels)}] C=[{','.join(self.state.active_code_levels)}])\n"
                text_widget.insert(tk.END, no_content_msg)

            # Get the index after inserting content or no content message
            end_index_node_block = text_widget.index(tk.END)

            # Tag the entire node block (header + content/no content) with the node ID
            text_widget.tag_add(f"node_{node_id}", start_index_node_block, end_index_node_block)

            # Add separator if not the last node
            if i < len(self.state.node_list) - 1:
                separator_start_index = text_widget.index(tk.END)
                text_widget.insert(tk.END, separator)
                separator_end_index = text_widget.index(tk.END)
                # Tag the separator with the node ID as part of the previous node's block
                # This makes the separator clickable and selects the previous node
                text_widget.tag_add(f"node_{node_id}", separator_start_index, separator_end_index)


        text_widget.config(state=tk.DISABLED)
        self._highlight_current_node_detail() # Highlight the current node after rendering

    def _highlight_current_node_detail(self):
        """Highlights the current node's section in the scrollable detail list."""
        text_widget = self._node_detail_text_widget
        if not text_widget:
            return

        # Remove previous highlights
        text_widget.tag_remove("highlight", "1.0", tk.END)

        current_node = self.state.get_current_node()
        if current_node:
            node_id = current_node.get('id', 'N/A')
            # Find the start and end indices for the current node's tag
            # ScrolledText tags apply to ranges of text. We can find all ranges with the node's tag.
            tag_name = f"node_{node_id}"
            ranges = text_widget.tag_ranges(tag_name)
            if ranges:
                # Apply highlight tag to all ranges associated with this node ID tag
                for i in range(0, len(ranges), 2):
                    start, end = ranges[i], ranges[i+1]
                    text_widget.tag_add("highlight", start, end)

                # Scroll to the beginning of the first range for this node
                if ranges: # Ensure ranges is not empty before trying to access ranges[0]
                    text_widget.see(ranges[0])


    def _handle_node_selection_change(self, selected_index):
        """Update UI elements when the current node changes."""
        tree = self.ui_elements.get('node_tree_widget')
        if tree:
            current_id = self.state.get_current_node_id()
            # Update treeview selection without triggering its binding again
            if tree.exists(current_id):
                 tree.selection_remove(tree.selection()) # Deselect all
                 tree.selection_add(current_id)         # Select current
                 tree.see(current_id) # Scroll treeview to selected item

        # Highlight the corresponding section in the detail list
        self._highlight_current_node_detail()
        self._update_nav_buttons_state()

    def _handle_verbosity_change(self):
        # Re-render all details when verbosity changes
        self._render_all_node_details()
        # Re-highlight the current node after re-rendering
        self._highlight_current_node_detail()


    def _update_status_bar(self, message, msg_type):
        status_bar = self.ui_elements.get("StatusBar")
        if status_bar:
            status_bar.config(text=f"{message}")
            colors = {"error": "red", "success": "green", "info": "black"}
            status_bar.config(fg=colors.get(msg_type, "black"))

    def _update_nav_buttons_state(self):
        pb, nb = self.ui_elements.get('PrevButton'), self.ui_elements.get('NextButton')
        count, idx = self.state.get_node_count(), self.state.current_node_index
        if pb: pb.config(state=tk.DISABLED if idx <= 0 or count == 0 else tk.NORMAL)
        if nb: nb.config(state=tk.DISABLED if idx >= count - 1 or count == 0 else tk.NORMAL)

    # --- Navigation methods ---
    def _show_prev_node(self):
        if self.state.current_node_index > 0:
            self.state.select_node_by_index(self.state.current_node_index - 1, source="prev_button")

    def _show_next_node(self):
        if self.state.current_node_index < self.state.get_node_count() - 1:
            self.state.select_node_by_index(self.state.current_node_index + 1, source="next_button")
    # --------------------------

    def _on_command_focus_in(self, event):
        entry, ph = self.ui_elements.get('CommandEntry'), self.ui_elements.get('command_entry_placeholder')
        if entry and entry.get() == ph:
            entry.delete(0, tk.END)
            entry.config(fg='black')
    def _on_command_focus_out(self, event):
        entry, ph = self.ui_elements.get('CommandEntry'), self.ui_elements.get('command_entry_placeholder')
        if entry and not entry.get():
            entry.insert(0, ph)
            entry.config(fg='grey')

    def _on_command_submit(self, event):
        cmd_entry = self.ui_elements.get('CommandEntry')
        if not cmd_entry:
            return
        command_str = cmd_entry.get().strip()
        placeholder = self.ui_elements.get('command_entry_placeholder')
        if command_str and command_str != placeholder:
            cmd_entry.delete(0, tk.END)
            self._execute_cli_command(command_str)

    def _execute_cli_command(self, command_str):
        """Handle commands, including new 'quit' or 'q' for graceful exit."""
        parts = command_str.split(maxsplit=1)
        first_part = parts[0].lower()
        args_str = parts[1] if len(parts) > 1 else ""

        # Handle quit command
        if first_part in ['quit', 'q']:
            self._on_closing()
            return

        # Existing command handling
        if first_part in self.commands: # Error reported here
            command_obj = self.commands[first_part]
            original_args = command_str.split(maxsplit=1)[1] if len(command_str.split(maxsplit=1)) > 1 else ""
            command_obj.execute(self.state, self, original_args)
        elif self.verbosity_command_regex.match(command_str):
            verbosity_cmd_obj = SetVerbosityCommand()
            verbosity_cmd_obj.execute(self.state, self, command_str)
        else:
            self.state.update_status(f"Unknown command: '{first_part}'", "error")

# --- Main Execution ---
if __name__ == "__main__":
    print("Loading TKML...")
    parsed_comp_layout = load.tkml_string(comp_tkml)
    print("Loading TOML...")
    parsed_style_config = load.toml_string(style_toml)
    print("Loading GNML...")
    parsed_nodes_data = load.gnml_string(nodes_gnml)

    # Initialize AppState with loaded data
    app_state = AppState(parsed_nodes_data, parsed_style_config)

    root = tk.Tk()
    # Initialize the main application UI, passing the state and configurations
    app_ui = NodeNavigatorApp(root, app_state, parsed_comp_layout, parsed_style_config)
    root.mainloop()

