"""
	U.S. Environmental Protection Agency - Ecosystem Goods and Services (egs)
	
	web service that returns JSON formatted data that navigates starting with Seven Enviroatlas Benefit Categories
	
	Note: requires using a python 2.7 interpreter
	Note: testing on the command line is controlled in section that tests if environmental variable 'GATEWAY_INTERFACE' is set

	Jimmy Bisese
	Tetra Tech, Inc.
	2018-March-29
	
"""
import os.path
import sys
import json
from collections import OrderedDict
import cgi
import cgitb
cgitb.enable()
try:
	import ConfigParser
	config = ConfigParser.SafeConfigParser()
	config.optionxform = str
except:
	import configparser
	config = configparser.SafeConfigParser()
	config.optionxform = str
	
root_path = os.path.split(os.path.abspath(__file__))[0]

lib_path = os.path.join(root_path, 'lib')

sys.path.append(lib_path)

config_file = os.path.join(lib_path, 'epa_egs.config')

if not os.path.exists(config_file):
	raise IOError('Unable to find configuration file.\n\t%s' % (config_file))

try:
	# feed in the value of 'root' which is one folder above the current script folder
	config.add_section('PATHS')
	config.set('PATHS', 'root', root_path)
	
	with open(config_file) as f:
		config.readfp(f)
		
	custom_text_file = config.get('PATHS', 'egs_custom_text_file')
		
	with open(custom_text_file) as f:
		config.readfp(f)
except:
	ex = sys.exc_info()
	raise IOError('Unable to read configuration file.\n\t%s' % (ex[1]))

from BenefitTree import BenefitTree

gateway = BenefitTree()

gateway.config = config

def main():
	
	gateway.data_path = config.get('PATHS', 'data_directory')
	
	gateway.egs_data_file = config.get('PATHS',  'egs_data_file')
	
	gateway.egs_literature_data_file = config.get('PATHS',  'egs_literature_data_file')

	gateway.benefit_categories_ordered_list = config.get('ORDERED_LISTS',  'benefit_categories')
	
	gateway.ecosystem_ordered_list = config.get('ORDERED_LISTS',  'ecosystems')
	
	gateway.contribution_pathway_ordered_list = config.get('ORDERED_LISTS',  'contribution_pathways')

	arguments = cgi.FieldStorage()
	
	'''
		set values for testing on the command line.  when run as a web service, 
		the variable will be set and this block skipped.  On the command line this is used to pass in arguments for testing.

		values are set in the epa_egs.config file
		
	'''
	if not 'GATEWAY_INTERFACE' in os.environ:
		for name, value in {
			"benefit_category" : config.has_option('TESTING','benefit_category') and config.get('TESTING','benefit_category') or None,
			"ecosystem_type": config.has_option('TESTING','ecosystem_type') and config.get('TESTING','ecosystem_type') or None,
			"contribution_pathway": config.has_option('TESTING','contribution_pathway') and config.get('TESTING','contribution_pathway') or None,
			"benefit_type": config.has_option('TESTING','benefit_type') and config.get('TESTING','benefit_type') or None,
			"data_layer": config.has_option('TESTING','data_layer') and config.get('TESTING','data_layer') or None,
			}.items():
			if (value):
				arguments.list.append(cgi.MiniFieldStorage(name, value))
	
	'''
		return JSON data based on the highest level filter.
		
		Note: the method names reflect the name of the children available based on the users arguments.
		For example, if 'ecosystem_type' is in the arguments, then 'benefit_category' is also available, 
		and there is enough information to figure out which 'contribution_pathway' data to return

	'''
	data = OrderedDict()
	
	if 'data_layer' in arguments:
		data = gateway.data_layer_details(arguments.getvalue('data_layer'), 
											arguments.getvalue('benefit_type'),
											arguments.getvalue('contribution_pathway'), 
											arguments.getvalue('ecosystem_type'), 
											arguments.getvalue('benefit_category'))
	elif 'benefit_type' in arguments:
		data = gateway.data_layer(arguments.getvalue('benefit_type'),
									arguments.getvalue('contribution_pathway'), 
									arguments.getvalue('ecosystem_type'), 
									arguments.getvalue('benefit_category'))
	elif 'contribution_pathway' in arguments:
		data = gateway.benefit_type(arguments.getvalue('contribution_pathway'), 
									arguments.getvalue('ecosystem_type'), 
									arguments.getvalue('benefit_category'))
	elif 'ecosystem_type' in arguments:
		data = gateway.contribution_pathway(arguments.getvalue('ecosystem_type'), 
									arguments.getvalue('benefit_category'))
	elif 'benefit_category' in arguments:
		data = gateway.ecosystem_type(arguments.getvalue('benefit_category'))
	else:
		data = gateway.benefit_categories()

	if not 'GATEWAY_INTERFACE' in os.environ:
		print(json.dumps(data, indent=4, default=lambda x: None))
	else:
		print('Content-Type: application/json')
		print('')
		print(json.dumps(data, default=lambda x: None))

if __name__ == '__main__':
	
	main()