init:
	@git clone https://github.com/tgree/tgcurses
	@git clone https://github.com/tgree/modm-devices


clean:
	@rm -rf tgcurses modm-devices 2>/dev/null or true
