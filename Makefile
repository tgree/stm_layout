.PHONY: all
all: modm_devices


modm-devices:
	@git clone -b develop_with_gpio_xml https://github.com/tgree/modm-devices


.xml: modm-devices
	@cd modm-devices/tools/generator && make init
	@cd modm-devices/tools/generator && make extract-stm32
	@cd modm-devices/tools/generator && make generate-stm32
	@touch .xml


modm_devices: modm-devices
	@ln -s modm-devices/tools/device/modm_devices


clean:
	@rm -rf modm-devices .xml 2>/dev/null or true
