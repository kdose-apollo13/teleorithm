import tkinter as tk
import json

from vbwise import load


toml_source = '''
[styles.list_item_label_style]
font = "Helvetica 12"
foreground = "black"
background = "#f0f0f0"
anchor = "w" 
relief = "solid" 
borderwidth = 1

[styles.content_frame_style] 
background = "white" # Canvas content frame background

[layouts.fill_frame_layout] # For scrollHostFrame in root
grid = { row = 0, column = 0, sticky = "nsew" }
weight = { row = 0, column = 0 } # Makes cell (0,0) of root expand

[layouts.canvas_layout_in_host] # For myCanvas in scrollHostFrame
grid = { row = 0, column = 0, sticky = "nsew" }
weight = { row = 0, column = 0 } # Makes cell (0,0) of scrollHostFrame expand

[layouts.scrollbar_layout_in_host] # For myScrollbar in scrollHostFrame
grid = { row = 0, column = 1, sticky = "ns" }

[layouts.list_item_layout] # For dynamic labels inside canvasContentFrame
pack = { side = "top", fill = "x", pady = 2, padx = 5 }
'''

json_state = '''
{
    "list_title": "My Items",
    "items": [
        { "id": "item1", "text": "First item" },
        { "id": "item2", "text": "Second item, a bit longer" },
        { "id": "item3", "text": "Third item" },
        { "id": "item4", "text": "Fourth item" },
        { "id": "item5", "text": "Fifth item" },
        { "id": "item6", "text": "Sixth item" },
        { "id": "item7", "text": "Seventh item" },
        { "id": "item8", "text": "Eighth item" },
        { "id": "item9", "text": "Ninth item" },
        { "id": "item10", "text": "Tenth item" },
        { "id": "item11", "text": "Eleventh item" },
        { "id": "item12", "text": "Twelfth item" },
        { "id": "item13", "text": "Thirteenth item" },
        { "id": "item14", "text": "Fourteenth item" },
        { "id": "item15", "text": "Fifteenth item - scroll!" }
    ]
}
'''

# tkml_source is implicitly used by the MockLoad, but kept here for reference
tkml_source_for_reference = '''
Tk {
    id: root
    title: "Wisp22: Scrollable List" 
    geometry: "350x450"
    Frame { 
        id: scrollHostFrame
        layout_style: "fill_frame_layout" 
        Canvas {
            id: myCanvas
            layout_style: "canvas_layout_in_host"
            
            scrollable: { content_frame: "canvasContentFrame", scrollbar: "myScrollbar" }
            Frame { 
                id: canvasContentFrame 
                style: "content_frame_style"
                
                dynamic_parts: {
                    type: "Label" 
                    style: "list_item_label_style" 
                    layout_style: "list_item_layout" 
                    data_bind: { text: "text" } 
                    repeat: "items" 
                }
            }
        }
        Scrollbar { 
            id: myScrollbar
            orient: "vertical"
            layout_style: "scrollbar_layout_in_host" 
        }
    }
}
'''


