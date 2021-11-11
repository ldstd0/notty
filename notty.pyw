#!/usr/bin/python3
import sys, os, json
import tkinter.filedialog as fd
import webbrowser as wb
from tkinter import *
from pygments.lexers import *
from pygments.token import Token as tkn

def info (i): p_info ['text'] = i

cs_keyword, cs_name = 'violet', 'cyan'
cs_other, cs_str = 'orange', 'yellow'
cs_comment, cs_builtin = '#999999', 'cyan'

tkn_type_to_tag = {
	tkn.Keyword: 'keyword', tkn.Other: 'other',
	tkn.Keyword.Constant: 'other', tkn.Operator: 'keyword',
	tkn.Literal.String.Single: 'str_literal',
	tkn.Literal.String.Double: 'str_literal',
	tkn.Comment.Single: 'comment', tkn.Comment.Hashbang: 'comment',
	tkn.Comment.Multiline: 'comment'
}

def tkns_init ():
	txt.tag_config ('keyword', foreground = cs_keyword)
	txt.tag_config ('str_literal', foreground = cs_str)
	txt.tag_config ('comment', foreground = cs_comment)
	txt.tag_config ('other', foreground = cs_other)

def tkns_get (lexer):
	global txt
	def get_text_coord (s: str, i: int):
		for row_number, line in enumerate (
			s.splitlines (keepends = True), 1):
			if i < len (line): return f'{row_number}.{i}'
			i -= len (line)
	delete_tkns ()
	s = txt.get (1.0, 'end')
	tkns = lexer.get_tokens_unprocessed (s)
	for i, tkn_type, tkn in tkns:
		j = i + len (tkn)
		tkn_type in tkn_type_to_tag and txt.tag_add (
			tkn_type_to_tag [tkn_type],
			get_text_coord (s, i), get_text_coord (s, j)
			)
	txt.edit_modified (0)

def delete_tkns ():
	for tag in txt.tag_names (): txt.tag_remove (tag, 1.0, 'end')

def syntax_switch (event):
	global ext, syntax, txt, p_syntax, switched
	if syntax != 'text':
		syntax, switched = 'text', True
		delete_tkns ()
	elif switched:
		if ext != None: syntax = ext [1:]
		else: return
		switched = False
		if ext == '.py' or '.pyw':
			syntax = 'py'
			tkns_get (PythonLexer())
		elif ext == '.js': tkns_get (JavascriptLexer())
		elif ext == '.c': tkns_get (CLexer())
		elif ext == '.cpp': tkns_get (CppLexer())
		elif ext == '.html': tkns_get (HtmlLexer())
		elif ext == '.css': tkns_get (CssLexer())
		elif ext == '.json': tkns_get (JsonLexer())
		elif ext == '.md': tkns_get (MarkdownLexer())
		elif ext == '.java': tkns_get (JavaLexer())

def syntax_set (name):
	global syntax, p_syntax, txt
	syntax, p_syntax ['text'] = name, name
	if name == 'text': delete_tkns()
	elif name == 'py': tkns_get (PythonLexer ())
	elif name == 'c': tkns_get (CLexer ())
	elif name == 'cpp': tkns_get (CppLexer ())
	elif name == 'json': tkns_get (JsonLexer ())
	elif name == 'html': tkns_get (HtmlLexer ())
	elif name == 'css': tkns_get (CssLexer ())
	elif name == 'js': tkns_get (JavascriptLexer ())
	elif name == 'md': tkns_get(MarkdownLexer ())
	elif name == 'java': tkns_get(JavaLexer ())

ftypes = [('all', '*'),
	('python', '*.py*'),
	('javascript', '*.js'),
	('c lang', '*.c'),
	('c++ lang', '*.cpp'),
	('css', '*.css'),
	('html', '*.html'),
	('json', '*.json'),
	('java', '*.java'),
	('markdown', '*.md')
]
onstart = True
ext, path = None, None
edit, switched = False, False
syntax = 'text'
show_menu, show_p, show_left_p = 'true', 'true', 'true' 

def txt_clr (): txt.delete (1.0, 'end')
def txt_ins (t): txt.insert (1.0, t)

