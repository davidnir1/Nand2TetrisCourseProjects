class Symbol:
	""" Class which represents a single symbol, which is used in the symbol table to keep
		track of available variables. """

	def __init__(self, sym_type, sym_kind, sym_index):
		"""
		Initialize new symbol object
		:param sym_type: Symbol's type
		:param sym_kind: Symbol's kind
		:param sym_index: Symbol's index
		"""
		self.__type = sym_type  # int, String, etc
		self.__kind = sym_kind  # static, field, etc
		self.__index = sym_index  # some integer

	def get_type(self):
		"""
		:return: Symbol's type
		"""
		return self.__type

	def get_kind(self):
		"""
		:return: Symbol's kind
		"""
		return self.__kind

	def get_index(self):
		"""
		:return: Symbol's index
		"""
		return self.__index