def process_widget(spec, toml_data, is_root=False):
    """ Transforms a single widget spec, merging TOML data. """
    widget_data = {
        "type": spec.get("type"),
        "props": {"config": {}, "grid": {}, "pack": {}}, # Initialize all layout types
        "parts": {}
    }
    
    props = spec.get("props", {})
    for key, value in props.items():
        if key == "id": # ID is used for widget lookup, not a Tk prop itself
            continue
        elif is_root and key in ["title", "geometry"]: # Root Tk properties
            widget_data["props"][key] = value
        elif key == "scrollable": # New: special property for scrollable setup
            widget_data["props"]["scrollable"] = value
        elif key == "dynamic_parts": # New: special property for dynamic content
            widget_data["props"]["dynamic_parts"] = value
        elif key == "data_bind": # For data binding
            widget_data["props"]["data_bindings"] = value
        elif key == "bind": # For event bindings
            widget_data["props"]["bind"] = value
        elif key == "style" and value in toml_data.get("styles", {}):
            style_config = toml_data["styles"][value]
            widget_data["props"]["config"].update(style_config)
        elif key == "layout_style" and value in toml_data.get("layouts", {}):
            layout_info = toml_data["layouts"][value]
            if "grid" in layout_info:
                widget_data["props"]["grid"].update(layout_info["grid"])
            if "pack" in layout_info:
                widget_data["props"]["pack"].update(layout_info["pack"])
            if "weight" in layout_info: # Pass weight config for grid
                # Ensure 'grid' exists in props to attach weight to
                if "grid" not in widget_data["props"]: widget_data["props"]["grid"] = {}
                widget_data["props"]["grid"]["weight"] = layout_info["weight"]
        else:
            # Assume other properties are valid Tk config options (e.g., orient for Scrollbar)
            widget_data["props"]["config"][key] = value

    # Process child widgets (parts)
    parts_list = spec.get('parts', [])
    for part_spec in parts_list:
        part_id = part_spec.get('props', {}).get('id') # Assumes ID is in props
        if part_id is None and "id" in part_spec: # Fallback for simpler mock structure
             part_id = part_spec["id"]

        if part_id:
            widget_data['parts'][part_id] = process_widget(part_spec, toml_data)
        else:
            # This case should ideally not happen if TKML is well-formed and parser is correct
            print(f"Warning: Child widget spec is missing an 'id'. Type: {part_spec.get('type')}")
            # Potentially create a default ID or skip
    
    return widget_data

def transform_ui_spec(tkml_data, toml_data):
    """ Transforms the entire UI specification from parsed TKML and TOML. """
    # tkml_data is the root dictionary from the (mock) parser
    root_id = tkml_data.get('props', {}).get('id', 'root') # Get root ID or default
    return {root_id: process_widget(tkml_data, toml_data, is_root=True)}

