# app_state.py - Application State (Model)

import json
import os
import re

APP_STATE_FILE = "wisp_app_state.json"

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
