#!/usr/bin/python
import argparse
import collections


CHIP_PACAKGES = {}

DEFAULT_MODER = {
    'PA' : 0xABFFFFFF,
    'PB' : 0xFFFFFEBF,
    'PC' : 0xFFFFFFFF,
    'PD' : 0xFFFFFFFF,
    'PE' : 0xFFFFFFFF,
    'PF' : 0xFFFFFFFF,
    'PG' : 0xFFFFFFFF,
    'PH' : 0xFFFFFFFF,
    'PI' : 0xFFFFFFFF,
    'PJ' : 0xFFFFFFFF,
    'PK' : 0xFFFFFFFF,
}
DEFAULT_OTYPER = {
    'PA' : 0x00000000,
    'PB' : 0x00000000,
    'PC' : 0x00000000,
    'PD' : 0x00000000,
    'PE' : 0x00000000,
    'PF' : 0x00000000,
    'PG' : 0x00000000,
    'PH' : 0x00000000,
    'PI' : 0x00000000,
    'PJ' : 0x00000000,
    'PK' : 0x00000000,
}
DEFAULT_OSPEEDR = {
    'PA' : 0x0C000000,
    'PB' : 0x000000C0,
    'PC' : 0x00000000,
    'PD' : 0x00000000,
    'PE' : 0x00000000,
    'PF' : 0x00000000,
    'PG' : 0x00000000,
    'PH' : 0x00000000,
    'PI' : 0x00000000,
    'PJ' : 0x00000000,
    'PK' : 0x00000000,
}
DEFAULT_PUPDR = {
    'PA' : 0x64000000,
    'PB' : 0x00000100,
    'PC' : 0x00000000,
    'PD' : 0x00000000,
    'PE' : 0x00000000,
    'PF' : 0x00000000,
    'PG' : 0x00000000,
    'PH' : 0x00000000,
    'PI' : 0x00000000,
    'PJ' : 0x00000000,
    'PK' : 0x00000000,
}
DEFAULT_ALTFNR = {
    'PA' : 0x0000000000000000,
    'PB' : 0x0000000000000000,
    'PC' : 0x0000000000000000,
    'PD' : 0x0000000000000000,
    'PE' : 0x0000000000000000,
    'PF' : 0x0000000000000000,
    'PG' : 0x0000000000000000,
    'PH' : 0x0000000000000000,
    'PI' : 0x0000000000000000,
    'PJ' : 0x0000000000000000,
    'PK' : 0x0000000000000000,
}


class Choice(object):
    def __init__(self, name, choices, val):
        self.name        = name
        self.choices     = choices
        self.default_val = val
        self.val         = val
        self.enabled     = [True for _ in choices]


