from datetime import datetime
from dateutil.relativedelta import relativedelta
import re

s = '{y}.{d-m-1}.1'

def replace_data(match):
	year = datetime.now().year
	month = datetime.now().month
	day = datetime.now().day

	print(match)

	s = match.group(1)
	print('Match: ',s)

	s = s.replace('y',str(year))
	s = s.replace('m',str(month))
	s = s.replace('d',str(day))

	print('substitution: ',s)
	return s


print('Original: ',s)
#p = r'\{(.+(?:[+-].+)(?=[+-].+)*)\}'
p = r'\{((?:[ymd]|\d+)(?:[+-](?:[ymd]|\d+))*)\}'
s = re.sub(p,replace_data,s)
print('Modified: ',s)
parts = s.split('.')
print(parts)

try:
	delta = relativedelta(years = eval(parts[0]) - 1,
						months = eval(parts[1]) - 1,
						days = eval(parts[2]) - 1)
	print(delta)

	day = datetime(1,1,1) + delta
	print(day)
except SyntaxError:
	print('SyntaxError')






#for y in range(2007,2023):
#	b = 21 - (y - 2007) % 7 - (1 * (y % 4 == 0))
#	print(y,b)


"""
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


	year = datetime.now().year
	month = datetime.now().month
	day = datetime.now().day

	s = s.replace('{year}',str(year))
	s = s.replace('{month}',str(month))
	s = s.replace('{day}',str(day))
	print(s)
	"""