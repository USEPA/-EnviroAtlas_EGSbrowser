# -*- coding: utf-8 -*-
"""
	read a set of MS Word files and parse the text and create a single JSON file containing the 
	Ecosystem Goods and Services Literature review
	
	@author: Jimmy Bisese
	
	Note: Python 2.7 is required.  Encoding not completely working in python > 2.7

"""
import os
import io
import sys
import glob
import datetime
import tzlocal
import logging
try:
	import ConfigParser
	config = ConfigParser.SafeConfigParser()
	config.optionxform = str
except:
	import configparser
	config = configparser.SafeConfigParser()
	config.optionxform = str
import json
import argparse

import codecs
codecs.BOM_UTF8
from collections import OrderedDict
import docx

def create_logger():
	log = logging.getLogger(__name__)
	out_hdlr = logging.StreamHandler(sys.stdout)
	out_hdlr.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', 
							datefmt='%Y-%m-%d %H:%M:%S ' + datetime.datetime.now(tzlocal.get_localzone()).strftime('%Z')))
	log.addHandler(out_hdlr)
	log.setLevel(logging.INFO)
	return log

# create logger
log = create_logger()

''' get these folder paths based on where the script is located in the file system '''
script_path = os.path.split(os.path.abspath(__file__))[0]	# <script_path>/script.py
lib_path 	= os.path.join(script_path, 'lib')				# <script_path>/lib/
root_path 	= os.path.split(script_path)[0]				    # ../<script_path>/

config_file = os.path.join(lib_path, 'epa_egs_backend.config')

if not os.path.exists(lib_path):
	raise IOError('Unable to find library folder. %s' % (lib_path))

sys.path.append(lib_path)

if not os.path.exists(config_file):
	raise IOError('Unable to find configuration file.\n\t%s' % (config_file))

try:
	config.add_section('PATHS')
	config.set('PATHS', 'root_path', root_path)
	
	with open(config_file) as f:
		config.readfp(f)
except:
	ex = sys.exc_info()
	raise IOError('Unable to read configuration file.\n\t%s' % (ex[1]))

"""
 process all command line arguments
"""
description = """

Read a set of MS Word files and parse the text and create a single JSON file containing the 
Ecosystem Goods and Services Literature review

creates output file
	{0}


Note: there is something confusing about reading MS Word files and the use of ASCII and Unicode
		if this needs to run in python 3.6 the encoding stuff needs to be worked out first

""".format(config.get('PATHS', 'egs_literature_json'))

parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("-l", "--logger", nargs='?', choices=config.get('DEFAULTS', 'log_level_choices').split(','), \
						default=config.get('DEFAULTS', 'log_level'), 
						help='set the amount of messages to print to STDOUT. default is ' + config.get('DEFAULTS', 'log_level'))


"""

	normalize the names (strings) to make them consistent between all the files

"""
normalize_ecosystems = dict(config.items('NORMALIZE_ECOSYSTEMS'))
normalize_categories = dict(config.items('NORMALIZE_CATEGORIES'))
	
def main():

	args = parser.parse_args()

	log.setLevel(args.logger)

	# output file is JSON format
	json_file = config.get('PATHS', 'egs_literature_json')
	
	# get a list of all the files
	word_document_path = config.get('PATHS', 'word_document_path')

	os.chdir(word_document_path)
	
	files = glob.glob('*.docx')
	
	log.info('Reading %d MS Word Documents from directory:\n\t%s\n' % (len(files), word_document_path))
	
	log.info('Writing JSON (text) file:\n\t%s\n' % (json_file))
	
	source_data = OrderedDict()
	
	# read all the files
	for file_nm in files:
		if file_nm.find('~', 0) > -1:
			continue
		source_data[file_nm] = read_docx_file(os.path.join(word_document_path, file_nm))

	output_data = OrderedDict()

	# process the data from each file
	for file_nm in source_data:

		ecosystem_type = source_data[file_nm]['ecosystem_type']
		benefit_category = source_data[file_nm]['category']
		
		if not benefit_category in output_data.keys():
			output_data[benefit_category] = {}
		
		output_data[benefit_category][ecosystem_type] = source_data[file_nm]
		output_data[benefit_category][ecosystem_type].pop('category')
		output_data[benefit_category][ecosystem_type].pop('ecosystem_type')
	
	# dump the output_data into the output file in JSON format
	if sys.version_info[0] < 3:
		with io.open(json_file, 'wb') as outfile:
			json.dump(output_data, outfile, indent = 4, ensure_ascii=False)
	else:
		with io.open(json_file, 'w') as outfile:
			json.dump(output_data, outfile, indent = 4, ensure_ascii=False)
	
	log.info('Wrote JSON (text) file.   File Size {0}:\n\t{1}'.format(sizeof_fmt(os.path.getsize(json_file)), json_file))

	return 

