import flet as ft
#import sys
from datetime import datetime,timedelta,timezone
import re
import json
#from time import sleep
#import pytz
#import fsm
from jira_client import jira_client

###############################################################################

# FIXME
# Q: What happens if in an interval, start > end.
# A: Nothing, it returns an empty array.
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

					x = [start + timedelta(days = i) for i in range(n)]

					days.extend(x)
				else:
					day = datetime.strptime(p,'%Y.%m.%d')
					days.extend([day])

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

	return days

###############################################################################

ERROR = 'error'
OK = 'ok'

###############################################################################


def main(page: ft.Page):

	valid = {
		'issue':False,
		'time':False,
		'dates':False
		}

	##################################################

	def page_init():
		# Page properties.
		page.title = 'Jira WoLoLo'
		page.window_resizable = True
		page.window_width = 650
		page.window_height = 370
		page.window_maximizable = False
		page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
		page.vertical_alignment = ft.MainAxisAlignment.START
		page.update()

	##############################

	def display_loading(show,value = None):
		if show:
			stk_loading.controls.append(cnt_loading)
			rng_loading.value = value
			cnt_left.disabled = True
		else:
			stk_loading.controls.pop()
			rng_loading.value = None
			cnt_left.disabled = False
		page.update()

	##############################

	def get_jira_issues():
		client = jira_client()
		client.update_issues()
		client_issues = client.get_issues()
		for i in client_issues:
			ddw_issue.options.append(ft.dropdown.Option(i))
		return client

	##############################

	def upload_callback(e):
		issue = ddw_issue.value
		time = txf_time.value
		comment = txf_comment.value
		dates = parse_days(txf_dates.value)

		tz = datetime.now(timezone.utc).astimezone().tzinfo
		# If dates is empty, no work log will be uploaded.

		n = len(dates)
		i = 0
		display_loading(True,0)
		for d in dates:
			d = d.astimezone(tz)
			d = d.replace(hour = 9,minute = 0,second = 0)
			client.upload_worklog(issue,time,comment,d)

			i += 1/n
			display_loading(True,i)
			#sleep(0.25)

		display_loading(False)

		txf_time.value = ''

		# FIXME
		# Find out how to call the txt_time callback manually.
		# txt_time.on_change()
		btn_upload.disabled = True

		page.update()

	##############################

	def save_callback(e):
		page.dialog = dlg_confirm
		dlg_confirm.open = True
		page.update()

	##############################

	def delete_callback(e):
		name = e.control.label.value
		dlg_delete.content.value = f'Do you really want to delete <{name}> chip?'
		page.dialog = dlg_delete
		dlg_delete.open = True
		page.update()

	def close_dlg(e):
		pass

	##############################

	def issue_callback(e):
		issue_validation()

	def issue_validation():
		issue = ddw_issue.value
		if issue != None:
			answer = True if issue in client.get_issues() else False
			valid['issue'] = answer
		manage_errors()

	##############################

	def time_callback(e):
		time_validation()

	def time_validation():
		time = txf_time.value
		p1 = r'^(\d+w)( \d+d)?( \d+h)?( \d+m)?$'
		p2 = r'^(\d+d)( \d+h)?( \d+m)?$'
		p3 = r'^(\d+h)( \d+m)?$'
		p4 = r'^(\d+m)$'
		pattern = f'{p1}|{p2}|{p3}|{p4}'
		match = re.search(pattern,time)
		valid['time'] = True if match else False
		manage_errors()

	##############################

	def dates_callback(e):
		dates_validation()

	def dates_validation():
		dates = txf_dates.value
		try:
			parse_days(dates)
			valid['dates'] = True
			#txf_dates.error_text = ''
			txf_dates.label = 'Dates'
		except ValueError:
			valid['dates'] = False
			#txf_dates.error_text = 'Error'
			txf_dates.label = 'Dates - ERROR'
		manage_errors()

	##############################

	def manage_errors():
		state = all(valid.values())
		if state:
			btn_upload.disabled = False
			btn_save.disabled = False
		else:
			btn_upload.disabled = True
			btn_save.disabled = True
		page.update()

	##############################

	def name_callback(e):
		name = txf_save_name.value
		if name not in saved.keys() and name != '':
			btn_confirm_save.disabled = False
		else:
			btn_confirm_save.disabled = True
		page.update()

	def confirm_callback(e):
		name = txf_save_name.value
		saved[name] = {
			'issue':ddw_issue.value,
			'time':txf_time.value,
			'comment':txf_comment.value,
			'dates':txf_dates.value,
			'weekend':False,
			'color':'#55FF0000'
			}

		with open('saved.json','w') as f:
			json.dump(saved,f,indent = 4)

		chp_saved = create_chips(saved)

		lst_saved.controls = list(chp_saved.values())

		dlg_confirm.open = False
		page.update()

	def confirm_delete_callback(e):
		# FIXME
		# This is a really bad way to pass information between functions.
		# The data is enbeded in the control string value.
		name = re.search('Do you really want to delete <(.*)> chip?',dlg_delete.content.value)
		name = name.group(1)
		saved.pop(name)

		with open('saved.json','w') as f:
			json.dump(saved,f,indent = 4)

		chp_saved = create_chips(saved)

		lst_saved.controls = list(chp_saved.values())

		dlg_delete.open = False
		page.update()

	def cancel_save_callback(e):
		dlg_confirm.open = False
		page.update()

	def cancel_delete_callback(e):
		dlg_delete.open = False
		page.update()

	def options_callback(e):
		value = rdo_dates.value
		now = datetime.now()
		#datetime.strptime(interval[0],'%Y.%m.%d')

		if value == 'custom':
			txf_dates.disabled = False
		elif value == 'today':
			now = datetime.strftime(now,'%Y.%m.%d')
			txf_dates.value = now
			txf_dates.disabled = True
		elif value == 'yesterday':
			yesterday = now - timedelta(1)
			yesterday = datetime.strftime(yesterday,'%Y.%m.%d')
			txf_dates.value = yesterday
			txf_dates.disabled = True

		page.update()

	##################################################

	# ddw = Dropdown.
	# txf = TextField.
	# btn = ElevatedButton.
	# rom = Row.
	# col = Column.
	# cnt = Container
	# rng = ProgressRing

	txf_save_name = ft.TextField(
		label = 'Chip name',
		on_change = name_callback,
		expand = True
		)

	btn_confirm_save = ft.OutlinedButton(
		text = "Save",
		on_click = confirm_callback,
		disabled = True
	)

	dlg_confirm = ft.AlertDialog(
		modal = True,
		title = ft.Text("Save Chip"),
		content = ft.Column(
			controls = [
				ft.Text('Please enter new chip name.'),
				txf_save_name
				],
			expand = False
			),
		actions = [
			btn_confirm_save,
			ft.OutlinedButton(
				text = "Cancel",
				on_click = cancel_save_callback
				)
			],
		actions_alignment = ft.MainAxisAlignment.END,
		#on_dismiss = lambda e: print("Modal dialog dismissed!"),
		)

	dlg_delete = ft.AlertDialog(
		modal = True,
		title = ft.Text('Please confirm'),
		content = ft.Text('Text will be completed later.'),
		actions = [
			ft.OutlinedButton(
				text = "Yes",
				on_click = confirm_delete_callback
				),
			ft.OutlinedButton(
				text = "No",
				on_click = cancel_delete_callback
				)
			],
		actions_alignment=ft.MainAxisAlignment.END,
		)

	##################################################

	ddw_issue = ft.Dropdown(
		label = 'Issue',
		hint_text = 'COMMONACT-3',
		on_change = issue_callback,
		expand = True
		)

	txf_time = ft.TextField(
		label = 'Time Spent',
		hint_text = '1w 2d 3h 4m',
		on_change = time_callback,
		expand = False,
		width = 150
		)

	txf_comment = ft.TextField(
		label = 'Comment',
		hint_text = 'Wololo Rules!'
		)

	txf_dates = ft.TextField(
		label = 'Dates',
		hint_text = '2023.11.01:2023.11.03,2023.11.20,-2023.11.02',
		on_change = dates_callback
		)

	rdo_dates = ft.RadioGroup(
		content = ft.Row([
			ft.Radio(value = "custom", label = "Custom"),
			ft.Radio(value = "today", label = "Today"),
			ft.Radio(value = "yesterday", label = "Yesterday")
			],
			alignment = ft.MainAxisAlignment.CENTER
			),
		on_change = options_callback
		)
	rdo_dates.value = 'custom'

	btn_upload = ft.ElevatedButton(
		text = 'Upload Work Log',
		icon = 'upload',
		on_click = upload_callback,
		disabled = True,
		expand = True
		)

	btn_save = ft.ElevatedButton(
		text = 'Save Work Log',
		icon = 'save',
		on_click = save_callback,
		disabled = True,
		expand = True
		)

	##############################

	row_issues = ft.Row(
		controls = [ddw_issue,txf_time]
		)

	col_left = ft.Column(
		controls = [
			row_issues,
			txf_comment,
			txf_dates,
			rdo_dates],
		expand = True
		)

	rng_loading = ft.ProgressRing()

	cnt_loading = ft.Container(
		content = rng_loading,
		alignment = ft.alignment.center,
		height = 200,
		#width = 400
		)

	stk_loading = ft.Stack(
		controls = [col_left])

	##############################

	def chips_callback(e):
		for c in lst_saved.controls:
			if c != e.control:
				c.selected = False

		if e.control.selected:
			ddw_issue.disabled = True
			rdo_dates.value = 'custom'
			txf_dates.disabled = False

			ddw_issue.value = saved[e.control.label.value]['issue']
			txf_time.value = saved[e.control.label.value]['time']
			txf_comment.value = saved[e.control.label.value]['comment']
			txf_dates.value = saved[e.control.label.value]['dates']

			issue_validation()
			time_validation()
			dates_validation()
		else:
			ddw_issue.disabled = False

		page.update()

	with open('saved.json','r') as f:
		saved = json.load(f)
		#json.dump(saved,f,indent = 4)
		#print(saved)

	def create_chips(saved):
		chips = {}
		for name in saved.keys():
			color = saved[name]['color']
			chips[name] = ft.Chip(
				label = ft.Text(name),
		#		leading = ft.Icon(ft.icons.MAP_SHARP),
				show_checkmark = True,
				on_select = chips_callback,
				on_delete = delete_callback,
				bgcolor = color
				)
		return chips

	chp_saved = create_chips(saved)

	lst_saved = ft.ListView(
		controls = list(chp_saved.values()),
		#controls = [ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola'),ft.Text('hola')],
		spacing = 3,
		#auto_scroll = True,
		#tight = True,
		#scroll = ft.ScrollMode.ALWAYS,
		height = 200
		)

	##############################

	row_buttons = ft.Row(
		controls = [
			ft.Column(
				controls = [btn_upload],
				expand = False),
			ft.Column(
				controls = [btn_save],
				expand = False)
		],
		alignment = ft.MainAxisAlignment.CENTER,
		expand = True
		)

	cnt_left = ft.Container(
		content = stk_loading,
#		border_radius = 10,
#		border = ft.border.all(2),
		width = 400
		#expand =
		)

	cnt_right = ft.Container(
		content = lst_saved,
		expand = True,
#		width = 200
		)

	row_main = ft.Row(
		controls = [
			cnt_left,
			# FIXME
			# For some reason, this vertical divider does not show up.
			ft.VerticalDivider(thickness = 10,color = ft.colors.BLACK),
			cnt_right
			],
		expand = False
		)

	col_main = ft.Column(
		controls = [
			row_main,
			ft.Divider(thickness = 1,color = ft.colors.BLACK),
			row_buttons
			],
		expand = True
		)

	cnt_main = ft.Container(
		content = col_main,
		expand = True
		)
	page.add(cnt_main)

	##################################################

# =============================================================================
# 	def page_resize(e):
# 		print('Page size:', page.window_width, page.window_height)
# 		print('Row size:', row_buttons.width, page.height)
#
# 	page.on_resize = page_resize
# =============================================================================

	page_init()
	display_loading(True)
	client = get_jira_issues()
	display_loading(False)

########################################################################

# Web app.
#ft.app(target = main,view = ft.WEB_BROWSER)
# Desktop app.
ft.app(target = main)








































































"""







	##################################################







	##############################

	def process_inputs(e):
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

	##############################

	def change_page_theme(state):
		if state == OK:
			page.theme = None
		elif state == ERROR:
			page.theme = ft.Theme(
				color_scheme_seed = 'red',
				visual_density = ft.ThemeVisualDensity.COMPACT
				)



	##############################







"""
