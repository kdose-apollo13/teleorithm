# Dummy vbwise/data/initial_content.py
INITIAL_NODES_SOURCE = """
### NODE: help_commands
# Available Commands
TXT> goto <node_id>         - Display a specific node.
TXT> layout <type>          - Change view (single, split_v_2, split_h_2, scrolled_list).
TXT> verbosity <level>      - Set global detail level (0-3).
TXT> select <id|all|none>   - Select node(s). Use --add to append.
TXT> set_selected_verbosity <level> - Set detail for selected nodes.
TXT> follow <link_type> [id] - Start pathway navigation.
TXT> next                   - Go to next node in pathway.
TXT> stop                   - Stop pathway navigation.
TXT> quit                   - Exit the application.
### ENDNODE

"""
