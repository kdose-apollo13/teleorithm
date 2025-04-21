"""
    // what is the state of a Scrollable? how can you tell? how does it change? //

    | teleorithm |

    keep it simple: F(Frame, style) -> widget

"""
from textwrap import dedent
from tkinter import *
from time import time
import pprint # Import pprint for cleaner dictionary printing

import wrapped_methods


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


# root = Tk()
# root.grid_rowconfigure(0, weight=1)         # allow root to expand
# root.grid_columnconfigure(0, weight=1)
#
# # Capture the container and canvas when creating the scrollable
# scrollable_container, scrollable_canvas = create_scrollable(root)
#
# # Bind a key press (e.g., 's' for state) to the root window
# def on_key_press(event):
#     if event.char == 's':
#         # Use the captured canvas reference
#         state = get_scroll_state(scrollable_canvas)
#         print("\n--- Scrollable State ---")
#         pprint.pprint(state)
#         print("------------------------")
#
# root.bind("<Key>", on_key_press)
#
# root.mainloop()

def inner_frame(view):
    f = Frame(view)
    f.grid_columnconfigure(0, weight=1)
    return f

source = dedent('''
    Tkml {
        Scrollable {
            Frame {
                id: container

                Canvas {
                    id: viewport
                    config: yscrollcommand: scrollbar.set

                    Frame { 
                        id: content 
                    }
                }

                Scrollbar { 
                    id: scrollbar
                    config: command: viewport.yview
                }
            }
        }
    }
''')


def create_widget(tk_class, base, options):
    """
        tk_class
            : Callable
            : accepts tkinter.Widget
            : returns tkinter.Widget

        base
            : tkinter.Widget

        options
            : dict

        returns
            -> tkinter.Widget
    """
    widget = tk_class(base)
    # print(options)
    # keys are method names

    for name, opt in options.items():
        func = getattr(wrapped_methods, name, None)
        func(widget, opt)

    return widget


if __name__ == '__main__':
    import tkinter
    import tomllib

    with open('wisp7_style.toml', 'rb') as r:
        style = tomllib.load(r)

    type_name, options = list(style.items())[0]
    tk_class = getattr(tkinter, type_name)

    root = Tk()
    root.geometry('300x200+1100+400')
    w = create_widget(tk_class, root, options)

    root.mainloop()




