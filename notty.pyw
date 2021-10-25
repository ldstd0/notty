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

#sys.path.append ('src/')

err_json = False
err_tk = False
err_pygment = False
err_browser = False

def traceback (msg):
	global p_info
	p_info ['text'] = '(!) ' + msg

try:
	import json
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

try:
	import webbrowser as wb
except ImportError:
	err_browser = True
	print ('(!) web browser import error')

try:
	from pygments.lexers import JsonLexer as jsonl
	from pygments.lexers import CLexer as cl
	from pygments.lexers import HtmlLexer as htmll
	from pygments.lexers import CssLexer as cssl
	from pygments.lexers import CppLexer as cppl
	from pygments.lexers import PythonLexer as pyl
	from pygments.lexers import JavascriptLexer as jsl
	from pygments.lexers import MarkdownLexer as mdl
	from pygments.token import Token as tkn
except ImportError:
	err_pygment = True
	print ('(!) pygments import error')

cs_keyword = '#ff00cc'
cs_string_literal = '#00cc66'
cs_comment = '#999999'
cs_name_builtin = '#3399cc'
cs_keyword_ext = '#ff0000'

tkn_type_to_tag = {
		tkn.Keyword: 'keyword',
		tkn.Keyword.Type: 'keyword_ext',
		tkn.Keyword.Reserved: 'keyword_ext',
		tkn.Keyword.Constant:'keyword_ext',
		tkn.Operator.Word: 'keyword',
		tkn.Name.Builtin: 'name_builtin',
		tkn.Literal.String.Single: 'string_literal',
		tkn.Literal.String.Double: 'string_literal',
		tkn.Comment.Single: 'comment',
		tkn.Comment.Hashbang: 'comment',
		tkn.Comment.Multiline: 'comment'
}

def tkns_init ():

	txt.tag_config (
		'keyword',
		foreground = cs_keyword
		)
	txt.tag_config (
		'keyword_ext',
		foreground = cs_keyword_ext
		)
	txt.tag_config (
		'name_builtin',
		foreground = cs_name_builtin
		)
	txt.tag_config (
		'string_literal',
		foreground = cs_string_literal
		)
	txt.tag_config (
		'comment',
		foreground = cs_comment
		)

def tkns_get (lexer):

	global txt
	def get_text_coord (s: str, i: int):
		for row_number, line in enumerate (
			s.splitlines (keepends = True), 1):
			if i < len (line):
				return f'{row_number}.{i}'
			i -= len (line)
	a = "%.1f" % float(txt.index (tk.INSERT))
	vis_start = float (str(int(str(a)[:-2]) - 50) + '.0')
	if vis_start < 0: vis_start = 1.0
	vis_end = float (str(int(str(a)[:-2]) + 50) + '.0')
	for tag in txt.tag_names ():
		txt.tag_remove (
			tag,
			vis_start,
			vis_end
			)
	s = txt.get (
		vis_start,
		vis_end
		)
	tkns = lexer.get_tokens_unprocessed (s)
	for i, tkn_type, tkn in tkns:
		j = i + len (tkn)
		tkn_type in tkn_type_to_tag and txt.tag_add (
			tkn_type_to_tag [tkn_type],
			get_text_coord(s, i),
			get_text_coord(s, j)
			)
	txt.edit_modified (0)

def delete_tkns ():

	global txt
	for tag in txt.tag_names ():
		txt.tag_remove (
			tag,
			1.0,
			'end'
			)

def syntax_switch (event):
	
	global extension, syntax, txt, p_syntax, switched
	if syntax != 'text':
		syntax = 'text'
		delete_tkns ()
		switched = True
	elif switched == True:
		if extension != None:
			syntax = extension [1:]
		else:
			return
		switched = False
		if extension == '.py' or '.pyw':
			syntax='py'
			err_pygment == False and tkns_get (pyl())
		elif extension == '.js':
			err_pygment == False and tkns_get (jsl())
		elif extension == '.c':
			err_pygment == False and tkns_get (cl())
		elif extension == '.cpp':
			err_pygment == False and tkns_get (cppl())
		elif extension == '.html':
			err_pygment == False and tkns_get (htmll())
		elif extension == '.css':
			err_pygment == False and tkns_get (cssl())
		elif extension == '.json':
			err_pygment == False and tkns_get (jsonl())
		elif extension == '.md':
			err_pygment == False and tkns_get (mdl())

