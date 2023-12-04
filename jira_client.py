# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 14:04:50 2023

@author: arovero



Bad domain
ERROR:  Site temporarily unavailable

Bad user or token.
ERROR:  Client must be authenticated to access this resource.

"""

from jira import JIRA
import jira
from dotenv import dotenv_values

class jira_client():
	def __init__(self):
		self.client = None
		self.me = ''
		self.issues = []

		config = dotenv_values('.env')

		server = config['SERVER']
		email = config['EMAIL']
		token = config['TOKEN']

		jira_options = {'server':server}
		credentials = (email,token)

		try:
			# This line catches an error in the server variable.
			self.client = JIRA(options = jira_options,basic_auth = credentials)

			# While these 2 catch errors in the credencials variables.
			me = self.client.current_user()
			self.me = self.client.user(me)

		except jira.JIRAError as e:
			print('ERROR: ',e.text)
			raise Exception('Sorry. Server or user credentials are incorrect.')


	def update_issues(self):
		jql = 'worklogAuthor = currentUser()'
		issues = self.client.search_issues(jql_str = jql,maxResults = 0)
		self.issues = [i.key for i in issues]

	def get_issues(self):
		return self.issues

	def upload_worklog(self,issue,time,comment = '',date = ''):
		self.client.add_worklog(
			issue = issue,
			timeSpent = time,
			comment = comment,
			started = date)

#yo = jira_client()
#yo.update_issues()
#print(yo.get_issues())