def edit_event (event):
	global p_pos, txt
	p_pos ['text'] = txt.index (INSERT)
	count = len (txt.get ('1.0', 'end').splitlines ())
	lines, lines_p = 1, ''
	while lines <= count:
		if lines == count: lines_p += str (lines)
		else: lines_p += str (lines) + '\n'
		lines += 1
	left_p ['state'] = 'normal'
	left_p.delete ('1.0', 'end')
	left_p.insert ('1.0', lines_p)
	left_p ['state'] = 'disabled'
	if switched == False:
		if syntax == 'py' or syntax == 'pyw': tkns_get (PythonLexer())
		elif syntax == 'js': tkns_get (JavascriptLexer())
		elif syntax == 'c': tkns_get (CLexer())
		elif syntax == 'cpp': tkns_get (CppLexer())
		elif syntax == 'html': tkns_get (HtmlLexer())
		elif syntax == 'css': tkns_get (CssLexer())
		elif syntax == 'json': tkns_get (JsonLexer())
		elif syntax == 'md': tkns_get (MarkdownLexer())
		elif syntax == 'java': tkns_get (JavaLexer())
	edit = True
	try:
		w.title (
			os.path.basename (path) + ' - notty' if path != None
			else 'untitled - notty'
			)
		if path == 'editor/config.json': w.title ('config - notty')
		elif path == 'README.md': w.title ('readme - notty')
		elif path == 'CHANGELOG.md': w.title ('changelog - notty')
		elif path == 'LICENSE': w.title ('license - notty')
	except TypeError:
		w.title ('error - notty')
		info ('(!) title error')

def _exit (event): w.destroy ()

def _new (event):
	global path, onstart
	s_destroy ()
	init_editor_ui ()
	syntax_switch (0)
	txt_clr ()
	info ('new tab opened')
	path, onstart = None, False

def path_open (fpath = None):
	global path, edit, ext, syntax, p_syntax
	s_destroy ()
	init_editor_ui ()
	if not fpath:
		path = fd.Open (w, filetypes = ftypes).show ()
		if path == '': return
		txt_clr ()
		try: txt_ins (open (path).read ().rstrip ('\n'))
		except TypeError:
			path = None
			return
	else:
		path = fpath
		try:
			txt_clr ()
			txt_ins (open (path).read ().rstrip ('\n'))
		except FileNotFoundError:
			path = None
			txt_clr()
			traceback ('file not found')
			return
	edit, onstart = False, False
	ext = os.path.splitext (os.path.basename (path)) [1]
	syntax, p_syntax ['text'] = ext [1:], syntax
	info (path + ' opened')
	if ext == '': syntax, p_syntax ['text'] = 'text', 'text'

def _open (event): path_open ()

def _save (event):
	global path, edit
	if path != None:
		try: open (path, 'wt').write (txt.get ('1.0', 'end'))
		except FileNotFoundError: path = None
	else:
		path = fd.SaveAs (w, filetypes = ftypes).show ()
		if path == '': return
		try: open (path, 'wt').write (txt.get ('1.0', 'end'))
		except TypeError:
			path = None
			return
	edit = False
	info (path + ' saved')

def _saveas (event):
	global path, edit
	path = fd.SaveAs (w, filetypes = ftypes).show ()
	if path == '': return
	try: open (path,'wt').write (txt.get ('1.0', 'end'))
	except TypeError:
		path = None
		return
	edit = False
	info (path + ' saved')

def conf_open (event): path_open ('editor/config.json')
def changelog_open (): path_open ('CHANGELOG.md')
def readme_open (): path_open ('README.md')
def license_open (): path_open ('LICENSE')

t_bg, t_fg = '#222222', 'silver'
t_font, t_caret = 'Consolas 11', 'orange'
t_p_bg, t_p_fg, t_p_font = 'whitesmoke', 'black', 'Consolas 10'

