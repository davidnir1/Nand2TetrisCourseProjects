# ============== Imports ==============

from srcFiles.Symbol import Symbol

# ============= Constants =============

STATIC_STR = "static"
LOCAL_STR = "local"
FIELD_STR = "field"
ARGUMENT_STR = "argument"
STATIC = 0
FIELD = 1
ARGUMENT = 2
LOCAL = 4

# ======= Class Implementation =======


class SymbolTable:
	""" Class which represents a symbol table, the idea is that in each scope we will have
	a symbol table which keeps track of the variables that exist in this scope and also
	allows access to variables which exist in outer scopes. """

	def __init__(self, previous=None):
		"""
		Initialize a new symbol table object
		:param previous:
		"""
		self.__prev = previous
		self.__dict = {}
		# this will keep track of how many symbols we have in each kind
		self.__kind_counter = {ARGUMENT_STR: 0, FIELD_STR: 0, LOCAL_STR: 0, STATIC_STR: 0}
		self.__symbol_count = 0

	def get_prev(self):
		"""
		:return: Previous
		"""
		return self.__prev

	def add_symbol(self, symbol_name, symbol_type, symbol_kind):
		""" creates a symbol from given inputs and adds it to the table """
		# since we assume valid input, we do not check that same symbol name already exists
		symbol_ind = self.__kind_counter.get(symbol_kind)
		# increment correct counter
		self.__kind_counter.update({symbol_kind: symbol_ind})
		new_sym = Symbol(symbol_type, symbol_kind, symbol_ind)
		self.__dict.update({symbol_name: new_sym})
		# increment total counter
		self.__kind_counter.update({symbol_kind: symbol_ind + 1})
		self.__symbol_count += 1

	def get_symbol(self, symbol_name):
		""" returns the symbol with the given name, if it doesn't exist in this table, it will
		ask the parent table to check for it.
		if there is no parent table, it returns None (should not happen since we assume
		valid inputs)"""
		out_sym = self.__dict.get(symbol_name)
		# this if covers the case: symbol exists in previous table
		if out_sym is None and self.__prev is not None:
			return self.__prev.get_symbol(symbol_name)
		# this line covers the cases: symbol exists HERE and symbol does not exist at all
		return out_sym

	def get_kind_count(self, symbol_kind):
		""" returns the number of symbols from a given kind"""
		return self.__kind_counter.get(symbol_kind)

	def get_total_symbol_count(self):
		""" returns the total number of items in our dictionary of symbols """
		return self.__symbol_count

	def print_self(self):
		"""
		Print table
		"""
		print("contents (total count: " + str(self.__symbol_count) + "):")
		for key in self.__dict.keys():
			val = self.__dict.get(key)
			tt = val.get_type()
			kk = val.get_kind()
			ii = str(val.get_index())
			print("\t" + key + " | " + tt + " | " + kk + " | " + ii)
