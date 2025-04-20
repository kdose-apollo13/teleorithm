"""
    // what is the state of a Scrollable? how can you tell? how does it change? //

    | teleorithm |

    minimal Scrollable demo -> tkinter
"""
from tkinter import *
from time import time

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

    return container

root = Tk()
root.grid_rowconfigure(0, weight=1)         # allow root to expand
root.grid_columnconfigure(0, weight=1)
create_scrollable(root)
root.mainloop()

