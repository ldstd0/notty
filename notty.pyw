#!/usr/bin/python3

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import sys, os

sys.path.append ('src/')

err_json = False ; err_tk = False
err_syntax = False ; err_browser = False

try: import json
except ImportError:
	err_json = True
	print ('(!) json import error')

try:
	import tkinter as tk
	import tkinter.filedialog as fd
	from tkinter import ttk
except ImportError:
	err_tk = True
	print ('(!) tkinter import error')

try: import webbrowser as wb
except ImportError:
	err_browser = True
	print ('(!) web browser import error')

try: import syntax as s
except ImportError:
	err_syntax = True
	print ('(!) syntax lib import error')

onstart = True

ftypes = [
	('all', '*'),
	('python', '*.py*'),
	('javascript', '*.js'),
	('c lang', '*.c'),
	('c++ lang', '*.cpp'),
	('css', '*.css'),
	('html', '*.html'),
	('json', '*.json'),
	('markdown', '*.md')
]

extension = None
path = None
syntax = 'text'
edit = False
switched = False

title = 'notty'
title_separator = '-'
title_edited = '#'
title_error = 'error'
title_config = ''

show_menu = 'true'
show_p = 'true'
show_left_p = 'true' 

def edit_event (event):

	global p_pos, txt

	p_pos ['text'] = txt.index(tk.INSERT)

	count = len(txt.get ('1.0', 'end').splitlines ())
	lines = 1
	lines_p = ''
	while lines <= count:
		if lines == count:
			lines_p += str(lines)
		else:
			lines_p += str(lines) + '\n'
		lines += 1
	left_p ['state'] = 'normal'
	left_p.delete ('1.0', 'end')
	left_p.insert ('1.0', lines_p)
	left_p ['state'] = 'disabled'

	s.edit_event (err_syntax, syntax, txt, switched)
	edit = True
	try:
		w.title (
			title_edited + ' ' + os.path.basename(path) + ' ' + title_separator + ' ' + title if path != None 
			else title_edited + ' untitled ' + title_separator + ' ' + title
			)
	except TypeError:
		w.title (
			title_error + ' '  + title_separator + ' ' + title
			)
		print ('(!) unknown title error')

def exit (event):
	
	w.destroy ()

def new (event):
	
	global path, onstart
	onstart = False
	p_syntax ['text'] = 'plain text'
	txt.delete ('1.0', 'end')
	w.title (
		'untitled ' + title_separator + ' ' + title
		)
	path = None
	verscroll.pack (
		fill = 'y',
		side = 'right'
		)
	horscroll.pack (
		fill = 'x',
		side = 'bottom'
		)
	show_left_p != 'false' and left_p.pack (fill = 'y', side = 'left')
	txt.pack (
		side = 'left',
		fill = 'both',
		expand = True
		)
	s.switch (extension,
		syntax, txt,
		p_syntax, switched)

def openfile (event):

	global path, edit, extension, syntax, onstart
	onstart = False
	verscroll.pack (
		fill = 'y',
		side = 'right'
		)
	horscroll.pack (
		fill = 'x',
		side = 'bottom'
		)
	show_left_p != 'false' and left_p.pack (fill = 'y', side = 'left')
	txt.pack (
		side = 'left',
		fill = 'both',
		expand = True
		)
	path = fd.Open (w, filetypes = ftypes).show ()
	if path == '': return
	txt.delete ('1.0', 'end')
	try:
		txt.insert ('1.0', open (path).read ().rstrip ('\n'))
	except TypeError:
		path=None
		return
	edit = False
	basename = os.path.basename (path)
	extension = os.path.splitext (basename) [1]
	s.open (extension,
		err_syntax, syntax,
		txt, p_syntax)
	try:
		w.title (
			os.path.basename (path) + ' ' + title_separator + ' ' + title
			)
	except TypeError:
		w.title (
			title_error + ' '  + title_separator + ' ' + title
			)
		print ('(!) unknown title error')

def save(event):
	
	global path, edit
	if path != None:
		try:
			open(path, 'wt').write (txt.get ('1.0', 'end'))
		except FileNotFoundError:
			path=None
	elif path == 'editor/config.json':
		open ('editor/config.json', 'wt').write (txt.get('1.0', 'end'))
	else:
		path = fd.SaveAs(w, filetypes = ftypes).show ()
		if path == '': return
		try:
			open (path, 'wt').write (txt.get ('1.0', 'end'))
		except TypeError:
			path = None
			return
	edit = False
	try:
		w.title (
			os.path.basename (path) + ' ' + title_separator + ' ' + title
			)
	except TypeError:
		w.title (
			title_error + ' '  + title_separator + ' ' + title
			)
		print ('(!) unknown title error')
