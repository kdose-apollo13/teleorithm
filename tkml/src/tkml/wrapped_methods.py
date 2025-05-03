"""
    i
        : tkinter.Widget
        : instance for method

    d
        : dict
        : options to pass to method
"""

def grid_rowconfigure(i, d):
    i.grid_rowconfigure(d['row'], weight=d['weight'])

def grid_columnconfigure(i, d):
    i.grid_columnconfigure(d['col'], weight=d['weight'])

def grid(i, d):
    i.grid(row=d['row'], column=d['column'], sticky=d['sticky'])

def config(i, d):
    i.config(**d)

def bind(i, d):
    raise NotImplementedError()

def title(i, s):
    i.title(s)

def geometry(i, s):
    i.geometry(s)

def text(i, s):
    i.delete('1.0', tkinter.END)
    i.insert('1.0', s)