def conf_check ():
	global t_bg, t_fg, t_font, t_caret, t_p_bg, t_p_fg, t_p_font
	with open ('editor/config.json', 'r', encoding = 'utf-8') as out:
		conf_res = json.load (out)
	for conf_var in conf_res ['notty']:
		show_menu, show_p = conf_var ['menu'], conf_var ['panel']
		show_left_p = conf_var ['lines']
		t_path = 'themes/' + conf_var ['theme'] + '.json'
		cs_path = 'themes/cs/' + conf_var ['color-scheme'] + '.json'
	with open (t_path, 'r', encoding = 'utf-8') as out:
		res = json.load (out)
	for var in res ['textbox']:
		t_bg, t_fg = var ['bg'], var ['fg']
		t_font, t_caret = var ['font'], var ['caret']
	for var_p in res ['panel']:
		t_p_bg, t_p_fg = var_p ['bg'], var_p ['fg']
		t_p_font = var_p ['font']
	w ['bg'], p ['bg'] = t_bg, t_p_bg
	txt.configure (
		bg = t_bg, fg = t_fg, font = t_font, insertbackground = t_caret
		)
	for i in p_syntax, p_pos, p_info:
		i.configure (bg = t_p_bg, fg = t_p_fg, font = t_p_font)
	for i in s_logo, s_info, s_new, s_open, s_conf:
		i.configure (bg = t_bg, fg = t_fg)
	for i in s_new, s_open, s_conf: i.configure (font = 'Consolas 16')
	with open (cs_path, 'r', encoding = 'utf-8') as out:
		out_res = json.load (out)
	for out_vars in out_res ['colors']:
		cs_comment, cs_other = out_vars ['comment'], out_vars ['other']
		cs_keyword = out_vars ['keyword']
		cs_builtin, cs_str = out_vars ['builtin'], out_vars ['string']
	tkns_init ()

t_src = 'themes/'
def t_switch (name):
	t_path = 'themes/' + name + '.json'
	with open (t_path, 'r', encoding = 'utf-8') as out:
		out_res = json.load (out)
	for out_vars in out_res ['textbox']:
		t_bg, t_fg = out_vars ['bg'], out_vars ['fg']
		t_font, t_caret = out_vars ['font'], out_vars ['caret']
	for out_vars_p in out_res ['panel']:
		t_p_bg, t_p_fg = out_vars_p ['bg'], out_vars_p ['fg']
		t_p_font = out_vars_p ['font']
	w ['bg'], p ['bg'] = t_bg, t_p_bg
	txt.configure (
		bg = t_bg, fg = t_fg, font = t_font, insertbackground = t_caret
		)
	p_syntax.configure (
		bg = t_p_bg, fg = t_p_bg, font = t_p_font
		)
	if onstart:
		for i in s_logo, s_info, s_new, s_open, s_conf:
			i.configure (bg = t_bg, fg = t_fg)

def cs_switch (name):
	t_path = 'themes/cs/' + name + '.json'
	with open (t_path, 'r', encoding = 'utf-8') as out:
		out_res = json.load (out)
	for out_vars in out_res ['colors']:
		cs_comment, cs_other = out_vars ['comment'], out_vars ['other']
		cs_keyword = out_vars ['keyword']
		cs_builtin, cs_str =  out_vars ['builtin'], out_vars ['string']
	tkns_init ()

w, w ['bg'] = Tk (), t_bg
w.minsize (700, 400)
w.bind ('<Control-n>', _new)
w.bind ('<Control-o>', _open)
w.bind ('<Control-s>', _save)
w.bind ('<Control-Shift-s>', _saveas)
w.bind ('<Control-p>', conf_open)
w.bind ('<Control-q>', _exit)

class modifiedmixin:
	def _init (self):
		self.clearmodifiedflag ()
		self.bind_all ('<<Modified>>', self._beenmodified)
	def _beenmodified (self, event = None):
		if self._resetting_modified_flag: return
		self.clearmodifiedflag ()
		self.beenmodified (event)
	def beenmodified (self, event = None): pass
	def clearmodifiedflag (self):
		self._resetting_modified_flag = True
		try: self.tk.call (self._w, 'edit', 'modified', 0)
		finally: self._resetting_modified_flag = False

class txt_class (modifiedmixin, Text):
		def __init__ (self, *a, **b):
			Text.__init__ (self, *a, **b)
			self._init ()
		def beenmodified (self, event = None): edit_event (0)

txt = txt_class ()
txt.configure (
	relief = 'flat', highlightthickness = 0,
	undo = True, wrap = 'none', bg = t_bg,
	fg = t_fg, font = t_font,
	insertbackground = t_caret
	)
p = Frame (w, bg = 'whitesmoke', relief = 'flat', height = 20)

