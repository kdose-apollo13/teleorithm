import tkinter as tk
from tkinter import ttk, scrolledtext

class ScrollableFrame(tk.Frame):
    """
    A custom Tkinter frame that provides a scrollable area.
    Widgets added to the `self.scrollable_content_frame` will be scrollable.
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Canvas to hold the scrollable content
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        
        # Vertical scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Frame inside the canvas that will contain the actual widgets
        self.scrollable_content_frame = ttk.Frame(self.canvas)

        # Place the scrollable_content_frame inside the canvas
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_content_frame, anchor="nw")

        # Layout: scrollbar on the right, canvas takes the rest
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind events for resizing and scrolling
        self.scrollable_content_frame.bind("<Configure>", self._on_content_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Bind mouse wheel scrolling (platform-dependent)
        # For Windows and MacOS
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # For Linux
        self.canvas.bind_all("<Button-4>", self._on_mousewheel) # Scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel) # Scroll down

    def _on_content_frame_configure(self, event=None):
        """Updates the scrollregion of the canvas when the content frame's size changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        """Ensures the content frame width matches the canvas width."""
        self.canvas.itemconfig(self.canvas_frame_id, width=self.canvas.winfo_width())

    def _on_mousewheel(self, event):
        """Handles mouse wheel scrolling."""
        # Determine if the event is targeted for this scrollable area
        # This is a basic check; more sophisticated focus/event management might be needed in complex UIs
        widget_under_mouse = self.winfo_containing(event.x_root, event.y_root)
        is_relevant_scroll = False
        if widget_under_mouse:
            # Check if the widget under mouse is this canvas or a child of the scrollable_content_frame
            if widget_under_mouse == self.canvas:
                is_relevant_scroll = True
            else:
                current_widget = widget_under_mouse
                while current_widget is not None:
                    if current_widget == self.scrollable_content_frame:
                        is_relevant_scroll = True
                        break
                    current_widget = current_widget.master
        
        if not is_relevant_scroll and self.canvas.winfo_ismapped(): # Only scroll if relevant or canvas is visible
             # If not directly relevant, but the canvas is part of the active window, allow scroll.
             # This behavior might need refinement based on desired UX.
             pass


        if event.num == 5 or event.delta < 0:  # Scroll down (Linux or Windows/MacOS)
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:  # Scroll up (Linux or Windows/MacOS)
            self.canvas.yview_scroll(-1, "units")
        return "break" # Prevents event from propagating further if handled


class TkinterBuilder:
    """
    Builds a Tkinter UI from a dictionary-based TKML-like structure.
    """
    def __init__(self, style_dict=None):
        self.root = None
        self.widget_map = {} # To store widgets by ID if TKML supports it
        self.style_dict = style_dict if style_dict else {} # For future styling

    def _create_widget(self, parent, component_def):
        """
        Creates a single Tkinter widget based on its definition.
        """
        widget_type_str = component_def.get('type')
        props = component_def.get('props', {})
        parts = component_def.get('parts', []) # Child components

        widget = None

        # --- Widget Type Dispatcher ---
        if widget_type_str == 'Tk': # Root window
            if self.root is not None:
                raise ValueError("TKML definition can only have one root 'Tk' element.")
            self.root = tk.Tk()
            widget = self.root
            if 'title' in props:
                self.root.title(props['title'])
            if 'geometry' in props:
                self.root.geometry(props['geometry'])
        
        elif widget_type_str == 'Frame':
            widget = ttk.Frame(parent)
        elif widget_type_str == 'Label':
            widget = ttk.Label(parent, text=props.get('text', ''))
        elif widget_type_str == 'Button':
            widget = ttk.Button(parent, text=props.get('text', 'Click Me'))
            if 'command' in props: # Simple command handling (e.g., string name of a method)
                # For a real app, command would need to be resolved to a callable
                print(f"Button with command: {props['command']} (not implemented in this demo)")
        elif widget_type_str == 'Entry':
            widget = ttk.Entry(parent)
        elif widget_type_str == 'Text': # ScrolledText for multi-line
            widget = scrolledtext.ScrolledText(parent, wrap=tk.WORD)
            if 'text' in props: # Initial text content
                 widget.insert(tk.END, props['text'])
        elif widget_type_str == 'Scrollable': # Our custom composite widget
            # The 'ScrollableFrame' itself is the container.
            # Its 'parts' will be added to its 'scrollable_content_frame'.
            widget = ScrollableFrame(parent)
            # The children ('parts') of 'Scrollable' will be parented to widget.scrollable_content_frame
            for part_def in parts:
                self._create_widget(widget.scrollable_content_frame, part_def)
            # Return early as parts are handled internally for ScrollableFrame
            return widget 
            
        else:
            print(f"Warning: Unknown widget type '{widget_type_str}'. Creating a default Frame.")
            widget = ttk.Frame(parent) # Fallback

        # --- Apply Properties ---
        # This is a simplified property application. A real TKML might have 'config', 'pack', 'grid' etc.
        if 'id' in props:
            self.widget_map[props['id']] = widget
        
        # Example: applying general config options if present in props under a 'config' key
        if 'config' in props and isinstance(props['config'], dict):
            try:
                widget.configure(**props['config'])
            except tk.TclError as e:
                print(f"Error configuring widget {widget_type_str} with {props['config']}: {e}")

        # --- Recursively Create Child Widgets (Parts) ---
        # This section is skipped if widget_type_str == 'Scrollable' because it handles its parts internally.
        if widget_type_str != 'Scrollable':
            for part_def in parts:
                child_widget = self._create_widget(widget, part_def)
                if child_widget:
                    # Default packing for children if not specified by TKML layout props
                    # A more advanced builder would look for 'layout_type: pack/grid/place' and its options in TKML
                    child_widget.pack(padx=2, pady=2, fill=props.get('child_fill', 'x'), expand=props.get('child_expand', False))

        return widget

    def build(self, tkml_dict_root):
        """
        Builds the entire UI from the root TKML dictionary.
        """
        if not tkml_dict_root or tkml_dict_root.get('type') != 'Tk':
            raise ValueError("Root of TKML definition must be of type 'Tk'.")
        
        self.root = None # Reset in case of rebuild
        self.widget_map = {}
        
        ui = self._create_widget(None, tkml_dict_root) # Parent is None for the root Tk window
        return ui # Returns the root Tkinter widget (self.root)

