import platform
import sys


def register(**kwargs):
    module = sys.modules[__name__]
    del module.register

    config = kwargs[platform.system().lower()]
    for k, v in config.items():
        setattr(module, k, v)
