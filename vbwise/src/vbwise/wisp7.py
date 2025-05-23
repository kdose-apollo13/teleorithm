from collections import defaultdict
from graphlib import TopologicalSorter as TS
from itertools import count
import json
import tkinter

from vbwise import load


model = {
    'title': 'choomin\' with baba yaga',
    'geometry': '400x300'
}


tkml_source = '''
Tk {
    _id: root
    title: model.title
    geometry: model.geometry
    grid_rowconfigure: { row: 0, weight: 1 }
    grid_columnconfigure: { column: 0, weight: 1}

    Frame {
        _id: frame
        grid: { row: 0, column: 0, sticky: nesw }
        config: { background: #112233 }
    }
}
'''

t = load.tkml_string(tkml_source)
# print(t)


def next_widget_name(_type, counter):
    return '_'.join( (_type, str(next(counter))) )


class WidgetIDs:
    def __init__(self, sep='_'):
        self.sep = sep
        self.counter = count(start=1)
        self.names = []

    def _type_and_counter(self, node):
        i = next(self.counter)
        _type = node['type']
        _id = _type + self.sep + str(i)
        return _id
    
    def new_id(self, node):
        props = node.get('props', {})
        if props:
            if '_id' in props:
                _id = props['_id']
            else:
                _id = self._type_and_counter(node)
        else:
            _id = self._type_and_counter(node)

        return _id
        

def widget_specs_by_id(node, flat=defaultdict(dict), widget_ids=WidgetIDs()):
    """
        node
            : dict

        returns
            >> dict
            >> flattens node into an {id: base, ...} mapping
    """
    _id = widget_ids.new_id(node)
    _type = node.get('type', '')
    props = node.get('props', {})
    parts = node.get('parts', [])

    flat[_id].update({'_type': _type})

    methods = {k: v for k, v in props.items() if k[0] != '_'}
    flat[_id].update(methods)

    for part in parts:
        _part_id = widget_ids.new_id(part)
        flat[_part_id]['_base'] = _id
        widget_specs_by_id(part, flat, widget_ids)

    return flat


specs_by_id = widget_specs_by_id(t)
# print(json.dumps(specs_by_id, indent=2))


def widget_bases_by_id(specs_by_id):
    d = {}
    for _id, spec in specs_by_id.items():
        if '_base' in spec:
            d.update({_id: [spec['_base'],]})
    return d


bases_by_id = widget_bases_by_id(specs_by_id)
# print(bases_by_id)


def widget_creation_order(bases_by_id):
    ts = TS(bases_by_id)
    order = list(ts.static_order())
    return order


order = widget_creation_order(bases_by_id)


runtime = {}

for _id in order:
    spec = specs_by_id[_id]
    _type = spec['_type']
    _base = spec.get('_base', None)
    if _base:
        _base_widget = runtime[_base]['widget']
    else:
        _base_widget = None

    _class = getattr(tkinter, _type, None)
    widget = _class(_base_widget)
    runtime[_id] = {'widget': widget}

for _id, spec in specs_by_id.items():
    widget = runtime[_id]['widget']
    methods = {k: v for k, v in spec.items() if k[0] != '_'}

    for name, o in methods.items():

        if isinstance(o, str) and o.startswith('model.'):
            _, key = o.split('.')
            o = model[key]

        if name == 'grid_rowconfigure':
            widget.grid_rowconfigure(o['row'], weight=o['weight'])
        elif name == 'grid_columnconfigure':
            widget.grid_columnconfigure(o['column'], weight=o['weight'])
        elif name == 'grid':
            widget.grid(**o)
        elif name == 'geometry':
            widget.geometry(o)
        elif name == 'config':
            widget.config(**o)
        elif name == 'title':
            widget.title(o)
        else:
            print('unknown', name)

# print(runtime)
root = runtime['root']['widget']
root.mainloop()

