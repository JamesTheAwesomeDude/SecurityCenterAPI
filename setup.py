# https://packaging.python.org/tutorials/packaging-projects/#creating-setup-py

import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="scsuite",
	version="0.1.1",
	author="James Edington",
	author_email="james.edington@peraton.com",
	description="Collection of libraries for me to interface with SecurityCenter+Nessus",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/JamesTheAwesomeDude/SecurityCenterSuite",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3 :: Only",
		"Operating System :: POSIX :: Linux",
		"License :: OSI Approved :: MIT License",
		"Topic :: Security",
		"Topic :: Internet :: WWW/HTTP :: Dynamic Content ::: CGI Tools/Libraries"
	],
)

