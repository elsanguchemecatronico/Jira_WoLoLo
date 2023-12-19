# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 11:41:27 2023

@author: arovero
"""

import json

class saved_issues():
	def __init__(self,file):
		self.__file = file
		self.data = self.load()

	def load(self):
		with open(self.__file,'r',encoding = 'utf-8') as f:
			self.data = json.load(f)
		return self.data

	def save(self):
		with open(self.__file,'w',encoding = 'utf-8') as f:
			json.dump(self.data,f,indent = 4,ensure_ascii = True)

#	def get(self):
#		return self.__data

# =============================================================================
# s = saved_issues('saved.json')
# print(s.data)
# s.data['Licencia']['comment'] = 'Médico'
# s.save()
# print('===============================')
# print(s.data)
# =============================================================================
