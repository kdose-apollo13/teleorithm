import tkinter

from vbwise import load


model = {
    'title': 'back in shape',
    'label_text': 'the title is {model.title}'
}

widgets = {
    'root': {
        '_type': 'Tk',
        '_base': None,
        'geometry': '400x300',
        'grid_rowconfigure': {'row': 0, 'weight': 1},
        'grid_columnconfigure': {'column': 0, 'weight': 1},
    },
    'frame': {
        '_type': 'Frame',
        '_base': 'root',
        'grid': {'row': 0, 'column': 0, 'sticky': 'nsew'},
        'config': {'background': '#112233'},
    },
    'label': {
        '_type': 'Label',
        '_base': 'frame',
        'grid': {'row': 0, 'column': 0},
        'config': {'text': 'hello'},
    }
}


from graphlib import TopologicalSorter as TS

# this is what comes from tkml -> << id: [base,] >> mapping
# and also goes back to canonical tkml
d = {
    'root': [],
    'frame': ['root',],
    'canvas': ['frame',],
    'scrollbar': ['frame',],
    'subframe': ['canvas',],
}

ts = TS(d)
widget_creation_order = list(ts.static_order())
print(widget_creation_order)

refs = {}
for w, spec in widgets.items():
    # print(w, spec)
    _type = spec.get('_type', None)
    _base = spec.get('_base', None)
    _class = getattr(tkinter, _type, None)
    # if _class:
    #     widget = _class(_base)
        
    print(_type, _base)
    methods = [k[1:] for k in spec if k[0] == '_']
    print(methods)
        


root = tkinter.Tk()

root.geometry('400x300')
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

frame = tkinter.Frame(root)
frame.grid(row=0, column=0, sticky='nesw')
frame.config(background='#112233')

label = tkinter.Label(frame)
label.grid(row=0, column=0)
label.config(text='hello')

# root.mainloop()

