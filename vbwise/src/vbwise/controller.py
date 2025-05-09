# vbwise/controller.py

import sys
import traceback
from typing import Optional

from vbwise.app_state import AppState # Model

class CommandProcessor:
    """
    Controller component in the MVC architecture.
    Receives command strings, parses them, and interacts with the AppState (Model)
    to effect changes. It does not directly interact with the View.
    """
    def __init__(self, app_state: AppState):
        if not isinstance(app_state, AppState):
            raise TypeError("app_state must be an instance of AppState.")
        self.app_state = app_state

    def execute_command(self, command_string: str) -> tuple[str, str]:
        parts = command_string.strip().split(maxsplit=1)
        status = "error" 
        message = ""

        if not parts:
            status = "ignored"
            message = "Empty command."
            # Notify for feedback, even for ignored commands
            self.app_state._notify_observers(
                event_type="command_executed_feedback",
                command=command_string,
                status=status,
                message=message
            )
            return status, message

        command = parts[0].lower()
        args_string = parts[1] if len(parts) > 1 else ""
        args = args_string.split() 

        try:
            if command == 'goto' and len(args) == 1:
                node_id = args[0]
                if node_id not in self.app_state.all_nodes:
                    raise ValueError(f"Node '{node_id}' not found.")
                
                # If in scrolled_list layout, displayed_leaves usually contains all nodes.
                # If not, goto might imply changing displayed_leaves for other layouts.
                if self.app_state.layout != 'scrolled_list':
                    self.app_state.update_displayed_leaves([node_id])
                # For scrolled_list, we don't change displayed_leaves, just focus.
                # The view will handle scrolling to the focused item.

                self.app_state.focused_leaf_id = node_id 
                self.app_state.clear_selection()
                
                # Optionally clear overrides on goto
                # if self.app_state.leaf_detail_overrides:
                #     self.app_state.leaf_detail_overrides.clear()
                #     self.app_state._notify_observers(event_type="all_leaf_overrides_cleared")

                status = "success"
                message = f"Navigated to node: {node_id}"

            elif command == 'layout' and len(args) == 1:
                layout_type = args[0]
                self.app_state.layout = layout_type # Property setter handles validation & notification
                
                # If switching to scrolled_list and no specific nodes are "displayed"
                # (e.g. coming from a single view), populate with all nodes.
                if layout_type == 'scrolled_list' and not self.app_state.displayed_leaf_ids and self.app_state.all_nodes:
                    self.app_state.update_displayed_leaves(list(self.app_state.all_nodes.keys()))
                elif layout_type == 'scrolled_list' and not self.app_state.all_nodes: # no nodes loaded
                     self.app_state.update_displayed_leaves([])


                status = "success"
                message = f"Layout set to: {layout_type}"

            elif command == 'verbosity' and len(args) == 1:
                level_str = args[0]
                try:
                    level = int(level_str)
                    self.app_state.global_detail_level = level 
                    status = "success"
                    message = f"Global detail level set to: {level}"
                except ValueError:
                    raise ValueError(f"Invalid detail level: '{level_str}'. Must be an integer.")

            elif command == 'select':
                if not args:
                    raise ValueError("Select command requires arguments (e.g., all, none, <node_id>).")
                target = args[0].lower()
                add_to_selection = "--add" in args or "-a" in args

                if target == 'all':
                    self.app_state.select_all_displayed()
                    message = "Selected all displayed leaves."
                elif target == 'none':
                    self.app_state.clear_selection()
                    message = "Cleared selection."
                else: 
                    node_id_to_select = target
                    self.app_state.select_leaf(node_id_to_select, add_to_selection=add_to_selection)
                    action = "Added to" if add_to_selection else "Set"
                    message = f"{action} selection: {node_id_to_select}"
                status = "success"


            elif command == 'set_selected_verbosity' and len(args) == 1:
                level_str = args[0]
                try:
                    level = int(level_str)
                    if not self.app_state.selected_leaf_ids:
                        raise ValueError("No leaves selected to set verbosity.")
                    self.app_state.set_selected_leaves_detail_level(level)
                    status = "success"
                    message = f"Detail level for {len(self.app_state.selected_leaf_ids)} selected leaves set to: {level}"
                except ValueError as e_detail: # Catch specific error from AppState or int conversion
                    raise ValueError(f"Invalid detail level or no selection: {e_detail}")


            elif command == 'follow' and len(args) >= 1:
                link_type = args[0]
                start_node_id_arg = args[1] if len(args) > 1 else None
                self.app_state.start_pathway(link_type, start_node_id_arg) # AppState handles validation
                status = "success"
                current_path_node = self.app_state.active_pathway_current_node_id or "unknown"
                message = f"Started pathway '{link_type}' from '{current_path_node}'."

            elif command in ('next', 'pathway_next'):
                self.app_state.pathway_next() # AppState handles notifications
                status = "success"
                if self.app_state.active_pathway_current_node_id:
                    message = f"Moved to next in pathway: {self.app_state.active_pathway_current_node_id}"
                else: # Pathway might have ended
                    message = "Pathway ended or could not move next."


            elif command in ('prev', 'pathway_previous'):
                self.app_state.pathway_previous() 
                status = "not_implemented" # Assuming AppState notifies this
                message = "Previous pathway navigation not implemented."

            elif command in ('stop', 'pathway_stop'):
                self.app_state.stop_pathway()
                status = "success"
                message = "Pathway navigation stopped."

            elif command in ('quit', 'exit', 'q'):
                status = "quit"
                message = "Application quitting."
                # No AppState change here, MainWindow will handle quit.
                # Still notify for feedback.
                self.app_state._notify_observers(
                    event_type="command_executed_feedback",
                    command=command_string,
                    status=status,
                    message=message
                )
                return status, message 

            else:
                status = "error"
                message = f"Unknown command: '{command}'"

        except (ValueError, TypeError) as e:
            status = "error"
            message = f"Command error: {e}"
        except Exception as e: # Catch any other unexpected errors
            status = "error"
            message = f"Unexpected error processing command: {e}"
            traceback.print_exc(file=sys.stderr)


        self.app_state._notify_observers(
            event_type="command_executed_feedback",
            command=command_string,
            status=status,
            message=message
        )
        return status, message

