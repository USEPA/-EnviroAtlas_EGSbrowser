# -*- coding: utf-8 -*-
"""
	Read a set of CSV text files and parse the text and create a single JSON file containing the 
	Ecosystem Goods and Services data

	Created on Thu Nov 12 11:12:06 2015
	
	@author: Jimmy Bisese


"""
import os
import io
import sys
import glob
import logging
import datetime
import tzlocal
try:
	import ConfigParser
	config = ConfigParser.SafeConfigParser()
	config.optionxform=str
except:
	import configparser
	config = configparser.SafeConfigParser()
	config.optionxform=str
import json
import argparse
import csv
import codecs
codecs.BOM_UTF8
import collections

def create_logger():
	log = logging.getLogger(__name__)
	out_hdlr = logging.StreamHandler(sys.stdout)
	out_hdlr.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', 
							datefmt='%Y-%m-%d %H:%M:%S ' + datetime.datetime.now(tzlocal.get_localzone()).strftime('%Z')))
	log.addHandler(out_hdlr)
	log.setLevel(logging.DEBUG)
	return log

# create logger
log = create_logger()

''' get these folder paths based on where the script is located in the file system '''
script_path = os.path.split(os.path.abspath(__file__))[0]	# <script_path>/script.py
lib_path 	= os.path.join(script_path, 'lib')				# <script_path>/lib/
root_path 	= os.path.split(script_path)[0]				    # ../<script_path>/

config_file = os.path.join(lib_path, 'epa_egs_backend.config')

if not os.path.exists(lib_path):
	raise IOError('Unable to find library directory. %s' % (lib_path))

sys.path.append(lib_path)

if not os.path.exists(config_file):
	raise IOError('Unable to find configuration file.\n\t%s' % (config_file))

try:
	# feed in the value of 'root' which is one folder above the current script folder
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

Read a set of CSV text files and parse the text and create a single JSON file containing the 
Ecosystem Goods and Services data

creates output file
	{0}

""".format(config.get('PATHS', 'ecosystem_goods_and_services_json'))

parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("-l", "--logger", nargs='?', choices=config.get('DEFAULTS', 'log_level_choices').split(','), \
						default=config.get('DEFAULTS', 'log_level'), 
						help='set the amount of messages to print to STDOUT. default is ' + config.get('DEFAULTS', 'log_level'))


def makehash():
	return collections.defaultdict(makehash)
log.setLevel(logging.DEBUG)
def main():

	args = parser.parse_args()

	log.setLevel(args.logger)
	
	# output file is JSON format
	json_file = config.get('PATHS', 'ecosystem_goods_and_services_json')
	
	# get a list of all the files
	data_path = config.get('PATHS', 'csv_document_path')

	os.chdir(data_path)
	
	files = glob.glob('*.csv')

	log.info('Reading {0} CSV (text) files from directory:\n\t{1}'.format(len(files), data_path))
	
	log.info('Writing JSON (text) file:\n\t{0}'.format(json_file))

	files.sort()
	
	output_data = makehash() # this structure auto-vivicates dictionary keys
	
	# read and process all the files
	for file_nm in files:
		source_data =	read_csv_file(os.path.join(data_path, file_nm))
		output_data.update(source_data)

	# dump the output_data into the output file in JSON format
	if sys.version_info[0] < 3:
		with io.open(json_file, 'wb') as outfile:
			json.dump(output_data, outfile, indent = 4, ensure_ascii=False)
	else:
		with io.open(json_file, 'w') as outfile:
			json.dump(output_data, outfile, indent = 4, ensure_ascii=False)
	
	log.info('Wrote JSON (text) file.   File Size {0}:\n\t{1}'.format(sizeof_fmt(os.path.getsize(json_file)), json_file))

	return 

def sizeof_fmt(num, suffix='B'):
	for unit in ['','K','M','G','Ti','Pi','Ei','Zi']:
		if abs(num) < 1024.0:
			return "%.f %s%s" % (num, unit, suffix)
		num /= 1024.0
	return "%.1f %s%s" % (num, 'Yi', suffix)

"""

	read the csv file and create a data array

"""
def read_csv_file(csv_file):
	csv_data = makehash()

	if not len(csv_file):
		log.warn('you must set the csv_file before calling this function')
		exit()

	log.debug('Reading: {0}'.format(os.path.basename(csv_file)))
	try:
		infile = codecs.open(csv_file, 'r', encoding="utf-8-sig")  # CSV file
		reader = csv.DictReader(infile)
	except:
		ex = sys.exc_info()
		log.error('Exception 641: %s: %s' % (ex[0], ex[1]))
		exit()

	row_count = 0
	try:
		for row in reader:
			row_count += 1
			
			if len(row['Benefit_Category']) and len(row['Ecosystem_Types']) and len(row['Data_Layers']):
				clean_row = {}
				for f in row:
					if f == 'Benefit_Category' or f == 'Ecosystem_Types' or f == 'Data_Layers':
						continue
					
					if len(row[f]) > 0:
						clean_row[f] = row[f]
						
				'''
					check to make sure not to overwrite existing data.  will be more important in other orders
				'''
				if csv_data.get(row['Benefit_Category']) and \
					csv_data[row['Benefit_Category']].get(row['Ecosystem_Types']) and \
					csv_data[row['Benefit_Category']][row['Ecosystem_Types']].get(row['Data_Layers']):
					
					print("problem. entry already exists.\n{0} -> {1} -> {2}".format(row['Benefit_Category'],row['Ecosystem_Types'],row['Data_Layers']))
					
					exit()
				else:
					csv_data[row['Benefit_Category']][row['Ecosystem_Types']][row['Data_Layers']] = clean_row
					
		return csv_data
	except:
		print("Unexpected error:", sys.exc_info()[0])
		raise

if __name__ == '__main__':
	
	main()
