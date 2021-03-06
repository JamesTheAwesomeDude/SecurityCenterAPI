#!/usr/bin/env python3

from sys import argv,version_info,stderr
from getpass import getpass
import urllib3,logging,json
from io import BytesIO
from zipfile import ZipFile
from lxml import etree
from urllib3._collections import HTTPHeaderDict

assert version_info >= (3,)

VERSION=(0,1,1)

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
		if DEBUG:
			l=logging.getLogger("urllib3")
			logging.basicConfig(stream=stderr,level=logging.DEBUG)
		self._http = urllib3.PoolManager(
		 headers=HTTPHeaderDict(_headers, **extra_headers),
		 **dict(_http_kwargs, **extra_http_kwargs)
		)
		
		# Record the state of DEBUG mode
		self._DEBUG=DEBUG

		#Initialize empty authentication token		
		self._token = {'token': 0, 'cookies': {}}

		
		# Initialize (minor) helper functions
		## _ddel(dict, keys) -> dict, with all given keys purged
		self._ddel = lambda d, keys=[]:(
		 type(d)(
		  [(k,d[k]) for k in d if k not in keys]
		 )
		)
		## _r2u(resource_name) -> {url_of_resource}
		self._r2u = lambda resource ,protocol=protocol,hostname=hostname,port=str(port),endpoint=endpoint,s=('://',':','/') : ''.join(
		 (protocol,s[0],hostname,s[1],port,endpoint,s[2],resource)
		)
		## _t2hd(token) -> {dict of header for the token, or empty dict if not token}
		## _t2hd(value, key) -> {dict of given key:value, or empty dict if not value}
		self._t2hd = lambda t,k=token_header_name,dict=HTTPHeaderDict: (
		 dict({}, **{k: str(t)})
		) if t else dict()
		## _cd2chd(dict of cookies) -> {header-dict of the cookies, formatted, or empty dict if no cookies}
		self._cd2chd = lambda d,t2hd=self._t2hd: (
		 t2hd(
		  '; '.join(
		   ['{}={}'.format(c,d[c]) for c in d]
		  ) + (';' if len(d) > 1 else ''),
		  'Cookie'
		 )
		) if d else t2hd({})
		## _chl2cd(LIST OF values of 'Set-Cookie' headers) -> {dict representing the cookies, or empty dict if empty}
		self._chl2cd = lambda l: (
		 dict([
		  [s.strip() for s in c.split(';',1)[0].split('=',1)] # cookie-name,cookie-value
		  for C in l for c in C.split(',') # each element of l may contain comma-delimited cookie entries
		 ])
		) if l else {}
		## _pphd(header-dict) -> {pretty-printed string }
		self._pphd = lambda d: '\n   '.join([type(d).__name__+'{'] + [
		 (h+':').ljust(max([len(h) for h in d])+5)+d[h] for h in d
		])+'\n}'
		
		# _token_headers() -> {header-dict sufficient for authentication}
		self._token_headers = lambda t=self._token,t2hd=self._t2hd,cd2chd=self._cd2chd,dict=HTTPHeaderDict: dict(
		 t2hd(t['token']),
		 **cd2chd(t['cookies'])
		)
		
		# Log in
		if u_p[0]:
			self.login(*u_p)
		else:
			print("WARNING: deferring login. You will have to .login(username,password)!")
		
		## __init__ ENDS HERE ##
	
	def _get_resource(self, resource, method='GET', headers=None, fields={}, r2u=None, _req_kwargs={}, dict=HTTPHeaderDict):
		r2u = (self._r2u if r2u is None else r2u)
		headers = (dict() if headers is None else headers)
		url=r2u(resource)
		
		if self._DEBUG >= 2:
			print("##FETCH##")
			print("URL:         ", r2u(resource))
			print("[RESOURCE]:  ", resource)
			print("REQ_HEADERS: ", self._pphd(dict(headers, **self._http.headers)))
			print("FIELDS:      ", fields)
			print("_REQ_KWARGS: ", _req_kwargs)
		
		r = self._http.request(
		 method,
		 url,
		 headers=dict(headers, **self._http.headers),
		 fields=fields,
		 **_req_kwargs
		)
		
		if self._DEBUG >= 2:
			print("RESP_HEADERS:", self._pphd(r.headers))
			print("DATA:        ", r.data)
		
		if r.status // 100 == 4: #4XX
			raise urllib3.exceptions.HTTPError(r)
		return r,url
		
	def get(self, resource, method='_AUTO', token=None, headers=None, fields={}, _req_kwargs={}, _PROCESS="_AUTO",dict=HTTPHeaderDict):
		token = (self._token if token is None else token)
		headers = (dict() if headers is None else headers)
		
		if method=='_AUTO':
			method=(
			 
			 'POST' if (
			  resource.endswith("download")
			 )
			 
			 else
			 'GET'
			)
		
		r,u = self._get_resource(
		 resource=resource,
		 method=method,
		 headers=dict(
		  self._token_headers(),
		  **headers
		 ),
		 fields=fields,
		 _req_kwargs=_req_kwargs,
		 dict=dict
		)

		if self._DEBUG >= 2:
			try:
				print("JSON:       ", json.loads(r.data))
			except (UnicodeDecodeError,json.decoder.JSONDecodeError):
				pass
		
		_processes={None: lambda r:r}
		
		_processes['DATA']=lambda r:(
		 r.data
		)
		
		_processes['STR']=lambda r,ak=([],{}),d=_processes['DATA']:(
		 d(r).decode(*ak[0],**ak[1])
		)
		 
		_processes['JSON']=lambda r,s=_processes['STR']:(
		 json.loads( s(r) )
		)
		
		_processes['RESTRESP']=lambda r,j=_processes['JSON']:(
		 j(r)[ 'response' ]
		)
		 
		_processes['BYTESIO']=lambda r,d=_processes['DATA']:(
		 BytesIO( d(r) )
		)
		 
		_processes['ZIPFILE']=lambda r,b=_processes['BYTESIO']:(
		 ZipFile( b(r) )
		)
		 
		_processes['UNZIPFILES']=lambda r,z=_processes['ZIPFILE'],read=(lambda obj:obj.read()):(
		 (
		  lambda Z:(
		   [ read(Z.open(n)) for n in Z.namelist() ]
		  )
		 )( z(r) )
		)
		
		_processes['UNZIPXMLS']=lambda r,u=_processes['UNZIPFILES'],passthru=_processes[None]:(
		 [etree.parse(obj) for obj in u(r, read=passthru)]
		)
		
		if _PROCESS in _processes:
			_PROCESS=_processes[_PROCESS]
		elif _PROCESS == "_AUTO":
			_PROCESS=(
			 
			 _processes['DATA'] if (
			  method=='POST' or u.endswith('download')
			 )
			 
			 else
			 _processes['JSON'] if (
			  method=='GET'
			 )
			 
			 else
			 _processes[None]
			 
			)
		#elif callable(_PROCESS):
		#	pass
		
		return _PROCESS(r)

	def login(self, username, password):
		#TODO: make this interactive? Or something?
		
		#TODO: Client Certificate support
		# https://docs.tenable.com/sscv/api/System.html#SystemGET
		
		t,ch = self.get(
		 'token',
		 method='POST',
		 fields={
		  'username': username,
		  'password': password
		 },
		 _PROCESS=lambda r: (
		  json.loads(r.data.decode())['response']['token'],
		  r.headers['Set-Cookie']
		 )
		)
		
		self._token['token'] = t
		self._token['cookies']= self._chl2cd([ch])
		
	
#TODO: look up information about contextlib
	def __enter__(self):
		return self #TODO
		# Nothing needed...?
		#Is this where login goes?
		#What's the "pythonic" way to implement this?
		#Should I be prepared for "with SecurityCenterAPI(hostname) as SC",
		# or is that misuse? (i.e., is ContextManager even compatible with deferred login?)
	def __exit__(self, exc_type, exc_value, traceback):
		if self._token['token']:
			self.get('token', method='DELETE')
		if exc_type is not None:
			print(exc_type, exc_value, traceback)
			raise exc_type

def _raise_http_json(msg_dict):
	raise urllib3.exceptions.HTTPError(
	 '\n'.join(['{}\t{}'.format(
	   k, msg_dict[k]
	  ) for k in msg_dict
	 ])
	)

if __name__ == "__main__":
	quit("Please use the API!")
