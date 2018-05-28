#!/usr/bin/env python3

def dict1_from_xmlv2_root(root, v=None):
	#Adapted/stolen from:
	# https://avleonov.com/2017/01/25/parsing-nessus-v2-xml-reports-with-python/
	single_params = [
	 "agent",
	 "cvss3_basescore", "cvss3_temporal_score", "cvss3_temporal_vector", "cvss3_vector",
	 "description",
	 "exploit_available",
	 "exploitability_ease",
	 "exploited_by_nessus",
	 "fname",
	 "in_the_news",
	 "vuln_publication_date","patch_publication_date",
	 "plugin_name", "plugin_publication_date", "plugin_modification_date", "plugin_type",
	 "script_version",
	 "see_also",
	 "solution",
	 "synopsis"
	]
	
	if v is None:
		# We're to create+return a new dict
		vulnerabilities={}
	else:
		# We've given an existing dict to update
		vulnerabilities=v
	
	for tag in filter(lambda t: t.tag=='Report', root): # We only process <Report> nodes, filter out everything else
		for report_host in tag:
			host_properties_dict=dict()
			
			for report_item in report_host:
				if report_item.tag == "HostProperties":
					for host_properties in report_item:
						host_properties_dict[host_properties.attrib['name']] = host_properties.text
			
			for report_item in report_host:
				if 'pluginName' in report_item.attrib:
					vuln_id = '|'.join((
					   report_host.attrib['name'],
					   report_item.attrib['port'],
					   report_item.attrib['protocol'],
					   report_item.attrib['pluginID']
					))
					
					if vuln_id not in vulnerabilities:
						vulnerabilities[vuln_id]=dict()
					
					vulnerabilities[vuln_id].update([
					   (key, report_item.attrib[key])
					   for key in [
					      'port',
					      'pluginName',
					      'pluginFamily',
					      'pluginID',
					      'svc_name',
					      'protocol',
					      'severity',
					   ]
					])
					
					for param in report_item:
						if param.tag == "risk_factor":
							vulnerabilities[vuln_id]['riskFactor'] = param.text
							vulnerabilities[vuln_id]['host'] = report_host.attrib['name']
						elif param.tag == "plugin_output":
							if "plugin_output" not in vulnerabilities[vuln_id]:
								vulnerabilities[vuln_id]['plugin_output'] = list()
							if param.text not in vulnerabilities[vuln_id]['plugin_output']:
								vulnerabilities[vuln_id]['plugin_output'].append(param.text)
						else:
							if param.tag in single_params:
								vulnerabilities[vuln_id][param.tag] = param.text
							else:
								if param.tag not in vulnerabilities[vuln_id]:
									vulnerabilities[vuln_id][param.tag] = list()
								if param.text not in vulnerabilities[vuln_id][param.tag]:
									vulnerabilities[vuln_id][param.tag].append(param.text)
					
					for param in host_properties_dict:
						vulnerabilities[vuln_id][param] = host_properties_dict[param]
	if v is None:
		return vulnerabilities

def __main__(argv):
	from lxml import etree
	from json import dump
	with open(argv[1]) as fd:
		d=parse_xml_root(etree.parse(fd).getroot())
	dump(
	 dict([
	  (k,d[k])
	  for k in d if argv[2] in k
	 ]) if len(argv)>2 else d,
	 stdout, indent=2
	)

if __name__=="__main__":
	from sys import argv,stdout
	quit(__main__(argv))
