import glob

import modm_devices.parser
import modm_devices.pkg


DEVICES = None


def _populate_devices(prefix=None):
    global DEVICES
    DEVICES = {}
    basedir = modm_devices.pkg.get_filename('modm_devices', 'resources/devices')
    if prefix is None:
        prefix = ""
    for filename in glob.glob('{}/**/{}*.xml'.format(basedir, prefix)):
        parser  = modm_devices.parser.DeviceParser()
        devfile = parser.parse(filename)
        for device in devfile.get_devices():
            DEVICES[device.partname] = device


def find(name):
    if DEVICES is None:
        _populate_devices(name[:7])

    devs = []
    for partname, dev in DEVICES.items():
        if name in partname:
            devs.append(dev)

    return devs


def pin_count(dev):
    # Unfortunately, sometimes R means 64 and sometimes it means 68.  So, we
    # just count the pins.  For some reason, counting the pins goes slower.
    # Maybe modm-devices does some deferred loading? Yes it does. -Niklas
    return len(set(p['position']
                   for p in dev.get_driver('gpio')['package'][0]['pin']))


def package(dev):
    try:
        return dev.get_driver('gpio')['package'][0]['name']
    except Exception:
        pass
    raise Exception('Device %s has unknown package "%s".'
                    % (dev, dev.identifier.package))