def read_docx_file(docx_file):
	docx_data = OrderedDict()
	docx_data['file'] = docx_file
	docx_data['ecosystem_type'] = ''
	docx_data['category'] = ''
	
	# 8 Contribution Pathways
	docx_data['Materials'] = OrderedDict()
	docx_data['Nutrition'] = OrderedDict()
	docx_data['Energy'] = OrderedDict()
	docx_data['Mediation_of_Nuisances'] = OrderedDict()
	docx_data['Mediation_of_Flows'] = OrderedDict()
	docx_data['Experiences'] = OrderedDict()
	docx_data['Maintenance_of_Conditions'] = OrderedDict()
	docx_data['Interactions_with_Ecosystems'] = OrderedDict()
	
	docx_data['sources'] = []
	docx_data['orphan'] = []
	
	if not len(docx_file):
		log.warn('you must set the docx_file before calling this function')
		exit()

	document = None
	
	log.debug('Reading: %s' % (os.path.basename(docx_file)))
	
	try:
		document = docx.Document(docx_file)  # DOCX file
	except:
		ex = sys.exc_info()
		log.error('Exception 64d1: %s: %s' % (ex[0], ex[1]))
		exit()

	row_count = 0
	in_set = ''
	
	try:
		for paragraph in document.paragraphs:
			row_count += 1
			
			paragraph_text = paragraph.text
			paragraph_text = paragraph_text.encode('ascii', 'ignore')
			
			if paragraph_text == "" or paragraph_text.isspace():
				continue
			else:
				if paragraph_text.find('Supplier', 0, 15) > -1:
					if paragraph_text.find('not applicable') > -1:
						docx_data[in_set]['supplier'] = 'NA'
					else:
						paragraph_text = paragraph_text[10:]
						docx_data[in_set]['supplier'] = paragraph_text

				elif paragraph_text.find('Driver', 0, 10) > -1:
					if paragraph_text.find('not applicable') > -1:
						docx_data[in_set]['driver'] = 'NA'
					else:
						docx_data[in_set]['driver'] = paragraph_text[8:]
						
				elif paragraph_text.find('Demander', 0, 10) > -1:
					if paragraph_text.find('not applicable') > -1:
						docx_data[in_set]['demander'] = 'NA'
					else:
						docx_data[in_set]['demander'] = paragraph_text[10:]
						
				elif paragraph_text.find('Ecosystem Type: ') > -1:
					paragraph_text = paragraph_text.replace('Ecosystem Type: ','')
					docx_data['ecosystem_type'] = normalize_ecosystems[paragraph_text.strip()]
						
				elif paragraph_text.find('Category:', 0, 12) > -1:
					paragraph_text = paragraph_text.replace('Category: ','')
					docx_data['category'] = normalize_categories[paragraph_text.strip()]
					
				elif paragraph_text.find('Materials', 0, 20) > -1:
					in_set = 'Materials'
				elif paragraph_text.find('Nutrition', 0, 20) > -1:
					in_set = 'Nutrition'
				elif paragraph_text.find('Energy', 0, 10) > -1:
					in_set = 'Energy'
				elif paragraph_text.find('Mediation of Waste, Toxics, and Other Nuisances', 0) > -1:
					in_set = 'Mediation_of_Nuisances'
				elif paragraph_text.find('Mediation of Flows', 0) > -1:
					in_set = 'Mediation_of_Flows'
				elif paragraph_text.find('Maintenance of Physical, Chemical, and Biological Indicators', 0) > -1:
					in_set = 'Maintenance_of_Conditions'
				elif paragraph_text.find('Spiritual, Symbolic, Religious, and Social Experiences', 0) > -1:
					in_set = 'Experiences'
				elif paragraph_text.find('Physical and Intellectual Interactions w/ Biota, Ecosystems, and Land/Seascapes', 0) > -1:
					in_set = 'Interactions_with_Ecosystems'
				
				# two files have different cases
				elif paragraph_text.find('Mediation of waste, toxics, and other nuisances', 0) > -1:
					in_set = 'Mediation_of_Nuisances'
				elif paragraph_text.find('Mediation of flows', 0) > -1:
					in_set = 'Mediation_of_Flows'
				elif paragraph_text.find('Maintenance of physical, chemical, and biological indicators', 0) > -1:
					in_set = 'Maintenance_of_Conditions'
				elif paragraph_text.find('Spiritual, symbolic, religious, and social experiences', 0) > -1:
					in_set = 'Experiences'
				elif paragraph_text.find('Physical and intellectual interactions w/ biota, ecosystems, and land/seascapes', 0) > -1:
					in_set = 'Interactions_with_Ecosystems'					
				elif paragraph_text.find('Sources:', 0) > -1:
					in_set = 'sources'
					
				elif in_set == 'sources':
					docx_data['sources'].append(paragraph_text)
				else:
					print ("Orphan: " + paragraph_text)
					docx_data['orphan'].append(paragraph_text)

					
		return docx_data
	except:
		print("Unexpected error:", sys.exc_info()[0])
		raise

def sizeof_fmt(num, suffix='B'):
	for unit in ['','K','M','G','Ti','Pi','Ei','Zi']:
		if abs(num) < 1024.0:
			return "%.f %s%s" % (num, unit, suffix)
		num /= 1024.0
	return "%.1f %s%s" % (num, 'Yi', suffix)

if __name__ == '__main__':

	if sys.version_info[0] > 2.7:
		raise Exception("Python 2.7 is required.  Encoding not completely working in python > 2.7")

	main()
