# data.py - Extracted data and configuration strings for Wisp6

comp_tkml_wisp5 = """
RootApp {
    LeftPanel {
        ScrollableNodeDetailList {}
    }
    RightPanel {
        NodeListScrollable { LeafList {} }
    }
    BottomPanel {
        PrevButton { text: "<< Prev" }
        NextButton { text: "Next >>" }
        CommandEntry {}
        StatusBar { text: "Welcome to Wisp6!" anchor: "w" }
    }
}
"""

style_toml_wisp5 = """
[default.NodeListScrollable]
leaf_width = 15
leaf_side = "left"
indicator_height = 22

[default.LeafList]
default_text_levels = ["T1", "T2"]
default_code_levels = ["C1"]

[default.ScrollableNodeDetailList]
font_family = "Courier New"
font_size = 10
node_separator = "\\n---\\n"

[default.CommandEntry]
placeholder = "Cmd: goto <id> | t1 c123 | default | quit"

[default.StatusBar]
relief = "sunken"
anchor = "w"
height = 1

[default.PrevButton]
[default.NextButton]
"""

nodes_gnml_wisp5 = """
### NODE
--- id: help_node
T1> Welcome to Wisp Navigator! (T1)
T2> This is the interactive help node. (T2)
T2> Available commands:
T2>   goto <node_id>        (e.g., goto node_alpha)
T2>   select <node_id>      (alias for goto)
T2>   t[123|all] c[123|all] (e.g., t13 c2, tall c1)
T2>   t[123|all]            (e.g., t1)
T2>   c[123|all]            (e.g., c23)
T2>   default               (resets verbosity)
T2>   quit or q             (exit the application)
T3> (This is a T3 help line)
C1> print("Accessing help_node information...")
C2> pass
--- next: node_alpha
### ENDNODE

### NODE
--- id: node_alpha
T1> Alpha Node: Primary Information.
T2> Alpha Node: Secondary Details.
T3> Alpha Node: Tertiary/Fine print.
C1> alpha_var = "initialized"
C2> def alpha_main_op():
C2>     print(f"Alpha main operation with {alpha_var}")
C3> def alpha_utility():
C3>     return "Alpha utility done"
--- prev: help_node
--- next: node_beta
### ENDNODE

### NODE
--- id: node_beta
T1> Beta Node: Overview of Beta. (T1)
T2> Beta Node: Specific data points for Beta. (T2)
C1> BETA_CONFIG = {"param1": 10, "param2": "beta_value"}
C2> run_beta_core(BETA_CONFIG)
--- prev: node_alpha
--- next: node_gamma
### ENDNODE

### NODE
--- id: node_gamma
T1> Gamma Node: Summary and conclusions. (T1)
T3> Gamma Node: Detailed references (T3).
C1> print("Gamma entry point executed.")
C3> log_gamma_details("verbose logging data for gamma")
--- prev: node_beta
--- next: node_delta
### ENDNODE

### NODE
--- id: node_delta
T1> Delta Node: Text Level 1 only.
C1> delta_code_l1 = True
C2> delta_code_l2 = "active"
C3> delta_code_l3 = None
--- prev: node_gamma
### ENDNODE
"""
