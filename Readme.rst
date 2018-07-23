=====================
pySecurityCentersuite
=====================

| `SecurityCenter [REST]`__ and `Nessus [XML scan report, version 2]`__ bindings for Python 3
| *(Tested EXCLUSIVELY on Python 3.6.3, RHEL6 x86_64)*

.. __: https://docs.tenable.com/sccv/api/index.html
.. __: https://static.tenable.com/documentation/nessus_v2_file_format.pdf

Installation:
#############

::

	#apt-get install python3-pip
	#yum install rh-python36-python{,-pip} && ln -vsf '../../../opt/rh/rh-python36/root/usr/bin/python3' /usr/local/bin/
	
	python3 -m pip install "${source}"

Where ``"${source}"`` is one of:

a. A URL pointing to the ``.tar.gz`` of the desired version (or a path to one)

b. A local path to either this source code tree, or a compiled ``.whl`` file

c. Probably some other stuff; pip is pretty smart.

Usage:
######

Try the following (type it in manually, in REPL, for most effective learning) and you'll be able to grok it in no time::

	from scsuite.sc import SecurityCenterAPI
	from scsuite.nessus import dict1_from_xmlv2_root
	S=SecurityCenterAPI('localhost')
	S.login('securitymanager', 'p@$$w0rd')
	r=S.get('scanResult', _PROCESS='RESTRESP')
	id=r['usable'][-1]['id']
	x=S.get('scanResult/{id}/download'.format(id=id), _PROCESS='UNZIPFILES')[0]
	from lxml import etree
	r=dict1_from_xmlv2_root(etree.fromstring(x))
	#Example: count vulnerabilities
	vulnsbysev=[0]*6
	for id,res in r.items():
		lvl=int(res['severity'])
		vulnsbysev[lvl]+=1

.. todo:: more comprehensive documentation

.. warning:: This API is currently NOT STABLE!

Uninstallation:
###############

::

	python3 -m pip uninstall scsuite

(If this doesn't `seem` to work, try restarting your shell or relogging/rebooting)
