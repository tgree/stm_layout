#!/usr/bin/env python3
import argparse
import curses
import curses.ascii
import re

import tgcurses
import tgcurses.ui

from stm_layout import chip_db, chip_stm


# Errors in documentation:
#   UFBGA pin G3 is listed twice
#       - both times as VDD
#       - one time it has a bunch of alt fns that is impossible for a VDD pin

FOCUS_CHIP   = 0
FOCUS_SEARCH = 1
FOCUS_INFO   = 2
FOCUS_ALTFNS = 3
FOCUS_N      = 4
FOCUS        = FOCUS_CHIP
LAST_FOCUS   = FOCUS_CHIP
FOCUS_WIN    = None

REGEX_STR    = ''
REGEX_POS    = 0
REGEX        = None

INFO_POS     = 0
INFO_CHECKS  = 0

ALTFNS_POS   = 0

MODES     = ['GPI', 'GPO', 'Alternate', 'Analog']
SPEEDS    = ['Low', 'Med', 'High', 'Very High']
TYPES     = ['Push-Pull', 'Open-Drain']
RESISTORS = ['None', 'Pull-Up', 'Pull-Down']


def draw_cpu(cpu_win, chip, cursor):
    for x in range(chip.width):
        for y in range(chip.height):
            p = chip.pin_map[x][y]
            if p is None:
                continue

            attr = p._attr
            if p == cursor.pin:
                if FOCUS == FOCUS_CHIP:
                    attr |= curses.A_REVERSE
                else:
                    attr |= curses.A_BOLD
            cpu_win.content.addstr('%-*s' % (cpu_win._label_len - 1, p.name),
                                   pos=(y, x*cpu_win._label_len + 1),
                                   attr=attr)
    cpu_win.content.noutrefresh()


def draw_info(info_win, pin):
    is_f = (FOCUS == FOCUS_INFO)
    info_win.content.erase()
    attr = curses.color_pair(1) if REGEX and REGEX.search(pin.full_name) else 0
    info_win.content.addstr(
        '    Name: %-*s' % (info_win.content.width - 12, pin.full_name),
        pos=(0, 1), attr=attr)
    attr = curses.color_pair(1) if REGEX and REGEX.search(pin.key) else 0
    info_win.content.addstr(
        '     Pos: %-*s' % (info_win.content.width - 12, pin.key),
        pos=(1, 1), attr=attr)
    config = 'Custom' if not pin._default else 'Default'
    attr = curses.color_pair(1) if REGEX and REGEX.search(config) else 0
    info_win.content.addstr(
        '  Config: %-*s' % (info_win.content.width - 12, config),
        pos=(2, 1), attr=attr)
    y = 0
    for c in pin._choices:
        pattr = (curses.color_pair(1)
                 if REGEX and REGEX.search(c.choices[c.val]) else 0)
        info_win.content.addstr('%8s: ' % c.name, pos=(y+3, 1), attr=pattr)
        for i, v in enumerate(c.choices):
            hilite = curses.A_REVERSE if INFO_POS == y and is_f else 0
            attr   = pattr | hilite
            if c.enabled[i]:
                check = ' '
                if i == c.val:
                    check = 'x'
                    attr |= curses.A_BOLD
                info_win.content.addstr('[%c] %s' % (check, v), attr=attr,
                                        pos=(y+3, 12))
            else:
                info_win.content.addstr('    %s' % v, attr=attr, pos=(y+3, 12))
            while info_win.content.getyx()[1] < info_win.content.width - 1:
                info_win.content.addstr(' ', attr=pattr)
            y += 1
    info_win.content.noutrefresh()


def draw_alt_fns(alt_fns_win, alt_fns, pin_altfn):
    is_f = (FOCUS == FOCUS_ALTFNS)
    alt_fns_win.content.erase()
    for i, f in enumerate(alt_fns):
        pattr = (curses.color_pair(1)
                 if (REGEX and ((i == pin_altfn and REGEX.search('x')) or
                                REGEX.search(f)))
                 else 0)
        hilite = curses.A_REVERSE if ALTFNS_POS == i and is_f else 0
        attr   = pattr | hilite
        check  = ' '
        if i == pin_altfn:
            check = 'x'
            attr |= curses.A_BOLD
        alt_fns_win.content.addstr(
            '[%c] %2u: %-*s' % (check, i, alt_fns_win.content.width - 10, f),
            pos=(i, 1), attr=attr)
    alt_fns_win.content.noutrefresh()


def draw_add_fns(add_fns_win, add_fns):
    add_fns_win.content.erase()
    for i, f in enumerate(add_fns):
        attr = curses.color_pair(1) if REGEX and REGEX.search(f) else 0
        add_fns_win.content.addstr('%-*s' % (add_fns_win.content.width - 2, f),
                                   pos=(i, 1), attr=attr)
    add_fns_win.content.noutrefresh()