class App:
    def __init__(self, state, layout_spec, toml_data):
        self.state = state
        self.layout_spec = layout_spec # Transformed spec
        self.toml_data = toml_data
        self.widgets = {} # Stores actual Tkinter widget instances
        self.handlers = {} # For event bindings
        self.bindings_map = {} # For data bindings
        self.root_id = None # Will be set in build()

    def _apply_layout(self, widget, props):
        """Applies grid or pack layout to a widget."""
        grid_options = props.get("grid", {}).copy() 
        pack_options = props.get("pack", {}).copy()

        if grid_options: 
            weight_config = grid_options.pop("weight", {}) 
            
            if weight_config and hasattr(widget.master, "rowconfigure") and hasattr(widget.master, "columnconfigure"):
                master_row = weight_config.get("row")
                master_col = weight_config.get("column")
                weight_val = int(weight_config.get("weight_val", 1)) 

                if master_row is not None:
                    try:
                        widget.master.rowconfigure(int(master_row), weight=weight_val)
                    except (ValueError, tk.TclError) as e:
                        print(f"Layout Warning (rowconfigure): {e} for master of {widget} on row {master_row}")
                if master_col is not None:
                    try:
                        widget.master.columnconfigure(int(master_col), weight=weight_val)
                    except (ValueError, tk.TclError) as e:
                        print(f"Layout Warning (columnconfigure): {e} for master of {widget} on col {master_col}")
            
            if grid_options: # If there are other grid options besides weight
                widget.grid(**grid_options)

        elif pack_options: 
            if pack_options: # Ensure not empty
                 widget.pack(**pack_options)

    def _config(self, widget, props):
        """Applies configuration options from 'config' sub-dictionary."""
        config_options = props.get("config", {})
        if config_options:
            try:
                widget.config(**config_options)
            except Exception as e:
                print(f"Config error for widget {widget} (ID: {self.get_widget_id(widget)}): {e}")
                print(f"Config options: {config_options}")

    def get_widget_id(self, widget_instance):
        """Helper to find the ID of a widget instance."""
        for id_val, w_instance in self.widgets.items():
            if w_instance == widget_instance:
                return id_val
        return "UnknownWidget"

    def _bind_events(self, widget, props):
        """Binds event handlers."""
        for event, handler_name in props.get("bind", {}).items():
            if handler_name in self.handlers:
                widget.bind(event, self.handlers[handler_name])
            else:
                print(f"Warning: Handler '{handler_name}' not found for event '{event}'")

    def _setup_data_bindings(self, widget, props):
        """Sets up data bindings (for static parts, dynamic parts handle their own)."""
        data_bindings = props.get('data_bindings', {})
        for attr, state_key in data_bindings.items():
            if state_key in self.state:
                try:
                    widget.config(**{attr: self.state[state_key]})
                except Exception as e:
                    print(f"Data binding error for widget {widget} (ID: {self.get_widget_id(widget)}), attr {attr}: {e}")
            # Add to bindings_map for future updates by self.update_state_and_refresh
            self.bindings_map.setdefault(state_key, []).append((widget, attr))


    def _create_widget_recursive(self, parent_tk_widget, widget_id, spec_node):
        """Recursively creates a widget and its children."""
        widget_type_name = spec_node["type"]
        widget_class = getattr(tk, widget_type_name, None) # Basic Tk widgets
        if widget_class is None: # Fallback for ttk, though not used heavily in this wisp
            widget_class = getattr(tk.ttk, widget_type_name, None)
        
        if widget_class is None:
            print(f"Error: Widget type '{widget_type_name}' (ID: {widget_id}) not found.")
            return None

        # Create widget instance
        # Note: canvasContentFrame's parent is the Canvas widget itself.
        # This is handled because _create_widget_recursive passes the created parent widget.
        tk_widget = widget_class(parent_tk_widget)
        self.widgets[widget_id] = tk_widget
        
        # Recursively create children
        for part_id, part_node in spec_node.get("parts", {}).items():
            self._create_widget_recursive(tk_widget, part_id, part_node)
        
        return tk_widget

    def _configure_widget_recursive(self, widget_id, spec_node):
        """Recursively configures a widget and its children after creation."""
        if widget_id not in self.widgets:
            print(f"Warning: Widget ID '{widget_id}' not found during configuration phase.")
            return
            
        tk_widget = self.widgets[widget_id]
        props = spec_node["props"] # Transformed props including config, layout

        # Handle root-specific properties (title, geometry)
        if widget_id == self.root_id and spec_node["type"] == "Tk":
            if "title" in props: tk_widget.title(props["title"])
            if "geometry" in props: tk_widget.geometry(props["geometry"])
        
        self._config(tk_widget, props) # Apply styles and direct configs
        
        # canvasContentFrame is special: its layout is via canvas.create_window,
        # not grid/pack directly on itself relative to its parent (the Canvas).
        # Its children (the labels) will be packed or gridded *inside* it.
        if widget_id != "canvasContentFrame":
            self._apply_layout(tk_widget, props) # Apply grid/pack to place it in its parent
        
        self._bind_events(tk_widget, props)
        self._setup_data_bindings(tk_widget, props) # For non-dynamic bindings

        # Recursively configure children
        for part_id, part_node in spec_node.get("parts", {}).items():
            self._configure_widget_recursive(part_id, part_node)

    def _generate_dynamic_parts_recursive(self, current_widget_id, spec_node):
        """ Recursively finds 'dynamic_parts' specs and generates content. """
        if "dynamic_parts" in spec_node["props"]:
            parent_widget = self.widgets[current_widget_id] # The frame that will contain dynamic items
            dynamic_spec = spec_node["props"]["dynamic_parts"]
            
            repeat_key = dynamic_spec.get("repeat") # e.g., "items"
            if repeat_key and repeat_key in self.state:
                # Clear previous dynamic children if any (for refresh scenarios)
                for child in parent_widget.winfo_children():
                    child.destroy() # TODO: More selective destruction if static children exist

                items_data_list = self.state[repeat_key] # List of dicts
                
                # Get style and layout configs from TOML data (already processed into props by process_widget for static)
                # For dynamic parts, we look them up again or ensure they are passed correctly.
                item_style_name = dynamic_spec.get("style")
                item_style_config = self.toml_data.get("styles", {}).get(item_style_name, {})
                
                item_layout_name = dynamic_spec.get("layout_style")
                item_layout_info = self.toml_data.get("layouts", {}).get(item_layout_name, {})
                item_layout_props = {} # To pass to _apply_layout
                if "pack" in item_layout_info: item_layout_props["pack"] = item_layout_info["pack"]
                if "grid" in item_layout_info: item_layout_props["grid"] = item_layout_info["grid"]


                for idx, item_data_dict in enumerate(items_data_list):
                    # Create a unique ID for the dynamic widget (optional, but good for debugging)
                    # dynamic_widget_id = f"{current_widget_id}_dyn_{idx}"
                    
                    widget_class = getattr(tk, dynamic_spec["type"]) # e.g., tk.Label
                    dyn_widget = widget_class(parent_widget)
                    # self.widgets[dynamic_widget_id] = dyn_widget # Optionally store dynamic widgets

                    # 1. Configure (style) the dynamic widget
                    if item_style_config:
                        dyn_widget.config(**item_style_config)
                    
                    # 2. Apply data binding from item_data_dict
                    bindings = dynamic_spec.get("data_bind", {}) # e.g., {"text": "text"}
                    for widget_attr, data_key in bindings.items():
                        if data_key in item_data_dict:
                            dyn_widget.config(**{widget_attr: item_data_dict[data_key]})
                        else:
                            print(f"Warning: Data key '{data_key}' not found in item for dynamic widget.")
                    
                    # 3. Layout the dynamic widget within its parent_widget
                    if item_layout_props:
                        self._apply_layout(dyn_widget, item_layout_props) # Use the prepared layout props

        # Recurse for children
        for part_id, part_node in spec_node.get("parts", {}).items():
            self._generate_dynamic_parts_recursive(part_id, part_node)


    def _setup_scrollable_areas_recursive(self, widget_id, spec_node):
        """ Recursively finds 'Canvas' specs with 'scrollable' info and sets them up. """
        if spec_node["type"] == "Canvas" and "scrollable" in spec_node["props"]:
            canvas = self.widgets.get(widget_id)
            if not canvas: 
                print(f"Error: Canvas widget '{widget_id}' not found for scrollable setup.")
                return

            scrollable_config = spec_node["props"]["scrollable"]
            content_frame_id = scrollable_config.get("content_frame")
            scrollbar_id = scrollable_config.get("scrollbar")

            content_frame = self.widgets.get(content_frame_id)
            scrollbar = self.widgets.get(scrollbar_id)

            if canvas and content_frame and scrollbar:
                # Link scrollbar to canvas
                scrollbar.config(command=canvas.yview)
                canvas.config(yscrollcommand=scrollbar.set)
                
                # Place the content_frame (already a child of canvas) into the canvas's scrollable window
                # Store the window ID on the canvas instance for later use by _on_canvas_configure
                canvas.canvas_window_id = canvas.create_window(
                    (0, 0), window=content_frame, anchor="nw" 
                )
                # print(f"Canvas window created for {content_frame_id} on {widget_id}, ID: {canvas.canvas_window_id}")


                # Bind configure events to update scrollregion and content frame width
                # Pass canvas and content_frame specifically to avoid lambda scope issues with loop variables
                content_frame.bind("<Configure>", 
                                   lambda event, c=canvas: self._update_scroll_region(c))
                canvas.bind("<Configure>", 
                            lambda event, c=canvas, cf=content_frame: self._on_canvas_configure(c, cf))
            else:
                missing = []
                if not content_frame: missing.append(f"content_frame '{content_frame_id}'")
                if not scrollbar: missing.append(f"scrollbar '{scrollbar_id}'")
                print(f"Warning: Scrollable setup for Canvas '{widget_id}' is incomplete. Missing: {', '.join(missing)}.")
        
        # Recurse for children
        for part_id, part_node in spec_node.get("parts", {}).items():
            self._setup_scrollable_areas_recursive(part_id, part_node)

    def build(self):
        """Builds the entire UI."""
        if not self.layout_spec:
            print("Error: Layout specification is empty. Cannot build UI.")
            return

        self.root_id = list(self.layout_spec.keys())[0]
        root_spec = self.layout_spec[self.root_id]

        # Phase 1: Create all widget instances recursively
        self._create_widget_recursive(None, self.root_id, root_spec)
        
        # Phase 2: Configure widgets (styles, basic layout, non-dynamic bindings)
        self._configure_widget_recursive(self.root_id, root_spec)
        
        # Phase 3: Setup scrollable areas (linking canvas, scrollbar, content_frame)
        # This must happen *before* dynamic content is populated into the content_frame
        self._setup_scrollable_areas_recursive(self.root_id, root_spec)
        
        # Phase 4: Generate dynamic content (e.g., list items)
        # This populates the content_frame which is now part of the canvas window
        self._generate_dynamic_parts_recursive(self.root_id, root_spec)
        
        # Phase 5: Update Tkinter's internal geometry calculations
        self.widgets[self.root_id].update_idletasks() 
        
        # Phase 6: Update scroll regions for all canvases now that content is present and sized
        self._update_all_canvas_scroll_regions_recursive(self.root_id, root_spec)
        
        # Phase 7: Perform initial canvas configuration (e.g. content frame width sync)
        # This helps ensure the content frame width is correct from the start.
        # The <Configure> event on the canvas should also handle this, but an initial call is good.
        self._initial_canvas_configure_recursive(self.root_id, root_spec)
        
        # print("Build process completed.")
        # for id_w, w_instance in self.widgets.items():
        #     print(f"Widget: {id_w}, Type: {w_instance.winfo_class()}, Parent: {w_instance.master}")


    def _update_all_canvas_scroll_regions_recursive(self, widget_id, spec_node):
        """Helper to recursively find all Canvases and update their scroll regions."""
        if spec_node["type"] == "Canvas":
            canvas = self.widgets.get(widget_id)
            if canvas:
                self._update_scroll_region(canvas)
        
        for part_id, part_node in spec_node.get("parts", {}).items():
            self._update_all_canvas_scroll_regions_recursive(part_id, part_node)

    def _initial_canvas_configure_recursive(self, widget_id, spec_node):
        """Helper to call _on_canvas_configure for all relevant canvases initially."""
        if spec_node["type"] == "Canvas" and "scrollable" in spec_node["props"]:
            canvas = self.widgets.get(widget_id)
            content_frame_id = spec_node["props"]["scrollable"].get("content_frame")
            content_frame = self.widgets.get(content_frame_id)
            
            # Ensure canvas_window_id was set during _setup_scrollable_areas_recursive
            if canvas and content_frame and hasattr(canvas, 'canvas_window_id'):
                 self._on_canvas_configure(canvas, content_frame)
            # else:
            #     print(f"Skipping initial configure for canvas {widget_id}, missing info.")

        for part_id, part_node in spec_node.get("parts", {}).items():
            self._initial_canvas_configure_recursive(part_id, part_node)


    def _update_scroll_region(self, canvas):
        """Updates the scrollregion of a given canvas."""
        canvas.update_idletasks() # Ensure content within canvas is sized
        bbox = canvas.bbox("all") # Get bounding box of all items *on the canvas*
        # print(f"Updating scrollregion for {self.get_widget_id(canvas)} to: {bbox}")
        if bbox: # bbox can be None if canvas is empty or not yet drawn
            canvas.config(scrollregion=bbox)
        else:
            # If no content, set a minimal scrollregion to avoid issues
            canvas.config(scrollregion=(0,0,0,0))


    def _on_canvas_configure(self, canvas, content_frame_widget):
        """Handles canvas resize: adjusts width of the content_frame inside it."""
        canvas_width = canvas.winfo_width()
        # Ensure canvas_window_id attribute exists (set during _setup_scrollable_areas_recursive)
        if canvas_width > 0 and hasattr(canvas, 'canvas_window_id') and canvas.canvas_window_id:
            # Only set width of the frame on canvas; height is determined by its own content.
            canvas.itemconfigure(canvas.canvas_window_id, width=canvas_width)
            # print(f"Canvas {self.get_widget_id(canvas)} configured. Content frame width set to {canvas_width}")
        # After adjusting content frame width (which might cause reflow), update scroll region.
        self._update_scroll_region(canvas)


    def update_state_and_refresh(self, new_state_data=None, changed_keys=None):
        """Updates application state and refreshes affected UI parts."""
        if new_state_data:
            self.state.update(new_state_data) # Simple dict update
        
        keys_to_update = changed_keys or self.state.keys()

        # Handle static data bindings
        for key in keys_to_update:
            if key in self.bindings_map:
                for widget, attr in self.bindings_map[key]:
                    if widget.winfo_exists(): # Check if widget still exists
                        try:
                            widget.config(**{attr: self.state[key]})
                        except Exception as e:
                            print(f"Error refreshing widget {widget} for state key '{key}': {e}")
        
        # Check if any dynamic parts need regeneration
        # This needs to find the root of the spec again to start recursion
        root_spec_node = self.layout_spec[self.root_id]
        self._refresh_dynamic_parts_recursive(self.root_id, root_spec_node, keys_to_update)
        
        # After potential regeneration, update scroll regions
        self.widgets[self.root_id].update_idletasks()
        self._update_all_canvas_scroll_regions_recursive(self.root_id, root_spec_node)

    def _refresh_dynamic_parts_recursive(self, widget_id, spec_node, changed_keys):
        """ Helper to check if dynamic parts tied to changed_keys need refresh. """
        if "dynamic_parts" in spec_node["props"]:
            dynamic_spec = spec_node["props"]["dynamic_parts"]
            repeat_key = dynamic_spec.get("repeat")
            if repeat_key in changed_keys:
                # This part needs to re-trigger generation for this specific widget_id
                # The current _generate_dynamic_parts_recursive starts from root.
                # We need to be more targeted or just re-run the full dynamic generation.
                # For simplicity now, let's re-run full dynamic generation if 'items' changed.
                # This is okay if only one dynamic list is tied to 'items'.
                # A more robust solution would map repeat_key to the widget_id that uses it.
                
                # Re-generate dynamic parts for this specific node.
                # This requires _generate_dynamic_parts_recursive to be callable for a sub-tree.
                # Let's adapt it slightly or call the main one.
                # For now, the main _generate_dynamic_parts_recursive will clear and repopulate.
                # So, we just need to ensure it's called.
                
                # This logic is simplified: if any dynamic part's repeat key is in changed_keys,
                # we call the main generator which traverses from root.
                # This is inefficient if there are many dynamic parts.
                
                # Re-calling the main generator for dynamic parts:
                self._generate_dynamic_parts_recursive(self.root_id, self.layout_spec[self.root_id])
                return # Stop further recursion for this branch if dynamic content was regenerated from root

        for part_id, part_node in spec_node.get("parts", {}).items():
            self._refresh_dynamic_parts_recursive(part_id, part_node, changed_keys)


    def run(self):
        """Starts the Tkinter main event loop."""
        if self.root_id and self.root_id in self.widgets:
            # One final update_idletasks and scroll region update can sometimes catch
            # any remaining layout quirks before display.
            self.widgets[self.root_id].update_idletasks()
            self._update_all_canvas_scroll_regions_recursive(self.root_id, self.layout_spec[self.root_id])
            self.widgets[self.root_id].mainloop()
        else:
            print("Error: Root widget not built or not found. Cannot run application.")


