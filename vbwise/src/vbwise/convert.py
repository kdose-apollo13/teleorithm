import json # For pretty printing complex prop values if needed, and string escaping

def format_tkml_value(value):
    """
    Formats a Python value into a TKML string representation.
    """
    if isinstance(value, str):
        # Escape backslashes and quotes, and represent newlines as \n
        escaped_value = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        return f'"{escaped_value}"'
    elif isinstance(value, bool):
        return "true" if value else "false" # Assuming TKML might have true/false identifiers
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, dict): # For nested properties
        items = []
        for k, v in value.items():
            items.append(f"{k}: {format_tkml_value(v)}")
        return "{ " + ", ".join(items) + " }" # Simplified: no newlines for inner nested_props
    elif value is None:
        return "null" # Or handle as an empty string or omit, depending on TKML semantics
    else:
        # Fallback for other types, could be an identifier if it matches grammar
        return str(value)

def dict_to_tkml_string(component_dict, indent_level=0):
    """
    Converts a component dictionary (TKML-like) into a TKML string.
    """
    if not isinstance(component_dict, dict) or 'type' not in component_dict:
        return ""

    indent = "    " * indent_level
    tkml_parts = []

    component_type = component_dict.get('type', 'UnknownType')
    props = component_dict.get('props', {})
    parts = component_dict.get('parts', [])

    tkml_parts.append(f"{indent}{component_type} {{")

    # Format properties
    for key, value in props.items():
        # Skip properties that are not part of the standard TKML structure
        # (like child_fill, child_expand from the demo builder)
        # A more robust solution would be to have a list of known TKML props
        # or rely on the source dictionary being purely TKML-compliant.
        if key in ['child_fill', 'child_expand']: # Example of skipping non-TKML props
            continue
        tkml_parts.append(f"{indent}    {key}: {format_tkml_value(value)}")

    # Format parts (child components)
    for part_dict in parts:
        tkml_parts.append(dict_to_tkml_string(part_dict, indent_level + 1))

    tkml_parts.append(f"{indent}}}")
    return "\n".join(tkml_parts)

if __name__ == '__main__':
    # This is the sample_ui_definition from the tkml_to_tkinter_builder.py
    # It's the dictionary we want to convert back to a TKML string.
    sample_ui_definition_from_builder = {
        'type': 'Tk',
        'props': {'title': 'TKML Scrollable Demo', 'geometry': '450x400'},
        'parts': [
            {
                'type': 'Frame',
                'props': {'id': 'main_container', 'child_fill': 'both', 'child_expand': True},
                'parts': [
                    {
                        'type': 'Label',
                        'props': {'text': 'My Application Header'},
                        'parts': []
                    },
                    {
                        'type': 'Scrollable',
                        'props': {'id': 'my_scrollable_area'},
                        'parts': [
                            {'type': 'Label', 'props': {'text': 'Content Label 1 (Inside Scrollable)'}},
                            {'type': 'Button', 'props': {'text': 'Button A'}},
                            {'type': 'Entry', 'props': {}}, # Empty props
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
                        'type': 'Frame',
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

    print("--- TKML String generated from the Builder's Dictionary ---")
    generated_tkml_string = dict_to_tkml_string(sample_ui_definition_from_builder)
    print(generated_tkml_string)

    print("\n--- For comparison, the 'Guessed' TKML String (manually crafted) ---")
    # This is the string from the immersive artifact "guessed_tkml_for_demo"
    guessed_tkml_string_for_comparison = """Tk {
    title: "TKML Scrollable Demo"
    geometry: "450x400"

    Frame {
        id: "main_container"

        Label {
            text: "My Application Header"
        }

        Scrollable {
            id: "my_scrollable_area"

            Label { text: "Content Label 1 (Inside Scrollable)" }
            Button { text: "Button A" }
            Entry { }
            Label { text: "Content Label 2" }
            Text {
                text: "Multi-line text area.\\nWith a few lines.\\nTo test scrolling."
                config: { height: 5, width: 30 }
            }
            Label { text: "Content Label 3" }
            Button { text: "Button B" }
            Label { text: "Content Label 4" }
            Label { text: "Content Label 5" }
            Entry { }
            Label { text: "Content Label 6" }
            Label { text: "Content Label 7 - More text to ensure scrolling is needed for sure." }
            Button { text: "Button C (Near Bottom)" }
            Label { text: "Content Label 8 (Very Bottom)" }
        }

        Frame {
            id: "footer"

            Label {
                text: "Status: Ready"
            }
            Button {
                text: "Quit"
                command: "quit_app_command"
            }
        }
    }
}"""
    print(guessed_tkml_string_for_comparison)

