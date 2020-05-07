import modm_devices.parser
import glob
import math
import re

import chip_package


DEVICES = None


def _populate_devices():
    global DEVICES
    DEVICES = {}
    for filename in glob.glob('modm-devices/devices/**/*.xml'):
        parser  = modm_devices.parser.DeviceParser()
        devfile = parser.parse(filename)
        for device in devfile.get_devices():
            DEVICES[device.partname] = device


def find(name):
    if DEVICES is None:
        _populate_devices()

    devs = []
    for partname, dev in DEVICES.items():
        if name in partname:
            devs.append(dev)

    return devs


def pin_count(dev):
    # Unfortunately, sometimes R means 64 and sometimes it means 68.  So, we
    # just count the pins.  For some reason, counting the pins goes slower.
    # Maybe modm-devices does some deferred loading?
    return len(dev.properties['pin'])
    #return {'a' : 169,
    #        'b' : 208,
    #        'c' : 48,
    #        'k' : 32,
    #        'i' : 176,
    #        'm' : 80.5,
    #        'q' : 100,
    #        'r' : 64,
    #        'v' : 100,
    #        'x' : 240,
    #        'z' : 144,
    #        }[dev.identifier.pin]


def package(dev):
    return {'h' : 'TFBGA',
            'i' : 'UFBGA',  # 0.5 mm
            'k' : 'UFBGA',  # 0.65 mm
            'q' : 'UFBGA',
            't' : 'LQFP',
            'u' : 'UFQFPN',
            'v' : 'VFQFPN',
            'y' : 'WLCSP',
            }[dev.identifier.package]


def make_package(dev):
    p = package(dev)
    n = pin_count(dev)
    if p in ('TFBGA', 'UFBGA', 'WLCSP'):
        if n == 240:
            dim = 17    # 240+25
        elif n == 176:
            dim = 15    # 176+25
        else:
            dim = int(math.ceil(math.sqrt(float(n))))
        return chip_package.BGA(dim, dim)
    elif p in ('LQFP', 'UFQFPN', 'VFQFPN'):
        dim = int(math.ceil(float(n)/4.))
        return chip_package.LQFP(dim, dim)
    raise KeyError


GPIO_DEFAULTS = {
    'RM0399' : {    # STM32H745/747/755/757 (same defaults as RM0433)
        'MODER' : {
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
        },
        'OTYPER' : {
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
        },
        'OSPEEDR' : {
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
        },
        'PUPDR' : {
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
        },
    },
    'RM0433' : {    # STM32H742/743/750/753 (same defaults as RM0399)
        'MODER' : {
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
        },
        'OTYPER' : {
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
        },
        'OSPEEDR' : {
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
        },
        'PUPDR' : {
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
        },
    },
    'RM0440' : {    # STM32G4
        'MODER' : {
            'PA' : 0xABFFFFFF,
            'PB' : 0xFFFFFEBF,
            'PC' : 0xFFFFFFFF,
            'PD' : 0xFFFFFFFF,
            'PE' : 0xFFFFFFFF,
            'PF' : 0xFFFFFFFF,
            'PG' : 0xFFFFFFFF,
        },
        'OTYPER' : {
            'PA' : 0x00000000,
            'PB' : 0x00000000,
            'PC' : 0x00000000,
            'PD' : 0x00000000,
            'PE' : 0x00000000,
            'PF' : 0x00000000,
            'PG' : 0x00000000,
        },
        'OSPEEDR' : {
            'PA' : 0x0C000000,
            'PB' : 0x00000000,
            'PC' : 0x00000000,
            'PD' : 0x00000000,
            'PE' : 0x00000000,
            'PF' : 0x00000000,
            'PG' : 0x00000000,
        },
        'PUPDR' : {
            'PA' : 0x64000000,
            'PB' : 0x00000100,
            'PC' : 0x00000000,
            'PD' : 0x00000000,
            'PE' : 0x00000000,
            'PF' : 0x00000000,
            'PG' : 0x00000000,
        },
    },
}

REFM_TABLE = {
    '^stm32h742.*' : 'RM0433',
    '^stm32h743.*' : 'RM0433',
    '^stm32h745.*' : 'RM0399',
    '^stm32h747.*' : 'RM0399',
    '^stm32h750.*' : 'RM0433',
    '^stm32h753.*' : 'RM0433',
    '^stm32h755.*' : 'RM0399',
    '^stm32h757.*' : 'RM0399',
    '^stm32g4.*'   : 'RM0440',
}


def get_refm(part):
    identifier = str(part.identifier)
    for k, v in REFM_TABLE.items():
        regex = re.compile(k)
        if regex.search(identifier):
            return v
    raise KeyError


def get_gpio_ports(part):
    return GPIO_DEFAULTS[get_refm(part)]['MODER'].keys()


def get_gpio_defaults(part, port, pin):
    defs    = GPIO_DEFAULTS[get_refm(part)]
    moder   = defs['MODER'][port]
    otyper  = defs['OTYPER'][port]
    ospeedr = defs['OSPEEDR'][port]
    pupdr   = defs['PUPDR'][port]
    return ((moder >> (2*pin)) & 0x3,
            (otyper >> pin) & 0x1,
            (ospeedr >> (2*pin)) & 0x3,
            (pupdr >> (2*pin)) & 0x3,
            )