p_hided = False
def p_hide ():
	global p_hided, p
	if p_hided == False:
		p.pack_forget ()
		p_hided = True
	else:
		for i in verscroll, horscroll, left_p, txt: i.pack_forget ()
		p.pack (side = 'bottom', fill = 'x')
		onstart == False and init_editor_ui ()
		p_hided = False

left_p_hided = False
def left_p_hide ():
	global left_p_hided, left_p
	if left_p_hided == False:
		left_p.pack_forget ()
		left_p_hided = True
	else:
		txt.pack_forget ()
		onstart == False and left_p.pack (fill = 'y', side = 'left'
		), txt.pack (side = 'left', fill = 'both', expand = True)
		left_p_hided = False

p_pos = Label (p, bg = t_p_bg, fg = t_p_fg, font = t_p_font)
p_info = Label (p, bg = t_p_bg, fg = t_p_fg, font = t_p_font)
p_syntax = Label (p, bg = t_p_bg, fg = t_p_fg, font = t_p_font)
left_p = Text (w,
	bg = 'gray', fg = 'white',
	relief = 'flat', font = t_font,
	highlightthickness = 0, width = 6
	)
verscroll = Scrollbar (w,
	background = 'whitesmoke',
	relief = 'flat', width = 15,
	command = lambda *args: (
		txt.yview (*args), left_p.yview (*args)
		)
	)
horscroll = Scrollbar (w,
	background = 'whitesmoke', relief = 'flat',
	command = txt.xview, orient = 'horizontal'
	)

def about_menu ():
	info ('about opened')
	about_w, about_w ['bg'] = Tk (), 'white'
	about_w.geometry ('300x150+100+100')
	about_w.resizable (width = False, height = False)
	about_w.title ('about')
	about_title = Label (about_w,
		bg = 'white', font = 'Consolas 20',
		text = 'notty'
		).pack (ipady = 20)
	about_other = Label (about_w,
		font = t_font, bg = 'white',
		text = 'copyright © 2020-2021 loadystudio\n'
		'Apache License v2.0\n'
		'v' + _ver + ' (build ' + _bld + ') ' + _br
		).pack ()

def github_menu ():
	wb.open ('https://github.com/loadystudio', new = 2)
	info ('github opened')

def loadystudio_menu ():
	wb.open ('http://loadystudio.cf', new = 2)
	info ('loadystudio page opened')

menu = Menu (w)
menu_file = Menu (menu, tearoff = 0)
menu_pref = Menu (menu, tearoff = 0)
menu_pref_themes = Menu (menu_pref, tearoff = 0)
menu_pref_cs = Menu (menu_pref, tearoff = 0)
menu_view = Menu (menu, tearoff = 0)
menu_view_syntax = Menu (menu_view, tearoff = 0)
menu_other = Menu (menu, tearoff = 0)

menu_view.add_command (
	label = 'show/hide panel', command = p_hide
	)
menu_view.add_command (
	label = 'show/hide lines panel', command = left_p_hide
	)
menu_view.add_separator ()
menu_view_syntax.add_radiobutton (
	label = 'text', command = lambda: syntax_set ('text')
	)
menu_view_syntax.add_separator ()
langs = ['py', 'js', 'c', 'cpp', 'css', 'html', 'json', 'java', 'md']
for i in langs:
	menu_view_syntax.add_radiobutton (
		label = i, command = lambda: syntax_set (i)
	)
menu_file.add_command (
	label = 'new file (ctrl+n)', command = lambda: _new (0)
	)
menu_file.add_command (
	label = 'open file (ctrl+o)', command = lambda: _open (0)
	)
menu_file.add_command (
	label = 'save file (ctrl+s)', command = lambda: _save (0)
	)
menu_file.add_command (
	label = 'save file as (ctrl+shift+s)', command = lambda: _saveas (0)
	)
menu_file.add_separator ()
menu_file.add_command (
	label = 'exit (ctrl+q)', command = lambda: _exit (0)
	)
menu_pref.add_command (
	label = 'config', command = lambda: conf_open (0)
	)
menu_pref.add_separator ()
menu_pref_themes.add_radiobutton (
	label = 'dark', command = lambda: t_switch ('dark')
	)
menu_pref_themes.add_radiobutton (
	label = 'light', command = lambda: t_switch ('light')
	)
