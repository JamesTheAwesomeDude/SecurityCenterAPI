#!/usr/bin/env python3

from sys import argv,version_info
import serial

assert version_info >= (3,)

def send_bytes(data, port={'tty':'/dev/ttyACM0', 'baud':9600}):
	if type(port) is serial.Serial:
		write=port.write
	if type(port) is dict:
		write = serial.Serial(port['tty'], port['baud']).write
	write(data)

def set_leds(led_dict, writebytefunc=(send_bytes,[],{})):
	BITMASK_1BIT = [0b00000001<<i for i in range(8)]
	color_bitmask = {
	 'WHITE': BITMASK_1BIT[0],
	 'RED':   BITMASK_1BIT[3],
	 'YELLOW':BITMASK_1BIT[2],
	 'GREEN': BITMASK_1BIT[1],
	 'BLUE':  BITMASK_1BIT[4]
	}
	
	char=0b00000000
	for led in led_dict:
		char = char | ( color_bitmask[led] * led_dict[led] )
	
	writebytefunc[0](bytes([char]), *writebytefunc[1], **writebytefunc[2])

def _main_set(argv=['ard.py']):
	led_dict={}
	for color,value in [
	 (
	  ['WHITE', 'RED', 'YELLOW', 'GREEN', 'BLUE'][i],
	  bool(int( argv[i+1] ))
	 )
	 for i in range(len(argv)-1)
	]:
		led_dict[color]=value
	set_leds(led_dict)

if __name__ == "__main__":
	_main_set(argv)