class Pin(object):
    def __init__(self, name, key, alt_fns, add_fns):
        super(Pin, self).__init__()
        self.name     = name
        self.key      = key
        self._default = False
        self._altfn   = None
        if alt_fns == '-':
            self.alt_fns = []
        else:
            self.alt_fns = alt_fns.split(',')
        if add_fns == '-':
            self.add_fns = []
        else:
            self.add_fns = add_fns.split(',')

        self._choices = []
        gpio = name[:2]
        if gpio in DEFAULT_MODER:
            try:
                n             = int(name[2:])
                self._gpio    = gpio
                self._gpionum = n
                self._choices = [
                    Choice('Mode', ['GPI', 'GPO', 'Alternate', 'Analog'],
                           (DEFAULT_MODER[gpio] >> (2*n)) & 0x3),
                    Choice('Speed', ['Low', 'Med', 'High', 'Very High'],
                           (DEFAULT_OSPEEDR[gpio] >> (2*n)) & 0x3),
                    Choice('Type', ['Push-Pull', 'Open-Drain'],
                           (DEFAULT_OTYPER[gpio] >> n) & 1),
                    Choice('Resistor', ['None', 'Pull-Up', 'Pull-Down'],
                           (DEFAULT_PUPDR[gpio] >> (2*n)) & 0x3),
                    ]
                self._nchoices = sum(len(c.choices) for c in self._choices)
                if self._choices[0].val == 2:
                    self._altfn = 0
            except ValueError:
                pass

        self._reset()

    def _reset(self):
        self._default = True
        if hasattr(self, '_gpio'):
            gpio                 = self._gpio
            n                    = self._gpionum
            self._choices[0].val = (DEFAULT_MODER[gpio] >> (2*n)) & 0x3
            self._choices[1].val = (DEFAULT_OSPEEDR[gpio] >> (2*n)) & 0x3
            self._choices[2].val = (DEFAULT_OTYPER[gpio] >> n) & 1
            self._choices[3].val = (DEFAULT_PUPDR[gpio] >> (2*n)) & 0x3
            self._altfn          = 0 if self._choices[0].val == 2 else None
        self._update_choices()

    def _set_choice(self, n):
        self._default = False
        for choice in self._choices:
            if n < len(choice.choices):
                if choice.enabled[n]:
                    choice.val = n
                break
            n -= len(choice.choices)
        self._update_choices()

    def _set_altfn(self, n):
        assert n < 16
        self._default = False
        self._altfn   = n
        self._update_choices()

    def _clear_altfn(self):
        self._default = False
        self._altfn   = None
        self._update_choices()

    def _toggle_altfn(self, n):
        if self._altfn == n:
            self._clear_altfn()
        else:
            self._set_altfn(n)

    def _update_choices(self):
        if not self._choices:
            return

        if self._altfn is not None:
            self._choices[0].enabled = [False, False, True, False]
            self._choices[0].val     = 2
        else:
            self._choices[0].enabled = [True for _ in self._choices[0].choices]

        if self._choices[0].val in (1, 2):
            # GPO or AF.  Everything is enabled.
            self._choices[1].enabled = [True for _ in self._choices[1].choices]
            self._choices[2].enabled = [True for _ in self._choices[2].choices]
            self._choices[3].enabled = [True for _ in self._choices[3].choices]
        elif self._choices[0].val == 0:
            # GPI.  Only resistor is enabled.
            self._choices[1].enabled = [False for _ in self._choices[1].choices]
            self._choices[2].enabled = [False for _ in self._choices[2].choices]
            self._choices[3].enabled = [True for _ in self._choices[3].choices]
            self._choices[1].val     = self._choices[1].default_val
            self._choices[2].val     = self._choices[2].default_val
        elif self._choices[0].val == 3:
            # Analog.  Nothing enabled.
            self._choices[1].enabled = [False for _ in self._choices[1].choices]
            self._choices[2].enabled = [False for _ in self._choices[2].choices]
            self._choices[3].enabled = [False for _ in self._choices[3].choices]
            self._choices[1].val     = self._choices[1].default_val
            self._choices[2].val     = self._choices[2].default_val
            self._choices[3].val     = self._choices[3].default_val


