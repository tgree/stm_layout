import curses

import tgcurses.ui


class Workspace(tgcurses.ui.Workspace):
    def __init__(self, screen, chip):
        super().__init__(screen)

        self.chip = chip

        # Initialize colors.
        curses.use_default_colors()
        curses.init_pair(1, -1, curses.COLOR_GREEN)

        # Get the longest function names.
        alt_fn_len = 24
        add_fn_len = 24
        name_len   = 15
        label_len  = 1
        for p in chip.pins.values():
            alt_fn_len = max(alt_fn_len, max(len(f) for f in p.alt_fns+['']))
            add_fn_len = max(add_fn_len, max(len(f) for f in p.add_fns+['']))
            name_len   = max(len(p.full_name), name_len)
            label_len  = max(len(p.name) + 1, label_len)