def syntax_set (name):
	global syntax, p_syntax, txt
	p_syntax ['text'] = str(name)
	if name == 'text':
		delete_tkns()
	elif name == 'py':
		tkns_get (pyl ())
	elif name == 'c':
		tkns_get (cl ())
	elif name == 'cpp':
		tkns_get (cppl ())
	elif name == 'json':
		tkns_get (jsonl ())
	elif name == 'html':
		tkns_get (htmll ())
	elif name == 'css':
		tkns_get (cssl ())
	elif name == 'js':
		tkns_get (jsl ())
	elif name == 'md':
		tkns_get(mdl ())

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

	p_pos ['text'] = txt.index (tk.INSERT)

	count = len (
		txt.get (
			'1.0',
			'end'
			).splitlines ()
		)
	lines = 1
	lines_p = ''
	while lines <= count:
		if lines == count:
			lines_p += str (lines)
		else:
			lines_p += str (lines) + '\n'
		lines += 1
	left_p ['state'] = 'normal'
	left_p.delete (
		'1.0',
		'end'
		)
	left_p.insert (
		'1.0',
		lines_p
		)
	left_p ['state'] = 'disabled'
	if err_pygment != True and switched == False:
		if syntax == 'py' or syntax == 'pyw':
			tkns_get (pyl())
		elif syntax == 'js':
			tkns_get (jsl())
		elif syntax == 'c':
			tkns_get (cl())
		elif syntax == 'cpp':
			tkns_get (cppl())
		elif syntax == 'html':
			tkns_get (htmll())
		elif syntax == 'css':
			tkns_get (cssl())
		elif syntax == 'json':
			tkns_get (jsonl())
		elif syntax == 'md':
			tkns_get (mdl())
	edit = True
	try:
		w.title (
			title_edited + ' ' + os.path.basename(path) + ' ' + title_separator + ' ' + title if path != None 
			else title_edited + ' untitled ' + title_separator + ' ' + title
			)
		if path == 'editor/config.json':
			w.title (
				'config '  + title_separator + ' ' + title
				)
		elif path == 'README.md':
			w.title (
				'readme '  + title_separator + ' ' + title
				)
		elif path == 'CHANGELOG.md':
			w.title (
				'changelog '  + title_separator + ' ' + title
				)
		elif path == 'LICENSE':
			w.title (
				'license '  + title_separator + ' ' + title
				)
	except TypeError:
		w.title (
			title_error + ' '  + title_separator + ' ' + title
			)
		traceback ('unknown title error')

def exit (event):
	
	w.destroy ()

def new (event):
	
	global path, onstart
	onstart = False
	start_destroy ()
	p_syntax ['text'] = 'text'
	txt.delete (
		'1.0',
		'end'
		)
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
	show_left_p != 'false' and left_p.pack (
		fill = 'y',
		side = 'left'
		)
	txt.pack (
		side = 'left',
		fill = 'both',
		expand = True
		)
	syntax_switch (0)
	p_info ['text'] = 'new tab opened'

