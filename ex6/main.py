# ============== Imports ==============

import sys
import os.path
from pathlib import Path

# ============= Constants =============

READ_PERMISSIONS = "r"
ERROR_OCCURRED = -1
FILE_DOES_NOT_EXIST = "Error: file {} does not exist."
NOT_A_VALID_ASM_FILE = "Error: file {} is not a valid asm file."
WRITE_PERMISSIONS = "w"
HACK_FILE_SUFFIX = ".hack"
ASM_FILE_SUFFIX = ".asm"
M_DEST = 'M'
D_DEST = 'D'
A_DEST = 'A'
RAM_PREFIX = "R"
THAT_SYMBOL = "THAT"
THIS_SYMBOL = "THIS"
ARG_SYMBOL = "ARG"
LCL_SYMBOL = "LCL"
SP_SYMBOL = "SP"
KBD_SYMBOL = "KBD"
SCREEN_SYMBOL = "SCREEN"
FIRST_FREE_RAM_REGISTER_INDEX = 16
GOTO_LABEL_SUFFIX = ')'
GOTO_LABEL_PREFIX = '('
DEF_UNASSIGNED_VAL = "-"
COMP_SEPERATOR = '='
JMP_SEPERATOR = ';'
SPACE = " "
NO_JUMP = "000"
USUAL_C_INST_BIN_PREFIX = "111"
SHIFT_INST_BIN_PREFIX = "101"
M_IS_DEST = 1
M_INDEX = 2
D_IS_DEST = 1
D_INDEX = 1
A_IS_DEST = 1
A_INDEX = 0
NUMBER_OF_BITS = 15
A_INST_BIN_LEFTMOST_BIT = "0"
A_INST_PREFIX = '@'
COMMENT_LINE_PREFIX = "//"
DEF_THAT_RAM = 4
DEF_THIS_RAM = 3
DEF_ARG_RAM = 2
DEF_LCL_RAM = 1
DEF_SP_RAM = 0
KBD_RAM = 24576
SCREEN_RAM = 16384
DEF_RAM_LOCATIONS = 16

# ============= Dictionaries =============

jmp_dict = {"JGT": "001", "JEQ": "010", "JGE": "011", "JLT": "100", "JNE": "101",
			"JLE": "110", "JMP": "111"}

comp_0_dict = {"D>>": "0010000", "D<<": "0110000", "A>>": "0000000",
			   "A<<": "0100000", "M>>": "1000000", "M<<": "1100000"}

comp_1_dict = {"0": "0101010", "1": "0111111", "-1": "0111010",
			   "D": "0001100", "A": "0110000", "!D": "0001101",
			   "!A": "0110001", "-D": "0001111", "-A": "0110011",
			   "D+1": "0011111", "A+1": "0110111", "D-1": "0001110",
			   "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
			   "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
			   "M": "1110000", "!M": "1110001", "-M": "1110011",
			   "M+1": "1110111", "M-1": "1110010", "D+M": "1000010",
			   "D-M": "1010011", "M-D": "1000111", "D&M": "1000000",
			   "D|M": "1010101"}


# ============= Functions =============

def remove_comments_from_line(stripped_line):
	"""Retrieves a single stripped line from a given file.
	If the line contain any comments (starts with \\ prefix),
	remove the comment and return the given line.

	Args:
		stripped_line: Stripped single line from the given file.
	Returns:
		The given line without any comments
	"""

	comment_index = stripped_line.find(COMMENT_LINE_PREFIX)
	if comment_index != -1:
		return stripped_line[:comment_index].rstrip()
	return stripped_line


def get_stripped_line_list(input_file_path):
	"""Retrieves a file input, strip each non empty/whitespace lines,
	and add the output lines to a list.
	If a single line contain a comment at the end, remove it.

	Args:
		input_file_path: Path to an asm file with assembly commands
	Returns:
		A list of command lines without any spaces or comments
	"""

	input_file = open(input_file_path, READ_PERMISSIONS)
	input_file_lines = []
	for line in input_file:
		stripped_line = line.strip()
		# If not a comment and not an empty line, remove all unnecessary text
		if not stripped_line.startswith(COMMENT_LINE_PREFIX) and len(stripped_line) > 0:
			stripped_line = remove_comments_from_line(stripped_line)
			input_file_lines.append(stripped_line)
	input_file.close()
	return input_file_lines


