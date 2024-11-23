# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 10:24:31 2023
Modified on 2024-11-23

@author: arovero
"""

from datetime import datetime,timedelta
import re

# FIXME
# Q: What happens if in an interval, start > end.
# A: Nothing, it returns an empty array.
def parse_dates(s):
	def replace_year(match):
		print('Replace year')
		year = datetime.now().year
		offset = 0
		if match.group(1) != None:
			offset = int(match.group(1) + match.group(2))

		print('Group 1: ',match.group(1))
		print('Group 2: ',match.group(2))
		print('Offset: ',offset)

		return str(year + int(offset))

	def replace_month(match):
		print('Replace month')
		month = datetime.now().month
		offset = 0
		if match.group(1) != None:
			offset = int(match.group(1) + match.group(2))

		print('Group 1: ',match.group(1))
		print('Group 2: ',match.group(2))
		print('Offset: ',offset)

		return str(month + int(offset))

	def replace_day(match):
		print('Replace day')
		day = datetime.now().day
		offset = 0
		if match.group(1) != None:
			offset = int(match.group(1) + match.group(2))

		print('Group 1: ',match.group(1))
		print('Group 2: ',match.group(2))
		print('Offset: ',offset)

		return str(day + int(offset))

	pattern = r'{\s*year\s*(?:([\+,-])\s*(\d+))?}'
	s = re.sub(pattern,replace_year,s)
	pattern = r'{\s*month\s*(?:([\+,-])\s*(\d+))?}'
	s = re.sub(pattern,replace_month,s)
	pattern = r'{\s*day\s*(?:([\+,-])\s*(\d+))?}'
	s = re.sub(pattern,replace_day,s)

	print(s)

	days = []

	if s != '':
		s = s.replace('/','.')
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

	print(days)
	print('==============================')
	return days
