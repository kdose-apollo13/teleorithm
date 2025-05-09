# vbwise/data/initial_content.py

# This string should be in the format expected by vbwise.gramjam.NodeGrammar
INITIAL_NODES_SOURCE = """
### NODE
--- id: help_commands
--- meta: version=10, author=VibewiseSystem
--- tags: help, system, commands
--- next: example_node_1
T1> Welcome to Vibewise! Here are some commands you can use:
T1> 
T1> Navigation & Display:
T1>   goto <node_id>         - Focuses and displays the specified node.
T1>                            In 'scrolled_list' layout, scrolls to it.
T1>   layout <type>          - Change view layout.
T1>                            Types: single, split_v_2, split_h_2, scrolled_list.
T1>   verbosity <level>      - Set global detail level for node content (e.g., 0, 1, 2, 3).
T1>                            Higher numbers show more detail (L1, L2, L3, CODE).
T1> 
T1> Selection & Detail Overrides:
T1>   select <node_id|all|none> [--add | -a]
T1>                            - Selects one or more nodes. 'all' selects all currently
T1>                              displayed in 'scrolled_list', or visible in other layouts.
T1>                            - Use --add or -a to add to the current selection.
T1>   set_selected_verbosity <level>
T1>                            - Overrides the detail level for all selected nodes.
T1> 
T1> Pathway Navigation:
T1>   follow <link_type> [start_node_id]
T1>                            - Start navigating a pathway. <link_type> is usually 'next' or 'prev'.
T1>                            - If [start_node_id] is omitted, uses the currently focused node.
T1>   next                   - Moves to the next node in the active pathway (if a 'next' link exists).
T1>   prev                   - Moves to the previous node (if a 'prev' link exists and pathway supports it).
T1>   stop                   - Stops the current pathway navigation mode.
T1> 
T1> Application:
T1>   quit / exit / q        - Exits Vibewise.
T1>
C1> # Example of a code block within a node:
C1> def greet(name):
C1>     print(f"Hello, {name}!")
C2> # Code blocks can also have different detail levels (C1, C2, C3)
C2> # This C2 line would only show if global or node verbosity is 2 or higher.
### ENDNODE

### NODE
--- id: example_node_1
--- tags: example, content
--- prev: help_commands
--- next: example_node_2
T1> This is the first example node. It demonstrates basic content.
T2> This line (T2) requires verbosity 2 or higher to be visible.
T3> This line (T3) requires verbosity 3 or higher.
C1> print("Code from example_node_1")
### ENDNODE

### NODE
--- id: example_node_2
--- meta: status= wip, priority=medium
--- tags: example, advanced
--- prev: example_node_1
T1> This node shows more features, like metadata and multiple tags.
T1> It is linked from 'example_node_1' via a 'next' link,
T1> and links back via a 'prev' link.
C2> # A code block at C2 detail level
C2> data = {"key": "value", "count": 42}
C2> for k, v in data.items():
C2>     print(f"{k} = {v}")
### ENDNODE

### NODE
--- id: error_loading_fallback
T1> If you see this, it means the primary INITIAL_NODES_SOURCE
T1> from 'vbwise.data.initial_content' could not be loaded by main_window.py.
T1> This is a fallback defined directly in main_window.py.
T1> Please ensure 'vbwise/data/initial_content.py' exists and is correct.
### ENDNODE

"""

if __name__ == '__main__':
    parsed_nodes = parse_source_string_to_nodes(INITIAL_NODES_SOURCE )
    assert isinstance(parsed_nodes, dict)
    print(parsed_nodes)
    
