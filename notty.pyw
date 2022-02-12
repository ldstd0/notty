#!/usr/bin/python3
import sys, os, json
import tkinter.filedialog as fd
import sqlite3 as sql
import webbrowser as wb
from tkinter import *
from pygments.lexers import *
from pygments.token import Token as tkn

s_kw, s_name, s_other = 'violet', 'cyan', 'orange'
s_comment, s_builtin, s_str = '#999999', 'cyan', 'yellow'
t_bg, t_fg, t_font, t_caret = '#222222', 'silver', 'Consolas 11', 'orange'
t_p_bg, t_p_fg, t_p_font = 'whitesmoke', 'black', 'Consolas 10'
_name, syntax, onstart, _auth = 'user', 'text', True, False
ext, path, edit, switched = None, None, False, False
show_m, show_p, show_left_p, show_e = 'true', 'true', 'true', 'true'
p_hided, left_p_hided, e_hided = False, False, False
t_src = 'themes/'
ftypes = [('all', '*'),
	('python', '*.py*'), ('javascript', '*.js'), ('c lang', '*.c'),
	('c++ lang', '*.cpp'), ('css', '*.css'), ('html', '*.html'),
	('json', '*.json'), ('java', '*.java'), ('markdown', '*.md')
]
tkn_type_to_tag = {
	tkn.Keyword: 'keyword', tkn.Other: 'other',
	tkn.Keyword.Constant: 'other', tkn.Operator: 'keyword',
	tkn.Literal.String.Single: 'str_literal',
	tkn.Literal.String.Double: 'str_literal',
	tkn.Comment.Single: 'comment', tkn.Comment.Hashbang: 'comment',
	tkn.Comment.Multiline: 'comment'
}

def info (i): p_info ['text'] = i

def tkns_init ():
	txt.tag_config ('keyword', foreground = s_kw)
	txt.tag_config ('str_literal', foreground = s_str)
	txt.tag_config ('comment', foreground = s_comment)
	txt.tag_config ('other', foreground = s_other)
def tkns_get (lexer):
	global txt
	def get_text_coord (s: str, i: int):
		for row_number, line in enumerate (
			s.splitlines (keepends = True), 1):
			if i < len (line): return f'{row_number}.{i}'
			i -= len (line)
	delete_tkns ()
	s = txt.get (1.0, END)
	tkns = lexer.get_tokens_unprocessed (s)
	for i, tkn_type, tkn in tkns:
		j = i + len (tkn)
		tkn_type in tkn_type_to_tag and txt.tag_add (
			tkn_type_to_tag [tkn_type],
			get_text_coord (s, i), get_text_coord (s, j)
			)
	txt.edit_modified (0)
def delete_tkns ():
	for tag in txt.tag_names (): txt.tag_remove (tag, 1.0, END)

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
			syntax = 'py' ; tkns_get (PythonLexer())
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

def txt_clr (): txt.delete (1.0, END)
def txt_ins (t): txt.insert (1.0, t)

def edit_event (event):
	global p_pos, txt
	p_pos ['text'] = txt.index (INSERT)
	count = len (txt.get ('1.0', END).splitlines ())
	lines, lines_p = 1, ''
	while lines <= count:
		if lines == count: lines_p += str (lines)
		else: lines_p += str (lines) + '\n'
		lines += 1
	left_p ['state'] = 'normal'
	left_p.delete ('1.0', END)
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
		elif path == 'LICENSE': w.title ('license - notty')
	except TypeError:
		w.title ('error - notty') ; info ('(!) title error')

def _exit (event): w.destroy ()
def _new (event):
	global path, onstart
	s_exit () ; init () ;syntax_switch (0)
	txt_clr () ; info ('new tab opened')
	path, onstart = None, False
def path_open (fpath = None):
	global path, edit, ext, syntax, p_syntax
	s_exit () ; init ()
	if not fpath:
		path = fd.Open (w, filetypes = ftypes).show ()
		if path == '': return
		txt_clr ()
		try: txt_ins (open (path).read ().rstrip ('\n'))
		except TypeError: path = None ; return
	else:
		path = fpath
		try:
			txt_clr () ; txt_ins (open (path).read ().rstrip ('\n'))
		except FileNotFoundError:
			path = None ; txt_clr () ; info ('file not found') ; return
	edit, onstart = False, False
	ext = os.path.splitext (os.path.basename (path)) [1]
	syntax, p_syntax ['text'] = ext [1:], syntax
	info (path + ' opened')
	if ext == '': syntax, p_syntax ['text'] = 'text', 'text'
