Curses-based tool for configuring STM32 pins.
=============================================

This tool uses a fork of the amazing curated .xml from the modm-devices
project.  The modm-devices project provides metadata about all STM32 devices
in machine-parseable .xml format and is really what makes any tool like this
one possible.

Installing::

    pip3 install stm_layout

Usage::

    stm_layout -c <chip_name>

If chip_name is not fully-specified (i.e. 'stm32g474' is only a partial chip
name), then a list of available chips matching that part will be printed to
stdout.  If the chip name is fully-specified, (i.e. 'stm32g474cet6'), then a
curses UI will be brought up for browsing/searching pins and configuring them.

Navigate using the arrow keys and the tab key.  Search using standard regex
queries in the search bar.  In any pane but the search pane::

    q - quits
    w - writes /tmp/stm32_pinout.txt
    r - resets the current pin

The stm32_pinout.txt is an attempt to configure all the GPIO registers for
your chip; it is woefully incomplete for anything except the H7 and G4 chips
I have access to.
