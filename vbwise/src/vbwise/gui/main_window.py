# vbwise/gui/main_window.py

import tkinter as tk
import tkinter.ttk as ttk 
from tkinter import Canvas, Frame, Scrollbar
import sys
import os
import traceback
from typing import Optional, List, Dict # Added Dict

from vbwise.app_state import AppState # Model
from vbwise.controller import CommandProcessor # Controller
from vbwise.source_parser import parse_source_string_to_nodes
from vbwise.gui.leaf_widget import LeafWidget, DARK_BG_DEFAULT

# Attempt to import the initial content
try:
    from vbwise.initial_content import INITIAL_NODES_SOURCE
except ImportError:
    print(
        "ERROR: Could not import INITIAL_NODES_SOURCE from vbwise.data.initial_content.\n"
        "Make sure the file exists and the path is correct.",
        file=sys.stderr
    )
    INITIAL_NODES_SOURCE = """
### NODE
--- id: one.23.four.9-a
--- tags: single_tag
--- meta:
--- next:
--- prev: root
### ENDNODE
"""

class ScrollableLeafFrame(tk.Frame):
    """
    A frame that contains a canvas and a scrollbar, allowing multiple LeafWidgets
    to be displayed in a scrollable list.
    """
    def __init__(self, parent, app_state: AppState, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app_state = app_state # To pass to LeafWidgets if needed for click
        self.configure(bg=DARK_BG_DEFAULT)

        self.canvas = tk.Canvas(self, borderwidth=0, background=DARK_BG_DEFAULT)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # This frame will hold all the LeafWidgets
        self.inner_frame = tk.Frame(self.canvas, bg=DARK_BG_DEFAULT)
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", self._on_inner_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Bind mouse wheel scrolling (platform-dependent)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel) # Windows
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)   # Linux (scroll up)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)   # Linux (scroll down)

        self.leaf_widgets_map: Dict[str, LeafWidget] = {} # To access widgets for scrolling


    def _on_inner_frame_configure(self, event=None):
        """Updates the scrollregion of the canvas when the inner frame's size changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        """Ensures the inner frame width matches the canvas width."""
        self.canvas.itemconfig(self.canvas_frame_id, width=self.canvas.winfo_width())

    def _on_mousewheel(self, event):
        """Handles mouse wheel scrolling."""
        if event.num == 5 or event.delta < 0: # Scroll down
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0: # Scroll up
            self.canvas.yview_scroll(-1, "units")
    
    def add_leaf_widget(self, leaf_widget: LeafWidget, node_id: str):
        """Adds a LeafWidget to the scrollable list."""
        leaf_widget.pack(side=tk.TOP, fill=tk.X, expand=True, pady=5, padx=5)
        self.leaf_widgets_map[node_id] = leaf_widget # Store for scrolling

    def clear_leaves(self):
        """Removes all leaf widgets from the display."""
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.leaf_widgets_map.clear()

    def get_widget_by_id(self, node_id: str) -> Optional[LeafWidget]:
        return self.leaf_widgets_map.get(node_id)

    def scroll_to_widget(self, widget: LeafWidget):
        """Scrolls the canvas to make the specified widget visible."""
        self.canvas.update_idletasks() # Ensure geometry is up-to-date
        
        # Calculate the widget's position relative to the canvas
        # widget_y = widget.winfo_y() # This is relative to inner_frame
        
        # Find the widget's position within the inner_frame
        # Then map that to the canvas scroll position
        # A simpler way for yview_moveto is to get the fraction of the total height
        
        inner_frame_height = self.inner_frame.winfo_height()
        if inner_frame_height == 0: return # Avoid division by zero if frame not yet drawn

        widget_y_in_inner_frame = 0
        for child in self.inner_frame.winfo_children():
            if child == widget:
                break
            widget_y_in_inner_frame += child.winfo_height() + 10 # 5 pady top + 5 pady bottom
        
        scroll_fraction = widget_y_in_inner_frame / inner_frame_height
        self.canvas.yview_moveto(scroll_fraction)


class MainWindow(tk.Tk):
    """The main application window (View component) for Vibewise."""
    def __init__(self, app_state: AppState):
        super().__init__()

        if not isinstance(app_state, AppState):
            raise TypeError("app_state must be an instance of AppState.")
        self.app_state = app_state
        
        self.command_processor = CommandProcessor(self.app_state)

        self.title("Vibewise (MVC)")
        self.geometry("1000x700")

        self.main_content_area = tk.Frame(self, bg=DARK_BG_DEFAULT) # Give it a base color
        self.main_content_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Layout Containers ---
        self.single_leaf_container = tk.Frame(self.main_content_area, bg=DARK_BG_DEFAULT)
        self.h_split_paned_window = ttk.PanedWindow(self.main_content_area, orient=tk.HORIZONTAL)
        self.v_split_paned_window = ttk.PanedWindow(self.main_content_area, orient=tk.VERTICAL)
        self.scrollable_leaf_frame = ScrollableLeafFrame(self.main_content_area, self.app_state)


        self._leaf_widgets: dict[str, LeafWidget] = {} # Stores all instantiated LeafWidgets

        self.command_frame = tk.Frame(self, height=30)
        self.command_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.command_frame.pack_propagate(False)

        self.command_label = tk.Label(self.command_frame, text=">")
        self.command_label.pack(side=tk.LEFT, padx=2)

        self.command_entry = tk.Entry(self.command_frame)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", self.on_command_enter)
        self.command_entry.focus_set()

        self.status_bar_text = tk.StringVar() 
        self.status_bar = tk.Label(
            self, textvariable=self.status_bar_text,
            bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar_text.set("Initializing...")

    def on_command_enter(self, event=None) -> None:
        command_string = self.command_entry.get()
        self.command_entry.delete(0, tk.END)

        if command_string:
            status, message = self.command_processor.execute_command(command_string)
            if status == "quit":
                self.quit_application()
            # Status bar update is now handled by on_state_changed for "command_executed_feedback"

    def on_state_changed(self, app_state: AppState, event_type: Optional[str] = None, **kwargs) -> None:
        status_parts = []
        status_parts.append(f"Layout: {self.app_state.layout}")
        status_parts.append(f"Detail: {self.app_state.global_detail_level}")

        if self.app_state.focused_leaf_id:
            status_parts.append(f"Focused: {self.app_state.focused_leaf_id}")
        if self.app_state.selected_leaf_ids:
            status_parts.append(f"Selected: {len(self.app_state.selected_leaf_ids)}")
        
        if self.app_state.active_pathway_link_type:
            path_info = f"Pathway: {self.app_state.active_pathway_link_type}"
            if self.app_state.active_pathway_current_node_id:
                path_info += f" ({self.app_state.active_pathway_current_node_id})"
            status_parts.append(path_info)

        if event_type == "command_executed_feedback":
            cmd_status = kwargs.get("status", "unknown")
            cmd_message = kwargs.get("message", "")
            command_str = kwargs.get('command', '')
            if len(command_str) > 25: command_str = command_str[:22] + '...'
            
            if cmd_message:
                 status_parts.append(f"Cmd '{command_str}': {cmd_message} ({cmd_status})")
            else:
                 status_parts.append(f"Cmd '{command_str}': {cmd_status}")

        self.status_bar_text.set(" | ".join(status_parts))

        layout_affecting_events = [
            "data_loaded", "displayed_leaves_changed", "layout_changed",
            "pathway_started", "pathway_navigated",
        ]

        if event_type in layout_affecting_events:
            self._update_main_content_display()

        leaf_refresh_events = [
            "focused_leaf_changed", "selection_changed",
            "leaf_detail_override_changed", "leaf_detail_override_cleared",
            "all_leaf_overrides_cleared", "global_detail_level_changed",
            "leaf_detail_override_changed_batch",
        ]
        if event_type in leaf_refresh_events:
            self._refresh_displayed_leaf_widgets(event_type, **kwargs)
            if event_type == "focused_leaf_changed" and self.app_state.layout == 'scrolled_list':
                self.scroll_to_focused_leaf()


    def _update_main_content_display(self) -> None:
        current_displayed_node_ids = self.app_state.displayed_leaf_ids
        current_layout = self.app_state.layout

        # Hide all layout containers first
        self.single_leaf_container.pack_forget()
        self.h_split_paned_window.pack_forget()
        self.v_split_paned_window.pack_forget()
        self.scrollable_leaf_frame.pack_forget()
        
        # Clear PanedWindow panes explicitly if they were used
        for pane_child in self.h_split_paned_window.panes(): self.h_split_paned_window.forget(pane_child)
        for pane_child in self.v_split_paned_window.panes(): self.v_split_paned_window.forget(pane_child)


        # Destroy widgets that are no longer in displayed_leaf_ids OR if layout changes drastically
        # For simplicity, if layout changes, we might recreate.
        # More efficiently: only destroy if not in current_displayed_node_ids.
        ids_to_display_set = set(current_displayed_node_ids)
        existing_widget_ids_in_main_dict = set(self._leaf_widgets.keys())
        
        ids_to_destroy = list(existing_widget_ids_in_main_dict - ids_to_display_set)
        if current_layout != self.app_state.layout: # If layout itself changed, clear all
             ids_to_destroy.extend(list(ids_to_display_set))


        for node_id in ids_to_destroy:
            if node_id in self._leaf_widgets:
                widget_to_destroy = self._leaf_widgets.pop(node_id)
                widget_to_destroy.destroy()
        
        # Clear leaves from scrollable frame if it's not the active one, or if it is but needs full refresh
        if current_layout != 'scrolled_list':
            self.scrollable_leaf_frame.clear_leaves()


        active_container: Optional[tk.Widget] = None
        nodes_to_process: List[str] = []

        if not current_displayed_node_ids:
            self.status_bar_text.set("No nodes to display. Load data or use 'goto'.")
            # Ensure self._leaf_widgets is also cleared if no nodes are displayed
            for widget in self._leaf_widgets.values(): widget.destroy()
            self._leaf_widgets.clear()
            self.scrollable_leaf_frame.clear_leaves()
            return # Nothing more to do

        if current_layout == 'single':
            active_container = self.single_leaf_container
            nodes_to_process = current_displayed_node_ids[:1]
        elif current_layout == 'split_v_2':
            active_container = self.v_split_paned_window
            nodes_to_process = current_displayed_node_ids[:2]
        elif current_layout == 'split_h_2':
            active_container = self.h_split_paned_window
            nodes_to_process = current_displayed_node_ids[:2]
        elif current_layout == 'scrolled_list':
            active_container = self.scrollable_leaf_frame # The ScrollableLeafFrame itself
            nodes_to_process = current_displayed_node_ids # All of them
            self.scrollable_leaf_frame.clear_leaves() # Clear before repopulating
        else: # Fallback or unknown layout
            self.status_bar_text.set(f"Unknown layout: {current_layout}. Displaying first node if available.")
            active_container = self.single_leaf_container
            nodes_to_process = current_displayed_node_ids[:1]


        if active_container:
            active_container.pack(fill=tk.BOTH, expand=True)

            for node_id in nodes_to_process:
                if node_id not in self.app_state.all_nodes:
                    print(f"Warning: Node ID '{node_id}' not found in all_nodes during display update.", file=sys.stderr)
                    continue

                leaf_widget = self._leaf_widgets.get(node_id)
                
                # Determine parent for the LeafWidget
                parent_for_leaf = active_container
                if current_layout == 'scrolled_list':
                    parent_for_leaf = self.scrollable_leaf_frame.inner_frame

                if not leaf_widget or leaf_widget.master != parent_for_leaf :
                    if leaf_widget: # It exists but has wrong parent (e.g., layout change)
                        leaf_widget.destroy() # Destroy and recreate in new parent
                    leaf_widget = LeafWidget(parent_for_leaf, self.app_state, node_id)
                    self._leaf_widgets[node_id] = leaf_widget
                
                # Add to the specific layout container
                if current_layout == 'scrolled_list':
                    self.scrollable_leaf_frame.add_leaf_widget(leaf_widget, node_id)
                elif isinstance(active_container, tk.Frame) and current_layout == 'single': # Single Frame
                    leaf_widget.pack(fill=tk.BOTH, expand=True)
                elif isinstance(active_container, ttk.PanedWindow): # Split Panes
                    # Ensure widget is not already in a pane before adding
                    try:
                        active_container.add(leaf_widget, weight=1)
                    except tk.TclError as e:
                        if "window is already managed by window" not in str(e): # Ignore if already there
                           print(f"Error adding widget to PanedWindow: {e}", file=sys.stderr)


                if leaf_widget.winfo_exists():
                    leaf_widget.update_display() # Ensure content is current
                    self._apply_visual_state_to_widget(leaf_widget, node_id)

        self._refresh_displayed_leaf_widgets("layout_changed_refresh_all") # General refresh for visual states

    def _refresh_displayed_leaf_widgets(self, event_type: Optional[str] = None, **kwargs) -> None:
        node_ids_to_update_content = []
        if event_type in ["global_detail_level_changed", "all_leaf_overrides_cleared", "layout_changed_refresh_all"]:
            node_ids_to_update_content = list(self._leaf_widgets.keys())
        elif event_type in ["leaf_detail_override_changed", "leaf_detail_override_cleared"]:
            if "node_id" in kwargs and kwargs["node_id"] in self._leaf_widgets:
                node_ids_to_update_content = [kwargs["node_id"]]
        elif event_type == "leaf_detail_override_changed_batch":
            if "node_ids" in kwargs:
                node_ids_to_update_content = [
                    nid for nid in kwargs["node_ids"] if nid in self._leaf_widgets
                ]
        
        for node_id in node_ids_to_update_content:
            widget = self._leaf_widgets.get(node_id)
            if widget and widget.winfo_exists():
                 widget.update_display() # This updates content based on detail levels

        # Apply focus/selection visuals to all currently managed widgets
        for node_id, widget in list(self._leaf_widgets.items()): 
            if widget.winfo_exists(): # Check if it's still part of a displayed layout
                 # Check if the widget is actually visible (packed/in pane)
                is_displayed_in_current_layout = False
                if self.app_state.layout == 'scrolled_list':
                    if node_id in self.scrollable_leaf_frame.leaf_widgets_map:
                        is_displayed_in_current_layout = True
                elif self.app_state.layout == 'single':
                    if widget.master == self.single_leaf_container and widget.winfo_ismapped():
                        is_displayed_in_current_layout = True
                elif self.app_state.layout in ['split_h_2', 'split_v_2']:
                    # For paned windows, checking master is more complex due to internal panes
                    # A simpler check: is it one of the first N displayed_leaf_ids for these layouts?
                    limit = 1 if self.app_state.layout == 'single' else 2
                    if node_id in self.app_state.displayed_leaf_ids[:limit]:
                         is_displayed_in_current_layout = True


                if is_displayed_in_current_layout:
                    self._apply_visual_state_to_widget(widget, node_id)
            elif not widget.winfo_exists() and node_id in self._leaf_widgets:
                del self._leaf_widgets[node_id]


    def _apply_visual_state_to_widget(self, widget: LeafWidget, node_id: str) -> None:
        is_focused = (node_id == self.app_state.focused_leaf_id)
        is_selected = (node_id in self.app_state.selected_leaf_ids)
        widget.set_focused(is_focused)
        widget.set_selected(is_selected)

    def scroll_to_focused_leaf(self):
        """If in scrolled_list layout, scrolls to the currently focused leaf."""
        if self.app_state.layout == 'scrolled_list' and self.app_state.focused_leaf_id:
            focused_widget = self.scrollable_leaf_frame.get_widget_by_id(self.app_state.focused_leaf_id)
            if focused_widget:
                self.scrollable_leaf_frame.scroll_to_widget(focused_widget)


    def quit_application(self) -> None:
        self.quit()
        self.destroy()

def run_vibewise():
    main_window_instance = None
    try:
        app_state = AppState()
        main_window_instance = MainWindow(app_state)
        app_state.add_observer(main_window_instance.on_state_changed)

        if INITIAL_NODES_SOURCE:
            nodes_data = parse_source_string_to_nodes(INITIAL_NODES_SOURCE)
            app_state.load_nodes(nodes_data)
        else:
            print("Error: INITIAL_NODES_SOURCE is empty or not loaded.", file=sys.stderr)
            error_node_data = parse_source_string_to_nodes(
                "### NODE: critical_error\n# Critical Error\nTXT> No initial content could be loaded.\n### ENDNODE"
            )
            app_state.load_nodes(error_node_data)

        # --- Set initial display state in Model ---
        if app_state.layout == 'scrolled_list':
            if app_state.all_nodes:
                all_node_ids = list(app_state.all_nodes.keys())
                app_state.update_displayed_leaves(all_node_ids)
                if all_node_ids: # Focus the first one in the list
                    app_state.focused_leaf_id = all_node_ids[0]
            else: # No nodes loaded
                app_state.update_displayed_leaves([])
        else: # For other layouts like 'single'
            initial_node_id = 'help_commands' 
            if initial_node_id in app_state.all_nodes:
                app_state.update_displayed_leaves([initial_node_id])
                app_state.focused_leaf_id = initial_node_id
            elif app_state.all_nodes: 
                first_node_id = next(iter(app_state.all_nodes))
                app_state.update_displayed_leaves([first_node_id])
                app_state.focused_leaf_id = first_node_id
            else:
                app_state.update_displayed_leaves([])
        
        if not app_state.all_nodes:
             print("CRITICAL: No nodes available after attempting to load initial content.", file=sys.stderr)


    except Exception as e:
        print(f"Fatal error during application setup: {e}", file=sys.stderr)
        traceback.print_exc()
        if main_window_instance is None: 
            error_root = tk.Tk()
            error_root.title("Vibewise - Fatal Error")
            tk.Label(error_root, text=f"Application failed to start:\n{e}\n\nSee console for details.",
                     fg="red", padx=20, pady=20).pack()
            error_root.mainloop()
        sys.exit(1)

    if main_window_instance:
        main_window_instance.mainloop()
    else:
        print("Error: MainWindow instance not created. Cannot start application.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    vbwise_package_root = os.path.abspath(os.path.join(current_file_dir, '..', '..'))
    if vbwise_package_root not in sys.path:
        sys.path.insert(0, vbwise_package_root)

    # --- Ensure necessary dummy files exist for the imports to work if run directly ---
    # This is for standalone execution of main_window.py for testing.
    # In a packaged app, these would exist.
    vbwise_dir = os.path.join(vbwise_package_root, "vbwise")
    if not os.path.exists(vbwise_dir): os.makedirs(vbwise_dir)
    
    # Dummy node.py if not present
    node_py_path = os.path.join(vbwise_dir, "node.py")
    if not os.path.exists(node_py_path):
        with open(node_py_path, "w") as f:
            f.write("# Dummy vbwise/node.py for standalone main_window.py execution\n")
            f.write("from typing import Dict, List, Tuple\n")
            f.write("class Node:\n")
            f.write("    def __init__(self, id: str, title: str = '', content_lines: List[Tuple[str, str]] = None, links: Dict[str, str] = None, tags: List[str] = None, meta: Dict[str, str] = None):\n")
            f.write("        self.id = id\n")
            f.write("        self.title = title\n")
            f.write("        self.content_lines = content_lines if content_lines is not None else []\n")
            f.write("        self.links = links if links is not None else {}\n")
            f.write("        self.tags = tags if tags is not None else []\n")
            f.write("        self.meta = meta if meta is not None else {}\n")

    # Dummy source_parser.py if not present
    source_parser_py_path = os.path.join(vbwise_dir, "source_parser.py")
    if not os.path.exists(source_parser_py_path):
        with open(source_parser_py_path, "w") as f:
            f.write("# Dummy vbwise/source_parser.py\n")
            f.write("from typing import Dict\n")
            f.write("from vbwise.node import Node\n") # Requires node.py
            f.write("def parse_source_string_to_nodes(source_string: str) -> Dict[str, Node]:\n")
            f.write("    # This is a simplified parser for the dummy initial content.\n")
            f.write("    # Replace with your actual gramjam or other parsing logic.\n")
            f.write("    nodes = {}\n")
            f.write("    if '### NODE: help_commands' in source_string:\n")
            f.write("        nodes['help_commands'] = Node(\n")
            f.write("            id='help_commands',\n")
            f.write("            title='Available Commands',\n")
            f.write("            content_lines=[\n")
            f.write("                ('TXT', 'goto <node_id>         - Display a specific node.'),\n")
            f.write("                ('TXT', 'layout <type>          - Change view (single, split_v_2, split_h_2, scrolled_list).'),\n")
            f.write("                ('TXT', 'verbosity <level>      - Set global detail level (0-3).'),\n")
            f.write("                ('TXT', 'select <id|all|none>   - Select node(s). Use --add to append.'),\n")
            f.write("                ('TXT', 'set_selected_verbosity <level> - Set detail for selected nodes.'),\n")
            f.write("                ('TXT', 'follow <link_type> [id] - Start pathway navigation.'),\n")
            f.write("                ('TXT', 'next                   - Go to next node in pathway.'),\n")
            f.write("                ('TXT', 'stop                   - Stop pathway navigation.'),\n")
            f.write("                ('TXT', 'quit                   - Exit the application.'),\n")
            f.write("            ]\n")
            f.write("        )\n")
            f.write("    if '### NODE: error_loading' in source_string:\n")
            f.write("        nodes['error_loading'] = Node(id='error_loading', title='Error', content_lines=[('TXT', 'Error loading content.')])\n")
            f.write("    if '### NODE: critical_error' in source_string:\n")
            f.write("        nodes['critical_error'] = Node(id='critical_error', title='Critical Error', content_lines=[('TXT', 'No initial content.')])\n")
            f.write("    return nodes\n")

    # Dummy initial_content.py if not present
    initial_content_dir = os.path.join(vbwise_dir, "data")
    if not os.path.exists(initial_content_dir): os.makedirs(initial_content_dir)
    initial_content_py_path = os.path.join(initial_content_dir, "initial_content.py")
    if not os.path.exists(initial_content_py_path):
         with open(initial_content_py_path, "w") as f:
            f.write("# Dummy vbwise/data/initial_content.py\n")
            f.write("INITIAL_NODES_SOURCE = \"\"\"\n")
            f.write("### NODE: help_commands\n")
            f.write("# Available Commands\n")
            f.write("TXT> goto <node_id>         - Display a specific node.\n")
            f.write("TXT> layout <type>          - Change view (single, split_v_2, split_h_2, scrolled_list).\n")
            f.write("TXT> verbosity <level>      - Set global detail level (0-3).\n")
            f.write("TXT> select <id|all|none>   - Select node(s). Use --add to append.\n")
            f.write("TXT> set_selected_verbosity <level> - Set detail for selected nodes.\n")
            f.write("TXT> follow <link_type> [id] - Start pathway navigation.\n")
            f.write("TXT> next                   - Go to next node in pathway.\n")
            f.write("TXT> stop                   - Stop pathway navigation.\n")
            f.write("TXT> quit                   - Exit the application.\n")
            f.write("### ENDNODE\n\n")
            f.write("\"\"\"\n")


    run_vibewise()