menu_pref_cs.add_radiobutton (
	label = 'standart', command = lambda: cs_switch ('standart')
	)
menu_other.add_command (
	label = 'github', command = github_menu
	)
menu_other.add_command (
	label = 'loadystudio', command = loadystudio_menu
	)
menu_other.add_separator ()
menu_other.add_command (
	label = 'readme', command = readme_open
	)
menu_other.add_command (
	label = 'changelog', command = changelog_open
	)
menu_other.add_command (
	label = 'license', command = license_open
	)
menu_other.add_command (
	label = 'about', command = about_menu
	)

menu.add_cascade (label = 'file', menu = menu_file)
menu.add_cascade (label = 'view', menu = menu_view)
menu.add_cascade (label = 'preferences', menu = menu_pref)
menu.add_cascade (label = 'other', menu = menu_other)
menu_view.add_cascade (label = 'syntax', menu = menu_view_syntax)
menu_pref.add_cascade (label = 'themes', menu = menu_pref_themes)
menu_pref.add_cascade (label = 'color schemes', menu = menu_pref_cs)

def txt_cut (): txt_copy () ; txt_del ()
def txt_paste (): txt.insert (INSERT, txt.clipboard_get ())

def txt_copy ():
	sel = txt.tag_ranges (SEL)
	try: sel and txt.clipboard_clear (), txt.clipboard_append (txt.get (*sel))
	except TypeError: return

def txt_del ():
	sel = txt.tag_ranges (SEL)
	sel and txt.delete (*sel)

popup = Menu (w, tearoff = 0, bg = 'whitesmoke')
popup.add_command (label = 'cut (ctrl+x)', command = txt_cut)
popup.add_command (label = 'copy (ctrl+c)', command = txt_copy)
popup.add_command (label = 'paste (ctrl+v)', command = txt_paste)
popup.add_command (label = 'delete (del)', command = txt_del)

def show_popup (event): popup.post (event.x_root, event.y_root)

txt.bind ('<Button-3>', show_popup)

def init_editor_ui ():
	global verscroll, horscroll, show_left_p, left_p, txt
	verscroll.pack (fill = 'y', side = 'right')
	horscroll.pack (fill = 'x', side = 'bottom')
	show_left_p != 'false' and left_p.pack (fill = 'y', side = 'left')
	txt.pack (side = 'left', fill = 'both', expand = True)

def s_destroy ():
	global s_logo, s_info, s_new, s_open, s_conf
	for i in s_logo, s_info, s_new, s_open, s_conf: i.destroy ()

with open ('editor/manifest.json', 'r', encoding = 'utf-8') as out:
	out_res = json.load (out)
for out_vars in out_res ['notty']:
	_ver, _bld = out_vars ['version'], out_vars ['build']
	_br = out_vars ['branch']

s_logo = Label (w, font = 'Consolas 30', text = 'notty')
s_info = Label (w, font = 'Consolas 10',
		text = 'v' + _ver + ' (build ' + _bld + ') ' + _br + '\n'
		'copyright © 2020-2021 loadystudio'
		)
s_new = Label (w,text = 'new file')
s_open = Label (w, text = 'open file')
s_conf = Label (w, text = 'open config')

if __name__ == '__main__':
	conf_check ()
	show_menu != 'false' and w.config (menu = menu)
	p_pos.pack (side = 'left')
	p_info.pack (side = 'left')
	p_syntax.pack (side = 'right')
	p_syntax.bind ('<Button-1>', syntax_switch)
	show_p != 'false' and p.pack (side = 'bottom', fill = 'x')
	txt.configure (
		yscrollcommand = verscroll.set, xscrollcommand = horscroll.set
		)
	left_p ['yscrollcommand'] = verscroll.set
	s_logo.pack (ipady = 45)
	s_info.pack (ipady = 20)
	for i in s_logo, s_new, s_open, s_conf: i.pack()
	s_new.bind ('<Button-1>', _new)
	s_open.bind ('<Button-1>', _open)
	s_conf.bind ('<Button-1>', conf_open)
	w.title ('notty')
	w.call ('wm', 'iconphoto', w._w, PhotoImage (file = 'icon.png'))
	w.geometry ('700x400+50+50')
	if len (sys.argv) > 1: path_open (str(sys.argv[1]))
	w.mainloop ()