def create_symbol_table():
	"""Initialize a symbol table with known constant symbols in dictionary data structure.

	Returns:
		A dictionary with some known symbols
	"""

	symbol_table = {}
	for i in range(DEF_RAM_LOCATIONS):
		symbol_table.update({RAM_PREFIX + str(i): i})
	symbol_table.update({SCREEN_SYMBOL: SCREEN_RAM})
	symbol_table.update({KBD_SYMBOL: KBD_RAM})
	symbol_table.update({SP_SYMBOL: DEF_SP_RAM})
	symbol_table.update({LCL_SYMBOL: DEF_LCL_RAM})
	symbol_table.update({ARG_SYMBOL: DEF_ARG_RAM})
	symbol_table.update({THIS_SYMBOL: DEF_THIS_RAM})
	symbol_table.update({THAT_SYMBOL: DEF_THAT_RAM})
	return symbol_table


def translate_single_line(line, output_lines, symbol_table, memory_index):
	"""Retrieves a single assembly command and replace symbols with the memory numeric index,
	based on the given symbols dictionary. Then add it to the output lines file.

	Args:
		line: A single command of assembly code
		output_lines:  A list of translated commands
		symbol_table: A dictionary of known symbols in the code
		memory_index: The current free memory index
	Returns:
		The next free memory index
	"""

	if line.startswith(GOTO_LABEL_PREFIX):
		return memory_index
	elif line.startswith(A_INST_PREFIX):
		label = line[1:]
		if not label.isnumeric():
			if label not in symbol_table:
				symbol_table.update({label: memory_index})
				memory_index += 1
			output_lines.append(line.replace(label, str(symbol_table[label])))
		else:
			output_lines.append(line)
	else:
		output_lines.append(line)
	return memory_index


def get_a_instruction(assembly_line):
	"""Retrieves a single assembly A command (after symbols translated to memory indexes)
	and return the binary representation of it.

	Args:
		assembly_line: An assembly A command line (after symbols translated to memory indexes)
	Returns:
		The binary representation of the given assembly line
	"""

	# leftmost bit is 0 to represent an a instruction
	int_address = int(assembly_line[1:])
	# zfill(NUMBER_OF_BITS) is used to make sure the binary number is 15 bits
	binary_address = bin(int_address)[2:].zfill(NUMBER_OF_BITS)
	string_address = str(binary_address)
	binary_line = A_INST_BIN_LEFTMOST_BIT + string_address
	return binary_line


def translate_dest(dest):
	"""Retrieves a dest command, translate it and return the translated output

	Args:
		dest: A valid dest assembly command
	Returns:
		The binary representation of it
	"""

	bin_arr = [0, 0, 0]
	if A_DEST in dest:
		bin_arr[A_INDEX] = A_IS_DEST
	if D_DEST in dest:
		bin_arr[D_INDEX] = D_IS_DEST
	if M_DEST in dest:
		bin_arr[M_INDEX] = M_IS_DEST
	output = ""
	for i in bin_arr:
		output += str(i)
	return output


def translate_comp(comp):
	"""Retrieves a comp command (assumes it is a valid comp command),
	translate it and return the translated output

	Args:
		comp: A valid comp assembly command
	Returns:
		The binary representation of it
	"""

	output = comp_1_dict.get(comp)
	if output is None:
		return SHIFT_INST_BIN_PREFIX + comp_0_dict.get(comp)
	return USUAL_C_INST_BIN_PREFIX + output


def translate_jmp(jump):
	"""Retrieves a jump command, translate it and return the translated output

	Args:
		jump: A valid jump assembly command
	Returns:
		The binary representation of it
	"""

	output = jmp_dict.get(jump)
	if output is None:
		output = NO_JUMP
	return output


def get_binary_c_instruction(dest, comp, jmp):
	""" Translates a c instruction represented by the 3 parameters into a binary command and returns it.

	Args:
		dest: The destination value
		comp: The computation value
		jmp: The jump value
	Returns:
		The binary version of given command

	"""
	
	bin_dest = translate_dest(dest)
	bin_comp = translate_comp(comp)
	bin_jmp = translate_jmp(jmp)
	return bin_comp + bin_dest + bin_jmp


def get_c_instruction(assembly_line):
	"""Retrieves a single assembly C command (leftmost 3 bits are 1 to represent a c instruction)
	get rid of whitespaces, and return the binary representation of it.

	Args:
		assembly_line: An assembly C command line (after symbols translated to memory indexes)
	Returns:
		The binary representation of the given assembly line
	"""

	assembly_line = assembly_line.replace(SPACE, "")
	eq_index = assembly_line.find(COMP_SEPERATOR)
	smq_index = assembly_line.find(JMP_SEPERATOR)
	dest, comp, jump = (DEF_UNASSIGNED_VAL, DEF_UNASSIGNED_VAL, DEF_UNASSIGNED_VAL)
	if smq_index == -1:
		smq_index = len(assembly_line)
	else:
		jump = assembly_line[smq_index + 1:].strip()
	comp = assembly_line[eq_index + 1:smq_index].strip()
	if eq_index != -1:
		dest = assembly_line[:eq_index].strip()
	binary_line = get_binary_c_instruction(dest, comp, jump)
	return binary_line


