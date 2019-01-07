WRITE_PERMISSIONS = "w"

class VMWriter:
	"""
	Emits VM commands into a file, using the VM command syntax.
	"""

	def __init__(self, output_file):
		"""
		Receives output file object.
		:param output_file: Output file object
		"""
		self.__file = output_file

	def __write_line(self, line, end = "\n"):
		"""
		Writes a given line to output file.
		:param line: Wanted line
		:param end: Wanted char to add at the end of the line
		"""
		self.__file.write(line + end)

	def write_push(self, segment, index):
		"""
		Writes a VM push command.
		:param segment: The segment to which we want to push the value
		:param index: Wanted segment's index
		"""
		if segment == "field":
			segment = "this"
		self.__write_line("push " + segment + " " + str(index))

	def write_pop(self, segment, index):
		"""
		Writes a VM pop command.
		:param segment: The segment from which we want to pop the value
		:param index: Wanted segment's index
		"""
		if segment == "field":
			segment = "this"
		self.__write_line("pop " + segment + " " + str(index))

	def write_arithmetic(self, command):
		"""
		Writes a VM arithmetic command.
		:param command: Wanted command to write
		"""
		self.__write_line(command)

	def write_label(self, label):
		"""
		Writes a VM label command.
		:param label: Wanted label to write
		"""
		self.__write_line("label " + label)

	def write_goto(self, label):
		"""
		Writes a VM goto command.
		:param label: Wanted goto command to write
		"""
		self.__write_line("goto " + label)

	def write_if(self, label):
		"""
		Writes a VM If-goto command.
		:param label: Wanted if-goto command to write
		"""
		self.__write_line("if-goto " + label)

	def write_call(self, name, nargs):
		"""
		Writes a VM call command.
		:param name: subroutine's name
		:param nargs: Number of arguments
		"""
		self.__write_line("call " + name + " " + str(nargs))

	def write_function(self, name, nlocals):
		"""
		Writes a VM function command.
		:param name: function's name
		:param nlocals: Number of local variables
		"""
		self.__write_line("function " + name + " " + str(nlocals))

	def write_return(self):
		"""
		Writes a VM return command.
		"""
		self.__write_line("return")

	def write_comment(self, str):
		"""
		writes a VM comment.
		:param str: The comment string
		"""
		#self.__write_line("// " + str )

	def write_push_true(self):
		"""
		writes a VM true representation.
		"""
		self.__write_line("push constant 0\nnot")

	def write_push_false(self):
		"""
		writes a VM false representation.
		"""
		self.__write_line("push constant 0")

	def write_push_null(self):
		"""
		writes a VM null representation.
		"""
		self.__write_line("push constant 0")

	def write_push_this(self):
		"""
		writes a VM push this command.
		"""
		self.__write_line("push pointer 0")

	def close(self):
		"""
		Closes the output file.
		"""
		self.__file.close()
