# ============== Imports ==============

from srcFiles.TokenTypes import Type as TTT
from srcFiles.TokenTypes import Keyword as TTK
from srcFiles.TokenTypes import Symbol as TTS
from srcFiles.TokenTypes import keyword_dict as key_dict
from srcFiles.TokenTypes import symbols_dict as sym_dict
from srcFiles.SymbolTable import SymbolTable

# ============ General constants ====================

VAR_DECLARE_NOT_FOUND_EXCEPTION = "Expected var declare but got "
SUBROUTINE_NOT_FOUND_EXCEPTION = "Expected subroutine type but got "
FUNC_DECLARE_NOT_FOUND_EXCEPTION = "Expected function declaration but got "
CLASS_TOKEN_NOT_FOUND_EXCEPTION = "Expected class token which was not found"
IDENTIFIER_NOT_FOUND_EXCEPTION = "Expected identifier after class"
UNEXPECTED_TOKEN_EXCEPTION = "Unexpected token "
TOKENIZER_EMPTY_EXCEPTION = "Attempt to get tokens but tokenizer has no more tokens!"
UNKN_OP_EXCEPTION = "Unknown op exception"
NEWLINE = "\n"

# ============ VM related constants =================

EQ_COMMAND = "eq"
LT_COMMAND = "lt"
GT_COMMAND = "gt"
OR_COMMAND = "or"
AND_COMMAND = "and"
SUB_COMMAND = "sub"
NOT_COMMAND = "not"
NEG_COMMAND = "neg"
ADD_COMMAND = "add"
IF_END_LABEL = "IF_END"
IF_FALSE_LABEL = "IF_FALSE"
IF_TRUE_LABEL = "IF_TRUE"
LOOP_START_LABEL = "WHILE_EXP"
LOOP_END_LABEL = "WHILE_END"
LOCAL_KIND = "local"
ARGUMENTS_KIND = "argument"
THIS_KIND = "this"
THAT_KIND = "that"
POINTER_KIND = "pointer"
CONSTANT_KIND = "constant"
FIELD_KIND = "field"
TEMP_KIND = "temp"
THIS_SYM_NAME = "this"
STRING_APPEND_FUNC = "String.appendChar"
STRING_NEW_FUNC = "String.new"
MATH_DIV_SUBROUTINE = "Math.divide"
MATH_MUL_SUBROUTINE = "Math.multiply"
MEMORY_ALLOC_SUBROUTINE = "Memory.alloc"
STR_CONST_CREATION = "String constant creation start"
SUBROUTINE_DEC_COMMENT = "subroutine declaration"
DO_COMMENT = "do"
LET_COMMENT = "let"
IF_COMMENT = "if"
WHILE_LOOP_COMMENT = "while loop"

