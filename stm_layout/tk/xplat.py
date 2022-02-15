import platform


SYSTEM = platform.system().lower()
CONFIG = {}


def register(**kwargs):
    global CONFIG
    CONFIG = kwargs[SYSTEM]


def get(key):
    return CONFIG[key]