def saveas(event):
	global path, edit
	path = fd.SaveAs (w, filetypes = ftypes).show ()
	if path == '': return
	try:
		open (path, 'wt').write (txt.get ('1.0', 'end'))
	except TypeError:
		path = None
	edit = False
	try:
		w.title (
			os.path.basename (path) + ' ' + title_separator + ' ' + title
			)
	except TypeError:
		w.title (
			title_error + ' '  + title_separator + ' ' + title
			)
		print ('(!) unknown title error')

def config_open (event):

	try:
		verscroll.pack (
			fill = 'y',
			side = 'right'
			)
		horscroll.pack (
			fill = 'x',
			side = 'bottom'
			)
		show_left_p != 'false' and left_p.pack (fill = 'y', side = 'left')
		txt.pack (
			side = 'left',
			fill = 'both',
			expand = True
			)
		global path, edit, syntax, onstart
		path = 'editor/config.json'
		if path == '': return
		txt.delete ('1.0', 'end')
		txt.insert ('1.0', open (path).read ().rstrip ('\n'))
		edit = False
		basename = os.path.basename (path)
		extension = os.path.splitext (basename) [1]
		syntax = 'json'
		err_syntax != True and s.tokens_get (txt, s.jsonl ())
		p_syntax ['text'] = 'config'
		onstart = False
		try:
			w.title (
				'config ' + title_separator + ' ' + title
				)
		except TypeError:
			w.title (
				title_error + ' '  + title_separator + ' ' + title
				)
		print ('(!) unknown title error')
	except FileNotFoundError:
		path = None
		txt.delete ('1.0', 'end')
		print ('(!) config not found')

t_bg = '#222222'
t_fg = 'silver'
t_font = 'Consolas 10'
t_caret = 'orange'

def config_check ():

	global t_bg, t_fg, t_font, t_caret, t_p_bg, t_p_fg, t_p_font, p_syntax, p
	global title, title_separator, title_edited, show_menu, show_p, show_left_p
	if err_json != True:
		with open('editor/config.json','r',encoding='utf-8') as config_output:
			config_output_result = json.load (config_output)
		for config_output_variables in config_output_result ['notty']:
			title = config_output_variables ['title']
			title_separator = config_output_variables ['title-separator']
			title_edited = config_output_variables ['title-edited']
			show_menu = config_output_variables ['show-menu']
			show_p = config_output_variables ['show-panel']
			show_left_p = config_output_variables ['show-lines-panel']
			t_path = 'themes/' + config_output_variables ['theme'] + '.json'
		with open(t_path, 'r', encoding = 'utf-8') as output:
			output_result = json.load (output)
		for output_variables in output_result ['textbox']:
			t_bg = output_variables ['bg']
			t_fg = output_variables ['fg']
			t_font = output_variables ['font']
			t_caret = output_variables ['caret']
		for output_variables_p in output_result ['panel']:
			t_p_bg = output_variables_p ['bg']
			t_p_fg = output_variables_p ['fg']
			t_p_font = output_variables_p ['font']
		w ['bg'] = t_bg
		txt ['bg'] = t_bg
		txt ['fg'] = t_fg
		txt ['font'] = t_font
		txt ['insertbackground'] = t_caret
		p ['bg'] = t_p_bg
		p_syntax ['bg'] = t_p_bg
		p_syntax ['fg'] = t_p_fg
		p_syntax ['font'] = t_p_font

def syntax_switch_event (event): 
	
	s.switch (extension, syntax, txt, p_syntax, switched)

def manifest_check ():

	global notty_version, notty_build
	if err_json != True:
		with open('editor/manifest.json','r',encoding='utf-8') as manifest_out:
			manifest_out_res = json.load (manifest_out)
		for manifest_out_vars in manifest_out_res ['notty']:
			notty_version = manifest_out_vars ['version']
			notty_build = manifest_out_vars ['build']

t_src = 'themes/'

