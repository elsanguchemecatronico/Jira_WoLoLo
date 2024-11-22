# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 14:04:50 2023

@author: arovero





https://jira.readthedocs.io/examples.html#issues

https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-group-issue-worklogs



Acá dejé una consulta por los 5000 worklogs que se trae la funcion- worklogs().
https://community.atlassian.com/t5/Jira-Software-questions/Return-more-than-5000-worklogs-for-a-given-issue/qaq-p/2215910#U2590805


Creé un nuevo ticket
https://community.atlassian.com/t5/Jira-questions/Return-more-than-5000-worklogs-for-a-given-issue-using-hte/qaq-p/2695166#M1016759


"""

from jira import JIRA
import jira
from dotenv import dotenv_values

class jira_client():
	"""
	At initialization tries to read the .env file, which must contain 3 lines:
		SERVER = 'Your domain'
		EMAIL = 'Your Jira account email'
		TOKEN = 'Your Jira token'

	Will raise an exception in case of wrong data in the .env file:
	Bad domain -> ERROR: Site temporarily unavailable
	Bad user or token -> ERROR: Client must be authenticated to access this resource.
	"""

	################################################################

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

			# While these catch errors in the credencials variables.
			me = self.client.current_user()
			self.me = self.client.user(me)

		except jira.JIRAError as e:
			print('ERROR: ',e.text)
			raise Exception('Sorry. Server or user credentials are incorrect.')

	################################################################

	def update_issues(self):
		"""
		Searchs for the issues the user already has worklogs and saves the keys (i.e. the names).

		Returns
		-------
		None.

		"""
		jql = 'worklogAuthor = currentUser()'
		issues = self.client.search_issues(jql_str = jql,maxResults = 0)
		self.issues = [i.key for i in issues]

	################################################################

	def get_issues(self):
		"""
		Returns the list of issue keys.

		Returns
		-------
		List
			DESCRIPTION.

		"""
		return self.issues

	################################################################

	def upload_worklog(self,issue,time,comment = '',date = ''):
		"""
		Uploads a work log to Jira.

		Parameters
		----------
		issue : str
			DESCRIPTION.
		time : str
			DESCRIPTION.
		comment : str, optional
			DESCRIPTION. The default is ''.
		date : str, optional
			DESCRIPTION. The default is ''.

		Returns
		-------
		None.

		"""
		self.client.add_worklog(
			issue = issue,
			timeSpent = time,
			comment = comment,
			started = date)

	################################################################