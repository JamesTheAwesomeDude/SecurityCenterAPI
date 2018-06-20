# https://packaging.python.org/tutorials/packaging-projects/#creating-setup-py

import setuptools

with open("Readme.rst", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="scsuite",
	version="1.0.1b1",
	author="James Edington",
	author_email="james.edington@peraton.com",
	description="Collection of libraries for me to interface with SecurityCenter+Nessus",
	long_description=long_description,
	long_description_content_type="text/x-rst",
	url="https://github.com/JamesTheAwesomeDude/pySecurityCenterSuite",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3 :: Only",
		"Operating System :: POSIX :: Linux",
		"License :: OSI Approved :: MIT License",
		"Topic :: Security",
		"Topic :: Internet :: WWW/HTTP :: Dynamic Content ::: CGI Tools/Libraries"
	],
)