def t_switch (name):

	global t_bg, t_fg, t_font, t_caret, t_p_bg, t_p_fg, t_p_font, p_syntax, p
	if err_json != True:
		t_path = 'themes/' + name + '.json'
		with open(t_path, 'r', encoding = 'utf-8') as out:
			out_res = json.load (out)
		for out_vars in out_res ['txt']:
			t_bg = out_vars ['bg']
			t_fg = out_vars ['fg']
			t_font = out_vars ['font']
			t_caret = out_vars ['caret']
		for out_vars_p in out_res ['panel']:
			t_p_bg = out_vars_p ['bg']
			t_p_fg = out_vars_p ['fg']
			t_p_font = out_vars_p ['font']
		w ['bg'] = t_bg
		txt ['bg'] = t_bg
		txt ['fg'] = t_fg
		txt ['font'] = t_font
		txt ['insertbackground'] = t_caret
		p ['bg'] = t_p_bg
		p_syntax ['bg'] = t_p_bg
		p_syntax ['fg'] = t_p_fg
		p_syntax ['font'] = t_p_font

w = tk.Tk ()
w ['bg'] = t_bg
w.minsize (700, 400)
w.bind ('<Control-n>', new)
w.bind('<Control-o>', openfile)
w.bind ('<Control-s>', save)
w.bind('<Control-Shift-s>',saveas)
w.bind ('<Control-p>', config_open)
w.bind ('Control-q', exit)

class modifiedmixin:

	def _init (self):
		self.clearmodifiedflag ()
		self.bind_all ('<<Modified>>', self._beenmodified)
	def _beenmodified (self, event = None):
		if self._resetting_modified_flag: return
		self.clearmodifiedflag () ; self.beenmodified (event)
	def beenmodified (self, event = None): pass
	def clearmodifiedflag (self):
		self._resetting_modified_flag = True
		try: self.tk.call (self._w, 'edit', 'modified', 0)
		finally: self._resetting_modified_flag = False

class txt_class (modifiedmixin, tk.Text):

		def __init__ (self, *a, **b):
			tk.Text.__init__ (self, *a, **b)
			self._init ()
		def beenmodified (self, event=None):
			edit_event (0)

txt = txt_class()
txt ['relief'] = 'flat'
txt ['highlightthickness'] = 0
txt ['undo'] = True
txt ['wrap'] = 'none'
txt ['bg'] = t_bg
txt ['fg'] = t_fg
txt ['font'] = t_font
txt ['insertbackground'] = t_caret

if err_syntax != True: s.tokens_init(txt)

p = tk.Frame (w,
	bg = 'whitesmoke',
	relief = 'flat',
	height = 20
	)

p_hided = False
def p_hide ():

	global p_hided, p
	if p_hided == False:
		p.pack_forget ()
		p_hided = True
	else:
		verscroll.pack_forget ()
		horscroll.pack_forget ()
		left_p.pack_forget ()
		txt.pack_forget ()
		p.pack(
			side = 'bottom',
			fill = 'x'
			)
		if onstart == False:
			verscroll.pack (
				fill = 'y',
				side = 'right'
				)
			horscroll.pack (
				fill = 'x',
				side = 'bottom'
				)
			show_left_p != 'false' and left_p.pack (fill = 'y', side = 'left')
			txt.pack (
				side = 'left',
				fill = 'both',
				expand = True
				)
		p_hided = False

left_p_hided = False
def left_p_hide ():

	global left_p_hided, left_p
	if left_p_hided == False:
		left_p.pack_forget ()
		left_p_hided = True
	else:
		txt.pack_forget ()
		onstart == False and left_p.pack (fill = 'y', side = 'left'), txt.pack (side = 'left', fill = 'both', expand = True)
		left_p_hided = False

p_pos = tk.Label (p,
	bg = 'whitesmoke',
	fg = 'black',
	text = ''
	)
p_info = tk.Label (p,
	bg = 'whitesmoke',
	fg = 'black',
	text = ''
	)
p_syntax = tk.Label (p,
	bg = 'whitesmoke',
	fg = 'black',
	text = ''
	)

left_p = tk.Text (w,
	bg = 'gray',
	fg = 'white',
	relief = 'flat',
	font = 'Consolas 10',
	highlightthickness = 0,
	width = 6
	)

verscroll = tk.Scrollbar (w,
	background = 'whitesmoke',
	relief = 'flat',
	width = 15,
	command = lambda *args: (txt.yview(*args), left_p.yview(*args))
)
horscroll = tk.Scrollbar (w,
	background = 'whitesmoke',
	relief = 'flat',
	command = txt.xview,
	orient = 'horizontal'
	)

