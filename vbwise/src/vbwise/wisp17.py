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
    title: "Elegant Data-Driven Demo"
    geometry: "300x150"

    Frame {
        id: mainFrame
        layout_style: "main_frame_layout"

        Label {
            id: myLabel
            text: "Initial Text from TKML"
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

    def process_widget(ui_spec):
        widget_data = {
            'type': ui_spec['type'],
            'props': {},
            'parts': {}
        }
        widget_id = ui_spec.get('props', {}).get('id', f"anon_{ui_spec['type'].lower()}")

        # Collect configuration props from TKML (excluding 'id', 'style', 'layout_style', 'parts', 'bind')
        config_props = {}
        for prop, value in ui_spec.get('props', {}).items():
            if prop not in ['id', 'style', 'layout_style', 'parts', 'bind']:
                config_props[prop] = value
        if config_props:
            widget_data['props']['config'] = config_props

        # Apply style from TOML if referenced
        style_name = ui_spec.get('props', {}).get('style')
        if style_name and 'styles' in toml_data and style_name in toml_data['styles']:
            style_props = toml_data['styles'][style_name]
            if 'config' not in widget_data['props']:
                widget_data['props']['config'] = {}
            widget_data['props']['config'] = merge_dicts(
                widget_data['props']['config'], style_props
            )

        # Apply layout from TOML if referenced
        layout_name = ui_spec.get('props', {}).get('layout_style')
        if layout_name and 'layouts' in toml_data and layout_name in toml_data['layouts']:
            layout_props = toml_data['layouts'][layout_name]
            widget_data['props'] = merge_dicts(
                widget_data['props'], layout_props
            )

        # Process nested parts
        if 'parts' in ui_spec:
            for part_spec in ui_spec['parts']:
                part_name = part_spec.get('props', {}).get('id', f"anon_{part_spec['type'].lower()}")
                widget_data['parts'][part_name] = process_widget(part_spec)

        # Handle 'bind' from TKML
        if 'bind' in ui_spec.get('props', {}):
            widget_data['props']['bind'] = ui_spec['props']['bind']

        return widget_data
    
    root_spec = tkml_data

    # Ensure the root is named 'root' in the transformed data for wisp16 App
    transformed_data['root'] = process_widget(root_spec)

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
            "toggle_label_state": self.toggle_label_state # Ensure handler is registered
        }
        print(f"Initial state: {self.state}")
        print(f"Layout data: {self.layout}")


    def _title(self, widget, props):
        print(f"  Configuring title for {widget}: {props.get('title')}")
        widget.title(props.get("title", ""))

    def _geometry(self, widget, props):
        print(f"  Configuring geometry for {widget}: {props.get('geometry')}")
        widget.geometry(props.get("geometry", ""))

    def _grid(self, widget, props):
        print(f"  Applying grid for {widget}: {props.get('grid')}")
        grid_props = props.get("grid", {}).copy()
        weight = grid_props.pop('weight', {})
        if grid_props: # Only call grid if there are properties
            widget.grid(**grid_props)
            print(f"    Grid applied: {grid_props}")

            row = grid_props.get("row", 0)
            column = grid_props.get("column", 0)

            if "row" in weight and hasattr(widget.master, 'grid_rowconfigure'):
                print(f"    Configuring row {row} weight {weight['row']} on parent {widget.master}")
                widget.master.grid_rowconfigure(row, weight=weight["row"])
            if "column" in weight and hasattr(widget.master, 'grid_columnconfigure'):
                print(f"    Configuring column {column} weight {weight['column']} on parent {widget.master}")
                widget.master.grid_columnconfigure(column, weight=weight["column"])
        else:
            print(f"  No grid properties to apply for {widget}")


    def _config(self, widget, props):
        print(f"  Applying config for {widget}: {props.get('config')}")
        config_props = props.get("config", {})
        configs_to_apply = {}

        for key, value in config_props.items():
            if isinstance(value, dict) and "widget" in value and "method" in value:
                if value["widget"] in self.widgets:
                    ref_widget = self.widgets[value["widget"]]
                    method = getattr(ref_widget, value["method"], None)
                    if callable(method):
                        configs_to_apply[key] = method
                    else:
                        print(
                            f"Warning: Method '{value['method']}' "
                            "not found or not callable for widget "
                            f"'{value['widget']}'."
                        )
                else:
                    print(
                        f"Warning: Referenced widget '{value['widget']}' "
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
            print(f"  No config properties to apply for {widget}")


    def _bind(self, widget, props):
        print(f"  Applying bind for {widget}: {props.get('bind')}")
        bindings = props.get("bind", {})
        for event, cmd in bindings.items():
            handler = self.handlers.get(cmd)
            if handler:
                widget.bind(event, handler)
                print(f"    Bound event '{event}' to handler '{cmd}'")
            else:
                print(f"    Warning: Handler '{cmd}' not found for event '{event}'.")

    def _create_window(self, widget, props):
        canvas = widget
        content_frame_name = props["create_window"]["content"]
        
        if content_frame_name in self.widgets:
            content_frame = self.widgets[content_frame_name]
            
            canvas.create_window(
                (0, 0),
                window=content_frame,
                anchor="nw",
                tags="content_window"
            )
            
            # ensure content_frame's geometry is calculated based on its partren
            content_frame.update_idletasks()
            
            # Set the scrollregion for the canvas.
            bbox = canvas.bbox("all") 
            if bbox:
                canvas.config(scrollregion=bbox)
            else:
                # Fallback or if content_frame is empty, use its requested size
                req_width = content_frame.winfo_reqwidth()
                req_height = content_frame.winfo_reqheight()
                canvas.config(scrollregion=(0, 0, req_width, req_height))
                if req_width == 1 and req_height == 1:
                     print(
                        f"Warning: content_frame '{content_frame_name}' "
                        "has minimal size. Scrollregion might be incorrect.")
        else:
            print(
                f"Warning: Content frame '{content_frame_name}' "
                f"not found in widgets for canvas '{name}'."
            )

    def build(self):
        print("--- Starting App Build ---")
        # Phase 1: Create all widgets recursively
        def create_widgets(parent, name, node):
            kind = node.get("type")
            if not kind:
                print(f"Node '{name}' has no 'type'. Skipping widget creation.")
                return None

            print(f"Creating widget: {kind} with name '{name}'")

            widget = None
            if name == "root" and kind == "Tk":
                widget = tk.Tk()
            else:
                widget_class = getattr(tk, kind, None) or getattr(ttk, kind, None)
                if widget_class:
                    widget = widget_class(parent)
                else:
                    print(f"Unknown widget type '{kind}' for node '{name}'. Skipping.")
                    return None

            self.widgets[name] = widget
            print(f"  Widget '{name}' created and stored: {widget}")

            for part_name, part_node in node.get("parts", {}).items():
                create_widgets(widget, part_name, part_node)
            return widget # Return the created widget


        # Start creating from the root node in the layout dictionary
        root_node = self.layout.get("root")
        if root_node:
             create_widgets(None, "root", root_node)
        else:
             print("Error: 'root' node not found in layout dictionary.")
             return


        print("--- Finished Widget Creation ---")
        print(f"Widgets dictionary: {self.widgets}")


        # Phase 2: Configure all widgets recursively
        def configure_widgets(name, node):
            widget = self.widgets.get(name)
            if not widget:
                print(f"Widget '{name}' not found for configuration. Skipping.")
                return

            props = node.get("props", {})
            print(f"Configuring widget: '{name}' with props: {props}")

            if "title" in props:
                self._title(widget, props)
            if "geometry" in props:
                self._geometry(widget, props)

            # Configure parts before applying layout/config that might depend on child sizes
            for part_name, part_node in node.get("parts", {}).items():
                configure_widgets(part_name, part_node)

            # Apply layout and config after children are configured
            if "grid" in props:
                self._grid(widget, props)
            if "config" in props:
                self._config(widget, props)
            if "bind" in props:
                self._bind(widget, props)
            if "create_window" in props:
                self._create_window(widget, props)

            print(f"Finished configuring widget: '{name}'")


        # Start configuring from the root node
        if root_node:
             configure_widgets("root", root_node)
        else:
             print("Error: 'root' node not found in layout dictionary for configuration.")

        print("--- Finished App Build ---")


    def update(self):
        print("--- Updating UI ---")
        label_widget = self.widgets.get("myLabel")
        if label_widget:
            desired_text = self.state.get("text", "Default Text from State")
            if label_widget.cget("text") != desired_text:
                print(f"Updating myLabel text to: '{desired_text}'")
                label_widget.config(text=desired_text)
            else:
                print("myLabel text is already up to date.")
        else:
            print("myLabel widget not found for update.")

        print("--- UI Update Complete ---")


    def toggle_label_state(self, event=None):
        print("--- toggle_label_state handler called ---")
        # This is a state transformation function
        # In a real app, this would modify the AppState
        # For this demo, we'll just toggle the text in STORED_STATE
        if self.state.get('text') == 'Text from State One':
            self.state['text'] = 'Text from State Two Changed!'
        else:
            self.state['text'] = 'Text from State One'

        # print(f"STORED_STATE after toggle: {STORED_STATE}")
        # After changing state, trigger a UI update
        self.update()
        # print("--- toggle_label_state handler finished ---")


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


