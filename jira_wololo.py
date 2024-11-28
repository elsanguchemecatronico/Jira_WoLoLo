#!/usr/bin/env python3

import flet as ft
#import sys
from datetime import datetime,timedelta,timezone
import re
# https://regex101.com/
#from time import sleep
#import pytz
#import fsm
from jira_client import jira_client
from saved import saved_issues
from dates_parser import parse_dates
import calendar
from datetime import datetime
import time

###############################################################################

def main(page: ft.Page):
	ERROR = 'error'
	OK = 'ok'
	TITLE = 'Jira WoLoLo v1.3.1'

	valid = {
		'issue':False,
		'time':False,
		'dates':False
		}

	saved = saved_issues('saved.json')

	##################################################

	def page_init():
		# Page properties.

		# This is done here because there is a bug in flet.
		# https://github.com/electron/electron/issues/31233
		# The window gets resized when the resizing is disabled.
		# So the resizing is disabled and then the window is resized.
		page.window.resizable = False
		page.update()

		page.window.resizable = True
		page.window.width = 650
		page.window.height = 370
		page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
		page.vertical_alignment = ft.MainAxisAlignment.START
		page.title = TITLE
		page.update()

	##############################

	def display_loading(show,value = None):
		if show:
			cnt_loading.visible = True
			rng_loading.value = value
			col_main.disabled = True
		else:
			cnt_loading.visible = False
			rng_loading.value = None
			col_main.disabled = False
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
		dates = parse_dates(txf_dates.value)

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
		btn_save.disabled = True

		page.update()

	##############################

	def save_callback(e):
		page.dialog = dlg_confirm
		dlg_confirm.open = True
		page.update()

	def confirm_save_callback(e):
		name = txf_save_name.value
		saved.data[name] = {
			'issue':ddw_issue.value,
			'time':txf_time.value,
			'comment':txf_comment.value,
			'dates':txf_dates.value,
			'weekend':False,
			'color':'#55FF0000'
			}

#		with open('saved.json','w') as f:
#			json.dump(saved,f,indent = 4)
		saved.save()

		chp_saved = create_chips(saved.data)

		lst_saved.controls = list(chp_saved.values())

		dlg_confirm.open = False
		page.update()

	def cancel_save_callback(e):
		dlg_confirm.open = False
		page.update()

	##############################

	def delete_callback(e):
		name = e.control.label.value
		dlg_delete.content.value = f'Do you really want to delete <{name}> chip?'
		page.overlay.append(dlg_delete)
		dlg_delete.open = True
		page.update()

	def confirm_delete_callback(e):
		# FIXME
		# This is a really bad way to pass information between functions.
		# The data is enbeded in the control string value.
		name = re.search('Do you really want to delete <(.*)> chip?',dlg_delete.content.value)
		name = name.group(1)
		saved.data.pop(name)