def _open (event): path_open ()
def _save (event):
	global path, edit
	if path != None:
		try: open (path, 'wt').write (txt.get ('1.0', END))
		except FileNotFoundError: path = None
	else:
		path = fd.SaveAs (w, filetypes = ftypes).show ()
		if path == '': return
		try: open (path, 'wt').write (txt.get ('1.0', END))
		except TypeError: path = None ; return
	edit = False ; info (path + ' saved')
def _saveas (event):
	global path, edit
	path = fd.SaveAs (w, filetypes = ftypes).show ()
	if path == '': return
	try: open (path,'wt').write (txt.get ('1.0', END))
	except TypeError: path = None ; return
	edit = False ; info (path + ' saved')

def _conf (event): path_open ('editor/config.json')
def readme (): path_open ('README.md')
def license (): path_open ('LICENSE')

def conf_check ():
	global t_bg, t_fg, t_font, t_caret, t_p_bg, t_p_fg, t_p_font, _ver, show_e
	global show_m, show_p, show_left_p, s_comment, s_other, s_kw, s_builtin, s_str
	with open ('editor/config.json', 'r', encoding = 'utf-8') as out:
		conf_res = json.load (out)
	for conf_var in conf_res ['notty']:
		_ver = conf_var ['version']
		show_m, show_p = conf_var ['menu'], conf_var ['panel']
		show_left_p, show_e = conf_var ['lines'], conf_var ['explorer']
		t_path = 'themes/' + conf_var ['theme'] + '.json'
	with open (t_path, 'r', encoding = 'utf-8') as out: res = json.load (out)
	for var in res ['textbox']:
		t_bg, t_fg = var ['bg'], var ['fg']
		t_font, t_caret = var ['font'], var ['caret']
	for var_p in res ['panel']:
		t_p_bg, t_p_fg, t_p_font = var_p ['bg'], var_p ['fg'], var_p ['font']
	for var_s in res ['syntax']:
		s_comment, s_other = var_s ['comment'], var_s ['other']
		s_kw = var_s ['keyword']
		s_builtin, s_str = var_s ['builtin'], var_s ['string']
	w ['bg'], p ['bg'] = t_bg, t_p_bg
	txt.configure (
		bg = t_bg, fg = t_fg, font = t_font, insertbackground = t_caret
		)
	for i in p_syntax, p_pos, p_info:
		i.configure (bg = t_p_bg, fg = t_p_fg, font = t_p_font)
	for i in s_logo, s_new, s_open, s_conf, s_proj: i['bg'], i['fg'] = t_bg, t_fg
	for i in s_new, s_open, s_conf, s_proj: i.configure (font = 'Consolas 16')
	tkns_init ()
def t_set (name):
	t_path = 'themes/' + name + '.json'
	with open (t_path, 'r', encoding = 'utf-8') as out: res = json.load (out)
	for var in res ['textbox']:
		t_bg, t_fg = var ['bg'], var ['fg']
		t_font, t_caret = var ['font'], var ['caret']
	for var_p in res ['panel']:
		t_p_bg, t_p_fg, t_p_font = var_p ['bg'], var_p ['fg'], var_p ['font']
	for var_s in res ['syntax']:
		s_comment, s_other = var_s ['comment'], var_s ['other']
		s_kw = var_s ['keyword']
		s_builtin, s_str =  var_s ['builtin'], var_s ['string']
	w ['bg'], p ['bg'] = t_bg, t_p_bg
	txt.configure (
		bg = t_bg, fg = t_fg, font = t_font, insertbackground = t_caret
		)
	p_syntax.configure (bg = t_p_bg, fg = t_p_bg, font = t_p_font)
	if onstart:
		for i in s_logo, s_new, s_open, s_conf, s_proj:
			i.configure (bg = t_bg, fg = t_fg)
	tkns_init ()