if __name__ == "__main__":
    # 1. Load specifications
    # The tkml_source string is used by the mock loader.
    # In a real scenario, you'd load from a file or other source.
    parsed_tkml = load.tkml_string(tkml_source_for_reference) 
    parsed_toml = load.toml_string(toml_source)
    initial_json_state = load.json_string(json_state)

    # 2. Transform TKML into a structured layout specification, merging TOML data
    ui_layout_spec = transform_ui_spec(parsed_tkml, parsed_toml)
    
    # Optional: Print the transformed spec for debugging
    # import json as py_json # Alias if json module name conflicts
    # print("Transformed UI Layout Specification:")
    # print(py_json.dumps(ui_layout_spec, indent=2))

    # 3. Create and build the application
    app = App(state=initial_json_state, layout_spec=ui_layout_spec, toml_data=parsed_toml)
    app.build()
    
    # Example: Test state update after build (optional)
    # def update_later():
    #     print("Updating state...")
    #     new_data = {
    #         "items": [
    #             {"id": "new_item1", "text": "This is a NEW item!"},
    #             {"id": "new_item2", "text": "Another NEW one."},
    #         ] + initial_json_state["items"][:2] # Mix new and old
    #     }
    #     app.update_state_and_refresh(new_state_data=new_data, changed_keys=["items"])
    #
    # app.widgets[app.root_id].after(2000, update_later) # Update after 3 seconds

    # 4. Run the application
    app.run()