# --- Sample TKML-like Dictionary ---
# This defines the UI structure declaratively.
sample_ui_definition = {
    'type': 'Tk',
    'props': {'title': 'TKML Scrollable Demo', 'geometry': '450x400'},
    'parts': [
        {
            'type': 'Frame', # Main container frame
            'props': {'id': 'main_container', 'child_fill': 'both', 'child_expand': True}, # Make scrollable fill
            'parts': [
                {
                    'type': 'Label',
                    'props': {'text': 'My Application Header'},
                    'parts': []
                },
                {
                    'type': 'Scrollable', # Use our custom ScrollableFrame
                    'props': {'id': 'my_scrollable_area'},
                    # 'parts' for Scrollable are its content
                    'parts': [ 
                        {'type': 'Label', 'props': {'text': 'Content Label 1 (Inside Scrollable)'}},
                        {'type': 'Button', 'props': {'text': 'Button A'}},
                        {'type': 'Entry', 'props': {}},
                        {'type': 'Label', 'props': {'text': 'Content Label 2'}},
                        {'type': 'Text', 'props': {'text': 'Multi-line text area.\nWith a few lines.\nTo test scrolling.', 'config': {'height': 5, 'width': 30}}},
                        {'type': 'Label', 'props': {'text': 'Content Label 3'}},
                        {'type': 'Button', 'props': {'text': 'Button B'}},
                        {'type': 'Label', 'props': {'text': 'Content Label 4'}},
                        {'type': 'Label', 'props': {'text': 'Content Label 5'}},
                        {'type': 'Entry', 'props': {}},
                        {'type': 'Label', 'props': {'text': 'Content Label 6'}},
                        {'type': 'Label', 'props': {'text': 'Content Label 7 - More text to ensure scrolling is needed for sure.'}},
                        {'type': 'Button', 'props': {'text': 'Button C (Near Bottom)'}},
                        {'type': 'Label', 'props': {'text': 'Content Label 8 (Very Bottom)'}},
                    ]
                },
                {
                    'type': 'Frame', # A footer frame
                    'props': {'id': 'footer', 'child_fill': 'x', 'child_expand': False},
                    'parts': [
                        {'type': 'Label', 'props': {'text': 'Status: Ready'}},
                        {'type': 'Button', 'props': {'text': 'Quit', 'command': 'quit_app_command'}}
                    ]
                }
            ]
        }
    ]
}

if __name__ == "__main__":
    builder = TkinterBuilder()
    
    try:
        root_window = builder.build(sample_ui_definition)
        
        # Example of how to access a widget by ID (if defined in TKML)
        if 'my_scrollable_area' in builder.widget_map:
            scroll_area = builder.widget_map['my_scrollable_area']
            # You could interact with scroll_area here if needed
            print(f"Scrollable area widget: {scroll_area}")

        if 'footer' in builder.widget_map:
            footer_frame = builder.widget_map['footer']
            # Modify the quit button's command if it was found
            # This is a bit manual; a better TKML would handle command binding more robustly
            for child in footer_frame.winfo_children():
                if isinstance(child, ttk.Button) and child.cget("text") == "Quit":
                    child.configure(command=root_window.destroy)
                    print("Quit button command configured.")
                    break
        
        if root_window:
            root_window.mainloop()
        else:
            print("Failed to build the UI. Root window is None.")

    except ValueError as e:
        print(f"Error building UI: {e}")
    except Exception as e_gen:
        print(f"An unexpected error occurred: {e_gen}")
        import traceback
        traceback.print_exc()

