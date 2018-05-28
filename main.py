#!/usr/bin/env python3

from sc import SecurityCenterAPI
from ard import set_leds
from nes import dict1_from_xmlv2_root
from lxml import etree
from io import BytesIO
from zipfile import ZipFile
from getpass import getpass
from time import sleep
from sys import version_info,argv,stdout
from json import dump
assert version_info >= (3,)

def __main__(argv=argv):
	username=hostname=password=None
	protocol,port,endpoint = 'https',443,'/rest' #TODO
	
	if len(argv) > 1:
		# There is at least one argument
		hostname=argv[1]
		# [http[s]://][username[:password]@]hostname[:port][endpoint]
		
		if '://' in hostname[:10]:
			# protocol (http/https) specified, prune it off
			protocol,hostname=hostname.split('://', 1)
		
		if '@' in hostname:
			# There was an @ in it; we got a username
			username,hostname=hostname.rsplit('@', 1)
			if ':' in username: # 'username:pa55w0rd'
				# For convenience lol
				username,password=username.split(':', 1)
				# probably don't use this
				print("\x1b[31;1mWARNING: insecure password entry method.\x1b[0m")
				# (but I'm not your mom so do what you want)
		
		# Potential password is now purged, so we can SAFELY split ':' and '/'
		if '/' in hostname:
			hostname,endpoint=hostname.split('/',1)
			endpoint='/'+endpoint
		if ':' in hostname:
			hostname,port=hostname.split(':',1)
			port=int(port)
	else:
		# There were no arguments; we HAVE to ask the hostname
		hostname=input("Please enter the SecurityCenter hostame/IP address:\t")
	if username is None:
		# Username not deduced from arguments
		username=input("Please enter the username:\t")
	if password is None:
		# Likewise with password
		password=getpass("Please enter the SecurityCenter password:\t")
	
	
	with SecurityCenterAPI(
	 u_p=(username,password),
	 hostname=hostname,
	 port=port,
	 protocol=protocol,
	 endpoint=endpoint
	) as SC:
		scanResultList=SC.get('scanResult')['response']['usable']
		nessusDicts=[]
		v={}
		for scanResultIndex in scanResultList:
			nessusDicts.append(
			 dict1_from_xmlv2_root(
			  SC.get(
			   'scanResult/{}/download'.format(scanResultIndex['id']),
			   _PROCESS='UNZIPXMLS'
			  )[0].getroot()
			 )
			)
			for vuln in nessusDicts[-1]:
				if int(nessusDicts[-1][vuln]["severity"]):
					print("VULNERABILITY OF NON-ZERO SEVERITY FOUND!")
				if int(nessusDicts[-1][vuln]["severity"]) not in v:
					v[int(nessusDicts[-1][vuln]["severity"])]=0
				v[int(nessusDicts[-1][vuln]["severity"])]+=1
		print("Vulnerabilities by severity:", v)
		s=max(k for k in v)
		print("Worst vulnerability is level", s)
		col=["GREEN", "YELLOW", "YELLOW", "RED"][s]
		print("So illuminating the", col, "LED.")
		n=v[s]
		print("There were", n, "of these vulnerabilities,")
		p=(
		 1 if s==0 #All green! 0.5hz blinking
		 else 3/(n+s-2) if (n+s-2)>0 # Some problems
		 else 2.5  # 0.2hz Fallback for divide-by-zero error when not-quite-severe-enough
		)
		print("So will flash the LED at about {}Hz.".format( 1/(2 * p) ))
		while True:
			set_leds({col: True})
			sleep(p)
			set_leds({})
			sleep(p)
			

if __name__ == "__main__":
	quit(__main__(argv))
