import tkinter as tk
from tkinter import scrolledtext, ttk  # Added ttk for Treeview
import re
import json
import os

# --- Attempt to import vbwise or use dummy loaders ---
try:
    from vbwise import load
    print("vbwise.load imported successfully.")
except ImportError:
    print("Warning: vbwise.load not found. Using dummy loaders for standalone execution.")
    class DummyLoad:
        def tkml_string(self, s):
            print(f"DummyTKML: Processing TKML...")
            return {"type": "RootApp", "props": {}, "parts": [
                {"type": "LeftPanel", "props": {}, "parts": [
                    {"type": "NodeListScrollable", "props": {}, "parts": [
                        {"type": "LeafList", "props": {}, "parts": []}
                    ]}
                ]},
                {"type": "RightPanel", "props": {}, "parts": [
                    {"type": "DetailView", "props": {}, "parts": []}
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
            return { "default": {
                    "NodeListScrollable": {"leaf_width": 10, "leaf_side": "left", "indicator_height": 20},
                    "LeafList": {"default_text_levels": ["T1"], "default_code_levels": ["C1"]},
                    "DetailView": {"font_family": "Arial", "font_size": 10},
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

# --- Data Strings (Unchanged) ---
comp_tkml_wisp5 = """
RootApp {
    LeftPanel {
        NodeListScrollable { LeafList {} }
    }
    RightPanel {
        DetailView {}
    }
    BottomPanel {
        PrevButton { text: "<< Prev" }
        NextButton { text: "Next >>" }
        CommandEntry {}
        StatusBar { text: "Welcome to Wisp6!" anchor: "w" }
    }
}
"""

style_toml_wisp5 = """
[default.NodeListScrollable]
leaf_width = 15
leaf_side = "left"
indicator_height = 22

[default.LeafList]
default_text_levels = ["T1", "T2"]
default_code_levels = ["C1"]

[default.DetailView]
font_family = "Courier New"
font_size = 10

[default.CommandEntry]
placeholder = "Cmd: goto <id> | t1 c123 | default | quit"

[default.StatusBar]
relief = "sunken"
anchor = "w"
height = 1 

[default.PrevButton]
[default.NextButton]
"""

nodes_gnml_wisp5 = """
### NODE
--- id: help_node
T1> Welcome to Wisp Navigator! (T1)
T2> This is the interactive help node. (T2)
T2> Available commands:
T2>   goto <node_id>        (e.g., goto node_alpha)
T2>   select <node_id>      (alias for goto)
T2>   t[123|all] c[123|all] (e.g., t13 c2, tall c1)
T2>   t[123|all]            (e.g., t1)
T2>   c[123|all]            (e.g., c23)
T2>   default               (resets verbosity)
T2>   quit or q             (exit the application)
T3> (This is a T3 help line)
C1> print("Accessing help_node information...")
C2> pass
--- next: node_alpha
### ENDNODE

### NODE
--- id: node_alpha
T1> Alpha Node: Primary Information.
T2> Alpha Node: Secondary Details.
T3> Alpha Node: Tertiary/Fine print.
C1> alpha_var = "initialized"
C2> def alpha_main_op():
C2>     print(f"Alpha main operation with {alpha_var}")
C3> def alpha_utility():
C3>     return "Alpha utility done"
--- prev: help_node
--- next: node_beta
### ENDNODE

### NODE
--- id: node_beta
T1> Beta Node: Overview of Beta. (T1)
T2> Beta Node: Specific data points for Beta. (T2)
C1> BETA_CONFIG = {"param1": 10, "param2": "beta_value"}
C2> run_beta_core(BETA_CONFIG)
--- prev: node_alpha
--- next: node_gamma
### ENDNODE

### NODE
--- id: node_gamma
T1> Gamma Node: Summary and conclusions. (T1)
T3> Gamma Node: Detailed references (T3).
C1> print("Gamma entry point executed.")
C3> log_gamma_details("verbose logging data for gamma")
--- prev: node_beta
--- next: node_delta
### ENDNODE

### NODE
--- id: node_delta
T1> Delta Node: Text Level 1 only.
C1> delta_code_l1 = True
C2> delta_code_l2 = "active"
C3> delta_code_l3 = None
--- prev: node_gamma
### ENDNODE
"""

APP_STATE_FILE = "wisp_app_state.json"

# --- Application State (Model) - Unchanged ---
class AppState:
    def __init__(self, nodes_data, style_config_data):
        self.node_list = []
        self.nodes_map = {}
        self._build_node_graph(nodes_data if isinstance(nodes_data, list) else [])
        
        self.current_node_index = 0
        self.active_text_levels = []
        self.active_code_levels = []
        self.default_text_levels = ["T1", "T2", "T3"]
        self.default_code_levels = ["C1", "C2", "C3"]
        
        self._selection_callbacks = []
        self._verbosity_callbacks = []
        self._status_callbacks = []

        self._load_verbosity_defaults(style_config_data)
        self._load_persistent_state()

        print(f"AppState Initialized: Nodes: {len(self.node_list)}, Active T: {self.active_text_levels}, Active C: {self.active_code_levels}, Index: {self.current_node_index}")

    def _build_node_graph(self, raw_nodes_data):
        self.node_list = raw_nodes_data
        for i, node_data in enumerate(raw_nodes_data):
            node_id = node_data.get('id')
            if node_id:
                self.nodes_map[node_id] = node_data
                node_data['_index_in_list'] = i
            else:
                print(f"Warning: Node at index {i} has no ID, cannot be mapped.")
        
        for node_id, node_data in self.nodes_map.items():
            for next_id in node_data.get('next', []):
                if next_id not in self.nodes_map:
                    print(f"Warning: Node '{node_id}' has 'next' link to non-existent ID '{next_id}'")
            for prev_id in node_data.get('prev', []):
                if prev_id not in self.nodes_map:
                    print(f"Warning: Node '{node_id}' has 'prev' link to non-existent ID '{prev_id}'")

    def _load_verbosity_defaults(self, style_conf):
        try:
            leaf_list_style = style_conf.get('default', {}).get('LeafList', {})
            dtl = leaf_list_style.get('default_text_levels')
            if isinstance(dtl, list) and all(isinstance(s, str) and re.fullmatch(r"T[1-3]", s.upper()) for s in dtl):
                self.default_text_levels = [level.upper() for level in dtl]
            dcl = leaf_list_style.get('default_code_levels')
            if isinstance(dcl, list) and all(isinstance(s, str) and re.fullmatch(r"C[1-3]", s.upper()) for s in dcl):
                self.default_code_levels = [level.upper() for level in dcl]
        except Exception as e:
            print(f"CRITICAL ERROR loading verbosity defaults: {e}. Using fallbacks.")

    def _load_persistent_state(self):
        initial_status_message = "No saved state found. Using default settings."
        initial_status_type = "info"
        try:
            if os.path.exists(APP_STATE_FILE):
                with open(APP_STATE_FILE, 'r') as f:
                    state_data = json.load(f)
                saved_node_id = state_data.get('current_node_id')
                if saved_node_id and saved_node_id in self.nodes_map:
                    self.current_node_index = self.nodes_map[saved_node_id].get('_index_in_list', 0)
                else:
                    self.current_node_index = 0

                self.active_text_levels = state_data.get('active_text_levels', list(self.default_text_levels))
                self.active_code_levels = state_data.get('active_code_levels', list(self.default_code_levels))
                initial_status_message = f"Loaded saved state from {APP_STATE_FILE}"
            else:
                self.active_text_levels = list(self.default_text_levels)
                self.active_code_levels = list(self.default_code_levels)
                self.current_node_index = 0 if self.node_list else -1
        except Exception as e:
            initial_status_message = f"Error loading persistent state: {e}. Using defaults."
            initial_status_type = "error"
            self.active_text_levels = list(self.default_text_levels)
            self.active_code_levels = list(self.default_code_levels)
            self.current_node_index = 0 if self.node_list else -1
        
        self.update_status(initial_status_message, initial_status_type)

        if not (0 <= self.current_node_index < len(self.node_list)) and len(self.node_list) > 0:
            self.current_node_index = 0
            self.update_status(f"Reset invalid saved index to 0.", "info")
        elif len(self.node_list) == 0:
            self.current_node_index = -1

    def save_persistent_state(self):
        current_node_id_to_save = self.get_current_node_id()
        state_data = {
            'current_node_id': current_node_id_to_save,
            'active_text_levels': self.active_text_levels,
            'active_code_levels': self.active_code_levels
        }
        try:
            with open(APP_STATE_FILE, 'w') as f:
                json.dump(state_data, f, indent=4)
            self.update_status(f"App state saved to {APP_STATE_FILE}", "info")
        except Exception as e:
            self.update_status(f"Error saving app state: {e}", "error")

    def on_selection_change(self, callback): self._selection_callbacks.append(callback)
    def on_verbosity_change(self, callback): self._verbosity_callbacks.append(callback)
    def on_status_update(self, callback): self._status_callbacks.append(callback)

    def _notify_selection_watchers(self):
        for cb in self._selection_callbacks: cb(self.current_node_index)
    def _notify_verbosity_watchers(self):
        for cb in self._verbosity_callbacks: cb()
    def _notify_status_watchers(self, message, msg_type):
        if hasattr(self, '_status_callbacks'):
            for cb in self._status_callbacks: cb(message, msg_type)
        else:
            print(f"EARLY STATUS ({msg_type.upper()}): {message} (_status_callbacks not yet init)")

    def update_status(self, message, msg_type="info"):
        print(f"STATUS ({msg_type.upper()}): {message}")
        self._notify_status_watchers(message, msg_type)

    def select_node_by_index(self, index, source="unknown"):
        if not self.node_list or not (0 <= index < len(self.node_list)):
            self.update_status(f"Invalid index {index} for node selection.", "error")
            return
        if self.current_node_index != index:
            self.current_node_index = index
            self._notify_selection_watchers()
            self.update_status(f"Node '{self.get_current_node_id()}' selected (source: {source}).", "info")
            self.save_persistent_state()

    def select_node_by_id(self, node_id):
        if node_id in self.nodes_map:
            node_data = self.nodes_map[node_id]
            list_index = node_data.get('_index_in_list', -1)
            if list_index != -1:
                self.select_node_by_index(list_index, source="id_lookup")
                return True
            else:
                self.update_status(f"Node ID '{node_id}' found in map but missing list index.", "error")
                return False
        self.update_status(f"Node ID '{node_id}' not found.", "error")
        return False

    def update_verbosity(self, text_flags_str=None, code_flags_str=None, reset_to_default=False):
        changed = False
        old_t, old_c = list(self.active_text_levels), list(self.active_code_levels)

        if reset_to_default:
            self.active_text_levels = list(self.default_text_levels)
            self.active_code_levels = list(self.default_code_levels)
            if old_t != self.active_text_levels or old_c != self.active_code_levels:
                changed = True
            self.update_status(f"Verbosity reset to defaults: T={self.active_text_levels}, C={self.active_code_levels}", "info")
        else:
            if text_flags_str is not None:
                new_t_levels = []
                if text_flags_str.lower() == "all": new_t_levels = [f"T{i}" for i in range(1, 4)]
                else: new_t_levels = sorted(list(set([f"T{num}" for num in text_flags_str if num in "123"])))
                if self.active_text_levels != new_t_levels:
                    self.active_text_levels = new_t_levels
                    changed = True
            
            if code_flags_str is not None:
                new_c_levels = []
                if code_flags_str.lower() == "all": new_c_levels = [f"C{i}" for i in range(1, 4)]
                else: new_c_levels = sorted(list(set([f"C{num}" for num in code_flags_str if num in "123"])))
                if self.active_code_levels != new_c_levels:
                    self.active_code_levels = new_c_levels
                    changed = True
            
            if changed and not reset_to_default:
                self.update_status(f"Verbosity updated: T={self.active_text_levels}, C={self.active_code_levels}", "info")
        
        if changed:
            self._notify_verbosity_watchers()
            self.save_persistent_state()

    def get_current_node(self):
        if self.node_list and 0 <= self.current_node_index < len(self.node_list):
            return self.node_list[self.current_node_index]
        return None
    def get_current_node_id(self):
        node = self.get_current_node()
        return node.get('id', 'N/A') if node else 'N/A'
    def get_all_nodes_info(self):
        return [{'id': n.get('id', f'Unnamed_{i}'), 'index': i} for i, n in enumerate(self.node_list)]
    def get_node_count(self): return len(self.node_list)

    def get_linked_nodes(self, node_id, link_type='next'):
        linked_node_objects = []
        if node_id in self.nodes_map:
            current_node_data = self.nodes_map[node_id]
            for linked_id in current_node_data.get(link_type, []):
                if linked_id in self.nodes_map:
                    linked_node_objects.append(self.nodes_map[linked_id])
                else:
                    self.update_status(f"Warning: Broken link '{link_type}' from '{node_id}' to '{linked_id}'", "error")
        return linked_node_objects

# --- Command Pattern (Unchanged) ---
class Command:
    def execute(self, app_state, app_ui, args_str):
        raise NotImplementedError

class GotoCommand(Command):
    def execute(self, app_state, app_ui, args_str):
        if args_str:
            app_state.select_node_by_id(args_str)
        else:
            app_state.update_status("Goto command requires a node ID.", "error")

class SetVerbosityCommand(Command):
    def execute(self, app_state, app_ui, args_str):
        if args_str.lower() == "default":
            app_state.update_verbosity(reset_to_default=True)
        else:
            text_match = re.search(r't([1-3]+|all)\b', args_str, re.IGNORECASE)
            code_match = re.search(r'c([1-3]+|all)\b', args_str, re.IGNORECASE)
            text_flags = text_match.group(1) if text_match else None
            code_flags = code_match.group(1) if code_match else None
            
            if not text_flags and not code_flags:
                app_state.update_status(f"Invalid verbosity command: '{args_str}'. Use t/c flags or 'default'.", "error")
                return
            app_state.update_verbosity(text_flags_str=text_flags, code_flags_str=code_flags)

# --- UI Application (View and Controller) ---
class NodeNavigatorApp:
    def __init__(self, root_tk, app_state, layout_config, style_config):
        self.root = root_tk
        self.state = app_state
        self.layout_config = layout_config
        self.style_config = style_config
        self.ui_elements = {}

        self.root.title("Wisp6 Navigator")  # Updated title
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.component_factories = {
            "LeftPanel": self._create_frame_widget,
            "RightPanel": self._create_frame_widget,
            "BottomPanel": self._create_frame_widget,
            "NodeListScrollable": self._create_node_tree_widget,  # Updated to use tree widget
            "DetailView": self._create_detail_view_widget,
            "PrevButton": self._create_button_widget,
            "NextButton": self._create_button_widget,
            "CommandEntry": self._create_command_entry_widget,
            "StatusBar": self._create_status_bar_widget,
            "LeafList": lambda parent, cfg: None,
            "RootApp": lambda parent, cfg: self.root
        }
        
        self.commands = {
            "goto": GotoCommand(),
            "select": GotoCommand(),
        }
        self.verbosity_command_regex = re.compile(r"^(t[1-3a-z]*|c[1-3a-z]*|default)\b", re.IGNORECASE)

        self._build_ui_recursive(self.root, self.layout_config)

        self.state.on_selection_change(self._handle_node_selection_change)
        self.state.on_verbosity_change(self._handle_verbosity_change)
        self.state.on_status_update(self._update_status_bar)

        self._populate_node_tree()  # Updated to populate tree
        if self.state.get_node_count() > 0:
            self._handle_node_selection_change(self.state.current_node_index)
        else:
            self._render_node_detail()
            self._update_nav_buttons_state()
            self.state.update_status("No nodes loaded.", "info")

    def _on_closing(self):
        self.state.save_persistent_state()
        self.root.destroy()

    def _get_style_props(self, component_type, tkml_props=None):
        style = self.style_config.get('default', {}).get(component_type, {}).copy()
        if tkml_props: style.update(tkml_props)
        return style

    def _build_ui_recursive(self, parent_tk_widget, tkml_config_node):
        component_type = tkml_config_node.get("type")
        tkml_props = tkml_config_node.get("props", {})
        factory_method = self.component_factories.get(component_type)
        current_widget = None
        if factory_method:
            current_widget = factory_method(parent_tk_widget, tkml_config_node)
            if current_widget and component_type not in ["RootApp"]:
                widget_name = tkml_props.get("id", component_type)
                self.ui_elements[widget_name] = current_widget
        else:
            print(f"Warning: No factory for TKML type: {component_type}")
            if tkml_config_node.get("parts"):
                current_widget = tk.Frame(parent_tk_widget)
                current_widget.pack(fill=tk.BOTH, expand=True)
        if current_widget:
            for part_config in tkml_config_node.get("parts", []):
                self._build_ui_recursive(current_widget, part_config)
        return current_widget

    def _create_frame_widget(self, parent_tk, tkml_config):
        props = self._get_style_props(tkml_config.get("type"), tkml_config.get("props"))
        frame = tk.Frame(parent_tk, bd=props.get("bd",1), relief=props.get("relief",tk.SUNKEN))
        frame.pack(side=props.get("side",tk.TOP), fill=props.get("fill",tk.BOTH), expand=props.get("expand",True),
                   padx=props.get("padx",0 if tkml_config.get("type")=="BottomPanel" else 5),
                   pady=props.get("pady",0 if tkml_config.get("type")=="BottomPanel" else 5))
        return frame

    def _create_node_tree_widget(self, parent_tk, tkml_config):
        """Create a Treeview widget to display nodes hierarchically."""
        container_frame = tk.Frame(parent_tk)
        container_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        tk.Label(container_frame, text="Nodes", font=('Arial',10,'bold')).pack(pady=(5,2), anchor=tk.W)
        tree = ttk.Treeview(container_frame, show='tree')  # 'tree' mode hides headers
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.ui_elements['node_tree'] = tree
        tree.bind('<<TreeviewSelect>>', self._on_tree_select)
        return container_frame

    def _on_tree_select(self, event):
        """Handle node selection in the Treeview."""
        tree = event.widget
        selected_items = tree.selection()
        if selected_items:
            selected_id = selected_items[0]  # Single selection assumed
            self.state.select_node_by_id(selected_id)

    def _create_detail_view_widget(self, parent_tk, tkml_config):
        props = self._get_style_props("DetailView", tkml_config.get("props"))
        tk.Label(parent_tk, text="Node Detail", font=('Arial',10,'bold')).pack(pady=(5,2), anchor=tk.W)
        detail_text = scrolledtext.ScrolledText(parent_tk, wrap=tk.WORD, height=props.get("height",10),
                                                relief=props.get("relief",tk.FLAT), font=(props.get("font_family","Courier New"), props.get("font_size",10)))
        detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))
        detail_text.config(state=tk.DISABLED)
        return detail_text

    def _create_button_widget(self, parent_tk, tkml_config):
        component_type = tkml_config.get("type")
        props = self._get_style_props(component_type, tkml_config.get("props"))
        command_action = None
        if component_type == "PrevButton": command_action = self._show_prev_node
        elif component_type == "NextButton": command_action = self._show_next_node
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
        tree = self.ui_elements.get('node_tree')
        if not tree:
            return
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        inserted_set = set()
        # Find root nodes (no 'prev' links)
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

    def _handle_node_selection_change(self, selected_index):
        """Update Treeview selection when the current node changes."""
        tree = self.ui_elements.get('node_tree')
        if tree:
            current_id = self.state.get_current_node_id()
            tree.selection_set(current_id)
            tree.see(current_id)  # Scroll to the selected item
        self._render_node_detail()
        self._update_nav_buttons_state()

    def _handle_verbosity_change(self):
        self._render_node_detail()

    def _update_status_bar(self, message, msg_type):
        status_bar = self.ui_elements.get("StatusBar")
        if status_bar:
            status_bar.config(text=f"{message}")
            colors = {"error": "red", "success": "green", "info": "black"}
            status_bar.config(fg=colors.get(msg_type, "black"))

    def _render_node_detail(self):
        dtw = self.ui_elements.get('DetailView')
        if not dtw:
            return
        dtw.config(state=tk.NORMAL)
        dtw.delete('1.0', tk.END)
        node = self.state.get_current_node()
        if not node:
            dtw.insert(tk.END, "No node selected.")
            dtw.config(state=tk.DISABLED)
            return
        content = []
        for tl in node.get('text_lines',[]):
            if tl.get('level','').upper() in self.state.active_text_levels:
                content.append(f"{tl['level']}> {tl.get('content','')}")
        for cl in node.get('code_lines',[]):
            if cl.get('level','').upper() in self.state.active_code_levels:
                content.append(f"{cl['level']}> {cl.get('content','')}")
        if content:
            dtw.insert(tk.END, "\n".join(content))
        else:
            dtw.insert(tk.END, f"Node '{node.get('id','N/A')}' no content for T=[{','.join(self.state.active_text_levels)}] C=[{','.join(self.state.active_code_levels)}]")
        dtw.config(state=tk.DISABLED)

    def _update_nav_buttons_state(self):
        pb, nb = self.ui_elements.get('PrevButton'), self.ui_elements.get('NextButton')
        count, idx = self.state.get_node_count(), self.state.current_node_index
        if pb: pb.config(state=tk.DISABLED if idx <= 0 or count == 0 else tk.NORMAL)
        if nb: nb.config(state=tk.DISABLED if idx >= count - 1 or count == 0 else tk.NORMAL)

    def _show_prev_node(self):
        if self.state.current_node_index > 0:
            self.state.select_node_by_index(self.state.current_node_index - 1, source="prev_button")
    def _show_next_node(self):
        if self.state.current_node_index < self.state.get_node_count() - 1:
            self.state.select_node_by_index(self.state.current_node_index + 1, source="next_button")

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
        if first_part in self.commands:
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
    parsed_comp_layout = load.tkml_string(comp_tkml_wisp5)
    print("Loading TOML...")
    parsed_style_config = load.toml_string(style_toml_wisp5)
    print("Loading GNML...")
    parsed_nodes_data = load.gnml_string(nodes_gnml_wisp5)

    app_state = AppState(parsed_nodes_data, parsed_style_config)

    root = tk.Tk()
    app_ui = NodeNavigatorApp(root, app_state, parsed_comp_layout, parsed_style_config)
    root.mainloop()