#		with open('saved.json','w') as f:
#			json.dump(saved,f,indent = 4)
		saved.save()

		chp_saved = create_chips(saved.data)

		lst_saved.controls = list(chp_saved.values())

		dlg_delete.open = False
		page.update()

	def cancel_delete_callback(e):
		dlg_delete.open = False
		page.update()

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
		s = r'\d*([.]\d+)?'
		p1 = fr'^({s}w)( {s}d)?( {s}h)?( {s}m)?$'
		p2 = fr'^({s}d)( {s}h)?( {s}m)?$'
		p3 = fr'^({s}h)( {s}m)?$'
		p4 = fr'^({s}m)$'
		pattern = f'{p1}|{p2}|{p3}|{p4}'
		match = re.search(pattern,time)
		valid['time'] = True if match else False
		manage_errors()

	##############################

	def dates_callback(e):
		dates_validation()

	def dates_validation():
		dates = txf_dates.value

		if parse_dates(dates) == None:
			valid['dates'] = False
			txf_dates.label = 'Dates - ERROR'
		else:
			valid['dates'] = True
			txf_dates.label = 'Dates'
			
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
		if name not in saved.data.keys() and name != '':
			btn_confirm_save.disabled = False
		else:
			btn_confirm_save.disabled = True
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
		elif value == 'thisweek':
			# Get the current year and week number. Day of week (monday = 1) is not used.
			year,week,dow = now.isocalendar() # DOW = day of week

			start = datetime.strptime(f'{year}-{week}-1',"%Y-%W-%w").date()
			end = datetime.strptime(f'{year}-{week}-5',"%Y-%W-%w").date()
			start = datetime.strftime(start,'%Y.%m.%d')
			end = datetime.strftime(end,'%Y.%m.%d')

			txf_dates.value = f'{start}:{end}'
			txf_dates.disabled = True
		elif value == 'lastweek':
			# Get the year and week number of 7 days ago. Day of week (monday = 1) is not used.
			year,week,dow = (now - timedelta(days = 7)).isocalendar() # DOW = day of week

			start = datetime.strptime(f'{year}-{week}-1',"%Y-%W-%w").date()
			end = datetime.strptime(f'{year}-{week}-5',"%Y-%W-%w").date()
			start = datetime.strftime(start,'%Y.%m.%d')
			end = datetime.strftime(end,'%Y.%m.%d')

			txf_dates.value = f'{start}:{end}'
			txf_dates.disabled = True
		elif value == 'thismonth':
			# Get the current year and month.
			year = now.year
			month = now.month
			num_days = calendar.monthrange(year,month)

			start = datetime.strptime(f'{year}-{month}-1',"%Y-%m-%d").date()
			end = datetime.strptime(f'{year}-{month}-{num_days[1]}',"%Y-%m-%d").date()
			start = datetime.strftime(start,'%Y.%m.%d')
			end = datetime.strftime(end,'%Y.%m.%d')

			txf_dates.value = f'{start}:{end}'
			txf_dates.disabled = True
		elif value == 'lastmonth':
			# Get the current year and month.
			last_month = now.replace(day = 1)
			last_month = last_month - timedelta(days = 1)
			year = last_month.year
			month = last_month.month
			num_days = calendar.monthrange(year,month)

			start = datetime.strptime(f'{year}-{month}-1',"%Y-%m-%d").date()
			end = datetime.strptime(f'{year}-{month}-{num_days[1]}',"%Y-%m-%d").date()
			start = datetime.strftime(start,'%Y.%m.%d')
			end = datetime.strftime(end,'%Y.%m.%d')

			txf_dates.value = f'{start}:{end}'
			txf_dates.disabled = True

		dates_validation()
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
		on_click = confirm_save_callback,
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
			ft.Radio(value = "yesterday", label = "Yesterday"),
			ft.Radio(value = "thisweek", label = "This Week"),
			ft.Radio(value = "lastweek", label = "Last Week"),
			ft.Radio(value = "thismonth", label = "This Month"),
			ft.Radio(value = "lastmonth", label = "Last Month")
			],
			scroll = ft.ScrollMode.HIDDEN,
			expand = True,
			alignment = ft.MainAxisAlignment.CENTER,
			vertical_alignment = ft.CrossAxisAlignment.CENTER
			),
		on_change = options_callback
		)
	rdo_dates.value = 'custom'

# =============================================================================
# 	lst = ft.ListView(
# 		controls = [rdo_dates],
# 		horizontal = True,
# 		expand = True
# 		)
# =============================================================================

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
		padding = 10
		#height = 200,
		#width = 400
		)

	page.overlay.append(cnt_loading)

	##############################

	def chips_callback(e):
		for c in lst_saved.controls:
			if c != e.control:
				c.selected = False

		if e.control.selected:
			ddw_issue.disabled = True
			rdo_dates.value = 'custom'
			txf_dates.disabled = False

			ddw_issue.value = saved.data[e.control.label.value]['issue']
			txf_time.value = saved.data[e.control.label.value]['time']
			txf_comment.value = saved.data[e.control.label.value]['comment']
			txf_dates.value = saved.data[e.control.label.value]['dates']

			issue_validation()
			time_validation()
			dates_validation()
		else:
			ddw_issue.disabled = False

		page.update()

#	with open('saved.json','r') as f:
#		saved = json.load(f)
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

	chp_saved = create_chips(saved.data)

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
		content = col_left,
		width = 400
		)

	cnt_right = ft.Container(
		content = lst_saved,
		expand = True
		)

	row_main = ft.Row(
		controls = [
			cnt_left,
			# FIXME
			# For some reason, this vertical divider does not show up.
			ft.VerticalDivider(thickness = 1,color = ft.colors.BLACK),
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
	page.title = f'{TITLE} - {client.me}'
	page.update()

########################################################################

# Web app.
#ft.app(target = main,view = ft.WEB_BROWSER)

# Desktop app.
ft.app(target = main)
