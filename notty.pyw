#!/usr/bin/python3
import sys, os, json
import tkinter.filedialog as fd
import sqlite3 as sql
import webbrowser as wb
from tkinter import *

import syntax as s

t_bg, t_fg, t_font, t_caret = '#222222', 'silver', 'Consolas 11', 'orange'
t_p_bg, t_p_fg, t_p_font = 'whitesmoke', 'black', 'Consolas 10'
user, sntx, onstart, _auth = 'user', 'text', True, False
ext, path, edit, sw = None, None, False, False
show_m, show_p, show_left_p, show_e = 'true', 'true', 'true', 'true'
p_hided, left_p_hided, e_hided = False, False, False
t_src = 'themes/'
ftypes = [('all', '*'),
	('python', '*.py*'), ('javascript', '*.js'), ('c lang', '*.c'),
	('c++ lang', '*.cpp'), ('css', '*.css'), ('html', '*.html'),
	('json', '*.json'), ('java', '*.java'), ('markdown', '*.md')
]

def s_sw (event): s.sw (txt, ext, sntx, sw)
def s_get (l):
	global txt
	s.get (txt, l, sw)

def s_set (name):
	s.set (txt, name)
	sntx, p_sntx ['text'] = name, name

def info (i): p_info ['text'] = i

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
	if sw == False:
		if sntx=='text': return
		elif sntx == 'py' or sntx == 'pyw': s_get ('py')
		else: s_get (sntx)
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
	s_del () ; init () ; s_sw(0)
	txt_clr () ; info ('new tab opened')
	path, onstart = None, False
def path_open (fpath = None):
	global path, edit, ext, sntx, p_sntx
	s_del () ; init ()
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
	sntx, p_sntx ['text'] = ext [1:], sntx
	info (path + ' opened')
	if ext == '': sntx, p_sntx ['text'] = 'text', 'text'
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
	for i in p_sntx, p_pos, p_info:
		i.configure (bg = t_p_bg, fg = t_p_fg, font = t_p_font)
	for i in s_logo, s_new, s_open, s_conf, s_proj: i['bg'], i['fg'] = t_bg, t_fg
	for i in s_new, s_open, s_conf, s_proj: i.configure (font = 'Consolas 16')
	s.init (txt)
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
	p_s_del.configure (bg = t_p_bg, fg = t_p_bg, font = t_p_font)
	if onstart:
		for i in s_logo, s_new, s_open, s_conf, s_proj:
			i.configure (bg = t_bg, fg = t_fg)
	s.init (txt)

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
		for i in vscroll, hscroll, left_p, txt: i.pack_forget ()
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
		for i in vscroll, hscroll, left_p, txt: i.pack_forget ()
		onstart == False and init ()
		p_hided = False

p_pos = Label (p, bg = t_p_bg, fg = t_p_fg, font = t_p_font)
p_info = Label (p, bg = t_p_bg, fg = t_p_fg, font = t_p_font)
p_sntx = Label (p, bg = t_p_bg, fg = t_p_fg, font = t_p_font)
p_user = Label (p, bg = t_p_bg, fg = t_p_fg, font = t_p_font)
left_p = Text (w,
	bg = 'gray', fg = 'whitesmoke', relief = 'flat',
	font = t_font, highlightthickness = 0, width = 6
	)
e = Frame (w, bg = 'whitesmoke', relief = 'flat', width = 100)
vscroll = Scrollbar (w,
	background = 'whitesmoke',
	relief = 'flat', width = 15,
	command = lambda *args: (txt.yview (*args), left_p.yview (*args))
	)
hscroll = Scrollbar (w,
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
		global user, _auth
		name, pswd = u_name.get (), u_pswd.get ()
		cur.execute (f"SELECT name FROM users WHERE name = '{name}'")
		if cur.fetchall () == None: info ('user doesnt exist')
		elif cur.fetchall () != None:
			cur.execute (f"SELECT password FROM users WHERE name = '{name}'")
			try:
				db_pswd = cur.fetchall ()[0][0]
				if str (db_pswd) == str (pswd):
					user = name ; u_w.destroy () ; _auth = True
					p_user ['text'] = user
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
		global user
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
m_view_s.add_radiobutton (label = 'text', command = lambda: s_set ('text'))
m_view_s.add_separator ()
m_view_s.add_radiobutton (label = 'python', command = lambda: s_set ('py'))
m_view_s.add_radiobutton (label = 'javascript', command = lambda: s_set ('js'))
m_view_s.add_radiobutton (label = 'c lang', command = lambda: s_set ('c'))
m_view_s.add_radiobutton (label = 'c++ lang', command = lambda: s_set ('cpp'))
m_view_s.add_radiobutton (label = 'css', command = lambda: s_set ('css'))
m_view_s.add_radiobutton (label = 'html', command = lambda: s_set ('html'))
m_view_s.add_radiobutton (label = 'json', command = lambda: s_set ('json'))
m_view_s.add_radiobutton (label = 'java', command = lambda: s_set ('java'))
m_view_s.add_radiobutton (label = 'markdown', command = lambda: s_set ('md'))
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

def txt_cut():txt_copy();txt_del()
def txt_paste():txt.insert(INSERT,txt.clipboard_get())
def txt_copy():
	txt.clipboard_clear(),txt.clipboard_append(txt.get(*txt.tag_ranges(SEL)))
def txt_del():txt.delete(*txt.tag_ranges(SEL))
def txt_find():
	wb.open('https://google.com/search?q='+txt.get(*txt.tag_ranges(SEL)),new=2)
popup=Menu(w,tearoff=0,bg='whitesmoke')
popup.add_command(label='cut',command=txt_cut)
popup.add_command(label='copy',command=txt_copy)
popup.add_command(label='paste',command=txt_paste)
popup.add_command(label='delete',command=txt_del)
popup.add_command(label='find',command=txt_find)
def show_popup(event):popup.post(event.x_root,event.y_root)
txt.bind('<Button-3>',show_popup)
def init():
	global vscroll,hscroll,show_left_p,left_p,txt
	vscroll.pack (fill = 'y', side = 'right')
	hscroll.pack (fill = 'x', side = 'bottom')
	show_e != 'false' and e.pack (side = 'left', fill = 'y')
	show_left_p != 'false' and left_p.pack (fill = 'y', side = 'left')
	txt.pack (side = 'left', fill = 'both', expand = True)
def s_del ():
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
	txt ['yscrollcommand'], txt ['xscrollcommand'] = vscroll.set, hscroll.set
	left_p ['yscrollcommand'] = vscroll.set
	show_m != 'false' and w.config (menu = m)
	for i in p_pos, p_info: i.pack (side = 'left')
	for i in p_sntx, p_user: i.pack (side = 'right')
	p_sntx.bind ('<Button-1>', s_sw)
	show_p != 'false' and p.pack (side = 'bottom', fill = 'x')
	s_logo.pack (ipady = 50)
	for i in s_logo, s_new, s_open, s_conf, s_proj: i.pack()
	if len (sys.argv) > 1: path_open (str (sys.argv [1]))
	w.mainloop ()