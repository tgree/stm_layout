import modm_devices.parser
import glob
import math

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
    return {'a' : 169,
            'b' : 208,
            'c' : 48,
            'i' : 176,
            'm' : 80.5,
            'q' : 100,
            'r' : 64,
            'v' : 100,
            'x' : 240,
            'z' : 144,
            }[dev.identifier.pin]


def package(dev):
    return {'h' : 'TFBGA',
            'i' : 'UFBGA',  # 0.5 mm
            'k' : 'UFBGA',  # 0.65 mm
            't' : 'LQFP',
            'u' : 'UFQFPN',
            'y' : 'WLCSP',
            }[dev.identifier.package]


def make_package(dev):
    p = package(dev)
    n = pin_count(dev)
    if p in ('TFBGA', 'UFBGA', 'WLCSP'):
        dim = int(math.ceil(math.sqrt(float(n))))
        return chip_package.BGA(dim, dim)
    elif p in ('LQFP', 'UFQFPN'):
        dim = int(math.ceil(float(n)/4.))
        return chip_package.LQFP(dim, dim)
    raise KeyError