def new_menu (): new (0)
def open_menu (): openfile (0)
def save_menu (): save (0)
def saveas_menu (): saveas (0)
def exit_menu (): exit (0)
def config_menu(): config_open (0)

def set_text (): global syntax ; s.sset ('text', syntax, p_syntax, txt) ; syntax = 'text'
def set_py (): global syntax ; s.sset ('py', syntax, p_syntax, txt) ; syntax = 'py'
def set_c (): global syntax ; s.sset ('c', syntax, p_syntax, txt) ; syntax = 'c'
def set_cpp (): global syntax ; s.sset ('cpp', syntax, p_syntax, txt) ; syntax = 'cpp'
def set_json (): global syntax ; s.sset ('json', syntax, p_syntax, txt) ; syntax = 'json'
def set_html (): global syntax ; s.sset ('html', syntax, p_syntax, txt) ; syntax = 'html'
def set_css (): global syntax ; s.sset ('css', syntax, p_syntax, txt) ; syntax = 'css'
def set_js (): global syntax ; s.sset ('js', syntax, p_syntax, txt) ; syntax = 'js'
def set_md (): global syntax ; s.sset ('md', syntax, p_syntax, txt) ; syntax = 'md'

def about_menu ():

	about_w = tk.Tk()
	about_w.geometry ('300x150+100+100')
	about_w.resizable (width = False, height = False)
	about_w.title ('about')

	about_title = tk.Label (
		about_w,
		font = 'Consolas 20',
		text = 'notty'
		).pack (
		ipady = 20
		)
	about_other = tk.Label (
		about_w,
		text = 'copyright (c) 2020 - 2021 loadystudio\n version '+notty_version+' build '+notty_build
		).pack ()

def github_menu (): err_browser == False and wb.open ('https://github.com/loadystudio', new=2)

def loadystudio_menu (): err_browser == False and wb.open ('https://loadystudio.cf', new=2)

def changelog_menu ():

	try:
		verscroll.pack (fill = 'y', side = 'right')
		horscroll.pack (fill = 'x', side = 'bottom')
		left_p.pack (fill = 'y', side = 'left')
		txt.pack (side = 'left', fill = 'both', expand = True)
		global path, edit, syntax, onstart
		onstart = False
		path = 'CHANGELOG.md'
		if path == '': return
		txt.delete ('1.0', 'end')
		txt.insert ('1.0', open (path).read ().rstrip ('\n'))
		edit = False
		basename = os.path.basename (path)
		extension = os.path.splitext (basename) [1]
		syntax = 'md'
		err_syntax != True and s.tokens_get (txt, s.mdl ())
		p_syntax ['text'] = 'changelog'
		try:
			w.title (
				'changelog ' + title_separator + ' ' + title
				)
		except TypeError:
			w.title (
				title_error + ' '  + title_separator + ' ' + title
				)
		print ('(!) unknown title error')
	except FileNotFoundError:
		path = None
		txt.delete ('1.0', 'end')
		print ('(!) changelog not found')

def readme_menu ():

	try:
		verscroll.pack (fill = 'y', side = 'right')
		horscroll.pack (fill = 'x', side = 'bottom')
		left_p.pack (fill = 'y', side = 'left')
		txt.pack (side = 'left', fill = 'both', expand = True)
		global path, edit, syntax, onstart
		onstart = False
		path = 'README.md'
		if path == '': return
		txt.delete ('1.0', 'end')
		txt.insert ('1.0', open (path).read ().rstrip ('\n'))
		edit = False
		basename = os.path.basename (path)
		extension = os.path.splitext (basename) [1]
		syntax = 'md'
		err_syntax != True and s.tokens_get (txt, s.mdl ())
		p_syntax ['text'] = 'readme'
		try:
			w.title (
				'readme ' + title_separator + ' ' + title
				)
		except TypeError:
			w.title (
				title_error + ' '  + title_separator + ' ' + title
				)
		print ('(!) unknown title error')
	except FileNotFoundError:
		path = None
		txt.delete ('1.0', 'end')
		print ('(!) changelog not found')

def t_switch_dark (): t_switch ('dark')
def t_switch_light (): t_switch ('light')

