from vbwise import load


# not used here, just for reference
# notice <Return> and <Button-1> are NOT in quotes: identifiers not strings
EXAMPLE_TKML_SYNTAX = '''
Block {
    # comment line
    NestedBlock {}  # with trailing comment

    string: 'a "string" value'
    escaped: "what about \\"this\\" huh?"
    number: 31
    float: 23.529
    color: #AA1122
    dotted.property: 'yeah'

    multi_prop: { v: #123ABC q: 1000.xyz }
    comma_prop: { v: #123ABC, q: 1000, z: X.2 }
    multi_line_prop: {
        foo: 1.2.A.B
        bar: { 0: 1 },
    }

    bind: { <Return>: 'yeah' }

    nested_block {
        0: "digit identifier"
        one.two: "dotted identifier"
        bind: { <Button-1>: callback }
    }
}
'''

tkml_source = '''
Tk {
    id: root
    title: "Elegant Data-Driven Demo"
    geometry: "300x180"

    Frame {
        id: main_frame 
        0: 1
    }
}
'''

toml_source = '''
'''

json_source = '''
'''

parsed_tkml = load.tkml_string(tkml_source)
parsed_toml = load.toml_string(toml_source)
parsed_json = load.json_string(json_source)

assert parsed_tkml == {
  "type": "Tk",
  "props": {
    "id": "root",
    "title": "Elegant Data-Driven Demo",
    "geometry": "300x180"
  },
  "parts": [
    {
        'type': 'Frame',
        'props': {'id': 'main_frame', 0: 1},
        'parts': []
    }

  ]
}

assert parsed_toml == {}
assert parsed_json == {}