def get_binary_instruction(assembly_line):
	"""Returns the binary version of the given assembly instruction, according to the instruction's type.
		
	Args:
		assembly_line: The line in assembly code which we are translating
	Returns:
		Binary version of the given assembly line
	"""

	if assembly_line.startswith(A_INST_PREFIX):
		return get_a_instruction(assembly_line)
	return get_c_instruction(assembly_line)


def translate_assembly_to_binary(assembly_lines):
	"""Translates the given list of lines (in assembly) into a list of lines in binary.

	Args:
		assembly_lines: A list of assembly lines
	Returns:
		A list of binary lines
	"""

	binary_lines = []
	for line in assembly_lines:
		binary_lines.append(get_binary_instruction(line))

	return binary_lines


def translate_lines(input_file_lines):
	"""Parses the given list of raw lines from the input file and returns a list of binary commands.

	Args:
		Input_file_lines: The raw lines from the input file
	Returns:
		List containing the binary version of the code in the given list
	"""

	# create an initialized symbol table (with the default symbols required)
	symbol_table = create_symbol_table()
	# populate the symbol table with all the labels in the file
	do_first_pass(input_file_lines, symbol_table)
	# do the second pass
	output_file_lines = do_second_pass(input_file_lines, symbol_table)
	return output_file_lines


def do_first_pass(input_file_lines, symbol_table):
	"""Updates the symbol table with all the labels in the file.

	Args:
		input_file_lines: List containing raw lines from the file
		symbol_table: Dictionary containing symbols and their index
	"""

	memory_index = 0
	for line in input_file_lines:
		if line.startswith(GOTO_LABEL_PREFIX) and line.endswith(GOTO_LABEL_SUFFIX):
			symbol_table.update({line[1:-1]: memory_index})
		else:
			memory_index += 1


def do_second_pass(input_file_lines, symbol_table):
	"""Goes over each line in the given list of raw lines and returns the binary version of the code in these lines.

	Args:
		input_file_lines: List of raw lines in the file
		symbol_table: The symbol table accumulated so far
	Returns:

	"""

	assembly_lines = []
	memory_index = FIRST_FREE_RAM_REGISTER_INDEX
	for line in input_file_lines:
		memory_index = translate_single_line(line, assembly_lines, symbol_table, memory_index)
	return translate_assembly_to_binary(assembly_lines)


def write_output_file(input_file_path, output_file_lines):
	"""Retrieves the input file path and create a new hack file,
	in the same path with the same name (only different extension)
	Then it print the output binary code to the file and close it.

	Args:
		input_file_path: The path of the input asm file
		output_file_lines: The output binary code to write into the output file.
	"""

	output_file_path = input_file_path.replace(ASM_FILE_SUFFIX, HACK_FILE_SUFFIX)
	# write the translated version to a new file
	output_file = open(output_file_path, WRITE_PERMISSIONS)
	for line in output_file_lines:
		output_file.write(line + "\n")
	output_file.close()


def translate_file(arg):
	"""Translates the file in the given path, exits with error message and code if there is a problem
	
	Args: 
		arg: The path to the file
	"""
	# check if the file indeed is a .asm file
	if not arg.endswith(ASM_FILE_SUFFIX):
		print(NOT_A_VALID_ASM_FILE.format(arg))
		exit(ERROR_OCCURRED)
	# check if the .asm file even exists
	if not os.path.exists(arg):
		print(FILE_DOES_NOT_EXIST.format(arg))
		exit(ERROR_OCCURRED)
	# read from the file into a data structure
	input_file_lines = get_stripped_line_list(arg)
	# translate the lines we gathered into binary lines
	output_file_lines = translate_lines(input_file_lines)
	# generate a new file path with ".asm" replaced by ".hack"
	write_output_file(arg, output_file_lines)

def handle_arg(arg):
	"""Receives a single argument given to the program, then checks if it is a file or a
	directory and handles it accordingly (if it is a directory, it will translate all the files
	inside it and if it is a file, it will translate only the file).

	:param arg: The single argument we are handling at the moment.
	"""
	if os.path.isdir(arg):
		for file in os.listdir(arg):
			file_path = str(Path(arg) / file)
			if not os.path.isdir(file_path):
				translate_file(file_path)
	else:
		translate_file(arg)

def main():
	"""Retrieves (through argv) an input asm file with an assembly code,
	read it to a python data structure and translate it to binary code.
	The output binary code is written to an output file in the same path.
	"""

	for i in range(1, len(sys.argv)):
		handle_arg(sys.argv[i])


if __name__ == '__main__':
	main()