w, w ['bg'] = Tk (), t_bg
w.title ('notty') ; w.minsize (700, 400)
w.call ('wm', 'iconphoto', w._w, PhotoImage (file = 'icon.png'))
w.bind ('<Control-n>', _new) ; w.bind ('<Control-o>', _open)
w.bind ('<Control-s>', _save) ; w.bind ('<Control-Shift-s>', _saveas)
w.bind ('<Control-p>', _conf) ; w.bind ('<Control-q>', _exit)

class modmixin:
	def _init (self):
		self.clearmf () ; self.bind_all ('<<Modified>>', self._bm)
	def _bm (self, event = None):
		if self._reset_mf: return
		self.clearmf () ; self.bm (event)
	def bm (self, event = None): pass
	def clearmf (self):
		self._reset_mf = True
		try: self.tk.call (self._w, 'edit', 'modified', 0)
		finally: self._reset_mf = False
class txt_mod (modmixin, Text):
		def __init__ (self, *a, **b):
			Text.__init__ (self, *a, **b) ; self._init ()
		def bm (self, event = None): edit_event (0)
txt = txt_mod ()
txt.configure (
	relief = 'flat', highlightthickness = 0,
	undo = True, wrap = 'none', bg = t_bg,
	fg = t_fg, font = t_font, insertbackground = t_caret
	)
p = Frame (w, bg = 'white', relief = 'flat', height = 20)

def p_hide ():
	global p_hided, p
	if p_hided == False: p.pack_forget () ; p_hided = True
	else:
		for i in verscroll, horscroll, left_p, txt: i.pack_forget ()
		p.pack (side = 'bottom', fill = 'x')
		onstart == False and init ()
		p_hided = False
def left_p_hide ():
	global left_p_hided, left_p
	if left_p_hided == False: left_p.pack_forget () ; left_p_hided = True
	else:
		txt.pack_forget ()
		onstart == False and left_p.pack (fill = 'y', side = 'left'
		), txt.pack (side = 'left', fill = 'both', expand = True)
		left_p_hided = False
def e_hide ():
	global e_hided, e
	if e_hided == False: e.pack_forget () ; e_hided = True
	else:
		for i in verscroll, horscroll, left_p, txt: i.pack_forget ()
		onstart == False and init ()
		p_hided = False

p_pos = Label (p, bg = t_p_bg, fg = t_p_fg, font = t_p_font)
p_info = Label (p, bg = t_p_bg, fg = t_p_fg, font = t_p_font)
p_syntax = Label (p, bg = t_p_bg, fg = t_p_fg, font = t_p_font)
p_user = Label (p, bg = t_p_bg, fg = t_p_fg, font = t_p_font)
left_p = Text (w,
	bg = 'gray', fg = 'whitesmoke', relief = 'flat',
	font = t_font, highlightthickness = 0, width = 6
	)
e = Frame (w, bg = 'whitesmoke', relief = 'flat', width = 100)
verscroll = Scrollbar (w,
	background = 'whitesmoke',
	relief = 'flat', width = 15,
	command = lambda *args: (txt.yview (*args), left_p.yview (*args))
	)
horscroll = Scrollbar (w,
	background = 'whitesmoke', relief = 'flat',
	command = txt.xview, orient = 'horizontal'
	)

e_tabs = []
class e_tab:
	def __init__ (self, path, name):
		self.path, self.name = path, name
		self.name = Label (e, text = path + '\n')
		self.name.bind ('<Button-1>', path_open (path))
		self.name.pack (side = 'left')
	def destroy (): self.name.pack_forget ()

def about ():
	about_w, about_w ['bg'] = Tk (), t_bg
	about_w.geometry ('300x150+100+100')
	about_w.resizable (width = False, height = False)
	about_w.title ('about')
	about_title = Label (about_w,
		bg = t_bg, font = 'Consolas 20', text = 'notty', fg = t_fg
		).pack (ipady = 20)
	about_other = Label (about_w,
		font = t_font, bg = t_bg, fg = t_fg, text = '2022 © ldstd\nv' + _ver
		).pack ()

