# vbwise/gui/leaf_widget.py

import tkinter as tk
import tkinter.scrolledtext as scrolledtext
# from tkinter.font import Font # Not explicitly used
import re
import sys

from vbwise.node import Node
from vbwise.app_state import AppState

# --- Theme/Color Definitions ---
DARK_BG_DEFAULT = '#2b2b2b'
DARK_FG_DEFAULT = '#a9b7c6'
DARK_BG_FOCUSED = '#3c3f41'
DARK_BG_SELECTED = '#614b4b'
DARK_BORDER_COLOR = '#616161' # Used for default highlight if any
FOCUS_HIGHLIGHT_COLOR = '#78C7F0' # A distinct color for focus highlight border
SELECTION_HIGHLIGHT_COLOR = '#C778F0' # A distinct color for selection highlight border

COLOR_TXT = DARK_FG_DEFAULT
COLOR_L1 = '#6a8759'
COLOR_L2 = '#cc7832'
COLOR_L3 = '#a9b7c6'
COLOR_CODE_KEYWORD = '#cc7832'
COLOR_CODE_STRING = '#6a8759'
COLOR_CODE_COMMENT = '#808080'

SYNTAX_PATTERNS = [
    (re.compile(r'\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b'), 'code_keyword'),
    (re.compile(r'".*?"|\'.*?\''), 'code_string'),
    (re.compile(r'#.*$'), 'code_comment'),
]

