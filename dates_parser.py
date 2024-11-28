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
def parse_dates(s):

	################################################################

	def replace_data(match):
		year = datetime.now().year
		month = datetime.now().month
		day = datetime.now().day

#		print(match)
#		print(match.group(0))
		s = match.group(1)
#		print('Match: ',s)

		s = s.replace('y',str(year))
		s = s.replace('m',str(month))
		s = s.replace('d',str(day))

#		print('substitution: ',s)
		return str(eval(s))

	################################################################

	def parse_placeholders(s):
#		print('Input: ',s)
		pat = r'[-]?\{\s*((?:[ymd]|\d+)(?:\s*[+-]\s*(?:[ymd]|\d+))*)\s*\}'
		s = re.sub(pat,replace_data,s)
		fields = s.split('.')
		delta = relativedelta(years = int(fields[0]) - 1,
							  months = int(fields[1]) - 1,
							  days = int(fields[2]) - 1)
		s = (datetime(1,1,1) + delta).strftime('%Y.%m.%d')

#		print('Output: ',s)
		return s

	################################################################

	def separate_dates(s):
		days = []

		if s != '':
			parts = s.split(',')

			# Process all "positive" dates.
			for p in parts:
#				print('Processing: ',p)
				if not p.strip().startswith('-'):
					if ':' in p:
						interval = p.split(':')
						start = parse_placeholders(interval[0])
						end = parse_placeholders(interval[1])
						start = datetime.strptime(start,'%Y.%m.%d')
						end = datetime.strptime(end,'%Y.%m.%d')

						n = (end - start).days + 1

						x = [start + timedelta(days = i) for i in range(n)]

						days.extend(x)
					else:
#						print('Discrete date: ',p)
						p = parse_placeholders(p)
#						print(f'Processed: ${p}$')
						day = datetime.strptime(p,'%Y.%m.%d')
						days.extend([day])

			# Process all "negative" dates.
			for p in parts:
				p = p.strip()
				if p.startswith('-'):
					if ':' in p:
						interval = p.split(':')
						start = parse_placeholders(interval[0])
						end = parse_placeholders(interval[1])
						start = datetime.strptime(start,'%Y.%m.%d')
						end = datetime.strptime(end,'%Y.%m.%d')

						n = (end - start).days + 1

						x = [start + timedelta(days = i) for i in range(n)]
						days = [d for d in days if d not in x]
					else:
#						print('Discrete date: ',p)
						p = parse_placeholders(p)
#						print(f'Processed: ${p}$')
						day = datetime.strptime(p,'%Y.%m.%d')
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


	try:
		answer = separate_dates(s)
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
		'{y}.{m}.-10'
		]

	for s in benchmark:
		print(s.ljust(32),parse_dates(s))
		print('==============================')