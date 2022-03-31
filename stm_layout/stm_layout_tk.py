#!/usr/bin/env python3
import argparse
import sys

from stm_layout import chip_db, chip_stm, chip_package
import stm_layout.tk


stm_layout.tk.xplat.register(
    windows={
        'LABEL_FONT'        : ('Courier New', 10),
        'INFO_FONT'         : ('Courier New', 10),
        'PIN_FONT'          : ('Courier New', 9),
        'EDGE_PIN_H_KEY_DX' : 0,
        'EDGE_PIN_H_KEY_DY' : 1,
        'EDGE_PIN_V_KEY_DX' : 1,
        'BGA_PIN_NAME_DY'   : 1,
        'BGA_PIN_KEY_DX'    : 0,
        'BGA_PIN_KEY_DY'    : 1,
    },
    darwin={
        'LABEL_FONT'        : ('Monaco', 10),
        'INFO_FONT'         : ('Monaco', 10),
        'PIN_FONT'          : ('Monaco', 9),
        'EDGE_PIN_H_KEY_DX' : 1,
        'EDGE_PIN_H_KEY_DY' : 0,
        'EDGE_PIN_V_KEY_DX' : 0,
        'BGA_PIN_NAME_DY'   : 0,
        'BGA_PIN_KEY_DX'    : 1,
        'BGA_PIN_KEY_DY'    : 0,
    },
    linux={
        # TBD.
        'LABEL_FONT'        : ('Courier', 10),
        'INFO_FONT'         : ('Courier', 10),
        'PIN_FONT'          : ('Courier', 9),
        'EDGE_PIN_H_KEY_DX' : 0,
        'EDGE_PIN_H_KEY_DY' : 1,
        'EDGE_PIN_V_KEY_DX' : 1,
        'BGA_PIN_NAME_DY'   : 1,
        'BGA_PIN_KEY_DX'    : 0,
        'BGA_PIN_KEY_DY'    : 1,
    },
)

RECT_FILL       = 'white'
HILITE_FILL     = 'lightblue'
SELECT_FILL     = 'yellow'
RE_FILL         = 'lightgreen'


def main(chip, regex):
    if isinstance(chip.geometry, chip_package.LQFP):
        cls = stm_layout.tk.LQFPWorkspace
    elif isinstance(chip.geometry, chip_package.BGA):
        cls = stm_layout.tk.BGAWorkspace
    elif isinstance(chip.geometry, chip_package.TSSOP):
        cls = stm_layout.tk.TSSOPWorkspace
    else:
        raise Exception('Unsupported chip package.')

    ws = cls(chip, RECT_FILL, HILITE_FILL, SELECT_FILL, RE_FILL)
    if regex:
        ws.set_regex(regex)

    ws.mainloop()


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chip', '-c', required=True)
    parser.add_argument('--regex')
    rv = parser.parse_args()

    parts = chip_db.find(rv.chip.lower())
    if not parts:
        print('No devices found for "%s"' % rv.chip)
        sys.exit(1)
    if len(parts) == 1:
        part = parts[0]
    else:
        part = next( (p for p in parts if rv.chip.lower() == p.partname), None)
    if part is None:
        print('Multiple devices found for "%s"' % rv.chip)
        for p in parts:
            print('%s - %s' % (p, chip_db.package(p)))
        sys.exit(1)
    else:
        chip = chip_stm.make_chip(part)
        main(chip, rv.regex)


if __name__ == '__main__':
    _main()