class ChipPackage(object):
    class Cursor(object):
        def __init__(self, cp):
            self.chip = cp
            self.pos  = (-1, 0)
            self.right()

        @property
        def pin(self):
            return self.chip.pin_map[self.pos[0]][self.pos[1]]

        def left(self):
            x = self.pos[0]
            while x - 1 >= 0:
                x -= 1
                if self.chip.pin_map[x][self.pos[1]] != None:
                    self.pos = (x, self.pos[1])
                    return

        def right(self):
            x = self.pos[0]
            while x + 1 < self.chip.width:
                x += 1
                if self.chip.pin_map[x][self.pos[1]] != None:
                    self.pos = (x, self.pos[1])
                    return

        def up(self):
            y = self.pos[1]
            while y - 1 >= 0:
                y -= 1
                if self.chip.pin_map[self.pos[0]][y] != None:
                    self.pos = (self.pos[0], y)
                    return  

        def down(self):
            y = self.pos[1]
            while y + 1 < self.chip.height:
                y += 1
                if self.chip.pin_map[self.pos[0]][y] != None:
                    self.pos = (self.pos[0], y)
                    return

    def __init__(self, name, width, height, pins):
        super(ChipPackage, self).__init__()
        self.name    = name
        self.width   = width
        self.height  = height
        self.pins    = pins
        self.pin_map = []
        for _ in xrange(height):
            self.pin_map.append([None]*self.width)
        for k, p in pins.iteritems():
            x, y = self._key_to_pos(k)
            self.pin_map[x][y] = p

    def _make_cursor(self):
        return ChipPackage.Cursor(self)

    def cursor(self):
        return self._make_cursor()

    def serialize_settings(self):
        moder     = {}
        otyper    = {}
        ospeedr   = {}
        pupdr     = {}
        altfnr    = {}
        mask_1    = {}
        mask_2    = {}
        mask_4    = {}
        for k in DEFAULT_MODER.iterkeys():
            moder[k]   = 0x00000000
            otyper[k]  = 0x00000000
            ospeedr[k] = 0x00000000
            pupdr[k]   = 0x00000000
            altfnr[k]  = 0x0000000000000000
            mask_1[k]  = 0xFFFFFFFF
            mask_2[k]  = 0xFFFFFFFF
            mask_4[k]  = 0xFFFFFFFFFFFFFFFF

        for p in self.pins.itervalues():
            if p._default:
                continue
            if not hasattr(p, '_gpio'):
                continue
            
            port           = p._gpio
            n              = p._gpionum
            mask_1[port]  &= ~(0x1 <<   n)
            mask_2[port]  &= ~(0x3 << 2*n)
            mask_4[port]  &= ~(0xF << 4*n)
            moder[port]   |= (p._choices[0].val << 2*n)
            otyper[port]  |= (p._choices[2].val << 1*n)
            ospeedr[port] |= (p._choices[1].val << 2*n)
            pupdr[port]   |= (p._choices[3].val << 2*n)
            if p._altfn is not None:
                altfnr[port] |= (p._altfn << 4*n)

        s     = ''
        ports = ['PA', 'PB', 'PC', 'PD', 'PE', 'PF',
                 'PG', 'PH', 'PI', 'PJ', 'PK']
        for port in ports:
            if mask_2[port] == 0xFFFFFFFF:
                continue
            s += '%s.MODER   = (%s.MODER   & 0x%08X) | 0x%08X\n' % (
                    port, port, mask_2[port], moder[port])
            s += '%s.OTYPER  = (%s.OTYPER  & 0x%08X) | 0x%08X\n' % (
                    port, port, mask_1[port], otyper[port])
            s += '%s.OSPEEDR = (%s.OSPEEDR & 0x%08X) | 0x%08X\n' % (
                    port, port, mask_2[port], ospeedr[port])
            s += '%s.PUPDR   = (%s.PUPDR   & 0x%08X) | 0x%08X\n' % (
                    port, port, mask_2[port], pupdr[port])
            m = (mask_4[port] >> 0) & 0xFFFFFFFF
            if m != 0xFFFFFFFF:
                s += '%s.AFRL    = (%s.AFRL    & 0x%08X) | 0x%08X\n' % (
                        port, port,
                        (mask_4[port] >>  0) & 0xFFFFFFFF,
                        (altfnr[port] >>  0) & 0xFFFFFFFF)
            m = (mask_4[port] >> 32) & 0xFFFFFFFF
            if m != 0xFFFFFFFF:
                s += '%s.AFRH    = (%s.AFRH    & 0x%08X) | 0x%08X\n' % (
                        port, port,
                        (mask_4[port] >> 32) & 0xFFFFFFFF,
                        (altfnr[port] >> 32) & 0xFFFFFFFF)
        return s