def github (): wb.open ('https://github.com/ldstd0', new = 2)
def ldstd (): wb.open ('http://ldstd.cf', new = 2)

def u_select ():
	con = sql.connect ('editor/users.db')
	cur = con.cursor ()
	u_w, u_w ['bg'] = Tk (), t_bg
	u_w.geometry ('300x200+100+100')
	u_w.resizable (width = False, height = False)
	u_w.title ('auth')
	def u_login (event):
		global _name, _auth
		name, pswd = u_name.get (), u_pswd.get ()
		cur.execute (f"SELECT name FROM users WHERE name = '{name}'")
		if cur.fetchall () == None: info ('user doesnt exist')
		elif cur.fetchall () != None:
			cur.execute (f"SELECT password FROM users WHERE name = '{name}'")
			try:
				db_pswd = cur.fetchall ()[0][0]
				if str (db_pswd) == str (pswd):
					_name = name ; u_w.destroy () ; _auth = True
					p_user ['text'] = _name
				else: info ('password incorrect')
			except IndexError: info ('user doesnt exist')
		else: info ('error')
	def u_new (event):
		cur.execute ('SELECT COUNT(*) FROM users')
		values = cur.fetchone ()
		u_id = len (values) + 2
		name, pswd = u_name.get (), u_pswd.get ()
		cur.execute (f"INSERT INTO users('id', 'name', 'password') VALUES ({u_id}, '{name}', '{pswd}')")
		con.commit ()
	u_title = Label (u_w,
		bg = t_bg, fg = t_fg, font = 'Consolas 20', text = 'auth'
		).pack (ipady = 20)
	u_name = Entry (u_w,
		bg = t_bg, fg = t_fg, font = t_font, insertbackground = t_caret
		)
	u_pswd = Entry (u_w,
		bg = t_bg, fg = t_fg, font = t_font, insertbackground = t_caret
		)
	u_login_btn = Label (u_w,
		bg = t_bg, fg = t_fg, font = t_font, text = 'login'
		)
	u_new_btn = Label (u_w,
		bg = t_bg, fg = t_fg, font = t_font, text = 'create new account'
		)
	for i in u_name, u_pswd, u_login_btn, u_new_btn: i.pack ()
	u_login_btn.bind ('<Button-1>', u_login)
	u_new_btn.bind ('<Button-1>', u_new)
	u_w.bind ('<Return>', u_login)

def _proj (event):
	def proj_new (event):
			proj_new_w, proj_new_w ['bg'] = Tk (), t_bg
			proj_new_w.geometry ('300x300+100+100')
			proj_new_w.resizable (width = False, height = False)
			proj_new_w.title ('new project')
			proj_name = Entry (proj_new_w,
				bg = t_bg, fg = t_fg, font = t_font, insertbackground = t_caret
				)
			#for i in proj_name, proj_lang, proj_share: i.pack ()
	if _auth != True: u_select ()
	else:
		global _name
		proj_w, proj_w ['bg'] = Tk (), t_bg
		proj_w.geometry ('300x500+100+100')
		proj_w.resizable (width = False, height = False)
		proj_w.title ('projects')
		proj_new_btn = Label (proj_w,
			bg = t_bg, fg = t_fg, font = t_font, text = 'new project'
			)
		proj_new_btn.pack (ipady = 5)
		proj_new_btn.bind ('<Button-1>', proj_new)

