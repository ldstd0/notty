from pygments.lexers import *
from pygments.token import Token as t

kw, n, oth = 'violet', 'cyan', 'orange'
cmnt, bltin, st = '#999999', 'cyan', 'yellow'

tkns = {
	t.Keyword: 'kw',
	t.Other: 'oth',
	t.Keyword.Constant: 'oth',
	t.Operator: 'kw',
	t.Literal.String.Single: 'st',
	t.Literal.String.Double: 'st',
	t.Comment.Single: 'cmnt',
	t.Comment.Hashbang: 'cmnt',
	t.Comment.Multiline: 'cmnt'
}
def init (m):
	m.tag_config ('kw', foreground = kw)
	m.tag_config ('st', foreground = st)
	m.tag_config ('cmnt', foreground = cmnt)
	m.tag_config ('oth', foreground = oth)
def get (m, l, sw):
	if sw: return
	else:
		if l == 'py': lx = PythonLexer ()
		elif l == 'c': lx = CLexer ()
		elif l == 'cpp': lx = CppLexer ()
		elif l == 'json': lx = JsonLexer ()
		elif l == 'html': lx = HtmlLexer ()
		elif l == 'css': lx = CssLexer ()
		elif l == 'js': lx = JavascriptLexer ()
		elif l == 'md': lx = MarkdownLexer ()
		elif l == 'java': lx = JavaLexer ()
		def crd (s: str, i: int):
			for r, l in enumerate (
				s.splitlines (keepends = True), 1):
				if i < len (l): return f'{r}.{i}'
				i -= len (l)
		clr (m)
		s = m.get (1.0, 'end')
		tkns = lx.get_tokens_unprocessed (s)
		for i, types, t in tkns:
			j = i + len (t)
			types in tkns and m.tag_add (t [types], crd (s, i), crd (s, j))
		m.edit_modified (0)
def clr (m):
	for t in m.tag_names (): m.tag_remove (t, 1.0, 'end')
def sw (m, e, s, sw):
	if s != 'text':
		s, sw = 'text', True
		clr (m)
	elif sw:
		if e != None:
			s = e [1:]
		else:
			return
		sw = False
		if e == '.py' or '.pyw':
			s = 'py'
			get (m, PythonLexer())
		elif e == '.js':
			get (m, JavascriptLexer())
		elif e == '.c':
			get (m, CLexer())
		elif e == '.cpp':
			get (m, CppLexer())
		elif e == '.html':
			get (m, HtmlLexer())
		elif e == '.css':
			get (m, CssLexer())
		elif e == '.json':
			get (m, JsonLexer())
		elif e == '.md':
			get (m, MarkdownLexer())
		elif e == '.java':
			get (m, JavaLexer())
def set (m, n):
	if n == 'text':
		clr (m)
	elif n == 'py':
		get (m, PythonLexer ())
	elif n == 'c':
		get (m, CLexer ())
	elif n == 'cpp':
		get (m, CppLexer ())
	elif n == 'json':
		get (m, JsonLexer ())
	elif n == 'html':
		get (m, HtmlLexer ())
	elif n == 'css':
		get (m, CssLexer ())
	elif n == 'js':
		get (m, JavascriptLexer ())
	elif n == 'md':
		get (m, MarkdownLexer ())
	elif n == 'java':
		get (m, JavaLexer ())