# ============ XML related constants =================

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

	def __init__(self, tokenizer, output_file, translator=None):
		""" Creates a new compilation engine with the given input and output.
			Also allows choice of a translator object (such as VMWriter), so that if we want
			to change the translation target language we simply need to pass the constructor
			a different translator which works with VMWriter's API.
			The next routine called must be compileClass() """
		self.tokenizer = tokenizer
		self.output_file = output_file
		self.translator = translator
		# initialize a global symbol table
		self.__symbol_table = SymbolTable()
		self.__class_name = ""
		self.__current_subroutine_name = ""
		self.__current_vm_subroutine_name = ""
		self.__if_label_counter = 0  # this is used so we don't have conflicting labels
		self.__local_var_num = 0  # this is used to count local variables
		self.__num_of_expressions = 0  # this is used to count expressions
		self.__local_fields_num = 0  # this is used to count fields
		self.__while_label_counter = 0  # this is used same as label counter, for while labels

	# ============== Main API Methods ===============

	def compile_class(self):
		""" Compiles a complete class """
		self.skip_token()  # skip class token
		# get the class name for future use (this also advances)
		self.__class_name = self.get_token_value()
		self.skip_token()  # skip { token
		self.compile_class_body()
		self.skip_token()  # skip } token

	def compile_class_body(self):
		"""
		Helper method which compiles the entire class' body using the tokenizer.
		:return: a tasty burekas
		"""

		while self.next_token_is_class_var_dec():
			self.compile_class_var_dec()  # this method advances the tokenizer
		while self.next_token_is_subroutine():
			# create a new table for the new scope we enter with the method
			self.__symbol_table = SymbolTable(self.__symbol_table)
			self.compile_subroutine()  # this method advances the tokenizer
			# destroy current table and revert to the global one
			self.__symbol_table = self.__symbol_table.get_prev()

	def compile_class_var_dec(self):
		""" Compiles a static declaration or a field declaration
			note: assumes current token is indeed a classVarDec since calling
			method already checked that"""

		# get the params for the new symbol
		var_kind = self.get_token_value()
		# this is used because fields are treated differently
		is_field = var_kind == FIELD_KIND
		var_type = self.get_token_value()
		var_name = self.get_token_value()
		# add the symbol to the symbol table
		self.__symbol_table.add_symbol(var_name, var_type, var_kind)
		if is_field:
			self.__local_fields_num += 1  # since "this" is a field too
		# if there are any more variables
		while self.next_token_is_specific_symbol(TTS.COMMA):
			self.skip_token()  # skip the comma token
			# get the new variable's name and add the new symbol to the table
			var_name = self.get_token_value()
			self.__symbol_table.add_symbol(var_name, var_type, var_kind)
			if is_field:
				self.__local_fields_num += 1  # since "this" is a local member as well
		self.skip_token()  # skip the semicolon token

	def compile_subroutine(self):
		""" Compiles a complete method, function, or constructor """

		self.translator.write_comment(SUBROUTINE_DEC_COMMENT)
		# since we entered a new scope, we define a new symbol table for it
		subroutine_kind = self.get_token_value()
		# these are helping manage different subroutines in the correct way
		is_method = key_dict.get(subroutine_kind) == TTK.METHOD
		is_constructor = key_dict.get(subroutine_kind) == TTK.CONSTRUCTOR
		if is_method:  # since methods need a "this" variable
			self.__symbol_table.add_symbol(THIS_SYM_NAME, self.__class_name, ARGUMENTS_KIND)
		self.skip_token()  # skip the subroutine_type token (void | type | identifier)
		self.update_subroutine_name(self.get_token_value())  # update current subroutine name
		self.skip_token()  # skip the ( token
		self.compile_parameter_list()
		self.skip_token()  # skip the ) token
		self.skip_token()  # skip the { token
		# reset the counters before we enter the new subroutine
		self.__local_var_num = 0
		self.__if_label_counter = 0
		self.__while_label_counter = 0
		# compile the subroutine's variables
		while self.next_token_is_var():
			self.compile_var_dec()
		self.translator.write_function(self.__current_vm_subroutine_name, self.__local_var_num)
		if is_method:  # if this is a method, we need to prepare a "this" pointer
			self.translator.write_push(ARGUMENTS_KIND, 0)
			self.translator.write_pop(POINTER_KIND, 0)
		if is_constructor:  # this is a constructor, so we need allocate memory
			self.translator.write_push(CONSTANT_KIND, self.__local_fields_num)
			self.translator.write_call(MEMORY_ALLOC_SUBROUTINE, 1)
			self.translator.write_pop(POINTER_KIND, 0)
		# compile the subroutine's statements
		self.compile_statements()
		self.skip_token()  # skip the } token

	def compile_parameter_list(self):
		""" Compiles a (possibly empty) parameter list,
		not including the enclosing "()" """

		# taking care of an edge case with no parameters in the list
		if self.next_token_is_specific_symbol(TTS.RIGHT_PAR):
			return
		# this will help handle multiple parameters if there are
		multiple_params = False
		while not self.next_token_is_specific_symbol(TTS.RIGHT_PAR):
			if multiple_params:  # add the comma before the variable
				self.skip_token()  # skip the , token
			# prepare values for the new symbol and add it to the table
			par_type = self.get_token_value()
			par_name = self.get_token_value()
			self.__symbol_table.add_symbol(par_name, par_type, ARGUMENTS_KIND)
			multiple_params = True

	def compile_var_dec(self):
		""" Compiles all var declaration """

		self.skip_token()  # skip the var token
		# add first var as symbol to the table
		var_type = self.get_token_value()
		var_name = self.get_token_value()
		self.__symbol_table.add_symbol(var_name, var_type, LOCAL_KIND)
		self.__local_var_num += 1
		# add more vars if there are any
		while self.next_token_is_specific_symbol(TTS.COMMA):
			self.skip_token()  # skip the , token
			# prepare and add a new symbol to the table
			var_name = self.get_token_value()
			self.__symbol_table.add_symbol(var_name, var_type, LOCAL_KIND)
			self.__local_var_num += 1
		self.skip_token()  # skip the semicolon token

	def compile_statements(self):
		""" Compiles a sequence of statements,
		not including the enclosing "{}"
		assumes token is indeed a valid statement since caller method verified that"""

		# handle all statements, if there are any
		while self.next_token_is_statement():
			# figure out the correct statement and compile it
			tok_type = self.get_statement_type()
			if tok_type == TTK.LET:
				self.compile_let()
			elif tok_type == TTK.IF:
				self.compile_if()
			elif tok_type == TTK.WHILE:
				self.compile_while()
			elif tok_type == TTK.DO:
				self.compile_do()
			else:  # the last statement is RETURN
				self.compile_return()

	def compile_do(self):
		""" Compiles a do statement """

		self.translator.write_comment(DO_COMMENT)
		self.skip_token()  # skip the do token
		nargs = 0  # used to count the number of arguments sent
		identifier = self.get_token_value()
		symbol = self.__symbol_table.get_symbol(identifier)
		if symbol is not None:  # identifier is an object
			self.translator.write_push(symbol.get_kind(), symbol.get_index())  # Send it as this
			nargs += 1  # Count it as an argument
			identifier = symbol.get_type()  # Get it's class name
		# handle subroutine call from other class
		if self.next_token_is_specific_symbol(TTS.DOT):  # If not inner class method call
			identifier += "."
			self.skip_token()  # skip the . token
			identifier += self.get_token_value()
		else:
			self.translator.write_push(POINTER_KIND, 0)  # Push this
			nargs += 1  # Count it as an argument
			identifier = self.__class_name + "." + identifier  # Add class name before method name
		self.skip_token()  # skip the ( token
		# compile the expression list in the call
		nargs += self.compile_expression_list()
		self.skip_token()  # skip the ) token
		self.skip_token()  # skip the ; token
		self.translator.write_call(identifier, nargs)
		self.translator.write_pop(TEMP_KIND, 0)  # Ignore return value

	def compile_let(self):
		""" Compiles a let statement """

		self.translator.write_comment(LET_COMMENT)
		self.skip_token()  # skip the let token
		var_name = self.get_token_value()
		var_symbol = self.__symbol_table.get_symbol(var_name)
		var_k = var_symbol.get_kind()
		var_i = var_symbol.get_index()
		is_array = self.next_token_is_specific_symbol(TTS.LEFT_BRACKET)
		# the ('[' expression ']')? part, in case of an array
		if is_array:
			self.skip_token()  # skip the [ token
			# compile the expression inside the brackets
			self.compile_expression()  # now a value is pushed
			self.translator.write_push(var_k, var_i)
			self.translator.write_arithmetic(ADD_COMMAND)  # now the right index is in the stack
			var_k = THAT_KIND
			var_i = 0
			self.skip_token()  # skip the ] token
		self.skip_token()  # skip the = token
		# compile the expression
		self.compile_expression()  # now a value is pushed to the stack
		if is_array:  # get the pointer and prepare the value
			self.translator.write_pop(TEMP_KIND, 0)
			self.translator.write_pop(POINTER_KIND, 1)
			self.translator.write_push(TEMP_KIND, 0)
		# pop the result into the variable to complete the let statement
		self.translator.write_pop(var_k, var_i)
		self.skip_token()  # skip the ; token

	def compile_while(self):
		""" Compiles a while statement """

		self.translator.write_comment(WHILE_LOOP_COMMENT)
		# prepare the labels and increment the label counter
		start_label = self.get_unique_label(LOOP_START_LABEL, self.__while_label_counter)
		end_label = self.get_unique_label(LOOP_END_LABEL, self.__while_label_counter)
		self.inc_while_lbl_counter()
		self.skip_token()  # skip the while token
		self.translator.write_label(start_label)  # write the loop begin label
		self.skip_token()  # skip the ( token
		# compile the expression in the while condition
		self.compile_expression()
		self.skip_token()  # skip the ) token
		# negate the expression and jump to loop end
		self.translator.write_arithmetic(NOT_COMMAND)
		self.translator.write_if(end_label)
		self.skip_token()  # skip the { token
		# compile the loop's statements
		self.compile_statements()
		self.translator.write_goto(start_label)
		self.translator.write_label(end_label)
		self.skip_token()  # skip the } token

	def compile_return(self):
		""" Compiles a return statement """

		self.skip_token()  # skip the return token
		if not self.next_token_is_specific_symbol(TTS.SEMICOLON):  # in case we return a value
			# handle the expression
			self.compile_expression()
		else:  # in case we return nothing, push 0
			self.translator.write_push(CONSTANT_KIND, 0)
		self.skip_token()  # skip the ; token
		self.translator.write_return()

	def compile_if(self):
		""" Compiles an if statement, possibly with a trailing else clause """

		self.translator.write_comment(IF_COMMENT)
		self.skip_token()  # skip the if token
		self.skip_token()  # skip the ( token
		# compile an expression for the if
		self.compile_expression()  # the condition value is at top of stack now
		# check the condition value and jump to wherever is needed
		true_lab = self.get_unique_label(IF_TRUE_LABEL, self.__if_label_counter)
		false_lab = self.get_unique_label(IF_FALSE_LABEL, self.__if_label_counter)
		end_lab = self.get_unique_label(IF_END_LABEL, self.__if_label_counter)
		self.inc_if_lbl_counter()
		self.skip_token()  # skip the ) token
		self.skip_token()  # skip the { token
		# prepare the jump and label instructions
		self.translator.write_if(true_lab)
		self.translator.write_goto(false_lab)
		self.translator.write_label(true_lab)
		# compile the if's statements
		self.compile_statements()
		self.skip_token()  # skip the } token
		# the ('else' '{' statements '}')? part
		if self.next_token_is_else():  # if we have an else block
			self.translator.write_goto(end_lab)  # prepare the else skip jump instruction
			self.translator.write_label(false_lab)  # the else label (or if end label)
			self.skip_token()  # skip the else token
			self.skip_token()  # skip the { token
			# compile else's statements
			self.compile_statements()
			self.skip_token()  # skip the } token
			self.translator.write_label(end_lab)  # the end of the else block
		else:  # if we have no else block, we don't need the end label
			self.translator.write_label(false_lab)  # the else label (or if end label)

	def compile_expression(self):
		""" Compiles an expression """

		# compile the first term
		self.compile_term()  # now there's a value on the stack
		# the (op term)* part of the expression
		while self.next_token_is_op():
			op = self.get_token_value()
			# compile a term
			self.compile_term()  # now there's a value on the stack
			self.write_correct_op_command(op)  # use the correct op

	def compile_term(self):
		""" Compiles a term """

		# sanity check
		if not self.next_token_is_term():
			raise Exception(TERM_NOT_FOUND_EXCEPTION)
		# next lines figure out the correct term type and compile accordingly
		# handles constants
		if self.next_token_is_constant():
			const = self.get_and_advance_tokenizer()
			c_type = const.get_type()
			c_val = key_dict.get(const.get_value())
			if c_type == TTT.INT_CONST:  # integers
				# push the constant value we found
				self.translator.write_push(CONSTANT_KIND, const.get_value())
			elif c_type == TTT.STRING_CONST:  # strings
				self.do_string_vm_code(const)
			# these elif's take care of keyword constants
			elif c_val == TTK.TRUE:
				self.translator.write_push_true()
			elif c_val == TTK.THIS:
				self.translator.write_push_this()
			elif c_val == TTK.FALSE:
				self.translator.write_push_false()
			elif c_val == TTK.NULL:
				self.translator.write_push_null()
		# handles variables/arrays/methods/stuff with identifiers
		elif self.next_token_is_identifier():
			new_ident = self.get_token_value()
			var_sym = self.__symbol_table.get_symbol(new_ident)
			# handle array
			if self.next_token_is_specific_symbol(TTS.LEFT_BRACKET):
				self.skip_token()  # skip the [ token
				self.compile_expression()  # after this, the arr's address is pushed
				self.translator.write_push(var_sym.get_kind(), var_sym.get_index())
				self.translator.write_arithmetic(ADD_COMMAND)  # now we have the right index
				self.translator.write_pop(POINTER_KIND, 1)
				self.translator.write_push(THAT_KIND, 0)  # now the value is on the stack
				self.skip_token()  # skip the ] token
			# handle subroutine call from same class
			elif self.next_token_is_specific_symbol(TTS.LEFT_PAR):
				self.skip_token()  # skip the ( token
				exp_count = self.compile_expression_list()  # now params are on the stack
				self.translator.write_call(new_ident, exp_count)  # now values are on the stack
				self.skip_token()  # skip the ) token
			# handle subroutine call from other class
			elif self.next_token_is_specific_symbol(TTS.DOT):
				self.skip_token()  # skip the . token
				ident_sym = self.__symbol_table.get_symbol(new_ident)
				is_obj = ident_sym is not None
				if is_obj:  # in case the identifier represents an object
					new_ident = ident_sym.get_type()
					exp_count = 1
					self.translator.write_push(ident_sym.get_kind(), ident_sym.get_index())
				else:  # not an object
					exp_count = 0
				new_ident = new_ident + "." + self.get_token_value()  # get new identifier
				self.skip_token()  # skip the ( token
				exp_count += self.compile_expression_list()  # now params are on the stack
				self.translator.write_call(new_ident, exp_count)  # now values are on the stack
				self.skip_token()  # skip the ) token
			else:  # the identifier stands for some simple variable
				self.translator.write_push(var_sym.get_kind(), var_sym.get_index())
		# handle ( expression )
		elif self.next_token_is_specific_symbol(TTS.LEFT_PAR):
			self.skip_token()  # skip the ( token
			self.compile_expression()  # now the value is on the stack
			self.skip_token()  # skip the ) token
		# either negation minus or ~ (not)
		elif self.next_token_is_unary_op():
			un_op = self.get_token_value()
			self.compile_term()
			if sym_dict.get(un_op) == TTS.MINUS:  # negation minus
				self.translator.write_arithmetic(NEG_COMMAND)
			else:  # the op is ~ (not)
				self.translator.write_arithmetic(NOT_COMMAND)

	def compile_expression_list(self):
		""" Compiles a (possibly empty) comma-separated list of expressions """

		# this variable will help handle multiple expressions separated by a comma
		multiple_expression = False
		exp_count = 0
		get_another_expression = self.next_token_is_term()
		while get_another_expression:
			exp_count += 1
			if multiple_expression:
				self.skip_token()  # skip , token
			self.compile_expression()
			multiple_expression = True
			get_another_expression = self.next_token_is_specific_symbol(TTS.COMMA)
		return exp_count

	#  ================= XML API METHODS ==============================

	def xml_compile_class(self):
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
		self.xml_compile_class_body()
		""" Note: current token is now a token which is not a classVarDec or subroutineDec
			so when we return to compile_class we will check if it's a right brace
			so if it's not - we will catch this there and raise an exception like a boss"""
		# write <symbol> } </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_BRACE))
		# write </class>
		self.file_writeln(CLASS_XML_SUFFIX)

	def xml_compile_class_body(self):
		"""
		Helper method which compiles the entire class' body using the tokenizer.
		:return: a tasty burekas
		"""
		while self.next_token_is_class_var_dec():
			self.xml_compile_class_var_dec()  # this method advances the tokenizer
		while self.next_token_is_subroutine():
			self.xml_compile_subroutine()  # this method advances the tokenizer

	def xml_compile_class_var_dec(self):
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

	def xml_compile_subroutine(self):
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
		self.xml_compile_parameter_list()
		# write <symbol> ) </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_PAR))
		# write <subroutineBody>
		self.file_writeln(SUBROUTINE_BODY_XML_PREFIX)
		# write <symbol> { </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_BRACE))
		# compile all variable declarations, if there are any
		while self.next_token_is_var():
			self.xml_compile_var_dec()
		# compile the subroutine's statements
		self.xml_compile_statements()
		# write <symbol> } </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_BRACE))
		# write </subroutineBody>
		self.file_writeln(SUBROUTINE_BODY_XML_SUFFIX)
		# write </subroutineDec>
		self.file_writeln(SUBROUTINE_DEC_XML_SUFFIX)

	def xml_compile_parameter_list(self):
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

	def xml_compile_var_dec(self):
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

	def xml_compile_statements(self):
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
				self.xml_compile_let()
			elif type == TTK.IF:
				self.xml_compile_if()
			elif type == TTK.WHILE:
				self.xml_compile_while()
			elif type == TTK.DO:
				self.xml_compile_do()
			else:  # the last statement is RETURN
				self.xml_compile_return()
		self.file_writeln(STATEMENTS_XML_SUFFIX)

	def xml_compile_do(self):
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
		self.xml_compile_expression_list()
		# write <symbol> ) </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_PAR))
		# write <symbol> ; </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.SEMICOLON))
		# write </doStatement>
		self.file_writeln(DO_STATEMENT_XML_SUFFIX)

	def xml_compile_let(self):
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
			self.xml_compile_expression()
			# write <symbol> ] </symbol>
			self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_BRACKET))
		# write <symbol> = </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.EQUALS))
		# compile the expression
		self.xml_compile_expression()
		# write <symbol> ; </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.SEMICOLON))
		# write </letStatement>
		self.file_writeln(LET_STATEMENT_XML_SUFFIX)

	def xml_compile_while(self):
		""" Compiles a while statement """
		# write <whileStatement>
		self.file_writeln(WHILE_STATEMENT_XML_PREFIX)
		# write <keyword> while </keyword>
		self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
		# write <symbol> ( </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_PAR))
		# compile the expression in the while
		self.xml_compile_expression()
		# write <symbol> ) </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_PAR))
		# write <symbol> { </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_BRACE))
		# compile the loop's statements
		self.xml_compile_statements()
		# write <symbol> } </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_BRACE))
		# write </whileStatement>
		self.file_writeln(WHILE_STATEMENT_XML_SUFFIX)

	def xml_compile_return(self):
		""" Compiles a return statement """
		# write <returnStatement>
		self.file_writeln(RETURN_STATEMENT_XML_PREFIX)
		# write <keyword> return </keyword>
		self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
		if not self.next_token_is_specific_symbol(TTS.SEMICOLON):
			# handle the expression
			self.xml_compile_expression()
		# write <symbol> ; </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.SEMICOLON))
		# write </returnStatement>
		self.file_writeln(RETURN_XML_SUFFIX)

	def xml_compile_if(self):
		""" Compiles an if statement, possibly with a trailing else clause """
		# write <ifStatement>
		self.file_writeln(IF_STATEMENT_PREFIX)
		# write <keyword> if </keyword>
		self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
		# write <symbol> ( </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_PAR))
		# compile an expression for the if
		self.xml_compile_expression()
		# write <symbol> ) </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_PAR))
		# write <symbol> { </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_BRACE))
		# compile the if's statements
		self.xml_compile_statements()
		# write <symbol> } </symbol>
		self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_BRACE))
		# the ('else' '{' statements '}')? part
		if self.next_token_is_else():
			# write <keyword> else </keyword>
			self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
			# write <symbol> { </symbol>
			self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_BRACE))
			# compile else's statements
			self.xml_compile_statements()
			# write <symbol> } </symbol>
			self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_BRACE))
		# write </ifStatement>
		self.file_writeln(IF_STATEMENT_XML_SUFFIX)

	def xml_compile_expression(self):
		""" Compiles an expression """
		# write <expression>
		self.file_writeln(EXPRESSION_XML_PREFIX)
		# compile the term
		self.xml_compile_term()
		# the (op term)* part
		while self.next_token_is_op():
			# write <symbol> op </symbol>
			self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
			# compile a term
			self.xml_compile_term()
		# write </expression>
		self.file_writeln(EXPRESSION_XML_SUFFIX)

	def xml_compile_term(self):
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
				self.xml_compile_expression()
				self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_BRACKET))
			# handle subroutine call from same class
			elif self.next_token_is_specific_symbol(TTS.LEFT_PAR):
				self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
				self.xml_compile_expression_list()
				self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_PAR))
			# handle subroutine call from other class
			elif self.next_token_is_specific_symbol(TTS.DOT):
				self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
				self.file_writeln(self.get_identifier_XML())
				self.file_writeln(self.get_specific_symbol_XML(TTS.LEFT_PAR))
				self.xml_compile_expression_list()
				self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_PAR))
		# handle ( expression )
		elif self.next_token_is_specific_symbol(TTS.LEFT_PAR):
			self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
			self.xml_compile_expression()
			self.file_writeln(self.get_specific_symbol_XML(TTS.RIGHT_PAR))
		elif self.next_token_is_unary_op():
			self.file_writeln(self.get_and_advance_tokenizer().get_xml_form())
			self.xml_compile_term()
		# write </term>
		self.file_writeln(TERM_XML_SUFFIX)

	def xml_compile_expression_list(self):
		""" Compiles a (possibly empty) comma-separated list of expressions """
		# write <expressionList>
		self.file_writeln(EXPRESSION_LIST_XML_PREFIX)
		# this variable will help handle multiple expressions separated by a comma
		multiple_expression = False
		get_another_expression = self.next_token_is_term()
		while get_another_expression:
			if multiple_expression:
				self.file_writeln(self.get_specific_symbol_XML(TTS.COMMA))
			self.xml_compile_expression()
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

	def file_writeln(self, str_input):
		"""
		Method which receives a string and writes it as is in the output file, follow by a new
		line character,	if there is none.
		:param str_input: The string we are writing to the file
		"""
		if not str_input.endswith(NEWLINE):
			str_input = str_input + NEWLINE
		self.file_write(str_input)

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

	def skip_token(self):
		""" Causes the tokenizer to skip the current token """
		self.tokenizer.advance()

	def get_token_value(self):
		""" returns token's value, and advances the tokenizer"""
		return self.get_and_advance_tokenizer().get_value()

	def make_coffee(self, sugar_count):
		""" Method which receives a specific sugar count and makes some coffee """

		print("You didn't really think we will really make you coffee did you?")
		print("alright.. here you go.. coffee with " + sugar_count + "sugar.")

	# ================== XML Compilation Related Methods ==================

	""" Following methods get the xml version of each token type, they also cause the 
		tokenizer to advance, so they basically get a token from the tokenizer, advance and then 
		return the XML version of the token they got. 
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

	# ================== VM Compilation Related Methods ==================

	"""	Following methods are the VM extension of the CompilationEngine, basically they
		replace the xml version methods with the required VM translations of various processes,
		which allows compilation of some JACK file into usable VM code. """

	def inc_if_lbl_counter(self):
		""" Increment the label counter """

		self.__if_label_counter += 1

	def inc_while_lbl_counter(self):
		""" Increment the while label counter """

		self.__while_label_counter += 1

	def get_unique_label(self, label, counter):
		""" Returns a counter appended version of the label """

		return label + str(counter)

	def update_subroutine_name(self, subroutine_name):
		""" Updates the current subroutines name with the given one.
			Also updates the VM version of said subroutine accordingly. """

		self.__current_subroutine_name = subroutine_name
		self.__current_vm_subroutine_name = self.__class_name + "." + self.__current_subroutine_name

	def do_string_vm_code(self, token):
		""" Uses the translator to output the correct sequence of commands required
			to create a string in VM """

		self.translator.write_comment(STR_CONST_CREATION)
		const_str = token.get_value()
		self.translator.write_push(CONSTANT_KIND, len(const_str))
		self.translator.write_call(STRING_NEW_FUNC, 1)
		for char in const_str:  # add each char to the string we build
			self.translator.write_push(CONSTANT_KIND, ord(char))
			self.translator.write_call(STRING_APPEND_FUNC, 2)

	def write_correct_op_command(self, op):
		""" Figures out the correct operator command and causes the translator to
			output it."""

		op_sym = sym_dict.get(op)
		if op_sym == TTS.PLUS:
			self.translator.write_arithmetic(ADD_COMMAND)
		elif op_sym == TTS.MINUS:
			self.translator.write_arithmetic(SUB_COMMAND)
		elif op_sym == TTS.STAR:
			self.translator.write_call(MATH_MUL_SUBROUTINE, 2)
		elif op_sym == TTS.FORWARD_SLASH:
			self.translator.write_call(MATH_DIV_SUBROUTINE, 2)
		elif op_sym == TTS.AMPERSAND:
			self.translator.write_arithmetic(AND_COMMAND)
		elif op_sym == TTS.PIKE:
			self.translator.write_arithmetic(OR_COMMAND)
		elif op_sym == TTS.GREATER_THAN:
			self.translator.write_arithmetic(GT_COMMAND)
		elif op_sym == TTS.LESS_THAN:
			self.translator.write_arithmetic(LT_COMMAND)
		elif op_sym == TTS.EQUALS:
			self.translator.write_arithmetic(EQ_COMMAND)
		else:
			raise Exception(UNKN_OP_EXCEPTION)

# achievement - reached 1100 lines!
