#!/usr/bin/env python3

from sys import argv,version_info
from getpass import getpass
import urllib3,json

assert version_info >= (3,)

VERSION=(0,0,5)

class SecurityCenterAPI:
	def __init__(self,
	     hostname,
	     u_p=(None, None),
	     port=443,
	     protocol='https',
	     endpoint='/rest',
	     
	     extra_http_kwargs={
	      'assert_hostname': False #WORKAROUND Re:Jeff
	     },
	     extra_headers={
	      'Host':"10.10.10.8"      #WORKAROUND Re:Jeff
	     },
	     
	     # Overridable via the "extra_..", so should almost never be used:
	     _headers={
	      'User-Agent': 'ArduinoMonitor / {}'.format('.'.join([str(V) for V in VERSION]))
	     },
	     _http_kwargs={
	      'ca_certs': "/opt/sc/support/conf/TenableCA.crt",
	      'cert_reqs': 'CERT_REQUIRED' # idk what this does but the wiki said to put it when using custom CA
	     },
	     token_header_name='X-SecurityCenter',
	     DEBUG=True
	):
		## __init__ STARTS HERE ##
		
		# Initialize the HTTP Connection Pool
		self._http = urllib3.PoolManager(
		 headers=dict(_headers, **extra_headers),
		 **dict(_http_kwargs, **extra_http_kwargs)
		)
		
		# Record the state of DEBUG mode
		self._DEBUG=DEBUG
		
		# Initialize helper functions
		self._r2u = lambda resource ,protocol=protocol,hostname=hostname,port=str(port),endpoint=endpoint,s=('://',':','/') : ''.join(
		 (protocol,s[0],hostname,s[1],port,endpoint,s[2],resource)
		)
		self._t2h = lambda t,n=token_header_name: ({n: str(t)} if t else {})
		self._token = {'token': 0, 'Cookie': None}
		self._token_headers = lambda token=self._token,token_header_name=token_header_name,c2h=(lambda d: '; '.join( ['{}={}'.format(c,d[c]) for c in d] )+';'): (
		 dict(
		  (   {token_header_name: str(token['token' ])} if token['token']  else {}),
		  **( {'Cookie'         : c2h(token['Cookie'])} if token['Cookie'] else {})
		 )
		)
		
		# Log in
		if u_p[0]:
			self.login(*u_p)
		else:
			print("WARNING: deferring login. You will have to .login(username,password)!")
		
		## __init__ ENDS HERE ##
	
	def _get_resource(self, resource, method='GET', headers={}, r2u=None, _req_kwargs={}):
		r2u = (self._r2u if r2u is None else r2u)
		
		if self._DEBUG:
			print("##FETCH##")
			print("RESOURCE:   ", resource)
			print("HEADERS:    ", headers)
			print("_REQ_KWARGS:", _req_kwargs)
			print("URL:        ", r2u(resource))
		
		r = self._http.request(
		 method,
		 r2u(resource),
		 headers=headers,
		 **_req_kwargs
		)
		
		if r.status in [403,404,400]:
			raise urllib3.exceptions.HTTPError(r)
		return r
		
	def get(self, resource, method='GET', token=None, headers={}, _req_kwargs={}, _PROCESS=lambda r: (json.loads(r.data.decode())) ):
		if token is None:
			token=self._token
		
		r = self._get_resource(
		 resource=resource,
		 method=method,
		 headers=dict(
		  self._token_headers(),
		  **headers
		 ),
		 _req_kwargs=_req_kwargs
		)

		if self._DEBUG:
			print("JSON:       ", json.loads(r.data))
		
		return _PROCESS(r)

	def login(self, username, password):
		#TODO: Client Certificate support
		# https://docs.tenable.com/sscv/api/System.html#SystemGET
		
		t_c = self.get(
		 'token',
		 method='POST',
		 _req_kwargs={'fields':{
		  'username': username,
		  'password': password
		 }},
		 _PROCESS=lambda r: (json.loads(r.data.decode())['response']['token'], r.headers['Set-Cookie'].split(';', 1)[0])
		)
		if self._DEBUG:
			print(t_c)
		
		self._token['token'] = t_c[0]
		self._token['Cookie']= t_c[1]
	
	
#	def __enter__(self):
#		#TODO
#	def __exit__(self):
#		#TODO
	
	

def __main__(argv=argv):
	username=hostname=password=None
	protocol,port = 'https',443 # TODO
	
	if len(argv) > 1:
		# There is at least one argument
		if '@' not in argv[1]:
			# No @, so it's just the hostname
			hostname=argv[1]
			if ':' in hostname:
				# 'hostname:8080'
				hostname,port=hostname.rsplit(':', 1)
		else:
			# There was an @ in it; we got a username
			username,hostname=argv[1].rsplit('@', 1)
			if ':' in username: # 'username:pa55w0rd'
				# For convenience lol
				username,password=username.split(':', 1)
				# probably don't use this
				print("\x1b[31;1mWARNING: insecure password entry method.\x1b[0m")
				# (but I'm not your mom so do what you want)
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
	
	SC=SecurityCenterAPI(
	 u_p=(username,password),
	 hostname=hostname,
	 port=port,
	 protocol=protocol
	)
	
	print("Logged in! Token:", SC._token)
	
	print("Trying scanResult..")
	R=SC.get("scanResult", DEBUG=True)
	print("Status: \t"+ str(R.status))
	print("Headers:\t"+str([h for h in R.headers if h.startswith('X')]) + "\t(startswith('X') only)")


def _raise_http_json(msg_dict):
	raise urllib3.exceptions.HTTPError(
	 '\n'.join(['{}\t{}'.format(
	   k, msg_dict[k]
	  ) for k in msg_dict
	 ])
	)

if __name__ == "__main__":
	quit(__main__())
