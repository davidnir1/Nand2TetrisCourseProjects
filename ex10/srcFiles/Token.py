# ============== Imports ==============

from TokenTypes import *
# from .TokenTypes import *
# ============= Constants =============

IDENTIFIER_XML_P = "<identifier>"
IDENTIFIER_XML_S = "</identifier>"
INTEGER_CONSTANT_XML_S = "</integerConstant>"
INTEGER_CONSTANT_XML_P = "<integerConstant>"
STRING_CONSTANT_XML_S = "</stringConstant>"
STRING_CONSTANT_XML_P = "<stringConstant>"
AMP = " &amp; "
GREATER_THAN = " &gt; "
LESS_THAN = " &lt; "
QUOT = " &quot; "
SYMBOL_XML_S = "</symbol>"
SYMBOL_XML_P = "<symbol>"
KEYWORD_XML_SUFFIX = "</keyword>"
KEYWORD_XML_PREFIX = "<keyword>"

# ======= Class Implementation =======


class Token:
	"""
	This class represents a single Token.
	"""

	def __init__(self, type, value):
		"""
		Initialize a new token with a type and value
		:param type: Token's type
		:param value: Token's value
		"""
		self.__type = type
		self.__value = value

	def get_type(self):
		"""
		:return: Token's type
		"""
		return self.__type

	def get_value(self):
		"""
		:return: Token's value
		"""
		return self.__value

	def get_xml_form(self):
		"""
		:return: Current token xml form
		"""
		if self.__type is Type.KEYWORD:
			return KEYWORD_XML_PREFIX + " " + self.__value + " " + KEYWORD_XML_SUFFIX + "\n"
		if self.__type is Type.SYMBOL:
			if self.__value == '"':
				return SYMBOL_XML_P + QUOT + SYMBOL_XML_S + "\n"
			elif self.__value == "<":
				return SYMBOL_XML_P + LESS_THAN + SYMBOL_XML_S + "\n"
			elif self.__value == ">":
				return SYMBOL_XML_P + GREATER_THAN + SYMBOL_XML_S + "\n"
			elif self.__value == "&":
				return SYMBOL_XML_P + AMP + SYMBOL_XML_S + "\n"
			return SYMBOL_XML_P + " " + self.__value + " " + SYMBOL_XML_S + "\n"
		if self.__type is Type.STRING_CONST:
			return STRING_CONSTANT_XML_P + " " + self.__value + " " + STRING_CONSTANT_XML_S + "\n"
		if self.__type is Type.INT_CONST:
			return INTEGER_CONSTANT_XML_P + " " + self.__value + " " + INTEGER_CONSTANT_XML_S + "\n"
		if self.__type is Type.IDENTIFIER:
			return IDENTIFIER_XML_P + " " + self.__value + " " + IDENTIFIER_XML_S + "\n"
