# ============== Imports ==============

from TokenTypes import Type as TTT
from TokenTypes import Keyword as TTK
from TokenTypes import Symbol as TTS
from TokenTypes import keyword_dict as key_dict
from TokenTypes import symbols_dict as sym_dict

# ============= Constants ==============

VAR_DECLARE_NOT_FOUND_EXCEPTION = "Expected var declare but got "
SUBROUTINE_NOT_FOUND_EXCEPTION = "Expected subroutine type but got "
FUNC_DECLARE_NOT_FOUND_EXCEPTION = "Expected function declaration but got "
CLASS_TOKEN_NOT_FOUND_EXCEPTION = "Expected class token which was not found"
IDENTIFIER_NOT_FOUND_EXCEPTION = "Expected identifier after class"
UNEXPECTED_TOKEN_EXCEPTION = "Unexpected token "
TOKENIZER_EMPTY_EXCEPTION = "Attempt to get tokens but tokenizer has no more tokens!"
NEWLINE = "\n"
EXPRESSION_LIST_XML_SUFFIX = "</expressionList>"
EXPRESSION_LIST_XML_PREFIX = "<expressionList>"
TERM_XML_SUFFIX = "</term>"
TERM_XML_PREFIX = "<term>"
TERM_NOT_FOUND_EXCEPTION = "Expected term but didn't get any"
EXPRESSION_XML_SUFFIX = "</expression>"
EXPRESSION_XML_PREFIX = "<expression>"
IF_STATEMENT_XML_SUFFIX = "</ifStatement>"
IF_STATEMENT_PREFIX = "<ifStatement>"
RETURN_XML_SUFFIX = "</returnStatement>"
RETURN_STATEMENT_XML_PREFIX = "<returnStatement>"
WHILE_STATEMENT_XML_SUFFIX = "</whileStatement>"
WHILE_STATEMENT_XML_PREFIX = "<whileStatement>"
LET_STATEMENT_XML_SUFFIX = "</letStatement>"
LET_STATEMENT_XML_PREFIX = "<letStatement>"
DO_STATEMENT_XML_SUFFIX = "</doStatement>"
DO_STATEMENT_XML_PREFIX = "<doStatement>"
STATEMENTS_XML_SUFFIX = "</statements>"
STATEMENTS_XML_PREFIX = "<statements>"
VAR_DEC_XML_SUFFIX = "</varDec>"
VAR_DEC_XML_PREFIX = "<varDec>"
PARAMETER_LIST_XML_SUFFIX = "</parameterList>"
PARAMETER_LIST_XML_PREFIX = "<parameterList>"
SUBROUTINE_DEC_XML_SUFFIX = "</subroutineDec>"
SUBROUTINE_BODY_XML_SUFFIX = "</subroutineBody>"
SUBROUTINE_BODY_XML_PREFIX = "<subroutineBody>"
SUBROUTINE_DEC_XML_PREFIX = "<subroutineDec>"
CLASS_VAR_DEC_XML_SUFFIX = "</classVarDec>"
CLASS_VAR_DEC_XML_PREFIX = "<classVarDec>"
CLASS_XML_SUFFIX = "</class>"
CLASS_XML_PREFIX = "<class>"


# ======= Class Implementation =======