class LeafWidget(tk.Frame):
    """
    Displays a single Node, reacting to AppState changes for content and visuals.
    """
    def __init__(self, parent: tk.Widget, app_state: AppState, node_id: str, **kwargs):
        super().__init__(parent, bd=0, relief=tk.FLAT, bg=DARK_BG_DEFAULT, **kwargs) # bd=0 on frame itself

        if not isinstance(app_state, AppState):
            raise TypeError("app_state must be an instance of AppState.")
        self.app_state = app_state
        self.node_id = node_id

        # Configure overall frame border/highlight properties (will be changed by set_focused/selected)
        self.config(highlightthickness=2, highlightbackground=DARK_BORDER_COLOR, relief=tk.SOLID)


        self.header_label = tk.Label(
            self, anchor=tk.W, font=('TkDefaultFont', 10, 'bold'),
            bg=DARK_BG_DEFAULT, fg=DARK_FG_DEFAULT
        )
        self.header_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(2,0))

        self.content_display = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, state=tk.DISABLED, font=('TkDefaultFont', 9),
            bg=DARK_BG_DEFAULT, fg=DARK_FG_DEFAULT,
            insertbackground=DARK_FG_DEFAULT,
            relief=tk.FLAT, bd=0 
        )
        self.content_display.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Explicitly set the background of the internal Text widget
        # This can sometimes be necessary if the ScrolledText wrapper doesn't fully propagate bg
        try:
            self.content_display.text.config(bg=DARK_BG_DEFAULT)
        except AttributeError: # Should not happen with standard ScrolledText
            pass


        self._define_text_tags()

        self._is_focused = False
        self._is_selected = False

        self.bind("<Button-1>", self._on_click)
        self.header_label.bind("<Button-1>", self._on_click)
        self.content_display.bind("<Button-1>", self._on_click)
        if hasattr(self.content_display, 'vbar'):
            self.content_display.vbar.bind("<Button-1>", self._on_click)

        self._apply_visual_style() # Apply initial style

    def _define_text_tags(self) -> None:
        text_widget = self.content_display
        text_widget.tag_configure('txt', foreground=COLOR_TXT)
        text_widget.tag_configure('level', font=('TkDefaultFont', 9, 'italic'))
        text_widget.tag_configure('l1', foreground=COLOR_L1)
        text_widget.tag_configure('l2', foreground=COLOR_L2)
        text_widget.tag_configure('l3', foreground=COLOR_L3)
        text_widget.tag_configure('code', font=('Courier New', 9)) # BG handled by widget
        text_widget.tag_configure('code_keyword', foreground=COLOR_CODE_KEYWORD)
        text_widget.tag_configure('code_string', foreground=COLOR_CODE_STRING)
        text_widget.tag_configure('code_comment', foreground=COLOR_CODE_COMMENT, font=('Courier New', 9, 'italic'))

    def _on_click(self, event: tk.Event) -> None:
        if self.app_state.focused_leaf_id != self.node_id:
            self.app_state.focused_leaf_id = self.node_id

    def update_display(self) -> None:
        node = self.app_state.get_node_by_id(self.node_id)
        if not node:
            self.header_label.config(text=f"Error: Node '{self.node_id}' not found", bg='red', fg='white')
            self.content_display.config(state=tk.NORMAL)
            self.content_display.delete(1.0, tk.END)
            self.content_display.insert(tk.END, "Node data could not be loaded.", 'txt')
            self.content_display.config(state=tk.DISABLED)
            return

        effective_detail = self.app_state.get_effective_detail_level(self.node_id)
        header_text = node.id
        if node.title:
            header_text += f" - {node.title}"
        if self.node_id in self.app_state.leaf_detail_overrides:
            header_text += f" (Detail Override: {self.app_state.leaf_detail_overrides[self.node_id]})"
        self.header_label.config(text=header_text)

        self.content_display.config(state=tk.NORMAL)
        self.content_display.delete(1.0, tk.END)
        for prefix, line_text in node.content_lines:
            display_line = False
            if prefix == 'TXT': display_line = True
            elif prefix == 'CODE':
                if effective_detail >= 2: display_line = True
            elif prefix.startswith('L'):
                try:
                    if effective_detail >= int(prefix[1:]): display_line = True
                except ValueError: pass
            if display_line:
                tags = (prefix.lower(),) + (('level',) if prefix.startswith('L') else ())
                self.content_display.insert(tk.END, line_text + "\n", tags)
                if prefix == 'CODE':
                    self._apply_syntax_highlighting_to_last_line(line_text)
        self.content_display.config(state=tk.DISABLED)
        
        # After content update, ensure the background of text area is correct
        # based on current focus/selection state (which _apply_visual_style reads)
        self._apply_visual_style()


    def _apply_syntax_highlighting_to_last_line(self, line_text: str) -> None:
        text_widget = self.content_display
        line_start_index = text_widget.index("end-1c linestart")
        for pattern, tag_name in SYNTAX_PATTERNS:
            for match in pattern.finditer(line_text):
                start, end = match.span()
                widget_match_start = f"{line_start_index}+{start}c"
                widget_match_end = f"{line_start_index}+{end}c"
                text_widget.tag_add(tag_name, widget_match_start, widget_match_end)

    def _apply_visual_style(self) -> None:
        """Applies background and border styles based on focus and selection state."""
        bg_color = DARK_BG_DEFAULT
        highlight_color = DARK_BORDER_COLOR # Default highlight border color
        # relief_style = tk.SOLID # Default relief for the main frame border
        
        # The main frame itself will have a highlightthickness of 2 (set in __init__)
        # We just change its highlightbackground color.
        # The bd=0 and relief=tk.FLAT on the Frame itself means its own border is not visible,
        # only the highlight border.

        if self._is_focused:
            bg_color = DARK_BG_FOCUSED
            highlight_color = FOCUS_HIGHLIGHT_COLOR
        elif self._is_selected:
            bg_color = DARK_BG_SELECTED
            highlight_color = SELECTION_HIGHLIGHT_COLOR
        
        # Apply to the main LeafWidget Frame
        self.config(bg=bg_color, highlightbackground=highlight_color) # Frame bg, and its highlight border color

        # Apply to children
        self.header_label.config(bg=bg_color)
        self.content_display.config(bg=bg_color)
        try: # Explicitly set bg for the internal Text widget of ScrolledText
            self.content_display.text.config(bg=bg_color)
        except AttributeError:
            pass # Should not happen with standard ScrolledText

    def set_focused(self, is_focused: bool) -> None:
        if self._is_focused == is_focused:
            return
        self._is_focused = is_focused
        self._apply_visual_style()

    def set_selected(self, is_selected: bool) -> None:
        if self._is_selected == is_selected:
            return
        self._is_selected = is_selected
        self._apply_visual_style()


