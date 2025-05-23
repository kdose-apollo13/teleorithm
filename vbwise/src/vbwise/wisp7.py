from graphlib import TopologicalSorter as TS
import tkinter

from vbwise import load


tkml_source = '''
Tk {
    id: root
    Frame {
        id: frame
        Canvas { 
            id: canvas 
            Frame { id: subframe }
        }
        Scrollbar { id: scrollbar }
    }
}
'''

t = load.tkml_string(tkml_source)
# print(t)


def bases_by_id(node, flat={}):
    """
        node
            : dict

        returns
            >> recursively builds dict
    """
    _id = node['props']['id']
    parts = node['parts']
    for part in parts:
        # each part has own _id and base of _id
        flat[part['props']['id']] = [_id,]
        bases_by_id(part, flat)

    return flat


f = bases_by_id(t)
print(f)

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

ts = TS(bases_by_id(t))
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

