import tkinter as tk

from vbwise import load
from vbwise.utils import merge_dicts
# Assuming load.py is available and works as intended
# from vbwise import load

# app.toml - Defines reusable styles and layouts
toml_source = '''
[styles.label_style]
font = "Helvetica 14"
foreground = "blue"

[styles.button_style]
font = "Helvetica 19 bold"
background = "lightgray"

[layouts.main_frame_layout]
grid = { row = 0, column = 0, sticky = "nsew", weight = { row = 1, column = 1 } }

[layouts.label_layout]
grid = { row = 0, column = 0, sticky = "w" }

[layouts.button_layout]
grid = { row = 1, column = 0, sticky = "w", pady = 5 }

# You could also define default config options here
[config.default_label]
text = "Default Label Text"
'''

# app.tkml - Defines the UI structure and references styles/layouts
tkml_source = '''
Tk {
    id: root
    title: "Elegant Data-Driven Demo"
    geometry: "300x180"

    Frame {
        id: mainFrame
        layout_style: "main_frame_layout"

        Label {
            id: myLabel
            state_text: "text"
            style: "label_style"
            layout_style: "label_layout"
        }

        Button {
            id: myButton
            text: "Change Text"
            style: "button_style"
            layout_style: "button_layout"
            bind: { <Button-1>: toggle_label_state }
        }
    }
}
'''


def transform_ui_spec(tkml_data, toml_data):
    transformed_data = {}
    # Keep a reference to the absolute root spec for easy identification
    root_spec_from_tkml = tkml_data

    def process_widget(ui_spec):
        widget_type = ui_spec['type']
        # Determine if this ui_spec is the root Tk node
        is_root_tk_node = (ui_spec is root_spec_from_tkml and widget_type == 'Tk')

        widget_data = {
            'type': widget_type,
            'props': {},
            'parts': {}
        }
        # Use provided id or generate one. For root, it will be 'root' later.
        widget_id_from_tkml = ui_spec.get('props', {}).get('id')

        direct_props_for_widget = {} # For root title/geometry, or layout grid items
        config_from_tkml_attrs = {}  # For general attributes to go into widget.config()
        data_bindings = {}           # For state_ prefixed attributes

        tkml_props = ui_spec.get('props', {})
        for prop, value in tkml_props.items():
            if prop in ['id', 'style', 'layout_style', 'parts']: # 'bind' handled separately later
                continue

            if is_root_tk_node and prop in ['title', 'geometry']:
                direct_props_for_widget[prop] = value
            elif prop.startswith("state_"):
                actual_prop_name = prop.split("state_", 1)[1]
                state_key_name = value  # The value of state_text is the key in self.state
                data_bindings[actual_prop_name] = state_key_name
            elif prop == 'bind': # Defer bind processing
                pass
            else: # Regular TKML attributes go into config_from_tkml_attrs
                config_from_tkml_attrs[prop] = value
        
        # Start building widget_data['props']
        if direct_props_for_widget:
            widget_data['props'].update(direct_props_for_widget)
        
        current_config = {} # This will become props['config']
        if config_from_tkml_attrs:
            current_config = merge_dicts(current_config, config_from_tkml_attrs)

        # Apply style from TOML if referenced (styles contribute to 'config')
        style_name = tkml_props.get('style')
        if style_name and 'styles' in toml_data and style_name in toml_data['styles']:
            style_props = toml_data['styles'][style_name]
            # Assuming style_props are config options, merge them.
            # merge_dicts(base, updates) -> updates override base for common keys
            current_config = merge_dicts(current_config, style_props) 
        
        if current_config:
            widget_data['props']['config'] = current_config
            
        if data_bindings:
            widget_data['props']['data_bindings'] = data_bindings
        
        # Apply layout from TOML if referenced (layout props merge directly into 'props')
        layout_name = tkml_props.get('layout_style')
        if layout_name and 'layouts' in toml_data and layout_name in toml_data['layouts']:
            layout_props = toml_data['layouts'][layout_name]
            # Layout properties (like 'grid') are merged into the main 'props'
            widget_data['props'] = merge_dicts(widget_data['props'], layout_props)

        # Handle 'bind' from TKML, ensuring it's in 'props'
        if 'bind' in tkml_props:
            widget_data['props']['bind'] = tkml_props['bind']

        # Process nested parts
        if 'parts' in ui_spec:
            for part_spec in ui_spec['parts']:
                # Determine the part's name/id for the 'parts' dictionary
                part_id = part_spec.get('props', {}).get('id', f"anon_{part_spec['type'].lower()}_{len(widget_data['parts'])}")
                widget_data['parts'][part_id] = process_widget(part_spec)
        
        return widget_data
    
    # Process the root element from TKML. The key in transformed_data must be 'root'.
    transformed_data['root'] = process_widget(root_spec_from_tkml)
    # Ensure the root widget in the transformed spec explicitly carries 'root' as its original ID if needed,
    # or rely on the App class knowing that transformed_data['root'] is the root.
    # The App class's build method already expects self.layout.get("root").

    print("--- Transformation complete ---")
    return transformed_data