def draw_search_win(search_win):
    search_win.content.erase()
    search_win.content.addstr(
        '%-*s' % (search_win.content.width - 2, REGEX_STR), pos=(0, 1),
        attr=curses.A_UNDERLINE)
    search_win.content.noutrefresh()


def update_regex(chip, r):
    for p in chip.pins.values():
        if r:
            config = 'Custom' if not p._default else 'Default'
            match  = r.search(p.full_name)
            match  = match or r.search(config)
            match  = match or r.search(p.key)
            match  = match or any(r.search(f) for f in p.alt_fns)
            match  = match or any(r.search(f) for f in p.add_fns)
            match  = match or (p._altfn is not None and r.search('x'))
            for c in p._choices:
                match = match or r.search(c.choices[c.val])
        else:
            match = False
        if match:
            p._attr |= curses.color_pair(1)
        else:
            p._attr &= ~curses.color_pair(1)


def update_ui(cpu_win, info_win, alt_fns_win, add_fns_win, search_win, chip,
              cursor):
    update_regex(chip, REGEX)
    draw_cpu(cpu_win, chip, cursor)
    draw_info(info_win, cursor.pin)
    draw_alt_fns(alt_fns_win, cursor.pin.alt_fns or [], cursor.pin._altfn)
    draw_add_fns(add_fns_win, cursor.pin.add_fns or [])
    draw_search_win(search_win)

    if FOCUS == FOCUS_SEARCH:
        tgcurses.ui.curs_set(1)
        search_win.content.move(0, 1 + REGEX_POS)
        search_win.content.noutrefresh()
    else:
        tgcurses.ui.curs_set(0)


def set_focus(focus, cpu_win, info_win, alt_fns_win, add_fns_win, search_win,
              chip, cursor):
    global FOCUS
    global FOCUS_WIN
    global LAST_FOCUS

    LAST_FOCUS = FOCUS
    FOCUS      = focus
    if FOCUS == FOCUS_CHIP:
        FOCUS_WIN = cpu_win
    elif FOCUS == FOCUS_SEARCH:
        FOCUS_WIN = search_win
    elif FOCUS == FOCUS_INFO:
        FOCUS_WIN = info_win
    elif FOCUS == FOCUS_ALTFNS:
        FOCUS_WIN = alt_fns_win

    update_ui(cpu_win, info_win, alt_fns_win, add_fns_win, search_win, chip,
              cursor)