menu = tk.Menu (w, relief = 'flat', bg = 'whitesmoke')
menu_file = tk.Menu (menu, tearoff = 0, relief = 'flat', bg = 'whitesmoke')
menu_pref = tk.Menu (menu, tearoff = 0, relief = 'flat', bg = 'whitesmoke')
menu_pref_themes = tk.Menu(menu_pref, tearoff=0, relief = 'flat', bg = 'whitesmoke')
menu_view = tk.Menu (menu, tearoff = 0, relief = 'flat', bg = 'whitesmoke')
menu_view_syntax = tk.Menu (menu_view, tearoff = 0, relief = 'flat', bg = 'whitesmoke')
menu_other = tk.Menu (menu, tearoff = 0, relief = 'flat', bg = 'whitesmoke')

menu_view.add_command (label = 'show/hide panel', command = p_hide)
menu_view.add_command (label = 'show/hide lines panel', command = left_p_hide)
menu_view.add_separator ()

menu_view_syntax.add_radiobutton (label = 'plain text', command = set_text)
menu_view_syntax.add_separator ()
menu_view_syntax.add_radiobutton (label = 'python', command = set_py)
menu_view_syntax.add_radiobutton (label = 'c lang', command = set_c)
menu_view_syntax.add_radiobutton (label = 'c++ lang', command = set_cpp)
menu_view_syntax.add_radiobutton (label = 'json', command = set_json)
menu_view_syntax.add_radiobutton (label = 'html', command = set_html)
menu_view_syntax.add_radiobutton (label = 'css', command = set_css)
menu_view_syntax.add_radiobutton (label = 'javascript', command = set_js)
menu_view_syntax.add_radiobutton (label = 'markdown', command = set_md)

menu_file.add_command (label = 'new file (ctrl+n)', command = new_menu)
menu_file.add_command (label = 'open file (ctrl+o)', command = open_menu)
menu_file.add_command (label = 'save file (ctrl+s)', command = save_menu)
menu_file.add_command (label = 'save file as (ctrl+shift+s)', command = saveas_menu)
menu_file.add_separator ()
menu_file.add_command (label = 'exit (ctrl+q)', command = exit_menu)

menu_pref.add_command (label = 'config', command = config_menu)
menu_pref.add_separator ()

menu_pref_themes.add_radiobutton (label = 'dark', command = t_switch_dark)
menu_pref_themes.add_radiobutton (label = 'light', command = t_switch_light)

menu_other.add_command (label = 'github', command = github_menu)
menu_other.add_command (label = 'loadystudio', command = loadystudio_menu)
menu_other.add_separator ()
menu_other.add_command (label = 'readme', command = readme_menu)
menu_other.add_command (label = 'changelog', command = changelog_menu)
menu_other.add_command (label = 'about', command = about_menu)

menu.add_cascade (label = 'file', menu = menu_file)
menu.add_cascade (label = 'view', menu = menu_view)
menu.add_cascade (label = 'prefrences', menu = menu_pref)
menu.add_cascade (label = 'other', menu = menu_other)

menu_view.add_cascade (label = 'syntax', menu = menu_view_syntax)

menu_pref.add_cascade (label = 'themes', menu = menu_pref_themes)

def text_cut (): text_copy () ; text_delete ()

def text_copy ():
	selection = txt.tag_ranges (tk.SEL)
	selection and txt.clipboard_clear (), txt.clipboard_append (txt.get (*selection))

def text_paste (): txt.insert (tk.INSERT, txt.clipboard_get ())

def text_delete ():
	selection = txt.tag_ranges (tk.SEL)
	selection and txt.delete (*selection)

popup = tk.Menu (w, tearoff = 0, bg='whitesmoke')
popup.add_command (label = 'cut (ctrl+x)', command = text_cut)
popup.add_command (label = 'copy (ctrl+c)', command = text_copy)
popup.add_command (label = 'paste (ctrl+v)', command = text_paste)
popup.add_command (label = 'delete (del)', command = text_delete)

def show_popup(event): popup.post(event.x_root, event.y_root)

txt.bind('<Button-3>', show_popup)

def pack():
	show_menu != 'false' and w.config (menu = menu)
	p_pos.pack (side = 'left')
	p_info.pack (side = 'left')
	p_syntax.pack (side = 'right')
	show_p != 'false' and p.pack (side = 'bottom', fill = 'x')
	txt ['yscrollcommand'] = verscroll.set
	left_p ['yscrollcommand'] = verscroll.set
	txt ['xscrollcommand'] = horscroll.set

def glaunch():

	config_check() ; manifest_check() ; pack ()
	w.title (title)
	w.tk.call('wm', 'iconphoto', w._w, tk.PhotoImage (file = 'icon.png') )
	w.geometry ('700x400+50+50')
	w.mainloop ()

if __name__ == '__main__': glaunch()