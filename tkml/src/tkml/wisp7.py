"""
    // what is the state of a Scrollable? how can you tell? how does it change? //

    | teleorithm |
"""
from tkinter import *
from time import time
import pprint # Import pprint for cleaner dictionary printing

def label(base, i):
    lbl = Label(base, text=f'hello from label {i}')
    return lbl

def outer_frame(base):
    frm = Frame(base)
    frm.grid_columnconfigure(0, weight=1)
    frm.grid_rowconfigure(0, weight=1)
    return frm

def viewport_canvas(base):
    c = Canvas(base)
    c.grid(row=0, column=0, sticky="nsew")
    sb = Scrollbar(base, orient="vertical", command=c.yview)
    sb.grid(row=0, column=1, sticky="ns")
    c.config(yscrollcommand=sb.set)
    return c

def inner_frame(view):
    f = Frame(view)
    f.grid_columnconfigure(0, weight=1)
    return f

def get_scroll_state(canvas):
    """
    Captures the current scroll state of the canvas.
    Returns a dictionary with pixel offset and percentage offset (vertical).
    """
    # Get the fractional scroll position (0.0 to 1.0 for top edge visibility)
    yview_fraction = canvas.yview()
    scroll_fraction_top = yview_fraction[0]

    # Get the total scrollable area dimensions (bounding box of all items)
    bbox = canvas.bbox("all")
    total_height = bbox[3] - bbox[1] if bbox else 0

    # Calculate pixel offset
    pixel_offset_y = scroll_fraction_top * total_height if total_height > 0 else 0

    # Calculate percentage offset
    percentage_offset_y = scroll_fraction_top * 100

    # Get the visible canvas dimensions (viewport size)
    visible_width = canvas.winfo_width()
    visible_height = canvas.winfo_height()


    state = {
        "scroll_offset": {
            "pixels_y": pixel_offset_y,
            "percentage_y": percentage_offset_y,
        },
        "scrollable_area": {
            "width": bbox[2] - bbox[0] if bbox else 0, # Width from bbox
            "height": total_height,
        },
        "visible_area": {
            "width": visible_width,
            "height": visible_height,
        },
        "yview_fraction": yview_fraction, # Raw yview output for reference
    }
    return state


def create_scrollable(base):
    base.grid_rowconfigure(0, weight=1)     # allow expand
    base.grid_columnconfigure(0, weight=1)
    container = outer_frame(base)
    container.grid(row=0, column=0, sticky="nsew")

    view = viewport_canvas(container)
    content = inner_frame(view)
    win_id = view.create_window((0, 0), window=content, anchor="nw")

    # update scrollregion on content resize
    content.bind(
        "<Configure>",
        lambda e: view.config(scrollregion=view.bbox("all"))
    )
    # resize inner frame width with canvas
    view.bind(
        "<Configure>",
        lambda e: view.itemconfig(win_id, width=e.width)
    )

    for i in range(14):
        l = label(content, i)
        l.grid(row=i, column=0, sticky='ew')

    # Return the container and the canvas so we can access the canvas later
    return container, view


root = Tk()
root.grid_rowconfigure(0, weight=1)         # allow root to expand
root.grid_columnconfigure(0, weight=1)

# Capture the container and canvas when creating the scrollable
scrollable_container, scrollable_canvas = create_scrollable(root)

# Bind a key press (e.g., 's' for state) to the root window
def on_key_press(event):
    if event.char == 's':
        # Use the captured canvas reference
        state = get_scroll_state(scrollable_canvas)
        print("\n--- Scrollable State ---")
        pprint.pprint(state)
        print("------------------------")

root.bind("<Key>", on_key_press)

root.mainloop()

