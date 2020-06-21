#!/usr/bin/env python3
import argparse
import collections

import chip_db


class Choice(object):
    def __init__(self, name, choices, val):
        self.name        = name
        self.choices     = choices
        self.default_val = val
        self.val         = val
        self.enabled     = [True for _ in choices]

    def reset(self):
        self.val = self.default_val


class Pin(object):
    def __init__(self, name, key, alt_fns, add_fns, full_name):
        super(Pin, self).__init__()
        self.name      = name
        self.full_name = full_name
        self.key       = key
        self._default  = True
        self._altfn    = None
        self.alt_fns   = alt_fns
        self.add_fns   = add_fns
        self._choices  = []
        self._nchoices = 0


class GPIO(Pin):
    def __init__(self, name, key, alt_fns, add_fns, full_name, part):
        super(GPIO, self).__init__(name, key, alt_fns, add_fns, full_name)
        gpio = name[:2]
        try:
            n                             = int(name[2:])
            moder, otyper, ospeedr, pupdr = chip_db.get_gpio_defaults(part,
                                                                      gpio, n)
            self._gpio                    = gpio
            self._gpionum                 = n
            self._choices = [
                Choice('Mode', ['GPI', 'GPO', 'Alternate', 'Analog'], moder),
                Choice('Speed', ['Low', 'Med', 'High', 'Very High'], ospeedr),
                Choice('Type', ['Push-Pull', 'Open-Drain'], otyper),
                Choice('Resistor', ['None', 'Pull-Up', 'Pull-Down'], pupdr),
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
            gpio = self._gpio
            self._choices[0].reset()
            self._choices[1].reset()
            self._choices[2].reset()
            self._choices[3].reset()
            self._altfn = 0 if self._choices[0].val == 2 else None
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


class Chip(object):
    def __init__(self, part, chip_package, pins):
        self.name    = str(part).upper()
        self.part    = part
        self.chip    = chip_package
        self.width   = self.chip.width
        self.height  = self.chip.height
        self.pins    = pins
        self.pin_map = self.chip.pins
        for k, p in pins.items():
            self.chip[k] = p

    def cursor(self):
        return self.chip.cursor()

    def serialize_settings(self):
        moder     = {}
        otyper    = {}
        ospeedr   = {}
        pupdr     = {}
        altfnr    = {}
        mask_1    = {}
        mask_2    = {}
        mask_4    = {}
        keys      = chip_db.get_gpio_ports(self.part)
        for k in keys:
            moder[k]   = 0x00000000
            otyper[k]  = 0x00000000
            ospeedr[k] = 0x00000000
            pupdr[k]   = 0x00000000
            altfnr[k]  = 0x0000000000000000
            mask_1[k]  = 0xFFFFFFFF
            mask_2[k]  = 0xFFFFFFFF
            mask_4[k]  = 0xFFFFFFFFFFFFFFFF

        for p in self.pins.values():
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
        for port in keys:
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


def make_chip(part):
    pkg     = chip_db.make_package(part)
    pin_map = {}
    for p in part.properties['pin']:
        name            = p['name'].split('-')[0]
        name            = name.split(' ')[0]
        prefix          = name.split('_')[0]
        p['shortname']  = name
        pin_map[p['position']] = p

    gpios = part.get_driver('gpio')
    pins  = {}
    for gpio in gpios['gpio']:
        name = 'P%c%u' % (gpio['port'].upper(), int(gpio['pin'], 10))
        alt_fns = ['-']*16
        add_fns = []
        for s in gpio.get('signal', []):
            f = (s.get('driver', '').upper() + s.get('instance', '') +
                 '_' + s['name'].upper())
            if 'af' in s:
                i  = int(s['af'], 10)
                if alt_fns[i] == '-':
                    alt_fns[i] = f
                else:
                    alt_fns[i] += '/' + f
            else:
                add_fns.append(f)

        # TODO: Some small devices have multiplexed pins where the SYSCFG
        #       device can be used to select if the physical pin should be PA0
        #       or PA1 or...  This is different from a normal pin which is
        #       usually always just PA0 and then you select the alternate or
        #       analog function for that pin - i.e. it's another level of
        #       multiplexing to squash more functionality into a small pin
        #       count.  For these types of devices, there will be multiple
        #       GPIOs that have the same 'position' field and when we populate
        #       pins[key] we will only hold the last one there.
        key       = gpio['position']
        pin       = pin_map[key]
        name      = pin['shortname']
        fname     = pin['name']
        pins[key] = GPIO(name, key, alt_fns, add_fns, fname, part)

    for p in part.properties['pin']:
        key = p['position']
        if key not in pins:
            pins[key] = Pin(p['name'], key, [], [], p['name'])
    return Chip(part, pkg, pins)