class LQFP100(ChipPackage):
    class Cursor(ChipPackage.Cursor):
        def left(self):
            if self.pos[0] == 1:
                if self.pos[1] == 0:
                    self.pos = (0, 1)
                else:
                    self.pos = (0, self.chip.height - 2)
            else:
                super(LQFP100.Cursor, self).left()

        def right(self):
            if self.pos[0] == self.chip.width - 2:
                if self.pos[1] == 0:
                    self.pos = (self.pos[0] + 1, 1)
                else:
                    self.pos = (self.pos[0] + 1, self.chip.height - 2)
            else:
                super(LQFP100.Cursor, self).right()

        def up(self):
            if self.pos[1] == 1:
                if self.pos[0] == 0:
                    self.pos = (1, 0)
                else:
                    self.pos = (self.chip.width - 2, 0)
            else:
                super(LQFP100.Cursor, self).up()

        def down(self):
            if self.pos[1] == self.chip.height - 2:
                if self.pos[0] == 0:
                    self.pos = (1, self.pos[1] + 1)
                else:
                    self.pos = (self.chip.width - 2, self.pos[1] + 1)
            else:
                super(LQFP100.Cursor, self).down()

    def __init__(self, pins):
        super(LQFP100, self).__init__('lqfp100', 27, 27, pins)

    def _key_to_pos(self, k):
        k = int(k, 10)
        assert k >= 1 and k <= 100
        if 1 <= k and k <= 25:
            return (0, k)
        elif 26 <= k and k <= 50:
            return (k - 25, 26)
        elif 51 <= k and k <= 75:
            return (26, 76 - k)
        elif 76 <= k and k <= 100:
            return (101 - k, 0)

    def _make_cursor(self):
        return LQFP100.Cursor(self)


class UFBGA176_25(ChipPackage):
    def __init__(self, pins):
        super(UFBGA176_25, self).__init__('ufbga176+25', 15, 15, pins)

    def _key_to_pos(self, k):
        y = ord(k[0]) - ord('A')
        if ord(k[0]) >= ord('Q'):
            y -= 3
        elif ord(k[0]) >= ord('O'):
            y -= 2
        elif ord(k[0]) >= ord('I'):
            y -= 1
        x = int(k[1:]) - 1
        assert not (x < 0 or x >= self.width or y < 0 or y >= self.height)
        return (x, y)


class TFBGA240_25(ChipPackage):
    def __init__(self, pins):
        super(TFBGA240_25, self).__init__('tfbga240+25', 17, 17, pins)

    def _key_to_pos(self, k):
        y = ord(k[0]) - ord('A')
        if ord(k[0]) >= ord('S'):
            y -= 4
        elif ord(k[0]) >= ord('Q'):
            y -= 3
        elif ord(k[0]) >= ord('O'):
            y -= 2
        elif ord(k[0]) >= ord('I'):
            y -= 1
        x = int(k[1:]) - 1
        assert not (x < 0 or x >= self.width or y < 0 or y >= self.height)
        return (x, y)


class PinDB(object):
    def __init__(self, path):
        super(PinDB, self).__init__()
        self.lqfp_pins  = {}
        self.ufbga_pins = {}
        self.tfbga_pins = {}

        rows = []
        with open(path, 'r') as f:
            for n, l in enumerate(f):
                parts = l.strip().split(' ')
                if len(parts) != 9:
                    print 'Line %u: %u parts' % (n+1, len(parts))
                rows.append(parts)

        for r in rows:
            assert len(r) == 9
            lqfp, ufbga, tfbga, name, typ, struc, notes, alt_fns, add_fns = r
            if lqfp != '-':
                self.lqfp_pins[lqfp] = Pin(name, lqfp, alt_fns, add_fns)
            if ufbga != '-':
                self.ufbga_pins[ufbga] = Pin(name, ufbga, alt_fns, add_fns)
            if tfbga != '-':
                self.tfbga_pins[tfbga] = Pin(name, tfbga, alt_fns, add_fns)

        self.lqfp_chip  = LQFP100(self.lqfp_pins)
        self.ufbga_chip = UFBGA176_25(self.ufbga_pins)
        self.tfbga_chip = TFBGA240_25(self.tfbga_pins)


def main(rv):
    PinDB(rv.pin_db)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pin-db', '-p', required=True)
    rv = parser.parse_args()

    main(rv)