def openfile (event):

	global path, edit, extension, syntax, onstart, p_syntax
	start_destroy ()
	onstart = False
	verscroll.pack (
		fill = 'y',
		side = 'right'
		)
	horscroll.pack (
		fill = 'x',
		side = 'bottom'
		)
	show_left_p != 'false' and left_p.pack (
		fill = 'y',
		side = 'left'
		)
	txt.pack (
		side = 'left',
		fill = 'both',
		expand = True
		)
	path = fd.Open (
		w,
		filetypes = ftypes
		).show ()
	if path == '': return
	txt.delete (
		'1.0',
		'end'
		)
	try:
		txt.insert (
			'1.0',
			open (path).read ().rstrip ('\n'))
	except TypeError:
		path = None
		return
	edit = False
	basename = os.path.basename (path)
	extension = str(os.path.splitext (basename) [1])
	syntax = extension [1:]
	p_syntax ['text'] = syntax
	if extension == '.py':
		err_pygment == False and tkns_get (pyl())
	elif extension == '.pyw':
		syntax = 'py'
		p_syntax ['text']=syntax
		err_pygment == False and tkns_get (pyl())
	elif extension == '.js':
		err_pygment == False and tkns_get (jsl())
	elif extension == '.c':
		err_pygment == False and tkns_get (cl())
	elif extension == '.cpp':
		err_pygment == False and tkns_get (cppl())
	elif extension == '.html':
		err_pygment == False and tkns_get (htmll())
	elif extension == '.css':
		err_pygment == False and tkns_get (cssl())
	elif extension == '.json':
		err_pygment == False and tkns_get (jsonl())
	elif extension == '.md':
		err_pygment == False and tkns_get (mdl())
	else:
		syntax = 'text'
		p_syntax ['text'] = 'text'
	p_info ['text'] = path + ' opened'
	try:
		w.title (
			os.path.basename (path) + ' ' + title_separator + ' ' + title
			)
	except TypeError:
		w.title (
			title_error + ' '  + title_separator + ' ' + title
			)
		traceback ('unknown title error')

def save (event):
	
	global path, edit
	if path != None:
		try:
			open (
				path,
				'wt'
				).write (
				txt.get (
					'1.0',
					'end'
					)
				)
		except FileNotFoundError:
			path = None
	else:
		path = fd.SaveAs (
			w,
			filetypes = ftypes
			).show ()
		if path == '': return
		try:
			open (
				path,
				'wt'
				).write (
				txt.get (
					'1.0',
					'end'
					)
				)
		except TypeError:
			path = None
			return
	edit = False
	p_info ['text'] = path + ' saved'
	try:
		w.title (
			os.path.basename (path) + ' ' + title_separator + ' ' + title
			)
	except TypeError:
		w.title (
			title_error + ' '  + title_separator + ' ' + title
			)
		traceback ('unknown title error')

def saveas (event):
	global path, edit
	path = fd.SaveAs (
		w,
		filetypes = ftypes
		).show ()
	if path == '': return
	try:
		open (
			path,
			'wt'
			).write (
			txt.get (
				'1.0',
				'end'
				)
			)
	except TypeError:
		path = None
	edit = False
	p_info ['text'] = path + ' saved'
	try:
		w.title (
			os.path.basename (path) + ' ' + title_separator + ' ' + title
			)
	except TypeError:
		w.title (
			title_error + ' '  + title_separator + ' ' + title
			)
		traceback ('unknown title error')

def config_open (event):

	try:
		start_destroy ()
		verscroll.pack (
			fill = 'y',
			side = 'right'
			)
		horscroll.pack (
			fill = 'x',
			side = 'bottom'
			)
		show_left_p != 'false' and left_p.pack (
			fill = 'y',
			side = 'left'
			)
		txt.pack (
			side = 'left',
			fill = 'both',
			expand = True
			)
		global path, edit, syntax, onstart
		path = 'editor/config.json'
		if path == '': return
		txt.delete (
			'1.0',
			'end'
			)
		txt.insert (
			'1.0',
			open (path).read ().rstrip ('\n')
			)
		edit = False
		basename = os.path.basename (path)
		extension = os.path.splitext (basename) [1]
		syntax = 'json'
		err_pygment != True and tkns_get (jsonl ())
		p_syntax ['text'] = 'config'
		p_info ['text'] = 'config opened'
		onstart = False
	except FileNotFoundError:
		path = None
		txt.delete ('1.0', 'end')
		traceback ('config not found')

t_bg = '#222222'
t_fg = 'silver'
t_font = 'Consolas 10'
t_caret = 'orange'

