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
# specificuage governing permissions and limitations
# under the License.
err_pygment = False
import tkinter as tk
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
except ImportError: err_pygment = True ; print ('(!) pygments import error')
array=['json','c','cpp','html','css','py','js','md']
color_keyword = '#ff00cc'
color_string_literal = '#00cc66'
color_comment = '#999999'
color_name_builtin = '#3399cc'
color_keyword_ext = '#ff0000'
token_type_to_tag = {
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
def tokens_init (textbox):
	textbox.tag_config ('keyword', foreground = color_keyword)
	textbox.tag_config ('keyword_ext', foreground = color_keyword_ext)
	textbox.tag_config ('name_builtin', foreground = color_name_builtin)
	textbox.tag_config ('string_literal', foreground = color_string_literal)
	textbox.tag_config ('comment', foreground = color_comment)
def tokens_get(textbox,lexer):
	def get_text_coord (s: str, i: int):
		for row_number, line in enumerate (s.splitlines (keepends=True), 1):
			if i < len (line): return f'{row_number}.{i}'
			i -= len (line)
	for tag in textbox.tag_names (): textbox.tag_remove (tag, 1.0, 'end')
	s = textbox.get (1.0, 'end')
	tokens = lexer.get_tokens_unprocessed (s)
	for i, token_type, token in tokens:
		j = i + len (token)
		token_type in token_type_to_tag and textbox.tag_add(token_type_to_tag [token_type],get_text_coord(s, i),get_text_coord(s, j))
	textbox.edit_modified (0)
def delete_tokens(textbox):
	for tag in textbox.tag_names (): textbox.tag_remove (tag, 1.0, 'end')
def open(extension, err_syntax, syntax, textbox, p_syntax):
	syntax = extension[1:] ; p_syntax ['text'] = extension[1:]
	if extension == '.py' or '.pyw':
		syntax='py'; p_syntax='py'
		err_syntax == False and tokens_get (textbox, pyl())
	elif extension == '.js': err_syntax == False and tokens_get (textbox, jsl())
	elif extension == '.c': err_syntax == False and tokens_get (textbox, cl())
	elif extension == '.cpp': err_syntax == False and tokens_get (textbox, cppl())
	elif extension == '.html': err_syntax == False and tokens_get (textbox, htmll())
	elif extension == '.css': err_syntax == False and tokens_get (textbox, cssl())
	elif extension == '.json': err_syntax == False and tokens_get (textbox, jsonl())
	elif extension == '.md': err_syntax == False and tokens_get (textbox, mdl())
	else: syntax = 'text' ; p_syntax ['text'] = 'plain text'
def edit_event(err_syntax, syntax, textbox, switched):
	if err_syntax!=True and switched==False:
		if syntax=='py' or syntax=='pyw': tokens_get(textbox,pyl())
		elif syntax=='js': tokens_get(textbox,jsl())
		elif syntax=='c': tokens_get(textbox,cl())
		elif syntax=='cpp': tokens_get(textbox,cppl())
		elif syntax=='html': tokens_get(textbox,htmll())
		elif syntax=='css': tokens_get(textbox,cssl())
		elif syntax=='json': tokens_get(textbox,jsonl())
		elif syntax=='md': tokens_get(textbox, mdl())
def switch(extension,syntax,textbox,p_syntax,switched):
	if syntax != 'text':
		syntax = 'text'
		p_syntax['text']='text'
		delete_tokens(textbox)
		switched=True
	elif switched==True:
		syntax = extension[1:] ; p_syntax ['text'] = extension[1:] ; switched = False
		if extension == '.py' or '.pyw':
			syntax='py'; p_syntax='py'
			err_syntax == False and tokens_get (textbox, pyl())
		elif extension == '.js': err_syntax == False and tokens_get (textbox, jsl())
		elif extension == '.c': err_syntax == False and tokens_get (textbox, cl())
		elif extension == '.cpp': err_syntax == False and tokens_get (textbox, cppl())
		elif extension == '.html': err_syntax == False and tokens_get (textbox, htmll())
		elif extension == '.css': err_syntax == False and tokens_get (textbox, cssl())
		elif extension == '.json': err_syntax == False and tokens_get (textbox, jsonl())
		elif extension == '.md': err_syntax == False and tokens_get (textbox, mdl())
def sset (name, syntax, p_syntax, textbox):
	p_syntax ['text'] = name
	if name == 'plain text': delete_tokens(textbox)
	elif name == 'py': tokens_get (textbox, pyl ())
	elif name == 'c': tokens_get (textbox, cl ())
	elif name == 'cpp': tokens_get (textbox, cppl ())
	elif name == 'json': tokens_get (textbox, jsonl ())
	elif name == 'html': tokens_get (textbox, htmll ())
	elif name == 'css': tokens_get (textbox, cssl ())
	elif name == 'js': tokens_get (textbox, jsl ())
	elif name == 'md': tokens_get(textbox, mdl ())