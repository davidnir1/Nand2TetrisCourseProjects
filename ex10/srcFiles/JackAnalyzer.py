# ============== Imports ==============

import sys
import os.path
from pathlib import Path
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
# ============= Constants =============
JACK_SUFFIX_LENGTH = -5
ERROR_OCCURRED = -1
XML_SUFFIX = ".xml"
FILE_DOES_NOT_EXIST = "Error: file {} does not exist."
NOT_A_VALID_ASM_FILE = "Error: file {} is not a valid jack file."
WRITE_PERMISSIONS = "w"
JACK_FILE_SUFFIX = ".jack"
XML_FILE_SUFFIX = ".xml"
T_XML_FILE_SUFFIX = "T.xml"


# ============= Functions =============

def run_single_analyze(input_file_path):
	"""
	Creates a tokenizer and a compilation engine which together compile the file in the given
	file path as a .xml file in the same directory as the given file.
	:param input_file_path: The path to the file we will translate.
	"""
	# Create a JackTokenizer from the Xxx.jack input file
	tokenizer = JackTokenizer(input_file_path)
	# Create an output file called Xxx.xml and prepare it for writing
	out_path = input_file_path[:JACK_SUFFIX_LENGTH] + XML_SUFFIX
	out_file = open(out_path, WRITE_PERMISSIONS)
	# Create a compilation engine using the tokenizer to compile into the output file
	engine = CompilationEngine(tokenizer, out_file)
	# Use the CompilationEngine to compile the input JackTokenizer into the output file
	engine.compile_class()


def write_output_t_file(input_file_path):
	"""
	Writes the token xml file, used for testing.
	:param input_file_path: The path to the input file/directory
	"""
	output_file_path = input_file_path.replace(JACK_FILE_SUFFIX, T_XML_FILE_SUFFIX)
	# write the translated version to a new file
	output_file = open(output_file_path, WRITE_PERMISSIONS)
	# magical stuff happens here and the file is now ready
	output_file.close()


def translate_file(arg):
	"""
	Translates single file in given file path.
	This method ignores files not ending with a .jack suffix and throws exceptions if the files
	do not exist (i.e given a path but it does not represent an actual .jack file).
	:param arg: The path to our file
	"""
	# check if the file indeed is a .jack file
	if not arg.endswith(JACK_FILE_SUFFIX):
		return
	# check if the .jack file even exists
	if not os.path.exists(arg):
		print(FILE_DOES_NOT_EXIST.format(arg))
		exit(ERROR_OCCURRED)
	# Import jack file into a data structure and compile it into xml file

	run_single_analyze(arg)


def handle_arg(arg):
	"""
	Receives a single argument given to the program, then checks if it is a file or a
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
	"""
	Operates on a given source, where source is either a file name of the form Xxx.jack
	or a directory name containing one or more such files.
	For each source Xxx.jack file, the analyzer goes through the following logic:
	1. Create a JackTokenizer from the Xxx.jack input file.
	2. Create an output file called Xxx.xml and prepare it for writing.
	3. Use the CompilationEngine to compile the input JackTokenizer into the output file.
	"""
	for i in range(1, len(sys.argv)):
		handle_arg(sys.argv[i])


# call the main function
main()
