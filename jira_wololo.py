




# INSTALLATION
# pip install flet --upgrade
# pip install python-dotenv


from datetime import datetime,timedelta,timezone
import flet as ft
from jira import JIRA
from dotenv import load_dotenv
import re
import pytz

###############################################################################

def parse_days(s):
	days = []

	if s != '':
		s = s.replace('/','.')
		parts = s.split(',')


		for p in parts:
			if '-' not in p:
				if ':' in p:
					interval = p.split(':')
					start = datetime.strptime(interval[0],'%Y.%m.%d')
					end = datetime.strptime(interval[1],'%Y.%m.%d')

					n = (end - start).days + 1

	#				start = start.replace(hour = 9,minute = 0,second = 0)
					x = [start + timedelta(days = i) for i in range(n)]

					days.extend(x)
				else:
					day = datetime.strptime(p,'%Y.%m.%d')
	#				day = day.replace(hour = 9,minute = 0,second = 0)
					days.extend([day])

		for p in parts:
			if '-' in p:
				if ':' in p:
					interval = p.split(':')
					start = datetime.strptime(interval[0],'-%Y.%m.%d')
					end = datetime.strptime(interval[1],'%Y.%m.%d')

					n = (end - start).days + 1

	#				start = start.replace(hour = 9,minute = 0,second = 0)
					x = [start + timedelta(days = i) for i in range(n)]
					days = [d for d in days if d not in x]

				else:
					day = datetime.strptime(p,'-%Y.%m.%d')
	#				day = day.replace(hour = 9,minute = 0,second = 0)
					days = [d for d in days if d != day]

		# Removes Saturdays and Sundays.
		days = [d for d in days if d.weekday() not in [5,6]]

	return days

###############################################################################

s = '2023/11/01:2023.11.30,2023.1.1,2023.10.01:2023.10.03,-2023.10.02,-2023.11.02:2023.11.03'
d = parse_days(s)
print(d)

ERROR = 'error'
OK = 'ok'

########################################################################

def main(page: ft.Page):
	issue = ''
	time = ''
	comment = ''
	dates = ''
	dates = []

	valid = {
		'issue':False,
		'time':False,
		'dates':False
		}

	##############################

	def process_issue(issue):
		valid['issue'] = True if issue in all_issues else False

	def process_time(time):
		p1 = r'^(\d+w)( \d+d)?( \d+h)?( \d+m)?$'
		p2 = r'^(\d+d)( \d+h)?( \d+m)?$'
		p3 = r'^(\d+h)( \d+m)?$'
		p4 = r'^(\d+m)$'
		pattern = f'{p1}|{p2}|{p3}|{p4}'
		match = re.search(pattern,time)
		valid['time'] = True if match else False

	def process_dates(dates):
		try:
			parse_days(dates)
			valid['dates'] = True
		except ValueError:
			valid['dates'] = False

	def process_inputs(e):
		print(e.control.value)
		if e.control == txt_issue:
			issue = txt_issue.value
			process_issue(issue)
		elif e.control == txt_time:
			time = txt_time.value
			process_time(time)
		elif e.control == txt_dates:
			dates = txt_dates.value
			process_dates(dates)
		manage_errors()

	def change_page_theme(state):
		print('color theme changed',state)
		if state == OK:
			page.theme = None
		elif state == ERROR:
			page.theme = ft.Theme(
				color_scheme_seed = 'red',
				visual_density = ft.ThemeVisualDensity.COMPACT
				)

	def manage_errors():
		state = all(valid.values())
		if state:
			#change_page_theme(OK)
			btn_upload.disabled = False
		else:
			#change_page_theme(ERROR)
			btn_upload.disabled = True
		page.update()

	def upload_work_log(e):
		issue = txt_issue.value
		time = txt_time.value
		comment = txt_comment.value
		dates = parse_days(txt_dates.value)

		print(issue)
		print(time)
		print(comment)
		print(dates)

		tz = datetime.now(timezone.utc).astimezone().tzinfo
		for d in dates:
			d = d.astimezone(tz)
			d = d.replace(hour = 9,minute = 0,second = 0)
			answer = client.add_worklog(issue = issue,timeSpent = time,comment = comment,started = d)
			print(answer)

	txt_issue = ft.TextField(
		label = 'Issue',
		hint_text = 'FAMPVW-92',
		expand = True,
		on_change = process_inputs
		)

	txt_time = ft.TextField(
		label = 'Time Spent',
		hint_text = '1d 2h 3m',
		expand = False,
		width = 150,
		on_change = process_inputs
		)

	txt_comment = ft.TextField(
		label = 'Comment',
		hint_text = 'Wololo Rules!'
		)

	txt_dates = ft.TextField(
		label = 'Dates',
		hint_text = '2023.11.12',
		on_change = process_inputs
		)

	btn_upload = ft.ElevatedButton(
		text = 'Upload Work Log',
		icon = 'upload',
		on_click = upload_work_log
		)

	btn_saved = ft.ElevatedButton(
		text = 'Save Work Log',
		icon = 'save',
		on_click = upload_work_log,
		disabled = True
		)

	row_buttons = ft.Row(
		controls = [btn_upload],
		alignment = ft.MainAxisAlignment.CENTER,
#		expand = True
		)

	row = ft.Row(
		controls = [txt_issue,txt_time],
#		expand = True
		)

	col = ft.Column(
		controls = [row,txt_comment,txt_dates,row_buttons],
		expand = True
		)



	ring = ft.ProgressRing()
	ring_container = ft.Container(
		content = ring,
		alignment = ft.alignment.center,
		height = 200,
		#width = 400
		)
	st = ft.Stack(
		controls = [col])

	cnt = ft.Container(
		content = st,
#		border_radius = 10,
#		border = ft.border.all(2),
		expand = False
		)

	page.add(cnt)

	##############################

	# Page properties.
	page.title = 'Jira WoLoLo'
