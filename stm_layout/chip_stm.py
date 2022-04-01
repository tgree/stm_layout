#!/usr/bin/env python3
import math

from . import chip_db
from . import chip_geometry


class Pin:
    def __init__(self, name, key, alt_fns, add_fns, full_name):
        super().__init__()
        self.name      = name
        self.full_name = full_name
        self.key       = key
        self._default  = True
        self._altfn    = None
        self.alt_fns   = alt_fns
        self.add_fns   = add_fns


class Chip:
    def __init__(self, part, geometry, pins):
        self.name     = str(part).upper()
        self.part     = part
        self.geometry = geometry
        self.pins     = pins


def make_geometry(part, pins):
    p = chip_db.package(part)
    n = chip_db.pin_count(part)
    if any(name in p for name in ('TFBGA', 'UFBGA', 'WLCSP', 'EWLCSP')):
        if n == 240:
            dim = 17    # 240+25
        elif n == 176:
            dim = 15    # 176+25
        else:
            dim = int(math.ceil(math.sqrt(float(n))))
        return chip_geometry.BGA(p, dim, dim, pins)

    if any(name in p for name in ('LQFP', 'UFQFPN', 'VFQFPN')):
        dim = int(math.ceil(float(n)/4.))
        return chip_geometry.LQFP(p, dim, dim, pins)

    if any(name in p for name in ('TSSOP', 'SO8N')):
        dim = int(math.ceil(float(n)/2.))
        return chip_geometry.TSSOP(p, dim, pins)

    raise KeyError


def make_chip(part):
    gpio_driver = part.get_driver('gpio')

    gpios = {}
    for gpio in gpio_driver['gpio']:
        gpios['P%s%s' % (gpio['port'].upper(), gpio['pin'])] = gpio

    pins = {}
    for p in gpio_driver['package'][0]['pin']:
        # TODO: Some small devices have multiplexed pins where the SYSCFG
        #       device can be used to select if the physical pin should be PA0
        #       or PA1 or...  This is different from a normal pin which is
        #       usually always just PA0 and then you select the alternate or
        #       analog function for that pin - i.e. it's another level of
        #       multiplexing to squash more functionality into a small pin
        #       count.  For these types of devices, we will only show the
        #       default configuration, i.e. the non-remapped pin.
        if p.get('variant', '') == 'remap':
            continue

        full_name = p['name']
        key       = p['position']
        if key in pins:
            print('Pin Exists: %s %s is already %s.' % (repr(key), full_name,
                                                        pins[key].full_name))

        # GPIO pins don't have a type and non-GPIOs have nothing to extract,
        # so assign them directly.
        if 'type' in p:
            pins[key] = Pin(full_name, key, [], [], full_name)
            continue

        # Extract the short name and the GPIO key from the full name.  Sample
        # full names:
        #
        #   PA0
        #   PA11 [PA9]                  (stm32g050f6p6)
        #   PC14-OSC32_IN (PC14)        (stm32u585qii3)
        #   PC14/OSC32_IN               (stm32f767zit6)
        #   PC14OSC32_IN                (stm32f091rch6)
        #   PC15OSC32_OUT               (stm32f091rch6)
        #   PF11BOOT0                   (stm32f091rch6)
        #   PC2_C                       (stm32h745xgh6 has PC2 and PC2_C)
        #
        # The short name is the initial prefix except in the case of an "_C"
        # suffix, in which case the short name includes the suffix.  The GPIO
        # key is always strictly the prefix.
        short_name = full_name.split('-')[0]
        short_name = short_name.split('/')[0]
        short_name = short_name.split(' ')[0]
        short_name = short_name.split('OSC32_')[0]
        short_name = short_name.split('BOOT0')[0]
        gpio_key   = short_name.split('_')[0]

        # Extract the alternate (digital) functions and additional (analog)
        # functions.
        gpio    = gpios[gpio_key]
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

        # Assign the final pin.
        pins[key] = Pin(short_name, key, alt_fns, add_fns, full_name)

    geometry = make_geometry(part, pins)
    return Chip(part, geometry, pins)
