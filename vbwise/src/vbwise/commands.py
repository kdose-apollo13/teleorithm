# commands.py - Command Pattern Implementation

import re

class Command:
    def execute(self, app_state, app_ui, args_str):
        raise NotImplementedError

class GotoCommand(Command):
    def execute(self, app_state, app_ui, args_str):
        if args_str:
            app_state.select_node_by_id(args_str)
        else:
            app_state.update_status("Goto command requires a node ID.", "error")

class SetVerbosityCommand(Command):
    def execute(self, app_state, app_ui, args_str):
        if args_str.lower() == "default":
            app_state.update_verbosity(reset_to_default=True)
        else:
            text_match = re.search(r't([1-3]+|all)\b', args_str, re.IGNORECASE)
            code_match = re.search(r'c([1-3]+|all)\b', args_str, re.IGNORECASE)
            text_flags = text_match.group(1) if text_match else None
            code_flags = code_match.group(1) if code_match else None

            if not text_flags and not code_flags:
                app_state.update_status(f"Invalid verbosity command: '{args_str}'. Use t/c flags or 'default'.", "error")
                return
            app_state.update_verbosity(text_flags_str=text_flags, code_flags_str=code_flags)