#	page.bgcolor = '#FFFF0000'
#	page.vertical_alignment = ft.MainAxisAlignment.CENTER
#	page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
	page.window_resizable = False
#	page.scroll = ft.ScrollMode.ADAPTIVE
	page.window_width = 400
	page.window_height = 300
	page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
	page.vertical_alignment = ft.MainAxisAlignment.CENTER

	def page_resize(e):
		print('New page size:', page.window_width, page.window_height)

	page.on_resize = page_resize

	page.update()

	##############################

	server = 'https://mirgor-engineering.atlassian.net/'
	email = 'agustin.rovero@mirgor.com.ar'
	token = 'lwMKqlrL45YcPLgzh73e2E42'

	page.splash = None
	st.controls.append(ring_container)
# =============================================================================
# 	ft.Row(
# 		controls = [ft.ProgressRing()],
# 		alignment = ft.MainAxisAlignment.CENTER,
# 		vertical_alignment= ft.CrossAxisAlignment.CENTER,
# 		expand = True
# 		)
# =============================================================================
	cnt.disabled = True
	page.update()

	jira_options = {'server':server}
	credentials = (email,token)
	client = JIRA(options = jira_options,basic_auth = credentials)
#	me = client.current_user()
	jql = 'worklogAuthor = currentUser()'
	all_issues = client.search_issues(jql_str = jql,maxResults = 0)
	all_issues = [i.key for i in all_issues]
	print(all_issues)

	#all_issues = ['SEIACT-53', 'SEIACT-52', 'QAIACT-16', 'QAIACT-7', 'FAMPVW-3746', 'FAMPVW-3543', 'FAMPVW-3413', 'FAMPVW-3411', 'FAMPVW-3329', 'FAMPVW-3328', 'FAMPVW-3301', 'FAMPVW-3300', 'FAMPVW-3256', 'FAMPVW-3215', 'FAMPVW-3200', 'FAMPVW-3168', 'FAMPVW-3156', 'FAMPVW-3116', 'FAMPVW-2999', 'FAMPVW-2899', 'FAMPVW-2848', 'FAMPVW-2660', 'FAMPVW-2628', 'FAMPVW-2469', 'FAMPVW-2425', 'FAMPVW-2124', 'FAMPVW-2070', 'FAMPVW-2068', 'FAMPVW-2042', 'FAMPVW-1960', 'FAMPVW-1925', 'FAMPVW-1891', 'FAMPVW-1883', 'FAMPVW-1780', 'FAMPVW-1643', 'FAMPVW-1535', 'FAMPVW-1476', 'FAMPVW-1475', 'FAMPVW-1474', 'FAMPVW-1370', 'FAMPVW-1308', 'FAMPVW-1293', 'FAMPVW-1182', 'FAMPVW-1097', 'FAMPVW-1007', 'FAMPVW-1005', 'FAMPVW-887', 'FAMPVW-846', 'FAMPVW-821', 'FAMPVW-760', 'FAMPVW-732', 'FAMPVW-726', 'FAMPVW-725', 'FAMPVW-723', 'FAMPVW-716', 'FAMPVW-715', 'FAMPVW-640', 'FAMPVW-634', 'FAMPVW-601', 'FAMPVW-600', 'FAMPVW-571', 'FAMPVW-564', 'FAMPVW-562', 'FAMPVW-436', 'FAMPVW-419', 'FAMPVW-396', 'FAMPVW-383', 'FAMPVW-379', 'FAMPVW-356', 'FAMPVW-342', 'FAMPVW-318', 'FAMPVW-316', 'FAMPVW-315', 'FAMPVW-310', 'FAMPVW-241', 'FAMPVW-210', 'FAMPVW-195', 'FAMPVW-178', 'FAMPVW-148', 'FAMPVW-99', 'FAMPVW-98', 'FAMPVW-92', 'FAMPVW-91', 'FAMPVW-34', 'FAMPQNTDEV-2069', 'FAMPQNTDEV-2067', 'COMMONACT-21', 'COMMONACT-17', 'COMMONACT-14', 'COMMONACT-12', 'COMMONACT-7', 'COMMONACT-6', 'COMMONACT-3', 'COMMONACT-1']

	#page.splash = None
	st.controls.pop()
	cnt.disabled = False
	manage_errors()
	page.update()

########################################################################

# Web app.
#ft.app(target = main,view = ft.WEB_BROWSER)
# Desktop app.
ft.app(target = main)
