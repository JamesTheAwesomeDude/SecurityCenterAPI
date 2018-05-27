#!/usr/bin/env python3

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

def parse_xml_root(root, v=None):
	if v is None:
		# We'll have to return this, once we finish making it
		vulnerabilities={}
	else:
		# We've given an existing dict to update
		vulnerabilities=v
	
	for block in root:
		if block.tag == "Report":
			for report_host in block:
				host_properties_dict={}
				
#				for report_item in report_host:
#					if report_item.tag == "HostProperties":
#						for host_properties in report_item:
#							host_properties_dict[host_properties.attrib['name']] = host_properties.text
				
				for report_item in report_host:
					if report_item.tag == "HostProperties":
						for host_properties in report_item:
							host_properties_dict[host_properties.attrib['name']] = host_properties.text
				
					if 'pluginName' in report_item.attrib:
						vuln_id = (
						   report_host.attrib['name'],
						   int(report_item.attrib['port']),
						   report_item.attrib['protocol'],
						   int(report_item.attrib['pluginID'])
						)
						
						if vuln_id not in vulnerabilities:
							vulnerabilities[vuln_id]={}
						
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
									vulnerabilities[vuln_id]['plugin_output'] = []
								if param.text not in vulnerabilities[vuln_id]['plugin_output']:
									vulnerabilities[vuln_id]['plugin_output'].append(param.text)
							else:
								if param.tag in single_params:
									vulnerabilities[vuln_id][param.tag] = param.text
								else:
									if param.tag not in vulnerabilities[vuln_id]:
										vulnerabilities[vuln_id][param.tag] = []
									if param.text not in vulnerabilities[vuln_id][param.tag]:
										vulnerabilities[vuln_id][param.tag].append(param.text)
						
						for param in host_properties_dict:
							vulnerabilities[vuln_id][param] = host_properties_dict[param]
	if v is None:
		return vulnerabilities

def __main__(argv=[]):
	#TODO: passing .nessus files on the command-line
	raise NotImplementedError

if __name__=="__main__":
	quit(__main__())