class CompilationEngine:
	"""
	Effects the actual compilation output. Gets its input from a
	JackTokenizer and emits its parsed structure into an output file/stream.
	"""

	""" Sets which help determine token types in O(1) """
	class_var_decs = {TTK.STATIC, TTK.FIELD}
	subroutines = {TTK.METHOD, TTK.FUNCTION, TTK.CONSTRUCTOR}
	subroutine_types = {TTK.INT, TTK.BOOLEAN, TTK.CHAR, TTK.VOID}
	var_value_types = {TTK.INT, TTK.BOOLEAN, TTK.CHAR}
	var_types = {TTT.KEYWORD, TTT.IDENTIFIER}
	statements = {TTK.LET, TTK.IF, TTK.WHILE, TTK.DO, TTK.RETURN}
	constants = {TTT.INT_CONST, TTT.STRING_CONST}
	key_constants = {TTK.TRUE, TTK.FALSE, TTK.NULL, TTK.THIS}
	unary_ops = {TTS.MINUS, TTS.TILDE}
	ops = {TTS.PLUS, TTS.MINUS, TTS.STAR, TTS.FORWARD_SLASH, TTS.AMPERSAND, TTS.PIKE,
		   TTS.GREATER_THAN, TTS.LESS_THAN, TTS.EQUALS}

	# ================ Constructor ==================

	def __init__(self, tokenizer, output_file):
		""" Creates a new compilation engine with the given input and output.
			The next routine called must be compileClass() """
		self.tokenizer = tokenizer
		self.output_file = output_file

	# ============== Main API Methods ===============

	def compile_class(self):
		""" Compiles a complete class """
		# write <class>
		self.file_writeln(CLASS_XML_PREFIX)
		# write <keyword> class </keyword>
		self.file_writeln(self.get_class_XML())
		# write <identifier> name </identifier>
		self.file_writeln(self.get_identifier_XML())
		# write <symbol> { </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_BRACE))
		# this call should compile the inner structure of the class
		self.compile_class_body()
		""" Note: current token is now a token which is not a classVarDec or subroutineDec
			so when we return to compile_class we will check if it's a right brace
			so if it's not - we will catch this there and raise an exception like a boss"""
		# write <symbol> } </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_BRACE))
		# write </class>
		self.file_writeln(CLASS_XML_SUFFIX)

	def compile_class_body(self):
		"""
		Helper method which compiles the entire class' body using the tokenizer.
		:return: a tasty burekas
		"""
		while self.next_token_is_class_var_dec():
			self.compile_class_var_dec()  # this method advances the tokenizer
		while self.next_token_is_subroutine():
			self.compile_subroutine()  # this method advances the tokenizer

	def compile_class_var_dec(self):
		""" Compiles a static declaration or a field declaration
			note: assumes current token is indeed a classVarDec since calling
			method already checked that"""
		# write <classVarDec>
		self.file_writeln(CLASS_VAR_DEC_XML_PREFIX)
		# write <keyword> field/static </keyword>
		self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
		# write <keyword> type </keyword>
		self.file_writeln(self.get_type_XML())
		# write <identifier> name </identifier>
		self.file_writeln(self.get_identifier_XML())
		# in case there are more variables declared in the same line
		while self.next_token_is_specific_symbol(TTS.COMMA):
			# write <symbol> , </symbol>
			self.file_writeln(self.get_specific_symbol_XML(TTS.COMMA))
			# write <identifier> name </identifier>
			self.file_writeln(self.get_identifier_XML())
		# write <symbol> ; </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.SEMICOLON))
		# write </classVarDec>
		self.file_writeln(CLASS_VAR_DEC_XML_SUFFIX)

	def compile_subroutine(self):
		""" Compiles a complete method, function, or constructor """
		# write <subroutineDec>
		self.file_writeln(SUBROUTINE_DEC_XML_PREFIX)
		# write <keyword> (constructor|function|method) </keyword>
		self.file_writeln(self.get_function_declar_XML())
		# write <keyword | identifier> (void | type | identifier) </ keyword | identifier>
		self.file_writeln(self.get_subroutine_type_XML())
		# write <identifier> name </identifier>
		self.file_writeln(self.get_identifier_XML())
		# write <symbol> ( </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_PAR))
		# compile the parameter list
		self.compile_parameter_list()
		# write <symbol> ) </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_PAR))
		# write <subroutineBody>
		self.file_writeln(SUBROUTINE_BODY_XML_PREFIX)
		# write <symbol> { </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_BRACE))
		# compile all variable declarations, if there are any
		while self.next_token_is_var():
			self.compile_var_dec()
		# compile the subroutine's statements
		self.compile_statements()
		# write <symbol> } </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_BRACE))
		# write </subroutineBody>
		self.file_writeln(SUBROUTINE_BODY_XML_SUFFIX)
		# write </subroutineDec>
		self.file_writeln(SUBROUTINE_DEC_XML_SUFFIX)

	def compile_parameter_list(self):
		""" Compiles a (possibly empty) parameter list,
		not including the enclosing "()" """
		# this will help handle multiple parameters if there are
		multiple_params = False
		# write <parameterList>
		self.file_writeln(PARAMETER_LIST_XML_PREFIX)
		while not self.next_token_is_specific_symbol(TTS.RIGHT_PAR):
			if multiple_params:  # add the comma before the variable
				# write <symbol>,</symbol>
				self.file_writeln(self.get_specific_symbol_XML(TTS.COMMA))
			# write <keyword|identifier>type</keyword|identifier>
			self.file_writeln(self.get_type_XML())
			# write <identifier>name</identifier>
			self.file_writeln(self.get_identifier_XML())
			multiple_params = True
		# write</parameterList>
		self.file_writeln(PARAMETER_LIST_XML_SUFFIX)

	def compile_var_dec(self):
		""" Compiles all var declaration """
		# write <varDec>
		self.file_writeln(VAR_DEC_XML_PREFIX)
		# write <keyword> var </keyword>
		self.file_writeln(self.get_var_XML())
		# write <keyword|identifier> type </keyword|identifier>
		self.file_writeln(self.get_type_XML())
		# write <identifier> name </identifier>
		self.file_writeln(self.get_identifier_XML())
		# add any ", var" if there are
		while self.next_token_is_specific_symbol(TTS.COMMA):
			# write <symbol> , </symbol>
			self.file_writeln(self.get_specific_symbol_XML(TTS.COMMA))
			# write <identifier> name </identifier>
			self.file_writeln(self.get_identifier_XML())
		# write <symbol> ; </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.SEMICOLON))
		# write </varDec>
		self.file_writeln(VAR_DEC_XML_SUFFIX)

	def compile_statements(self):
		""" Compiles a sequence of statements,
		not including the enclosing "{}"
		assumes token is indeed a valid statement since caller method verified that"""
		# write <statements>
		self.file_writeln(STATEMENTS_XML_PREFIX)
		# handle all statements, if there are any
		while self.next_token_is_statement():
			# figure out the correct statement and compile it
			type = self.get_statement_type()
			if type == TTK.LET:
				self.compile_let()
			elif type == TTK.IF:
				self.compile_if()
			elif type == TTK.WHILE:
				self.compile_while()
			elif type == TTK.DO:
				self.compile_do()
			else:  # the last statement is RETURN
				self.compile_return()
		self.file_writeln(STATEMENTS_XML_SUFFIX)

	def compile_do(self):
		""" Compiles a do statement """
		# write <doStatement>
		self.file_writeln(DO_STATEMENT_XML_PREFIX)
		# write <keyword> do </keyword>
		self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
		# write <identifier> name </identifier>
		self.file_writeln(self.get_identifier_XML())
		# handle subroutine call from other class
		if self.next_token_is_specific_symbol(TTS.DOT):
			self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
			self.file_writeln(self.get_identifier_XML())
		# write <symbol> ( </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_PAR))
		# compile the expression list in the call
		self.compile_expression_list()
		# write <symbol> ) </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_PAR))
		# write <symbol> ; </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.SEMICOLON))
		# write </doStatement>
		self.file_writeln(DO_STATEMENT_XML_SUFFIX)

	def compile_let(self):
		""" Compiles a let statement """
		# write <letStatement>
		self.file_writeln(LET_STATEMENT_XML_PREFIX)
		# write <keyword> let </keyword>
		self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
		# write <identifier> name </identifier>
		self.file_writeln(self.get_identifier_XML())
		# the ('[' expression ']')? part
		if self.next_token_is_specific_symbol(TTS.LEFT_BRACKET):
			# write <symbol> [ </symbol>
			self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
			# compile the expression inside the brackets
			self.compile_expression()
			# write <symbol> ] </symbol>
			self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_BRACKET))
		# write <symbol> = </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.EQUALS))
		# compile the expression
		self.compile_expression()
		# write <symbol> ; </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.SEMICOLON))
		# write </letStatement>
		self.file_writeln(LET_STATEMENT_XML_SUFFIX)

	def compile_while(self):
		""" Compiles a while statement """
		# write <whileStatement>
		self.file_writeln(WHILE_STATEMENT_XML_PREFIX)
		# write <keyword> while </keyword>
		self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
		# write <symbol> ( </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_PAR))
		# compile the expression in the while
		self.compile_expression()
		# write <symbol> ) </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_PAR))
		# write <symbol> { </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_BRACE))
		# compile the loop's statements
		self.compile_statements()
		# write <symbol> } </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_BRACE))
		# write </whileStatement>
		self.file_writeln(WHILE_STATEMENT_XML_SUFFIX)

	def compile_return(self):
		""" Compiles a return statement """
		# write <returnStatement>
		self.file_writeln(RETURN_STATEMENT_XML_PREFIX)
		# write <keyword> return </keyword>
		self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
		if not self.next_token_is_specific_symbol(TTS.SEMICOLON):
			# handle the expression
			self.compile_expression()
		# write <symbol> ; </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.SEMICOLON))
		# write </returnStatement>
		self.file_writeln(RETURN_XML_SUFFIX)

	def compile_if(self):
		""" Compiles an if statement, possibly with a trailing else clause """
		# write <ifStatement>
		self.file_writeln(IF_STATEMENT_PREFIX)
		# write <keyword> if </keyword>
		self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
		# write <symbol> ( </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_PAR))
		# compile an expression for the if
		self.compile_expression()
		# write <symbol> ) </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_PAR))
		# write <symbol> { </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_BRACE))
		# compile the if's statements
		self.compile_statements()
		# write <symbol> } </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_BRACE))
		# the ('else' '{' statements '}')? part
		if self.next_token_is_else():
			# write <keyword> else </keyword>
			self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
			# write <symbol> { </symbol>
			self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_BRACE))
			# compile else's statements
			self.compile_statements()
			# write <symbol> } </symbol>
			self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_BRACE))
		# write </ifStatement>
		self.file_writeln(IF_STATEMENT_XML_SUFFIX)

	def compile_expression(self):
		""" Compiles an expression """
		# write <expression>
		self.file_writeln(EXPRESSION_XML_PREFIX)
		# compile the term
		self.compile_term()
		# the (op term)* part
		while self.next_token_is_op():
			# write <symbol> op </symbol>
			self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
			# compile a term
			self.compile_term()
		# write </expression>
		self.file_writeln(EXPRESSION_XML_SUFFIX)

	def compile_term(self):
		""" Compiles a term """
		if not self.next_token_is_term():
			raise Exception(TERM_NOT_FOUND_EXCEPTION)
		# write <term>
		self.file_writeln(TERM_XML_PREFIX)
		# next lines figure out the correct term type and compile accordingly
		if self.next_token_is_constant():
			self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
		elif self.next_token_is_identifier():
			self.file_writeln(self.get_identifier_XML())
			# handle array
			if self.next_token_is_specific_symbol(TTS.LEFT_BRACKET):
				self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
				self.compile_expression()
				self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_BRACKET))
			# handle subroutine call from same class
			elif self.next_token_is_specific_symbol(TTS.LEFT_PAR):
				self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
				self.compile_expression_list()
				self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_PAR))
			# handle subroutine call from other class
			elif self.next_token_is_specific_symbol(TTS.DOT):
				self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
				self.file_writeln(self.get_identifier_XML())
				self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_PAR))
				self.compile_expression_list()
				self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_PAR))
		# handle ( expression )
		elif self.next_token_is_specific_symbol(TTS.LEFT_PAR):
			self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
			self.compile_expression()
			self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_PAR))
		elif self.next_token_is_unary_op():
			self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
			self.compile_term()
		# write </term>
		self.file_writeln(TERM_XML_SUFFIX)

	def compile_expression_list(self):
		""" Compiles a (possibly empty) comma-separated list of expressions """
		# write <expressionList>
		self.file_writeln(EXPRESSION_LIST_XML_PREFIX)
		# this variable will help handle multiple expressions separated by a comma
		multiple_expression = False
		get_another_expression = self.next_token_is_term()
		while get_another_expression:
			if multiple_expression:
				self.file_writeln(self.get_specific_symbol_XML(TTS.COMMA))
			self.compile_expression()
			multiple_expression = True
			get_another_expression = self.next_token_is_specific_symbol(TTS.COMMA)
		# write </expressionList>
		self.file_writeln(EXPRESSION_LIST_XML_SUFFIX)

	# ============== Helper methods ================

	""" Following methods check various things about the next token we will receive, such as what 
		is it's type or if it is some special symbol, etc. """

	def next_token_is_specific_symbol(self, symbol):
		token = self.peek_tokenizer()
		type = token.get_type()
		if type != TTT.SYMBOL:
			return False
		value = sym_dict[token.get_value()]
		return value == symbol

	def next_token_is_statement(self):
		token = self.peek_tokenizer()
		type = token.get_type()
		value = token.get_value()
		return type == TTT.KEYWORD and key_dict[value] in CompilationEngine.statements

	def next_token_is_else(self):
		token = self.peek_tokenizer()
		return token.get_type() == TTT.KEYWORD and key_dict[token.get_value()] == TTK.ELSE

	def next_token_is_op(self):
		token = self.peek_tokenizer()
		return token.get_type() == TTT.SYMBOL and sym_dict[
			token.get_value()] in CompilationEngine.ops

	def next_token_is_constant(self):
		token = self.peek_tokenizer()
		type = token.get_type()
		value = token.get_value()
		constant = type in CompilationEngine.constants
		keyConstant = type == TTT.KEYWORD and key_dict[value] in CompilationEngine.key_constants
		return constant or keyConstant

	def next_token_is_identifier(self):
		return self.peek_tokenizer().get_type() == TTT.IDENTIFIER

	def next_token_is_unary_op(self):
		token = self.peek_tokenizer()
		return token.get_type() == TTT.SYMBOL and sym_dict[
			token.get_value()] in CompilationEngine.unary_ops

	def next_token_is_term(self):
		token = self.peek_tokenizer()
		type = token.get_type()
		value = token.get_value()
		constant = type in CompilationEngine.constants
		keyConstant = type == TTT.KEYWORD and key_dict[value] in CompilationEngine.key_constants
		# covers: var, var array, subroutine
		identifier = type == TTT.IDENTIFIER
		left_par = type == TTT.SYMBOL and sym_dict[value] == TTS.LEFT_PAR
		unary_op = type == TTT.SYMBOL and sym_dict[value] in CompilationEngine.unary_ops
		return constant | keyConstant | identifier | left_par | unary_op

	def next_token_is_class_var_dec(self):
		token = self.peek_tokenizer()
		return token.get_type() == TTT.KEYWORD and key_dict[
			token.get_value()] in CompilationEngine.class_var_decs

	def next_token_is_subroutine(self):
		token = self.peek_tokenizer()
		return token.get_type() == TTT.KEYWORD and key_dict[
			token.get_value()] in CompilationEngine.subroutines

	def next_token_is_var(self):
		token = self.peek_tokenizer()
		return token.get_type() == TTT.KEYWORD and key_dict[token.get_value()] == TTK.VAR

	def get_statement_type(self):
		token = self.peek_tokenizer()
		return key_dict[token.get_value()]

	def file_write(self, str):
		"""
		Method which receives a string and writes it as is in the output file.
		:param str: The string we are writing to the file
		"""
		self.output_file.write(str)

	def file_writeln(self, str):
		"""
		Method which receives a string and writes it as is in the output file, follow by a new
		line character,	if there is none.
		:param str: The string we are writing to the file
		"""
		if (not str.endswith(NEWLINE)):
			str = str + NEWLINE
		self.file_write(str)

	def get_and_advance_tokenizer(self):
		"""
		Method which returns the current token stored in the tokenizer and causes the tokenizer
		to advance.
		:return: Token object which was stored in the tokenizer
		"""
		token = self.peek_tokenizer()
		self.tokenizer.advance()
		return token

	def peek_tokenizer(self):
		"""
		Method which returns the current token stored in the tokenizer WITHOUT causing it to
		advance.
		:return: Token object which is currently stored in the tokenizer
		"""
		if not self.tokenizer.has_more_tokens():
			raise Exception(TOKENIZER_EMPTY_EXCEPTION)
		token = self.tokenizer.get_current_token()
		return token

	# ================== Compilation Related Methods ==================

	""" Following methods get the compiled version of each token type, they also cause the 
		tokenizer to advance, so they basically get a token from the tokenizer, advance and then 
		return the compiled version (the XML form currently) of the token they got. 
		Currently these methods get the XML version from each file, so if we would want to
		write output files in some other language or format, we would only need to change the
		way the Token objects give us the translation, or adjust minor things in these methods, 
		thus keeping our class future-proof. """

	def get_type_XML(self):
		token = self.get_and_advance_tokenizer()
		type = token.get_type()
		value = token.get_value()
		primitive = type == TTT.KEYWORD and key_dict[value] in CompilationEngine.var_value_types
		obj_type = type == TTT.IDENTIFIER
		if not primitive and not obj_type:
			raise Exception(UNEXPECTED_TOKEN_EXCEPTION + value)
		return token.get_xml_form()

	def get_specific_symbol_XML(self, symbol):
		token = self.get_and_advance_tokenizer()
		type = token.get_type()
		if type != TTT.SYMBOL or sym_dict[token.get_value()] != symbol:
			raise Exception(UNEXPECTED_TOKEN_EXCEPTION + token.get_value())
		return token.get_xml_form()

	def get_symbol_XML(self):
		token = self.get_and_advance_tokenizer()
		type = token.get_type()
		if type != TTT.SYMBOL:
			raise Exception(UNEXPECTED_TOKEN_EXCEPTION + token.get_value())
		return token.get_xml_form()

	def get_identifier_XML(self):
		token = self.get_and_advance_tokenizer()
		type = token.get_type()
		if type != TTT.IDENTIFIER:
			raise Exception(IDENTIFIER_NOT_FOUND_EXCEPTION)
		return token.get_xml_form()

	def get_class_XML(self):
		token = self.get_and_advance_tokenizer()
		type = token.get_type()
		value = token.get_value()
		if type != TTT.KEYWORD and (value not in key_dict or key_dict[value] != TTK.CLASS):
			raise Exception(CLASS_TOKEN_NOT_FOUND_EXCEPTION)
		return token.get_xml_form()

	def get_function_declar_XML(self):
		token = self.get_and_advance_tokenizer()
		if token.get_type() != TTT.KEYWORD or key_dict[token.get_value()] not in \
				CompilationEngine.subroutines:
			raise Exception(FUNC_DECLARE_NOT_FOUND_EXCEPTION + token.get_value())
		return token.get_xml_form()

	def get_subroutine_type_XML(self):
		token = self.get_and_advance_tokenizer()
		type = token.get_type()
		value = token.get_value()
		primitive = type == TTT.KEYWORD and key_dict[value] in CompilationEngine.subroutine_types
		obj = type == TTT.IDENTIFIER
		if not primitive and not obj:
			raise Exception(SUBROUTINE_NOT_FOUND_EXCEPTION + value)
		return token.get_xml_form()

	def get_var_XML(self):
		token = self.get_and_advance_tokenizer()
		if token.get_type() != TTT.KEYWORD or key_dict[token.get_value()] != TTK.VAR:
			raise Exception(VAR_DECLARE_NOT_FOUND_EXCEPTION + token.get_value())
		return token.get_xml_form()