def main(screen, chip):
    global REGEX
    global REGEX_STR
    global REGEX_POS
    global ALTFNS_POS
    global INFO_POS
    global FOCUS_WIN

    # Get the geometry.
    w, h = chip.width, chip.height

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
        p._attr    = 0

    # Initialize colors.
    curses.use_default_colors()
    curses.init_pair(1, -1, curses.COLOR_GREEN)

    # Create a workspace.
    ws = tgcurses.ui.Workspace(screen)

    # Add a CPU window.
    cpu_win            = ws.make_edge_window(chip.name, w=label_len*w+3, h=h+2)
    cpu_win._label_len = label_len
    cursor             = chip.cursor()
    cpu_win.content.timeout(100)
    cpu_win.content.keypad(1)
    FOCUS_WIN = cpu_win

    # Add a search window.
    search_win = ws.make_anchored_window(
        'Regex',
        left_anchor=cpu_win.frame.left_anchor(),
        top_anchor=cpu_win.frame.bottom_anchor(),
        right_anchor=cpu_win.frame.right_anchor(),
        h=3)
    search_win.content.timeout(100)
    search_win.content.keypad(1)

    # Add an info window.
    info_win = ws.make_anchored_window(
        'Pin Info',
        left_anchor=ws.canvas.frame.left_anchor(),
        top_anchor=search_win.frame.bottom_anchor(),
        w=14+name_len, h=18)

    # Add an alternate functions window.
    alt_fns_win = ws.make_anchored_window(
        'Alternate Functions',
        left_anchor=info_win.frame.right_anchor(),
        top_anchor=search_win.frame.bottom_anchor(),
        w=alt_fn_len+12, h=18)

    # Add an additional functions window.
    add_fns_win = ws.make_anchored_window(
        'Additional Functions',
        left_anchor=alt_fns_win.frame.right_anchor(),
        top_anchor=search_win.frame.bottom_anchor(),
        bottom_anchor=alt_fns_win.frame.bottom_anchor(),
        w=add_fn_len+4)

    # Handle user input.
    update_ui(cpu_win, info_win, alt_fns_win, add_fns_win, search_win, chip,
              cursor)
    tgcurses.ui.curs_set(0)
    while True:
        tgcurses.ui.doupdate()
        c = cpu_win.content.getch()
        if c == -1:
            continue

        if FOCUS != FOCUS_SEARCH and c == ord('q'):
            break

        if FOCUS != FOCUS_SEARCH and c == ord('/'):
            set_focus(FOCUS_SEARCH, cpu_win, info_win, alt_fns_win,
                      add_fns_win, search_win, chip, cursor)
        elif FOCUS != FOCUS_SEARCH and c == ord('w'):
            s = chip.serialize_settings()
            with open('/tmp/stm32_pinout.txt', 'w') as f:
                f.write(s)
        elif FOCUS != FOCUS_SEARCH and c == ord('r'):
            cursor.pin._reset()
        elif c == ord('\t'):
            set_focus((FOCUS + 1) % FOCUS_N, cpu_win, info_win, alt_fns_win,
                      add_fns_win, search_win, chip, cursor)
            if FOCUS == FOCUS_INFO and cursor.pin._nchoices == 0:
                set_focus((FOCUS + 1) % FOCUS_N, cpu_win, info_win, alt_fns_win,
                          add_fns_win, search_win, chip, cursor)
            if FOCUS == FOCUS_ALTFNS and not cursor.pin.alt_fns:
                set_focus((FOCUS + 1) % FOCUS_N, cpu_win, info_win, alt_fns_win,
                          add_fns_win, search_win, chip, cursor)
        elif c == curses.KEY_BTAB:
            set_focus((FOCUS - 1) % FOCUS_N, cpu_win, info_win, alt_fns_win,
                      add_fns_win, search_win, chip, cursor)
            if FOCUS == FOCUS_ALTFNS and not cursor.pin.alt_fns:
                set_focus((FOCUS - 1) % FOCUS_N, cpu_win, info_win, alt_fns_win,
                          add_fns_win, search_win, chip, cursor)
            if FOCUS == FOCUS_INFO and cursor.pin._nchoices == 0:
                set_focus((FOCUS - 1) % FOCUS_N, cpu_win, info_win, alt_fns_win,
                          add_fns_win, search_win, chip, cursor)
        elif FOCUS == FOCUS_CHIP:
            if c in (ord('j'), curses.KEY_DOWN):
                cursor.down()
            elif c in (ord('k'), curses.KEY_UP):
                cursor.up()
            elif c in (ord('l'), curses.KEY_RIGHT):
                cursor.right()
            elif c in (ord('h'), curses.KEY_LEFT):
                cursor.left()
        elif FOCUS == FOCUS_SEARCH:
            if c in (curses.KEY_BACKSPACE, curses.ascii.BS, curses.ascii.DEL):
                if REGEX_POS:
                    REGEX_STR  = (REGEX_STR[:REGEX_POS - 1] +
                                  REGEX_STR[REGEX_POS:])
                    REGEX_POS -= 1
                    try:
                        REGEX = re.compile(REGEX_STR) if REGEX_STR else None
                    except Exception:
                        REGEX = None
            elif c == curses.KEY_LEFT:
                REGEX_POS = max(REGEX_POS - 1, 0)
            elif c == curses.KEY_RIGHT:
                REGEX_POS = min(REGEX_POS + 1, len(REGEX_STR))
            elif c in (ord('\n'), ord(' '), curses.KEY_ENTER):
                set_focus(LAST_FOCUS, cpu_win, info_win, alt_fns_win,
                          add_fns_win, search_win, chip, cursor)
            elif curses.ascii.isprint(c):
                if len(REGEX_STR) < search_win.content.width - 10:
                    REGEX_STR  = (REGEX_STR[:REGEX_POS] + chr(c) +
                                  REGEX_STR[REGEX_POS:])
                    REGEX_POS += 1
                    try:
                        REGEX = re.compile(REGEX_STR)
                    except Exception:
                        REGEX = None
        elif FOCUS == FOCUS_INFO:
            if c in (ord('j'), curses.KEY_DOWN):
                INFO_POS = min(INFO_POS + 1, cursor.pin._nchoices - 1)
            elif c in (ord('k'), curses.KEY_UP):
                INFO_POS = max(INFO_POS - 1, 0)
            elif c in (ord('x'), ord('\n'), ord(' '), curses.KEY_ENTER):
                cursor.pin._set_choice(INFO_POS)
        elif FOCUS == FOCUS_ALTFNS:
            if c in (ord('j'), curses.KEY_DOWN):
                ALTFNS_POS = min(ALTFNS_POS + 1, 15)
            elif c in (ord('k'), curses.KEY_UP):
                ALTFNS_POS = max(ALTFNS_POS - 1, 0)
            elif c in (ord('x'), ord('\n'), ord(' '), curses.KEY_ENTER):
                cursor.pin._toggle_altfn(ALTFNS_POS)

        update_ui(cpu_win, info_win, alt_fns_win, add_fns_win, search_win, chip,
                  cursor)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chip', '-c', required=True)
    rv = parser.parse_args()

    parts = chip_db.find(rv.chip)
    if len(parts) > 1:
        for p in parts:
            print('%s - %s' % (p, chip_db.package(p)))
    else:
        chip = chip_stm.make_chip(parts[0])
        tgcurses.wrapper(main, chip)


if __name__ == '__main__':
    _main()
