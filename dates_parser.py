# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 10:24:31 2023
Modified on 2024-11-23

@author: arovero
"""

from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import re
import logging as log

# FIXME
# Q: What happens if in an interval, start > end.
# A: Nothing, it returns an empty array.

################################################################

class DateParser:
	def __init__(self):
		pass

	################################

	def __call__(self,dates:str):
		return self.parse(dates)

	################################

	def parse(self,s):

		# Accepts dates with '.' or '/' separators.
		s = s.replace('/','.')

		try:
			answer = self.separate_dates(s)
	#	except SyntaxError:
	#		log.error(f'SyntaxError on date; "{s}"')
	#		answer = None
		except ValueError:
			log.error(f'ValueError on date: "{s}"')
			answer = None
		except NameError:
			log.error(f'NameError on date: "{s}"')
			answer = None

		return answer

	################################

	def separate_dates(self,s):
		days = []

		if s != '':
			parts = s.split(',')

			# Process all "positive" dates.
			for p in parts:
				# Removes all whitespaces first.
				if not p.strip().startswith('-'):
					# If it is an interval.
					if ':' in p:
						interval = p.split(':')
						start = self.parse_placeholders(interval[0])
						end = self.parse_placeholders(interval[1])
						start = datetime.strptime(start,'%Y.%m.%d')
						end = datetime.strptime(end,'%Y.%m.%d')

						n = (end - start).days + 1

						x = [start + timedelta(days = i) for i in range(n)]

						days.extend(x)
					else:
						p = self.parse_placeholders(p)
						day = datetime.strptime(p,'%Y.%m.%d')
						days.extend([day])

			# Process all "negative" dates.
			for p in parts:
				p = p.strip()
				if p.startswith('-'):
					if ':' in p:
						interval = p.split(':')
						start = self.parse_placeholders(interval[0])
						end = self.parse_placeholders(interval[1])
						start = datetime.strptime(start,'%Y.%m.%d')
						end = datetime.strptime(end,'%Y.%m.%d')

						n = (end - start).days + 1

						x = [start + timedelta(days = i) for i in range(n)]
						days = [d for d in days if d not in x]
					else:
						p = self.parse_placeholders(p)
						day = datetime.strptime(p,'%Y.%m.%d')
						days = [d for d in days if d != day]

			# Removes Saturdays and Sundays.
			days = [d for d in days if d.weekday() not in [5,6]]

		return days

	################################

	def parse_placeholders(self,date:str):
		#
		regex = r'[-]?\{\s*((?:[ymd]|\d+)(?:\s*[+-]\s*(?:[ymd]|\d+))*)\s*\}'
		date = re.sub(regex,self.replace_data,date)

		# Separates the date into year, month and day.
		fields = date.split('.')
		delta = relativedelta(years = int(fields[0]) - 1,
							  months = int(fields[1]) - 1,
							  days = int(fields[2]) - 1)
		s = (datetime(1,1,1) + delta).strftime('%Y.%m.%d')

		return s

	################################

	def replace_data(self,match):
		"""
		This is the callback function for the re substitution function.
		"""

		date = datetime.now()
		year = date.year
		month = date.month
		day = date.day

		print(match)
#		print(match.group(0))
		s = match.group(1)
		print('Match: ',s)

		s = s.replace('y',str(year))
		s = s.replace('m',str(month))
		s = s.replace('d',str(day))

		return str(eval(s))

################################################################

if __name__ == '__main__':
	benchmark =	[
		'{y}.{m}.{d}',
		'{y}.11.08',
		'{y}.{m}.{d-1}',
		'{y}.{d-m-1}.1',
		'{y}.{d-m-}.1',
		'{y}.{m}.',
		'{y}.{m}.{d     }',
		'{ y }.{ m }.{ d     }',
		'  { y }.{ m }.{ d     }   ',
		'  { y }.{ m }.{ d     + 1  }   ',
		'{y}.{m}.{d-7}:{y}.{m}.{d}',
		'-{y}.{m}.{d}',
		'{y}.{m}.{d-7}:{y}.{m}.{d+1},-{y}.{m}.{d}',
		'{y}.{m}.{d-7}:{y}.{m}.{d+1},-{y}.{m}.{d-1}:{y}.{m}.{d}',
		'{year}.{m}.10',
		'{y}.{m}.{d*2}',
		'{y}.{m}.{d}-1',
		'{y}.{m}.0',
		'{y}.{m}.-10',
		'{y}.{m}.{d-7}:',
		]

	parser = DateParser()
	for s in benchmark:
		print(s.ljust(32),parser(s))
		print('==============================')