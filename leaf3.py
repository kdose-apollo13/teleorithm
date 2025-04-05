"""
    leaf widget

    ------------------------------------------------------
    |h | prompt | text                                   |
    |i |        |                                        |
    |l |        |                                        |
    |i |        |                                        |
    ------------------------------------------------------

"""
from configparser import ConfigParser
from tkinter import *
from tkinter.font import nametofont


class Leaf(Canvas):
    
    defaults = {
        'leaf': {
            'background_color': '#111177',
        },
        'leaf.hili': {
            'background_color': '#333333',
            'width': '9',
        },
        'leaf.prompt': {
            'background_color': '#117711',
            'font_style': 'fixed',
            'font_size': '14',
            'text': '>>> ',  # -> doesn't map to canvas 
            'foreground_color': '#CCCCCC',  # -> doesn't map to canvas 
        },
        'leaf.text': {
            'background_color': '#111111',
            'foreground_color': '#CCCCCC',
            'selected_background': '#777777',
            'selected_foreground': '#111111',
            'cursor_color': '#999999',
            'cursor_is_square': 'true',
            'wrap': 'none',
            'font_style': 'fixed',
            'font_size': '14',
        }
    }

    # c = ConfigParser()
    # for k in defaults:
        # c[k] = defaults[k]
    # with open('settings.ini', 'wt') as w:
        # c.write(w)

    def __init__(self, *args, options=None, **kwargs):
        """
            options: 
        """
        super().__init__(*args, **kwargs)

        font = nametofont('TkFixedFont')
        font.config(size=14)
        self.font = font
        
        # self.is_resizing = False
        self.is_redrawing = False
        self.visible_line_qty = 1
        
        # THE WIDGET -------------------
        # self = Canvas
        self.hili = Canvas(self)
        self.prompt = Canvas(self)
        self.text = Text(self) 
        # ------------------------------
        # print(self.options_are_ok(self.defaults))

        if options and self.options_are_ok(options):
            self.O = dict(options)
        else:
            self.O = self.defaults

        w_hili = self._width_of_hili()
        w_prompt = self._width_of_prompt()  # assume dynamic prompt

        self.create_window(
            0, 0, anchor='nw', window=self.hili
        )
        self.create_window(
            w_hili, 0, anchor='nw', window=self.prompt
        )
        self.create_window(
            w_hili + w_prompt, 0, anchor='nw', window=self.text
        )

        self._apply_config_options()

        self.__tab_ref = self.text.bind('<Tab>', self._handle_tab)

        self.redraw(800, 600)

    def redraw(self, width, height):
        if not self.is_redrawing:
            # ignore <Configure> events raised on parent by .config()
            self.is_redrawing = True
            
            self.config(width=width)

            # delete old prompt text
            # if hasattr(self, '__prompt_text_i'):
                # self.prompt.delete(self.__prompt_text_i)
            
            self.__prompt_text_i = self.prompt.create_text(
                0, 0, anchor='nw', 
                font=self.font,
                fill='#00FFFF',  # TODO: put in options
                text=self.O['leaf.prompt']['text']
            )
            char_width = self.font.measure(' ')
            w_hili = self._width_of_hili()
            w_prompt = self._width_of_prompt()
            char_qty = (width - w_hili - w_prompt) // char_width
            char_qty -= 1
            self.text.config(width=char_qty, height=self.visible_line_qty)

            self.is_redrawing = False

    def _width_of_hili(self):
        return int(self.O['leaf.hili']['width'])

    def _width_of_prompt(self):
        text = self.O['leaf.prompt']['text']
        text_width_px = self.font.measure(text)
        return text_width_px

    def options_are_ok(self, options):
        """
            checks key structure, any order ok    
        """
        match options:
            case {
                'leaf': {
                    'background_color': _,
                },
                'leaf.hili': {
                    'background_color': _,
                    'width': _,
                },
                'leaf.prompt': {
                    'background_color': _,
                    'foreground_color': _,
                    'text': _,
                    'font_style': _,
                    'font_size': _,
                },
                'leaf.text': {
                    'background_color': _,
                    'foreground_color': _,
                    'selected_background': _,
                    'selected_foreground': _,
                    'cursor_color': _,
                    'cursor_is_square': _,
                    'wrap': _,
                    'font_style': _,
                    'font_size': _,
                }
            }: 
                return True
            case _:
                return False

    def _apply_config_options(self):
        """
            apply tk widget config options
        """
        o_leaf = {
            'background': self.O['leaf']['background_color'],
            'highlightthickness': 0,
            'borderwidth': 0,
        }
        o_hili = {
            'background': self.O['leaf.hili']['background_color'],
            'width': self.O['leaf.hili']['width'],
            'highlightthickness': 0,
            'borderwidth': 0,
        }
        o_prompt = {
            'background': self.O['leaf.prompt']['background_color'],
            'highlightthickness': 0,
            'borderwidth': 0,
        }
        o_text = {
            'background': self.O['leaf.text']['background_color'],
            'foreground': self.O['leaf.text']['foreground_color'],
            'selectbackground': self.O['leaf.text']['selected_background'],
            'selectforeground': self.O['leaf.text']['selected_foreground'],
            'insertbackground': self.O['leaf.text']['cursor_color'],
            'blockcursor': self.O['leaf.text']['cursor_is_square'],
            'wrap': self.O['leaf.text']['wrap'],
            'insertofftime': 0,  # 0 -> solid cursor, do not blink
            'insertunfocussed': 'none',  # no focus -> no cursor
            'highlightthickness': 0,
            'borderwidth': 0,
        }

        self.config(o_leaf)
        self.hili.config(o_hili)
        self.prompt.config(o_prompt)
        self.text.config(o_text)

    def set_hili_color(self, color):
        """
            color: str like '#2323EE'
        """
        self.hl.config({'background': color})


    def _handle_tab(self, event):
        """
            <Tab> inserts spaces up to next multiple of 4

            event: tkinter.Event
        """
        lc = self.text.index('insert')  # line.column

        c = int(lc.split('.')[1])
        spaces_required = ((c // 4) + 1) * 4 - c

        self.text.insert(lc, ' ' * spaces_required)

        # prevent normal tab handling
        return 'break'

    def set_syntax(self, colormap, text_to_tagspans):
        """
            colormap
                : dict[str, str]
                : {'comment': '#232323', ...}

            text_to_tagspans
                : callable[str] -> [('comment', '1.0', '1.13'), ...]
                : return list of tag names each with corresponding tk indices
                : invoked on KeyRelease
        """
        for name, color in colormap.items():
            self.text.tag_config(name, foreground=color)

        self.colormap = colormap
        self.text_to_tagspans = text_to_tagspans
                
        self.__key_release_ref = self.text.bind(
            '<KeyRelease>', self._handle_key_release
        )

    def clear_syntax(self):
        """
            remove all previously added syntax stuff
        """
        self.text.unbind('<KeyRelease>', self.__key_release_ref)
        self.colormap = None
        self.text_to_tagspans = None
        self._clear_tags()
        # TODO: what about undo tag_config?
        # self.text.tag_delete(*colormap.values())

    def _handle_key_release(self, event):
        """
            event: tkinter.Event
        """
        text = self.text.get('1.0', 'end')
        tagspans = self.text_to_tagspans(text)

        self._clear_tags()

        for name, start, end in tagspans:
            self.text.tag_add(name, start, end)

    def _clear_tags(self):
        for name in self.colormap:
            self.text.tag_remove(name, '1.0', 'end')


if __name__ == '__main__':
    r = Tk()
    l = Leaf(r)
    l.grid(row=0, column=0)
    r.mainloop()
