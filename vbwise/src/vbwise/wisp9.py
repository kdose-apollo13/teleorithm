import tkinter as tk

tkml = {
    'type': 'Tk', 'props': {'title': 'Demo', 'geometry': '300x150'},
    'parts': [
        {'type': 'Label', 'props': {'id': 'label'}},
        {'type': 'Button', 'props': {'id': 'btn', 'text': 'Toggle',
                                     'bind': {'<Button-1>': 'toggle'}}}
    ]
}

toml = {
    'style': {'label': {'fg': 'blue'}, 'btn': {'bg': 'gray'}},
    'config': {'label_text': 'Hello'}
}

gnml = {
    'state': ['one', 'two'],
    'meta': {
        'one': {'label_text': 'State One'},
        'two': {'label_text': 'State Two'}
    }
}

class App:
    def __init__(self, tkml, toml, gnml):
        self.tkml, self.toml, self.gnml = tkml, toml, gnml
        self.widgets, self.state = {}, 'one'
        self.root = tk.Tk()
        self.build(tkml, self.root)
        self.style()
        self.bind()
        self.update()

    def build(self, spec, parent):
        cls = spec['type']
        props = spec.get('props', {})
        parts = spec.get('parts', [])

        w = parent if cls == 'Tk' else getattr(tk, cls)(parent)

        if 'text' in props:
            w.config(text=props['text'])
        if 'id' in props:
            self.widgets[props['id']] = w

        if cls != 'Tk':
            w.pack(fill='x', padx=10, pady=5)
        if cls == 'Tk':
            if 'title' in props:
                w.title(props['title'])
            if 'geometry' in props:
                w.geometry(props['geometry'])

        for part in parts:
            self.build(part, w)

    def style(self):
        for id_, widget in self.widgets.items():
            cfg = self.toml['style'].get(id_, {})
            try:
                widget.config(**cfg)
            except:
                pass

    def bind(self):
        for id_, binds in self.get_binds().items():
            widget = self.widgets.get(id_)
            for evt, fn in binds.items():
                if hasattr(self, fn):
                    widget.bind(evt, lambda e, f=fn: (getattr(self, f)(), self.update()))

    def get_binds(self):
        def scan(spec):
            out = {}
            if 'bind' in spec.get('props', {}):
                out[spec['props']['id']] = spec['props']['bind']
            for p in spec.get('parts', []):
                out.update(scan(p))
            return out
        return scan(self.tkml)

    def update(self):
        self.widgets['label'].config(
            text=self.gnml['meta'][self.state]['label_text'])

    def toggle(self):
        self.state = 'two' if self.state == 'one' else 'one'

App(tkml, toml, gnml).root.mainloop()

