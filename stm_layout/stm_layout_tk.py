#!/usr/bin/env python3
import argparse
import sys

from stm_layout import chip_db, chip_stm, chip_package
import stm_layout.tk


FONT            = ('Monaco', 10)
FONT_PIN_NUM    = ('Monaco', 9)
FONT_INFO       = ('Monaco', 10)
RECT_FILL       = 'white'
HILITE_FILL     = 'lightblue'
SELECT_FILL     = 'yellow'
RE_FILL         = 'lightgreen'


def main(chip, regex):
    if isinstance(chip.chip, chip_package.LQFP):
        cls = stm_layout.tk.LQFPWorkspace
    elif isinstance(chip.chip, chip_package.BGA):
        cls = stm_layout.tk.BGAWorkspace
    elif isinstance(chip.chip, chip_package.TSSOP):
        cls = stm_layout.tk.TSSOPWorkspace
    else:
        raise Exception('Unsupported chip package.')

    ws = cls(chip, FONT, FONT_PIN_NUM, FONT_INFO, RECT_FILL, HILITE_FILL,
             SELECT_FILL, RE_FILL)
    if regex:
        ws.set_regex(regex)

    ws.mainloop()


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chip', '-c', required=True)
    parser.add_argument('--regex')
    rv = parser.parse_args()

    parts = chip_db.find(rv.chip)
    if not parts:
        print('No devices found for "%s"' % rv.chip)
        sys.exit(1)
    part = next( (p for p in parts if rv.chip == p.partname), None)
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