def config_check ():

	global t_bg, t_fg, t_font, t_caret, t_p_bg, t_p_fg, t_p_font, p_syntax, p
	global title, title_separator, title_edited, show_menu, show_p, show_left_p
	if err_json != True:
		with open (
			'editor/config.json',
			'r',
			encoding = 'utf-8'
			) as out:
			config_out_res = json.load (out)
		for config_out_vars in config_out_res ['notty']:
			title = config_out_vars ['title']
			title_separator = config_out_vars ['title-separator']
			title_edited = config_out_vars ['title-edited']
			show_menu = config_out_vars ['show-menu']
			show_p = config_out_vars ['show-panel']
			show_left_p = config_out_vars ['show-lines-panel']
			t_path = 'themes/' + config_out_vars ['theme'] + '.json'
			cs_path = 'themes/cs/' + config_out_vars ['color-scheme'] + '.json'
		with open (
			t_path,
			'r',
			encoding = 'utf-8'
			) as out:
			out_res = json.load (out)
		for out_vars in out_res ['textbox']:
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
		global cs_comment, cs_keyword, cs_keyword_ext
		global cs_name_builtin, cs_string_literal
		with open (
			cs_path,
			'r',
			encoding = 'utf-8'
			) as out:
			out_res = json.load (out)
		for out_vars in out_res ['colors']:
			cs_comment = out_vars ['comment']
			cs_keyword = out_vars ['keyword']
			cs_keyword_ext = out_vars ['keyword-ext']
			cs_name_builtin = out_vars ['name-builtin']
			cs_string_literal = out_vars ['string-literal']
		tkns_init ()

def manifest_check ():

	global _ver, _bld
	if err_json != True:
		with open (
			'editor/manifest.json',
			'r',
			encoding = 'utf-8'
			) as manifest_out:
			manifest_out_res = json.load (manifest_out)
		for manifest_out_vars in manifest_out_res ['notty']:
			_ver = manifest_out_vars ['version']
			_bld = manifest_out_vars ['build']

t_src = 'themes/'

def t_switch (name):

	global t_bg, t_fg, t_font, t_caret, t_p_bg, t_p_fg, t_p_font, p_syntax, p
	global start_logo, start_info, start_help
	if err_json != True:
		t_path = 'themes/' + name + '.json'
		with open(t_path, 'r', encoding = 'utf-8') as out:
			out_res = json.load (out)
		for out_vars in out_res ['textbox']:
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
		start_logo ['bg'] = t_bg
		start_logo ['fg'] = t_fg
		start_info ['bg'] = t_bg
		start_info ['fg'] = t_fg
		start_help ['bg'] = t_bg
		start_help ['fg'] = t_fg

def cs_switch (name):

	global cs_comment, cs_keyword, cs_keyword_ext
	global cs_name_builtin, cs_string_literal
	if err_json != True:
		t_path = 'themes/cs/' + name + '.json'
		with open(t_path, 'r', encoding = 'utf-8') as out:
			out_res = json.load (out)
		for out_vars in out_res ['colors']:
			cs_comment = out_vars ['comment']
			cs_keyword = out_vars ['keyword']
			cs_keyword_ext = out_vars ['keyword-ext']
			cs_name_builtin = out_vars ['name-builtin']
			cs_string_literal = out_vars ['string-literal']
		tkns_init ()

w = tk.Tk ()
w ['bg'] = t_bg
w.minsize (700, 400)
w.bind (
	'<Control-n>',
	new
	)
w.bind (
	'<Control-o>',
	openfile
	)
w.bind (
	'<Control-s>',
	save
	)
w.bind (
	'<Control-Shift-s>',
	saveas
	)
w.bind (
	'<Control-p>',
	config_open
	)
w.bind (
	'Control-q',
	exit
	)

class modifiedmixin:

	def _init (self):
		self.clearmodifiedflag ()
		self.bind_all (
			'<<Modified>>',
			self._beenmodified
			)
	def _beenmodified (
		self,
		event = None
		):
		if self._resetting_modified_flag: return
		self.clearmodifiedflag ()
		self.beenmodified (event)
	def beenmodified (
		self,
		event = None
		): pass
	def clearmodifiedflag (self):
		self._resetting_modified_flag = True
		try:
			self.tk.call (
				self._w,
				'edit',
				'modified',
				0
				)
		finally:
			self._resetting_modified_flag = False

class txt_class (modifiedmixin, tk.Text):

		def __init__ (self, *a, **b):
			tk.Text.__init__ (self, *a, **b)
			self._init ()
		def beenmodified (self, event = None):
			edit_event (0)

