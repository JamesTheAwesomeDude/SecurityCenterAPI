#!/usr/bin/env python3

from sys import argv,version_info
from getpass import getpass
from collections import namedtuple
import urllib3,json

assert version_info >= (3,)

VERSION=(0,0,3)

def __main__(argv=argv):
	username=hostname=password=None
	protocol,port = 'https',443 # TODO
	
	if len(argv) > 1:
		# There is at least one argument
		if '@' not in argv[1]:
			# Assuming it's just the hostname
			hostname=argv[1]
		else:
			# There was an @ in it; we got a username
			username,hostname=argv[1].rsplit('@', 1)
			if ':' in username:
				# For convenience lol
				username,password=username.split(':', 1)
				print("\x1b[31;1mWARNING: insecure password entry method.\x1b[0m")
	else:
		# There were no arguments; we HAVE to ask the hostname
		hostname=input("Please enter the SecurityCenter hostame/IP address:\t")
	
	if username is None:
		# Username not deduced from arguments
		username=input("Please enter the username:\t")
	if password is None:
		# Likewise with password
		password=getpass("Please enter the SecurityCenter password:\t")
	
	
	print("Testing login...")
	
	sc=_init_sc(
	 (username,password),
	 hostname,
	 port,
	 protocol
	)
	
	if sc.token:
		return 0 # for Success
	else:
		return 1 # for Error


def _init_sc(
   u_p=(None,None),
   hostname=None,
   port=443,
   protocol='https'
):
	
	http = urllib3.PoolManager(	
	
	headers= {
	  'User-Agent':'ArduinoMonitor / {}'.format('.'.join([str(V) for V in VERSION]))
	 },
	 
	 cert_reqs='CERT_REQUIRED',
	 ca_certs="/opt/sc/support/conf/TenableCA.crt",
	 
	 # LEAVE THIS IN:
	 assert_hostname=False
	 # (at least until we can get Jeff to STAHP
	 #    conf'ing SC with non-loopback IPs)
	 
	)
	
	http.headers['Host']="10.10.10.8" #TODO
	
	base_url='https://{}:{}/rest'.format(hostname, port)
	r2u = lambda resource: '{}{}'.format(base_url, resource)
	
	make_get_function = lambda token,url_base_elements=(protocol, '://', hostname, '/rest'):(
	 lambda resource_name,method='GET',token=None,http=http,res2u=(  lambda resrcnm: ''.join(url_base_elements+(resrcnm,)) ),request_extra=([],{}):(
	  http.request(
	   method,
	   res2u(resource_name),
	   *request_extra[0],
	   **request_extra[1]
	  )
	 )
	)

	r_login=make_get_function(token=None)(
	 '/token',
	 method='POST',
	 request_extra=(
	  [],
	  {
	   'fields':{
	    'username': u_p[0],
	    'password': u_p[1]
	   }   
	  }
	 )
	)

	login_data=json.loads(r_login.data.decode())
	
	if 'error_code' in login_data and login_data['error_code']:
		_raise_http_json(login_data)
	
	
	token=login_data['response']['token']	
	http.headers['X-SecurityCenter']=str(token)
	
	return namedtuple(
		'SecurityCenterAPI',
		[
		 'http',
		 'token',
		 'get',
		]
	)(
		http,
		token,
		make_get_function(token)
	)

def _raise_http_json(msg_dict):
	raise urllib3.exceptions.HTTPError(
	 '\n'.join(['{}\t{}'.format(
	   k, msg_dict[k]
	  ) for k in msg_dict
	 ])
	)

if __name__ == "__main__":
	quit(__main__())