# --- App Class (from wisp16.py with added prints) ---

class App:
    def __init__(self, state, layout):
        print("--- Initializing App ---")
        self.state = state
        self.layout = layout
        self.widgets = {}
        self.handlers = {
            "toggle_label_state": self.toggle_label_state
        }
        print(f"Initial state: {self.state}")
        # print(f"Layout data: {json.dumps(self.layout, indent=2)}") # Pretty print layout

    # _title, _geometry, _grid, _config, _bind, _create_window methods remain largely the same,
    # but _config will no longer receive title/geometry for the root if transform_ui_spec is correct.

    def _title(self, widget, props): # props is the widget's direct props from layout
        title_val = props.get("title") # Expects title directly in props
        if title_val is not None:
            print(f"  Configuring title for {widget}: {title_val}")
            widget.title(title_val)

    def _geometry(self, widget, props): # props is the widget's direct props from layout
        geometry_val = props.get("geometry") # Expects geometry directly in props
        if geometry_val is not None:
            print(f"  Configuring geometry for {widget}: {geometry_val}")
            widget.geometry(geometry_val)

    def _grid(self, widget, props):
        # print(f"  Applying grid for {widget}: {props.get('grid')}") # Original
        grid_prop_value = props.get('grid') # Get the grid dict
        if not grid_prop_value:
            # print(f"  No grid properties to apply for {widget}") # Original
            return # No grid property defined for this widget

        print(f"  Applying grid for {widget}: {grid_prop_value}")
        grid_props_copy = grid_prop_value.copy() # Work with a copy
        weight = grid_props_copy.pop('weight', {})

        if grid_props_copy: # Only call grid if there are actual grid options like row, column, sticky
            widget.grid(**grid_props_copy)
            print(f"    Grid applied: {grid_props_copy}")

            row = grid_props_copy.get("row", 0) # Default to 0 if not specified
            column = grid_props_copy.get("column", 0) # Default to 0 if not specified

            if widget.master: # Ensure there is a master to configure
                if "row" in weight and hasattr(widget.master, 'grid_rowconfigure'):
                    print(f"    Configuring row {row} weight {weight['row']} on parent {widget.master}")
                    widget.master.grid_rowconfigure(row, weight=weight["row"])
                if "column" in weight and hasattr(widget.master, 'grid_columnconfigure'):
                    print(f"    Configuring column {column} weight {weight['column']} on parent {widget.master}")
                    widget.master.grid_columnconfigure(column, weight=weight["column"])
            elif weight: # Has weight but no master (should not happen for gridded items)
                print(f"    Warning: Grid weight specified for {widget}, but it has no master.")
        elif weight: # Only weight was specified in grid prop, no other grid options
            print(f"    Warning: Grid 'weight' specified for {widget} but no other grid properties (row, col, sticky). Weight may not apply as intended without grid placement.")
        else:
            print(f"  No actionable grid properties (row, col, sticky etc.) to apply for {widget}")


    def _config(self, widget, props):
        # print(f"  Applying config for {widget}: {props.get('config')}") # Original
        config_prop_value = props.get("config") # Get the config dict itself
        if not config_prop_value:
            # print(f"  No config properties to apply for {widget}") # Original
            return

        print(f"  Applying config for {widget}: {config_prop_value}")
        configs_to_apply = {}

        for key, value in config_prop_value.items():
            if isinstance(value, dict) and "widget" in value and "method" in value:
                if value["widget"] in self.widgets:
                    ref_widget = self.widgets[value["widget"]]
                    method = getattr(ref_widget, value["method"], None)
                    if callable(method):
                        configs_to_apply[key] = method
                    else:
                        print(
                            f"    Warning: Method '{value['method']}' "
                            "not found or not callable for widget "
                            f"'{value['widget']}'."
                        )
                else:
                    print(
                        f"    Warning: Referenced widget '{value['widget']}' "
                        f"not found for config key '{key}'."
                    )
            else:
                configs_to_apply[key] = value

        if configs_to_apply:
            try:
                widget.config(**configs_to_apply)
                print(f"    Config applied: {configs_to_apply}")
            except tk.TclError as e:
                print(f"    Warning: Could not apply config {configs_to_apply} to {widget}: {e}")
        else:
            print(f"  No config properties to apply for {widget} after processing.")


    def _bind(self, widget, props):
        # print(f"  Applying bind for {widget}: {props.get('bind')}") # Original
        bindings = props.get("bind") # Get the bind dict
        if not bindings:
            return
        print(f"  Applying bind for {widget}: {bindings}")
        for event, cmd in bindings.items():
            handler = self.handlers.get(cmd)
            if handler:
                widget.bind(event, handler)
                print(f"    Bound event '{event}' to handler '{cmd}'")
            else:
                print(f"    Warning: Handler '{cmd}' not found for event '{event}'.")
    
    # _create_window remains the same as in wisp18.py for now
    def _create_window(self, widget, props):
        # ... (existing _create_window logic from wisp18.py)
        # Ensure 'name' variable is available if used in print statements, or pass it.
        # For context, 'widget' is the canvas here.
        canvas = widget
        create_window_prop = props.get("create_window")
        if not create_window_prop:
            return
            
        content_frame_name = create_window_prop["content"]
        
        if content_frame_name in self.widgets:
            content_frame = self.widgets[content_frame_name]
            
            canvas.create_window(
                (0, 0),
                window=content_frame,
                anchor="nw",
                tags="content_window"
            )
            
            content_frame.update_idletasks()
            
            bbox = canvas.bbox("all") 
            if bbox:
                canvas.config(scrollregion=bbox)
            else:
                req_width = content_frame.winfo_reqwidth()
                req_height = content_frame.winfo_reqheight()
                canvas.config(scrollregion=(0, 0, req_width, req_height))
                if req_width == 1 and req_height == 1:
                     print(
                        f"Warning: content_frame '{content_frame_name}' "
                        "has minimal size. Scrollregion might be incorrect.")
        else:
            # If 'name' refers to the canvas widget's name:
            # Need to get it if not passed. For now, assume 'widget.winfo_name()' or similar context.
            # This method is called as self._create_window(widget, props), 'name' isn't directly passed.
            # Let's assume 'widget' is sufficient for context in prints or use a generic term.
            print(
                f"Warning: Content frame '{content_frame_name}' "
                f"not found in widgets for canvas '{str(widget)}'." 
            )


    def build(self):
        print("--- Starting App Build ---")
        # Phase 1: Create widgets (same as wisp18.py)
        def create_widgets(parent, name, node):
            kind = node.get("type")
            if not kind:
                print(f"Node '{name}' has no 'type'. Skipping widget creation.")
                return None
            print(f"Creating widget: {kind} with name '{name}'")
            widget_instance = None # Renamed from 'widget' to avoid conflict
            if name == "root" and kind == "Tk":
                widget_instance = tk.Tk()
            else:
                # ttk handling can be added here if needed: getattr(ttk, kind, None)
                widget_class = getattr(tk, kind, None)
                if widget_class:
                    widget_instance = widget_class(parent)
                else:
                    print(f"Unknown widget type '{kind}' for node '{name}'. Skipping.")
                    return None
            self.widgets[name] = widget_instance
            print(f"  Widget '{name}' created and stored: {widget_instance}")
            for part_name, part_node in node.get("parts", {}).items():
                create_widgets(widget_instance, part_name, part_node)
            return widget_instance

        root_node_data = self.layout.get("root")
        if root_node_data:
             create_widgets(None, "root", root_node_data)
        else:
             print("Error: 'root' node not found in layout dictionary.")
             return
        print("--- Finished Widget Creation ---")
        # print(f"Widgets dictionary: {self.widgets}")

        # Phase 2: Configure widgets
        def configure_widgets(current_widget_name, current_node_data):
            widget = self.widgets.get(current_widget_name)
            if not widget:
                print(f"Widget '{current_widget_name}' not found for configuration. Skipping.")
                return

            props = current_node_data.get("props", {})
            print(f"Configuring widget: '{current_widget_name}'") # Removed props from this print for brevity

            # Handle root-specific methods directly from its props
            if current_widget_name == "root": # or check widget type
                if "title" in props: # Title should be directly in props now
                    self._title(widget, props)
                if "geometry" in props: # Geometry should be directly in props now
                    self._geometry(widget, props)
            
            # Configure parts before applying layout/config of the parent
            for part_name, part_node in current_node_data.get("parts", {}).items():
                configure_widgets(part_name, part_node)

            # Apply layout, then static config, then data bindings, then event binds
            if "grid" in props:
                self._grid(widget, props)
            if "config" in props: # For static configurations from TKML/TOML
                self._config(widget, props)
            
            # Apply data bindings from state
            data_bindings = props.get("data_bindings", {})
            if data_bindings:
                print(f"  Applying data bindings for {current_widget_name}: {data_bindings}")
                for widget_attr, state_key in data_bindings.items():
                    if state_key in self.state:
                        value_from_state = self.state[state_key]
                        try:
                            widget.config(**{widget_attr: value_from_state})
                            print(f"    Data binding applied: {widget_attr} = '{value_from_state}' from state['{state_key}']")
                        except tk.TclError as e:
                            print(f"    Warning: TclError applying data binding {widget_attr} for {current_widget_name}: {e}")
                    else:
                        print(f"    Warning: State key '{state_key}' not found for data binding {widget_attr} on {current_widget_name}.")

            if "bind" in props:
                self._bind(widget, props)
            if "create_window" in props: # For canvas
                self._create_window(widget, props)

            print(f"Finished configuring widget: '{current_widget_name}'")

        if root_node_data:
             configure_widgets("root", root_node_data)
        else:
             print("Error: 'root' node not found for configuration.")
        print("--- Finished App Build ---")

    def update(self):
        print("--- Updating UI ---")
        # This specific update logic will work if myLabel's text is bound to self.state['text']
        # and self.state['text'] is what 'toggle_label_state' modifies.
        # For a general solution, update would iterate through known bindings.
        label_widget = self.widgets.get("myLabel")
        if label_widget:
            # Assuming 'text' property of myLabel is to be synced with self.state['text']
            # This could be generalized if widget props store their state key mapping
            state_key_for_label_text = "text" # This is the key used in toggle_label_state
            if state_key_for_label_text in self.state:
                desired_text = self.state[state_key_for_label_text]
                # Check if an update is actually needed
                # Using try-except in case widget is destroyed or cget fails for some reason
                try:
                    if label_widget.cget("text") != desired_text:
                        print(f"Updating myLabel text to: '{desired_text}'")
                        label_widget.config(text=desired_text)
                    # else:
                        # print("myLabel text is already up to date.")
                except tk.TclError:
                    print("Warning: Could not get or set text for myLabel (widget might be destroyed).")
            # else:
                # print(f"State key '{state_key_for_label_text}' not found in state for myLabel update.")
        # else:
            # print("myLabel widget not found for update.")
        print("--- UI Update Complete ---")


    def toggle_label_state(self, event=None):
        print("--- toggle_label_state handler called ---")
        current_text_state = self.state.get('text') # 'text' is the key this handler manipulates
        if current_text_state == 'Text from State One':
            self.state['text'] = 'Text from State Two Changed!'
        elif current_text_state == 'Text from State Two Changed!':
            self.state['text'] = 'Text from State Three (was Two)!'
        else: # Covers initial 'some_text' or any other state
            self.state['text'] = 'Text from State One'
        
        print(f"  New state['text']: {self.state['text']}")
        self.update()

# --- Main Application Execution ---

if __name__ == "__main__":
    dummy_persistent_state = {
        'text': 'some_text'
    }

    print("--- Starting Main Execution ---")
    # Simulate loading and parsing
    # Use the actual load.py functions if available, otherwise the dummies above
    parsed_tkml = load.tkml_string(tkml_source)
    parsed_toml = load.toml_string(toml_source)

    final_layout_dict = transform_ui_spec(parsed_tkml, parsed_toml)
    print("\n--- Final Transformed Layout Dictionary ---")
    import json
    print(json.dumps(final_layout_dict, indent=2))
    print("-------------------------------------------")

    # Initialize the App with the shared state and the transformed layout
    app = App(dummy_persistent_state , final_layout_dict)

    # Build the UI based on the layout
    app.build()

    # Perform initial UI update based on the initial state
    app.update()

    # Start the Tkinter event loop
    print("--- Starting Tkinter mainloop ---")
    app.widgets['root'].mainloop()
    print("--- Tkinter mainloop finished ---")


