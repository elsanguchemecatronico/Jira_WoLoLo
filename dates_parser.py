# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 10:24:31 2023
Modified on 2024-11-23

@author: arovero
"""

from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import re

# FIXME
# Q: What happens if in an interval, start > end.
# A: Nothing, it returns an empty array.
def parse_dates(s):

	################################################################

	def replace_data(match):
		year = datetime.now().year
		month = datetime.now().month
		day = datetime.now().day

		s = match.group(1)
#		print('Match: ',s)

		s = s.replace('y',str(year))
		s = s.replace('m',str(month))
		s = s.replace('d',str(day))

#		print('substitution: ',s)
		return s

	################################################################

	def separate_dates(s):
		days = []

		if s != '':
			parts = s.split(',')

			# Process all "positive" dates.
			for p in parts:
				if '-' not in p:
					if ':' in p:
						interval = p.split(':')
						start = datetime.strptime(interval[0],'%Y.%m.%d')
						end = datetime.strptime(interval[1],'%Y.%m.%d')

						n = (end - start).days + 1

						x = [start + timedelta(days = i) for i in range(n)]

						days.extend(x)
					else:
						day = datetime.strptime(p,'%Y.%m.%d')
						days.extend([day])

			# Process all "negative" dates.
			for p in parts:
				if '-' in p:
					if ':' in p:
						interval = p.split(':')
						start = datetime.strptime(interval[0],'-%Y.%m.%d')
						end = datetime.strptime(interval[1],'%Y.%m.%d')

						n = (end - start).days + 1

						x = [start + timedelta(days = i) for i in range(n)]
						days = [d for d in days if d not in x]
					else:
						day = datetime.strptime(p,'-%Y.%m.%d')
						days = [d for d in days if d != day]

			# Removes Saturdays and Sundays.
			days = [d for d in days if d.weekday() not in [5,6]]

#		print(days)
#		print('==============================')
		return days

	################################################################

	s = s.replace('/','.')

	#p = r'\{.+(?:[+-][a-zA-Z]+)*\}'
	#p = r'\{(.+(?:[+-].+)(?=[+-].+)*)\}'
	#p = r'\{(.*?(?:[+,-].+)*)\}'

	#p = r'\{((?:[ymd]|\d+)(?:[+-](?:[ymd]|\d+))*)\}'
	p = r'\{\s*((?:[ymd]|\d+)(?:\s*[+-]\s*(?:[ymd]|\d+))*)\s*\}'
	s = re.sub(p,replace_data,s)
	parts = s.split('.')


	try:
		delta = relativedelta(years = eval(parts[0]) - 1,
							  months = eval(parts[1]) - 1,
							  days = eval(parts[2]) - 1)
		s = (datetime(1,1,1) + delta).strftime('%Y.%m.%d')
		answer = separate_dates(s)
	except SyntaxError:
#		print('SyntaxError')
		answer = None
	except ValueError:
#		print('ValueError')
		answer = None

	return answer

if __name__ == '__main__':
	benchmark =	[
		'{y}.{m}.{d}',
		'{y}.{m}.{d-1}',
		'{y}.{d-m-1}.1',
		'{y}.{d-m-}.1',
		'{y}.{m}.',
		'{y}.{m}.{d     }',
		'{ y }.{ m }.{ d     }',
		'  { y }.{ m }.{ d     }   ',
		'  { y }.{ m }.{ d     + 1  }   ',
		'{y}.{m}.{d-7}:{y}.{m}.{d}',
		]

	for s in benchmark:
		print(s.ljust(32),parse_dates(s))