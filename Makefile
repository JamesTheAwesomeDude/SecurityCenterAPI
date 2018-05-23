ARDUINO_DIR		= /usr/share/arduino
#BOARD_TAG		= mega2560
#MCU			= atmega2560
BOARD_TAG		= uno
MCU			= atmega328p

include ${ARDUINO_DIR}/Arduino.mk

.PHONY: minicom

minicom :
	minicom -8 -b 9600 -D ${DEVICE_PATH}
