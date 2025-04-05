"""
attributed to:
JamesTheAwesomeDude
user:1874170
https://stackoverflow.com/a/78915021
"""

#!/usr/bin/env python3
# -*- filename: tkinter_iss47655_polyfill.py -*-

__all__ = ['check_for_bug', 'patch_bug', 'auto_patch_bug']

import logging
import os
import platform
import sys
import threading
import tkinter

FIXED_IN_CPYTHON_VERSION = (4,)  # FIXME update this when they actually fix it

# https://tkdocs.com/tutorial/eventloop.html
# "If you need to communicate from another thread to the thread running
# Tkinter, keep it as simple as possible. Use event_generate to post a
# virtual event to the Tkinter event queue, and then bind to that event
# in your code."


def auto_patch_bug(module=tkinter):
    # NOTE: check_for_bug and auto_patch_bug MUST be called from the
    # main thread because the tkinter module refuses to allow mainloop
    # on another thread.
    if platform.python_implementation() == 'CPython':
        if sys.version_info >= FIXED_IN_CPYTHON_VERSION:
            logging.debug("No need to polyfill tkinter issue 47655 on this Python runtime.")
        elif sys.version_info >= (3, 8):  # FIXME figure out what the actual lower bound this changeset applies seamlessly on is
            try:
                needs_patch = check_for_bug(module)
            except Exception:
                raise Exception("internal error checking for bug")
            if needs_patch:
                patch_bug(module)
                assert not check_for_bug(module), "Patch failed to apply!"
            else:
                logging.debug("No need to polyfill tkinter issue 47655 on this Python runtime.")
        else:
            raise Exception(f"patch not available on old CPython version {platform.python_version()}")
    else:
        # FIXME support other Python implementations
        raise Exception(f"patch not available yet on {platform.python_implementation()}")


def check_for_bug(module=tkinter):
    data = os.urandom(12).hex()  # NOTE: the associated data is coerced to str!
    root = module.Tk()
    root.withdraw()
    result = None
    def handle_ev(event):
        if hasattr(event, 'user_data'):
            nonlocal result
            result = event.user_data
        event.widget.quit()
    root.bind('<<test>>', handle_ev)
    t = threading.Thread(target=root.event_generate, args=('<<test>>',), kwargs={'data': data})
    t.start()
    root.mainloop()
    if result is None:
        # event never arrived, or was missing the .user_data property
        return True
    else:
        if result != data:
            # event arrived, had the .user_data property, but that property had an unexpected value
            raise RuntimeError(f"Could not validate presence of CPython Bug #47655; unexpected data arrived. (Expected {data}, got {result})")
        # event arrived, had the .user_data property, and that data was valid
        return False


def patch_bug(module=tkinter):
    def _substitute(self, *args):
        """https://github.com/python/cpython/pull/7142"""
        if len(args) != len(self._subst_format): return args
        getboolean = self.tk.getboolean

        getint = self.tk.getint
        def getint_event(s):
            """Tk changed behavior in 8.4.2, returning "??" rather more often."""
            try:
                return getint(s)
            except (ValueError, module.TclError):
                return s

        nsign, b, d, f, h, k, s, t, w, x, y, A, E, K, N, W, T, X, Y, D = args
        # Missing: (a, c, m, o, v, B, R)
        e = module.Event()
        # serial field: valid for all events
        # number of button: ButtonPress and ButtonRelease events only
        # detail: for Enter, Leave, FocusIn, FocusOut and ConfigureRequest
        # events certain fixed strings (see tcl/tk documentation)
        # user_data: data string from a virtual event or an empty string
        # height field: Configure, ConfigureRequest, Create,
        # ResizeRequest, and Expose events only
        # keycode field: KeyPress and KeyRelease events only
        # time field: "valid for events that contain a time field"
        # width field: Configure, ConfigureRequest, Create, ResizeRequest,
        # and Expose events only
        # x field: "valid for events that contain an x field"
        # y field: "valid for events that contain a y field"
        # keysym as decimal: KeyPress and KeyRelease events only
        # x_root, y_root fields: ButtonPress, ButtonRelease, KeyPress,
        # KeyRelease, and Motion events
        e.serial = getint(nsign)
        e.num = getint_event(b)
        e.user_data = d
        e.detail = d
        try: e.focus = getboolean(f)
        except module.TclError: pass
        e.height = getint_event(h)
        e.keycode = getint_event(k)
        e.state = getint_event(s)
        e.time = getint_event(t)
        e.width = getint_event(w)
        e.x = getint_event(x)
        e.y = getint_event(y)
        e.char = A
        try: e.send_event = getboolean(E)
        except module.TclError: pass
        e.keysym = K
        e.keysym_num = getint_event(N)
        try:
            e.type = module.EventType(T)
        except ValueError:
            e.type = T
        try:
            e.widget = self._nametowidget(W)
        except KeyError:
            e.widget = W
        e.x_root = getint_event(X)
        e.y_root = getint_event(Y)
        try:
            e.delta = getint(D)
        except (ValueError, module.TclError):
            e.delta = 0
        return (e,)

    _subst_format = ('%#', '%b', '%d', '%f', '%h', '%k',
             '%s', '%t', '%w', '%x', '%y',
             '%A', '%E', '%K', '%N', '%W', '%T', '%X', '%Y', '%D')

    _subst_format_str = " ".join(_subst_format)

    # FIXME this seems less elegant than just assigning module.Misc,
    # but I can't figure out how to make such an assignment propagate
    # "retroactively" to all the subclasses like Tk and the widgets
    module.Misc._substitute = _substitute
    module.Misc._subst_format = _subst_format
    module.Misc._subst_format_str = _subst_format_str
    logging.debug(f"Patched {module.__name__}.Misc to fix CPython Bug #47655.")


if __name__ == '__main__':
    auto_patch_bug()
