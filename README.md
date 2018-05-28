# Security Center suite

[SecurityCenter \[REST\]](https://docs.tenable.com/sccv/api/index.html) and [Nessus \[XML scan report, version 2\]](http://static.tenable.com/documentation/nessus_v2_file_format.pdf) bindings for Python 3  
_(Tested **exclusively** on Python 3.6.3, RHEL6 x86_64)_

## Installation:

#### Option a

legacy eggmode, requires fewer dependencies but doesn't install as cleanly, so is harder and less reliable to uninstall:

	#apt-get install python3-setuptools
	#yum install rh-python36-python{,-setuptools} && ln -vsf '../../../opt/rh/rh-python36/root/usr/bin/python3' /usr/local/bin/
	
	python3 setup.py install --user   #remove --user if you are doing this as root

#### Option b

ｆｕｔｕｒｅ wheel, requires more dependencies but installs+uninstalls more cleanly and reliably:

	#apt-get install python3-pip
	#yum install rh-python36-python{,-pip} && ln -vsf '../../../opt/rh/rh-python36/root/usr/bin/python3' /usr/local/bin/
	
	python3 setup.py clean bdist_wheel
	python3 -m pip install dist/*.whl

## Usage:

	from scsuite.sc import SecurityCenterAPI
	from scsuite.nessus import dict1_from_xmlv2_root

(Please see [main.py](main.py) for example usage)

**This API is currently NOT STABLE!**

## Uninstallation:

#### Option a

**Only** works for uninstalling egg:

1. Find and delete `scsuite*.egg`; it's probably in either 
 a) `~/.local/lib/python3*/site-packages/`
 b) `/usr/local/lib/python3*/dist-packages/`
 c) `/opt/rh/rh-python36/root/usr/lib/python3.6/site-packages/`
2. `sed -i '/scsuite.*/d' "${folder_from_step_1}/easy-install.pth"`

#### Option b:

Works for uninstalling egg _or_ wheel:

	python3 -m pip uninstall scsuite #If this doesn't work, try restarting your shell or relogging/rebooting