txt = txt_class ()
txt ['relief'] = 'flat'
txt ['highlightthickness'] = 0
txt ['undo'] = True
txt ['wrap'] = 'none'
txt ['bg'] = t_bg
txt ['fg'] = t_fg
txt ['font'] = t_font
txt ['insertbackground'] = t_caret

err_pygment == False and tkns_init ()

p = tk.Frame (
	w,
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
		p.pack (
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
			show_left_p != 'false' and left_p.pack (
				fill = 'y',
				side = 'left'
				)
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
		onstart==False and left_p.pack (
			fill = 'y',
			side = 'left'
			), txt.pack (
			side = 'left',
			fill = 'both',
			expand = True
			)
		left_p_hided = False

p_pos = tk.Label (p,
	bg = 'whitesmoke',
	fg = 'black',
	font = t_font,
	text = ''
	)
p_info = tk.Label (p,
	bg = 'whitesmoke',
	fg = 'black',
	font = t_font,
	text = ''
	)
p_syntax = tk.Label (p,
	bg = 'whitesmoke',
	fg = 'black',
	font = t_font,
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

def set_text():
	global syntax
	syntax_set('text')
	syntax = 'text'
def set_py():
	global syntax
	syntax_set('py')
	syntax = 'py'
def set_c():
	global syntax
	syntax_set('c')
	syntax = 'c'
def set_cpp():
	global syntax
	syntax_set('cpp')
	syntax = 'cpp'
def set_json():
	global syntax
	syntax_set('json')
	syntax = 'json'
def set_html():
	global syntax
	syntax_set('html')
	syntax = 'html'
def set_css():
	global syntax
	syntax_set('css')
	syntax = 'css'
def set_js():
	global syntax
	syntax_set('js')
	syntax = 'js'
def set_md ():
	global syntax
	syntax_set ('md')
	syntax = 'md'

def about_menu ():
	p_info ['text'] = 'about opened'
	about_w = tk.Tk ()
	about_w ['bg'] = 'white'
	about_w.geometry ('300x150+100+100')
	about_w.resizable (
		width = False,
		height = False
		)
	about_w.title ('about')

	about_title = tk.Label (
		about_w,
		bg = 'white',
		font = 'Consolas 20',
		text = 'notty'
		).pack (
		ipady = 20
		)
	about_other = tk.Label (
		about_w,
		font = t_font,
		bg = 'white',
		text = 'copyright © 2020-2021 loadystudio\nApache License v2.0\nv' + _ver + ' build ' + _bld + ' stable'
		).pack ()

def github_menu ():
	err_browser == False and wb.open (
		'https://github.com/loadystudio',
		new = 2
		)
	p_info ['text'] = 'https://github.com/loadystudio opened'

def loadystudio_menu ():
	err_browser == False and wb.open (
		'http://loadystudio.cf',
		new = 2
		)
	p_info ['text'] = 'http://loadystudio.cf opened'

def changelog_menu ():

	try:
		start_destroy ()
		verscroll.pack (
			fill = 'y',
			side = 'right'
			)
		horscroll.pack (
			fill = 'x',
			side = 'bottom'
			)
		left_p.pack (
			fill = 'y',
			side = 'left'
			)
		txt.pack (
			side = 'left',
			fill = 'both',
			expand = True
			)
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
		err_pygment != True and tkns_get (mdl ())
		p_syntax ['text'] = 'changelog'
		p_info ['text'] = 'changelog saved'
	except FileNotFoundError:
		path = None
		txt.delete ('1.0', 'end')
		traceback ('changelog not found')

def readme_menu ():

	try:
		start_destroy ()
		verscroll.pack (
			fill = 'y',
			side = 'right'
			)
		horscroll.pack (
			fill = 'x',
			side = 'bottom'
			)
		left_p.pack (
			fill = 'y',
			side = 'left'
			)
		txt.pack (
			side = 'left',
			fill = 'both',
			expand = True
			)
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
		err_pygment != True and tkns_get (mdl ())
		p_syntax ['text'] = 'readme'
		p_info ['text'] = 'readme opened'
	except FileNotFoundError:
		path = None
		txt.delete ('1.0', 'end')
		traceback ('changelog not found')

def license_menu ():

	try:
		start_destroy ()
		verscroll.pack (
			fill = 'y',
			side = 'right'
			)
		horscroll.pack (
			fill = 'x',
			side = 'bottom'
			)
		left_p.pack (
			fill = 'y',
			side = 'left'
			)
		txt.pack (
			side = 'left',
			fill = 'both',
			expand = True
			)
		global path, edit, syntax, onstart
		onstart = False
		path = 'LICENSE'
		if path == '': return
		txt.delete ('1.0', 'end')
		txt.insert ('1.0', open (path).read ().rstrip ('\n'))
		edit = False
		basename = os.path.basename (path)
		extension = os.path.splitext (basename) [1]
		syntax = 'text'
		p_syntax ['text'] = 'license'
		p_info ['text'] = 'license opened'
	except FileNotFoundError:
		path = None
		txt.delete ('1.0', 'end')
		traceback ('license not found')

def t_switch_dark ():
	t_switch ('dark')

def t_switch_light ():
	t_switch ('light')

def cs_switch_standart ():
	cs_switch ('standart')

menu = tk.Menu (
	w,
	relief = 'flat',
	bg = 'whitesmoke'
	)
menu_file = tk.Menu (
	menu,
	tearoff = 0,
	relief = 'flat',
	bg = 'whitesmoke'
	)
menu_pref = tk.Menu (
	menu,
	tearoff = 0,
	relief = 'flat',
	bg = 'whitesmoke'
	)
menu_pref_themes = tk.Menu (
	menu_pref,
	tearoff = 0,
	relief = 'flat',
	bg = 'whitesmoke'
	)
menu_pref_cs = tk.Menu (
	menu_pref,
	tearoff = 0,
	relief = 'flat',
	bg = 'whitesmoke'
	)
menu_view = tk.Menu (
	menu,
	tearoff = 0,
	relief = 'flat',
	bg = 'whitesmoke'
	)
menu_view_syntax = tk.Menu (
	menu_view,
	tearoff = 0,
	relief = 'flat',
	bg = 'whitesmoke'
	)
menu_other = tk.Menu(
	menu,
	tearoff = 0,
	relief = 'flat',
	bg = 'whitesmoke'
	)

menu_view.add_command (
	label = 'show/hide panel',
	command = p_hide
	)
menu_view.add_command (
	label = 'show/hide lines panel',
	command = left_p_hide
	)
menu_view.add_separator ()

menu_view_syntax.add_radiobutton (
	label = 'text',
	command = set_text
	)
menu_view_syntax.add_separator ()
menu_view_syntax.add_radiobutton (
	label = 'python',
	command = set_py
	)
menu_view_syntax.add_radiobutton (
	label = 'c lang',
	command = set_c
	)
menu_view_syntax.add_radiobutton (
	label = 'c++ lang',
	command = set_cpp
	)
menu_view_syntax.add_radiobutton (
	label = 'json',
	command = set_json
	)
menu_view_syntax.add_radiobutton (
	label = 'html',
	command = set_html
	)
menu_view_syntax.add_radiobutton (
	label = 'css',
	command = set_css
	)
menu_view_syntax.add_radiobutton (
	label = 'javascript',
	command = set_js
	)
menu_view_syntax.add_radiobutton (
	label = 'markdown',
	command = set_md
	)

menu_file.add_command (
	label = 'new file (ctrl+n)',
	command = new_menu
	)
menu_file.add_command (
	label = 'open file (ctrl+o)',
	command = open_menu
	)
menu_file.add_command (
	label = 'save file (ctrl+s)',
	command = save_menu
	)
menu_file.add_command (
	label = 'save file as (ctrl+shift+s)',
	command = saveas_menu
	)
menu_file.add_separator ()
menu_file.add_command (
	label = 'exit (ctrl+q)',
	command = exit_menu
	)

menu_pref.add_command (
	label = 'config',
	command = config_menu
	)
menu_pref.add_separator ()

menu_pref_themes.add_radiobutton (
	label = 'dark',
	command = t_switch_dark
	)
menu_pref_themes.add_radiobutton (
	label = 'light',
	command = t_switch_light
	)

menu_pref_cs.add_radiobutton (
	label = 'standart',
	command = cs_switch_standart
	)

menu_other.add_command (
	label = 'github',
	command = github_menu
	)
menu_other.add_command (
	label = 'loadystudio',
	command = loadystudio_menu
	)
menu_other.add_separator ()
menu_other.add_command (
	label = 'readme',
	command = readme_menu
	)
menu_other.add_command (
	label = 'changelog',
	command = changelog_menu
	)
menu_other.add_command (
	label = 'license',
	command = license_menu
	)
menu_other.add_command (
	label = 'about',
	command = about_menu
	)

menu.add_cascade (
	label = 'file',
	menu = menu_file
	)
menu.add_cascade (
	label = 'view',
	menu = menu_view
	)
menu.add_cascade (
	label = 'preferences',
	menu = menu_pref
	)
menu.add_cascade (
	label = 'other',
	menu = menu_other
	)

menu_view.add_cascade (
	label = 'syntax',
	menu = menu_view_syntax
	)
menu_pref.add_cascade (
	label = 'themes',
	menu = menu_pref_themes
	)
menu_pref.add_cascade (
	label = 'color schemes',
	menu = menu_pref_cs
	)

def txt_cut ():
	txt_copy ()
	txt_del ()

def txt_copy ():

	sel = txt.tag_ranges (tk.SEL)
	sel and txt.clipboard_clear (), txt.clipboard_append (txt.get (*sel))

def txt_paste ():

	txt.insert (
		tk.INSERT,
		txt.clipboard_get ()
		)

def txt_del ():

	sel = txt.tag_ranges (tk.SEL)
	sel and txt.delete (*sel)

popup = tk.Menu (w,
	tearoff = 0,
	bg='whitesmoke'
	)
popup.add_command (
	label = 'cut (ctrl+x)',
	command = txt_cut
	)
popup.add_command (
	label = 'copy (ctrl+c)',
	command = txt_copy
	)
popup.add_command (
	label = 'paste (ctrl+v)',
	command = txt_paste
	)
popup.add_command (
	label = 'delete (del)',
	command = txt_del
	)

def show_popup (event):

	popup.post (
		event.x_root,
		event.y_root
		)

txt.bind (
	'<Button-3>',
	show_popup
	)

def pack ():

	show_menu != 'false' and w.config (menu = menu)
	p_pos.pack (side = 'left')
	p_info.pack (side = 'left')
	p_syntax.pack (side = 'right')
	p_syntax.bind (
		'<Button-1>',
		syntax_switch
		)
	show_p != 'false' and p.pack (
		side = 'bottom',
		fill = 'x'
		)
	txt ['yscrollcommand'] = verscroll.set
	left_p ['yscrollcommand'] = verscroll.set
	txt ['xscrollcommand'] = horscroll.set
	global start_logo, start_info, start_help
	start_logo = tk.Label (
		w,
		bg = t_bg,
		fg = t_fg,
		font = 'Consolas 30',
		text = 'notty'
		)
	start_logo.pack (ipady = 45)
	start_info = tk.Label (
		w,
		bg = t_bg,
		fg = t_fg,
		font = 'Consolas 10',
		text = 'v' + _ver + ' build ' + _bld + ' stable\ncopyright © 2020-2021 loadystudio'
		)
	start_info.pack (ipady = 0)
	start_help = tk.Label (
		w,
		bg = t_bg,
		fg = t_fg,
		font = 'Consolas 20',
		text = 'new file (ctrl-n)\nopen file (ctrl-o)\nopen config (ctrl-p)'
		)
	start_help.pack (ipady = 30)

def start_destroy ():

	global start_logo, start_info, start_help

	start_logo.destroy ()
	start_info.destroy ()
	start_help.destroy ()

def launch ():

	config_check ()
	manifest_check ()
	pack ()
	w.title (title)
	w.tk.call (
		'wm',
		'iconphoto',
		w._w,
		tk.PhotoImage (
			file = 'icon.png'
			)
		)
	w.geometry ('700x400+50+50')
	w.mainloop ()

if __name__ == '__main__':
	launch ()