"""

	U.S. Environmental Protection Agency - Ecosystem Goods and Services (egs)
	
	web service that returns JSON formatted data containing ecosystem goods and services relations and literature review.
	
	Note: tested using a python 2.7 interpreter, but known to compile on 3.6
	Note: testing on the command line is controlled in section that tests if environmental variable 'GATEWAY_INTERFACE' is set

	Jimmy Bisese
	Tetra Tech, Inc.
	2018-March-29
	
"""

import os
import sys
import re
import csv
import logging
from collections import defaultdict,OrderedDict
from datetime import datetime as dt
import cgi
import cgitb
import json
import collections
def makehash():
	return collections.defaultdict(makehash)

try:
	import cPickle as pickle
except:
	import pickle

class BenefitTree(object):

	def __init__(self):
		'''
		Constructor
		'''
		self.args = None
		
		self.config = None
		
		self.data_path = None
		
		self.egs_data_file = None # ecosystem goods & services

		self.egs_data_file_pickle = None

		self.egs_data = defaultdict( dict )

		self.egs_literature_data_file = None # ecosystem goods & services literature review

		self.egs_literature_data_file_pickle = None

		self.egs_literature_data = OrderedDict() # defaultdict( dict )
		
		# this is an ordered list of the 7 broad benefit categories.  it gets read from the configuration file
		self.benefit_categories_ordered_list = None
		
		self.ecosystem_ordered_list = None
		
		# this is an ordered list of the Ecosystem Goods & Services
		self.contribution_pathway_ordered_list = None

	'''
		this is a bit of overkill, but it hides the fact that the lists are stored in a config file and need to be
		parsed a bit to make them into lists.
	'''
	@property
	def benefit_categories_ordered_list(self):
		return self.__benefit_categories_ordered_list

	@benefit_categories_ordered_list.setter
	def benefit_categories_ordered_list(self, benefit_categories_ordered_list):
		if benefit_categories_ordered_list == None:
			pass
		else:
			self.__benefit_categories_ordered_list = list(filter(None, (x.strip() for x in benefit_categories_ordered_list.splitlines())))

	@property
	def ecosystem_ordered_list(self):
		return self.__ecosystem_ordered_list

	@ecosystem_ordered_list.setter
	def ecosystem_ordered_list(self, ecosystem_ordered_list):
		if ecosystem_ordered_list == None:
			pass
		else:
			self.__ecosystem_ordered_list = list(filter(None, (x.strip() for x in ecosystem_ordered_list.splitlines())))

	@property
	def contribution_pathway_ordered_list(self):
		return self.__contribution_pathway_ordered_list

	@contribution_pathway_ordered_list.setter
	def contribution_pathway_ordered_list(self, contribution_pathway_ordered_list):
		if contribution_pathway_ordered_list == None:
			pass
		else:
			self.__contribution_pathway_ordered_list = list(filter(None, (x.strip() for x in contribution_pathway_ordered_list.splitlines())))

	
	
	
	'''
	
		update the text used in 'name' field on output so it is the complete, well-formed name.
	
		note: this is a bit risky. the way the string testing goes if you try and use a 'converted' string, the filter will fail.  
		seems weak.  you have to be sure to use the 'code' - not the 'name' for all processing
	'''
	def update_name(self, string_tx):
		
		switcher = self.config._sections['COMPLEX_NAMES']
		
		return switcher.get(string_tx, string_tx)

	@property
	def egs_data_file(self):
		return self.__egs_data_file

	@egs_data_file.setter
	def egs_data_file(self, egs_data_file):
		
		"""
			read the 'data_file' into an array - checks for a python 'pickle' version of the data file and 
			uses it if it exists, or creates it if it doesn't exist.
			
			Note: of this script is run using the python 3.6 interpreter, then the pickle file will be unreadable in python 2.7.
			You will have to delete the pickle file and run it using the 2.7 interpreter.
		"""
		def read_pickle():
			
			if not len(egs_data_file_pickle):
				raise ValueError('egs_data_file_pickle must be set before calling this function')
			if not os.path.exists(egs_data_file_pickle):
				raise IOError("Unable to find egs_data_file_pickle\n\t%s" % (egs_data_file_pickle))
			
			startTime = dt.now()
			pkl_file = open(egs_data_file_pickle, 'rb')

			[self.egs_data] = pickle.load(pkl_file)

			pkl_file.close()
			
			return
		
		def read():
	
			if not len(self.egs_data_file):
				raise ValueError('egs_data_file must be set before calling this function')
			if not os.path.exists(self.egs_data_file):
				raise IOError("Unable to find DATA file\n\t%s" % (self.egs_data_file))
			
			startTime = dt.now()

			try:
				with open(self.egs_data_file) as json_data:
					self.egs_data = json.load(json_data)
			except:
				cgitb.handler()
				sys.exit()
	
			row_count = 0
			try:
				'''
					create the pickle file for next time a user requests the file
				'''
				pickle_egs_data_file = self.egs_data_file.replace('.json', '.p')
				try:
					pickle.dump([self.egs_data], open(pickle_egs_data_file, 'wb'), pickle.HIGHEST_PROTOCOL)
				finally:
					pass
	
			except:
				cgitb.handler()
				sys.exit()
		
			return row_count
		
		if egs_data_file == None:
			pass
		else:
			egs_data_file_pickle = egs_data_file.replace('.json', '.p')
			
			# this will update the pickle file if the JSON file is newer
			if (os.path.exists(str(egs_data_file_pickle)) and 
				os.path.exists(str(egs_data_file)) and
				os.path.getmtime(str(egs_data_file_pickle)) < os.path.getmtime(str(egs_data_file))
				):
				os.remove(str(egs_data_file_pickle))
			
			if os.path.exists(str(egs_data_file_pickle)):
				read_pickle()
			elif os.path.exists(str(egs_data_file)):
				self.__egs_data_file = str(egs_data_file)
				read()
			else:
				raise IOError("Unable to find DATA file\n\t%s" % (egs_data_file))
			
	@property
	def egs_literature_data_file(self):
		return self.__egs_literature_data_file

	@egs_literature_data_file.setter
	def egs_literature_data_file(self, egs_literature_data_file):
		
		"""
			read the egs_literature_data_file into one array - self.egs_literature_data.
		"""
		def read_pickle():
			
			if not len(egs_literature_data_file_pickle):
				raise ValueError('egs_literature_data_file_pickle must be set before calling this function')
			if not os.path.exists(egs_literature_data_file_pickle):
				raise IOError("Unable to find egs_literature_data_file_pickle\n\t%s" % (egs_literature_data_file_pickle))
			
			startTime = dt.now()
			pkl_file = open(egs_literature_data_file_pickle, 'rb')

			[self.egs_literature_data] = pickle.load(pkl_file)

			pkl_file.close()
			
			return
		
		def read():
	
			if not len(self.egs_literature_data_file):
				raise ValueError('egs_literature_data_file must be set before calling this function')
			if not os.path.exists(self.egs_literature_data_file):
				raise IOError("Unable to find DATA file\n\t%s" % (self.egs_literature_data_file))
			
			startTime = dt.now()

			try:
				with open(self.egs_literature_data_file) as json_data:
					self.egs_literature_data = json.load(json_data)
			except:
				cgitb.handler()
				sys.exit()
	
			row_count = 0
			try:
				'''
					create the pickle file for next time a user requests the file
				'''
				pickle_data_file = self.egs_literature_data_file.replace('.json', '.p')
				
				# this will update the pickle file if the JSON file is newer
				if (os.path.exists(str(pickle_data_file)) and 
					os.path.exists(str(self.egs_literature_data_file)) and
					os.path.getmtime(str(pickle_data_file)) < os.path.getmtime(str(self.egs_literature_data_file))
					):
					os.remove(str(pickle_data_file))
				
				try:
					pickle.dump([self.egs_literature_data], open(pickle_data_file, 'wb'), pickle.HIGHEST_PROTOCOL)
				finally:
					pass
	
			except:
				cgitb.handler()
				sys.exit()
		
			return row_count
		
		if egs_literature_data_file == None:
			pass
		else:
			egs_literature_data_file_pickle = egs_literature_data_file.replace('.json', '.p')
			if os.path.exists(str(egs_literature_data_file_pickle)):
				read_pickle()
			elif os.path.exists(str(egs_literature_data_file)):
				self.__egs_literature_data_file = str(egs_literature_data_file)
				read()
			else:
				raise IOError("Unable to find DATA file\n\t%s" % (egs_literature_data_file))

	'''
		rebuild the array using benefit_category -> ecosystem_type -> contribution_pathway -> benefit_type -> data_layer
	'''
	def reorder_array_pk_benefit_category_ecosystem_type_contribution_pathway_benefit_type_data_layer(self, json_data):
	
		data = makehash()
		for benefit_category in json_data.keys():
			for ecosystem_type in json_data[benefit_category].keys():
				for data_layer in json_data[benefit_category][ecosystem_type].keys():
					for contribution_pathway in json_data[benefit_category][ecosystem_type][data_layer]:
						
						# this will be 'supplier', 'driver' or 'demander'
						benefit_type = json_data[benefit_category][ecosystem_type][data_layer][contribution_pathway].title()
						
						'''
							check to make sure not to overwrite existing data.
						'''
						if data.get(benefit_category) and \
							data[benefit_category].get(ecosystem_type) and \
							data[benefit_category][contribution_pathway].get(ecosystem_type) and \
							data[benefit_category][ecosystem_type].get(benefit_type) and \
							data[benefit_category][ecosystem_type][contribution_pathway][benefit_type].get(data_layer):
							
							print ("problem. entry already exists.\n{0} -> {1} -> {2}".format(benefit_category, ecosystem_type, benefit_type, data_layer))
							
							exit()
						else:
							data[benefit_category][ecosystem_type][contribution_pathway][benefit_type][data_layer] = \
								json_data[benefit_category][ecosystem_type][data_layer][contribution_pathway]
		return data


	'''
		rebuild the array using data_layer -> benefit_type -> contribution_pathway -> ecosystem_type -> benefit_category  
	'''
	def reorder_array_pk_data_layer_benefit_type_contribution_pathway_ecosystem_type_benefit_category(self, json_data):
		data = makehash()

		for benefit_category in json_data.keys():
			for ecosystem_type in json_data[benefit_category].keys():
				for data_layer in json_data[benefit_category][ecosystem_type].keys():
					for contribution_pathway in json_data[benefit_category][ecosystem_type][data_layer]:
						
						# this will be 'supplier', 'driver' or 'demander'
						benefit_type = json_data[benefit_category][ecosystem_type][data_layer][contribution_pathway].title()
						
						'''
							check to make sure not to overwrite existing data.
						'''
						if data.get(benefit_category) and \
							data[benefit_category].get(ecosystem_type) and \
							data[benefit_category][contribution_pathway].get(ecosystem_type) and \
							data[benefit_category][ecosystem_type].get(benefit_type) and \
							data[benefit_category][ecosystem_type][contribution_pathway][benefit_type].get(data_layer):
							
							print ("problem. entry already exists.\n{0} -> {1} -> {2}".format(benefit_category, ecosystem_type, benefit_type, data_layer))
							
							exit()
						else:
							data[data_layer][benefit_type][contribution_pathway][ecosystem_type][benefit_category] = \
								json_data[benefit_category][ecosystem_type][data_layer]
		return data


	def benefit_categories(self):
		primary_key = 'benefit_category'
		
		data = OrderedDict()
		data['name'] = self.update_name(primary_key)
		data['children'] = []
		
		for benefit_category in self.benefit_categories_ordered_list:
			child_data = {
							'code': benefit_category, 
							'name': '%s' % (self.update_name(benefit_category)),
							'extended_text': self.extended_text(benefit_category),
							'primary_key': primary_key
						}
			data['children'].append(child_data)
			
		return data
	
	def extended_text(self, benefit_category, ecosystem_type = None, contribution_pathway = None, benefit_type = None ):
		string_tx = ''
		if contribution_pathway != None:
			string_tx = self.config.get('CONTRIBUTION_PATHWAY_TEXT',  contribution_pathway)

		elif ecosystem_type != None:
			# this one is slightly more complex, since there is boilderplate text before and after specific text
			ecosystem_tx = self.config.get('ECOSYSTEM_TYPE_TEXT',  ecosystem_type).lstrip('\n').rstrip('\n')
			boilderplate_tx = self.config.get('BOILERPLATE_TEXT', 'ecosystem').lstrip('\n').rstrip('\n')
			
			string_tx = boilderplate_tx.replace('#ECOSYSTEM_TX#', ecosystem_tx)

		elif benefit_type != None:
			string_tx = self.config.get('BENEFIT_TYPE_TEXT',  benefit_type).lstrip('\n').rstrip('\n')
		else:
			string_tx = self.config.get('BENEFIT_CATEGORIES_TEXT',  benefit_category)
		
		string_tx = string_tx.lstrip('\n')
		string_tx = string_tx.replace('\n', '<br>')
		
		return string_tx
	
	def ecosystem_type(self, benefit_category):
		primary_key = 'ecosystem_type'
		
		data = OrderedDict()
		data['name'] = self.update_name(primary_key)
		data['query'] = OrderedDict([
			('benefit_category', benefit_category),
		])
		data['children'] = []
		
		if benefit_category in self.egs_data.keys():
			for ecosystem_type in self.ecosystem_ordered_list:
				child_data = OrderedDict([
							('code', ecosystem_type),
							('name', '%s' % (ecosystem_type)),
							('extended_text', self.extended_text(benefit_category, ecosystem_type)),
							('primary_key', primary_key),
							('is_available', "True" if (ecosystem_type in self.egs_data[benefit_category].keys()) else "False")
						])
				data['children'].append(child_data)

		return data


	def contribution_pathway(self, ecosystem_type, benefit_category):
		primary_key = 'contribution_pathway'
		
		reordered_egs_data = self.reorder_array_pk_benefit_category_ecosystem_type_contribution_pathway_benefit_type_data_layer(self.egs_data)
		
		data = OrderedDict()
		data['name'] = self.update_name(primary_key)
		data['query'] = OrderedDict([
			('benefit_category', benefit_category),
			('ecosystem_type', ecosystem_type),
		])
		data['children'] = []
		
		if benefit_category in reordered_egs_data.keys():
			if ecosystem_type in reordered_egs_data[benefit_category].keys():
				for contribution_pathway in self.contribution_pathway_ordered_list:
					child_data = OrderedDict([
							('code', contribution_pathway),
							('name', '%s' % (self.update_name(contribution_pathway))),
							('extended_text', self.extended_text(benefit_category, ecosystem_type, contribution_pathway)),
							('primary_key', primary_key),
							('is_available', "True" if (contribution_pathway in reordered_egs_data[benefit_category][ecosystem_type].keys()) else "False")
						])
					data['children'].append(child_data)
					
		return data

	'''
		when benefit name is clicked, it returns benefit types.
	
		this function returns the benefit types, and the children of benefit types - which are data layers
		including the children is what causes the interface to open all sub-layers when benefit name is clicked
	'''
	def benefit_type(self, contribution_pathway, ecosystem_type, benefit_category):
		primary_key = 'benefit_type'
		
		reordered_egs_data = self.reorder_array_pk_benefit_category_ecosystem_type_contribution_pathway_benefit_type_data_layer(self.egs_data)
		
		data = OrderedDict()
		data['name'] = self.update_name(primary_key)
		data['query'] = OrderedDict([
			('benefit_category', benefit_category),
			('ecosystem_type', ecosystem_type),
			('contribution_pathway', contribution_pathway),
		])
		data['children'] = []
		data['literature'] = self.get_literature(ecosystem_type, benefit_category)
		
		if benefit_category in reordered_egs_data.keys():
			if ecosystem_type in reordered_egs_data[benefit_category].keys():
				if contribution_pathway in reordered_egs_data[benefit_category][ecosystem_type].keys():
					for benefit_type in reordered_egs_data[benefit_category][ecosystem_type][contribution_pathway].keys():
						
						child_data = OrderedDict([
							('code', benefit_type),
							('name', '%s' % (self.update_name(benefit_type))),
							('extended_text', self.extended_text(None, benefit_type=benefit_type.lower())),
							('primary_key', primary_key),
							('children', []),
						])
							
						data['children'].append(child_data)

		return data


	def data_layer(self, benefit_type, contribution_pathway, ecosystem_type, benefit_category):
		primary_key = 'data_layer'
		leader_tx = self.update_name('data_layer_leader_tx')
		
		data = OrderedDict()
		data['name'] = self.update_name(primary_key)
		data['query'] = OrderedDict([
			('benefit_category', benefit_category),
			('ecosystem_type', ecosystem_type),
			('contribution_pathway', contribution_pathway),
			('benefit_type', benefit_type),
		])
		data['children'] = []
		data['literature'] = self.get_literature(ecosystem_type, benefit_category)
		
		reordered_egs_data = self.reorder_array_pk_benefit_category_ecosystem_type_contribution_pathway_benefit_type_data_layer(self.egs_data)
		
		if benefit_category in reordered_egs_data.keys():
			if ecosystem_type in reordered_egs_data[benefit_category].keys():
				if contribution_pathway in reordered_egs_data[benefit_category][ecosystem_type].keys():
					if benefit_type in reordered_egs_data[benefit_category][ecosystem_type][contribution_pathway].keys():
						for data_layer in reordered_egs_data[benefit_category][ecosystem_type][contribution_pathway][benefit_type].keys():
							child_data = {
									'code': data_layer, 
									'name': '%s%s' % (leader_tx, data_layer),
									'primary_key': primary_key
							}
							data['children'].append(child_data)
							
		return data


	def data_layer_details(self, data_layer, benefit_type, contribution_pathway, ecosystem_type, benefit_category):
		primary_key = 'data_layer_details'
		
		data = OrderedDict()
		data['name'] = self.update_name(primary_key)
		data['data_layer'] = data_layer
		data['children'] = []
		data[primary_key] = []
		
		'''
			the array is organized using data_layer -> benefit_type -> contribution_pathway -> ecosystem_type -> benefit_category  
		'''
		reordered_egs_data = self.reorder_array_pk_data_layer_benefit_type_contribution_pathway_ecosystem_type_benefit_category(self.egs_data)
		
		# make sure you can find the data layer first
		if not data_layer in reordered_egs_data.keys():
			return data
		
		# make sure that this benefit type ('Demander', 'Supplier', 'Driver')
		if not benefit_type in reordered_egs_data[data_layer].keys():
			data['benefit_type'] = benefit_type
			data['is_available'] = False
			return data

		data['literature'] = self.get_literature(ecosystem_type, benefit_category)

		for contribution_pathway in self.contribution_pathway_ordered_list:
			
			child_data = {
					'code': contribution_pathway,
					'name': '%s' % (self.update_name(contribution_pathway)),
					'primary_key': 'contribution_pathway',
					'is_available': False,
					'children': []
			}
							
			if (contribution_pathway in reordered_egs_data[data_layer][benefit_type].keys() and 
				ecosystem_type in reordered_egs_data[data_layer][benefit_type][contribution_pathway].keys()):
				
				child_data['is_available'] = True
				
				for benefit_category in self.benefit_categories_ordered_list:
					is_available = benefit_category in reordered_egs_data[data_layer][benefit_type][contribution_pathway][ecosystem_type].keys()

					benefit_category_data = {
						'code': benefit_category, 
						'name': '%s' % (self.update_name(benefit_category)),
						'primary_key': 'benefit_category',
						'is_available': is_available
					}
					child_data['children'].append(benefit_category_data)

			data[primary_key].append(child_data)

		return data


	def get_literature(self, ecosystem_type, benefit_category):
		data = []
		if benefit_category in self.egs_literature_data.keys():
			if ecosystem_type in self.egs_literature_data[benefit_category].keys():
				child_data = OrderedDict([
							('query', OrderedDict([
								('benefit_category', benefit_category),
								('ecosystem_type', ecosystem_type),
							])),
							('code', benefit_category),
							('name', '%s: %s' % ('Literature', benefit_category)),
							('primary_key', 'literature'),
							('data', self.egs_literature_data[benefit_category][ecosystem_type]),
						])
				data.append(child_data)
				
		return data

if __name__ == '__main__':
	
	print ("this is a library")
	
	exit()