m = Menu (w)
m_file = Menu (m, tearoff = 0)
m_pref = Menu (m, tearoff = 0)
m_pref_t = Menu (m_pref, tearoff = 0)
m_view = Menu (m, tearoff = 0)
m_view_s = Menu (m_view, tearoff = 0)
m_other = Menu (m, tearoff = 0)
m_view.add_command (label = 'show/hide panel', command = p_hide)
m_view.add_command (label = 'show/hide lines panel', command = left_p_hide)
m_view.add_command (label = 'show/hide explorer', command = e_hide)
m_view.add_separator ()
m_view_s.add_radiobutton (label = 'text', command = lambda: syntax_set ('text'))
m_view_s.add_separator ()
m_view_s.add_radiobutton (label = 'python', command = lambda: syntax_set ('py'))
m_view_s.add_radiobutton (label = 'javascript', command = lambda: syntax_set ('js'))
m_view_s.add_radiobutton (label = 'c lang', command = lambda: syntax_set ('c'))
m_view_s.add_radiobutton (label = 'c++ lang', command = lambda: syntax_set ('cpp'))
m_view_s.add_radiobutton (label = 'css', command = lambda: syntax_set ('css'))
m_view_s.add_radiobutton (label = 'html', command = lambda: syntax_set ('html'))
m_view_s.add_radiobutton (label = 'json', command = lambda: syntax_set ('json'))
m_view_s.add_radiobutton (label = 'java', command = lambda: syntax_set ('java'))
m_view_s.add_radiobutton (label = 'markdown', command = lambda: syntax_set ('md'))
m_file.add_command (label = 'new file', command = lambda: _new (0))
m_file.add_command (label = 'open file', command = lambda: _open (0))
m_file.add_command (label = 'save file', command = lambda: _save (0))
m_file.add_command (label = 'save file as', command = lambda: _saveas (0))
m_file.add_separator ()
m_file.add_command (label = 'exit', command = lambda: _exit (0))
m_pref.add_command (label = 'config', command = lambda: _conf (0))
m_pref.add_separator ()
m_pref_t.add_radiobutton (label = 'dark', command = lambda: t_set ('dark'))
m_pref_t.add_radiobutton (label = 'light', command = lambda: t_set ('light'))
m_other.add_command (label = 'github', command = github)
m_other.add_command (label = 'ldstd', command = ldstd)
m_other.add_separator ()
m_other.add_command (label = 'readme', command = readme)
m_other.add_command (label = 'license', command = license)
m_other.add_command (label = 'about', command = about)
m.add_cascade (label = 'file', menu = m_file)
m.add_cascade (label = 'view', menu = m_view)
m.add_cascade (label = 'preferences', menu = m_pref)
m.add_cascade (label = 'other', menu = m_other)
m_view.add_cascade (label = 'syntax', menu = m_view_s)
m_pref.add_cascade (label = 'themes', menu = m_pref_t)

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
popup.add_command (label = 'cut', command = txt_cut)
popup.add_command (label = 'copy', command = txt_copy)
popup.add_command (label = 'paste', command = txt_paste)
popup.add_command (label = 'delete', command = txt_del)
def show_popup (event): popup.post (event.x_root, event.y_root)
txt.bind ('<Button-3>', show_popup)

def init ():
	global verscroll, horscroll, show_left_p, left_p, txt
	verscroll.pack (fill = 'y', side = 'right')
	horscroll.pack (fill = 'x', side = 'bottom')
	show_e != 'false' and e.pack (side = 'left', fill = 'y')
	show_left_p != 'false' and left_p.pack (fill = 'y', side = 'left')
	txt.pack (side = 'left', fill = 'both', expand = True)
def s_exit ():
	for i in s_logo, s_new, s_open, s_conf, s_proj: i.destroy ()

s_logo = Label (w, font = 'Consolas 30', text = 'notty')
s_new = Label (w, text = 'new file')
s_open = Label (w, text = 'open file')
s_conf = Label (w, text = 'open config')
s_proj = Label (w, text = 'projects')
s_new.bind ('<Button-1>', _new) ; s_open.bind ('<Button-1>', _open)
s_conf.bind ('<Button-1>', _conf) ; s_proj.bind ('<Button-1>', _proj)

if __name__ == '__main__':
	conf_check ()
	txt['yscrollcommand'], txt['xscrollcommand'] = verscroll.set, horscroll.set
	left_p ['yscrollcommand'] = verscroll.set
	show_m != 'false' and w.config (menu = m)
	for i in p_pos, p_info: i.pack (side = 'left')
	for i in p_syntax, p_user: i.pack (side = 'right')
	p_syntax.bind ('<Button-1>', syntax_switch)
	show_p != 'false' and p.pack (side = 'bottom', fill = 'x')
	s_logo.pack (ipady = 50)
	for i in s_logo, s_new, s_open, s_conf, s_proj: i.pack()
	if len (sys.argv) > 1: path_open (str(sys.argv[1]))
	w.mainloop ()