# ============== Imports ==============

import sys
import os.path
from pathlib import Path
from srcFiles.JackTokenizer import JackTokenizer
from srcFiles.CompilationEngine import CompilationEngine
from srcFiles.VMWriter import VMWriter
from enum import Enum

# ============= Constants =============

JACK_SUFFIX_LENGTH = -5
ERROR_OCCURRED = -1
FILE_DOES_NOT_EXIST = "Error: file {} does not exist."
NOT_A_VALID_ASM_FILE = "Error: file {} is not a valid jack file."
WRITE_PERMISSIONS = "w"
JACK_FILE_SUFFIX = ".jack"
VM_FILE_SUFFIX = ".vm"
XML_FILE_SUFFIX = ".xml"
T_XML_FILE_SUFFIX = "T.xml"


# ======== Translation Mode ===========


class Mode(Enum):
	"""
	This Enum class allows us to choose which translation mode we want.
	This means that we can add more translation methods if we want to compile jack files
	to other languages :)
	"""
	XML_ONLY = 0,
	VM_ONLY = 1,
	XML_AND_VM = 2


# ============= Functions =============

def run_single_analyze(input_file_path, translation_mode):
	"""
	For a given mode (language we want to translate to):
	Creates a tokenizer and a compilation engine which together compile the file in the given
	file path as a .vm or .xml file in the same directory as the given file.
	:param input_file_path: The path to the file we will translate.
	:param translation_mode: The mode we want to translate in
	"""
	if translation_mode == Mode.VM_ONLY:
		translate_xml(input_file_path)
	elif translation_mode == Mode.XML_ONLY:
		translate_vm(input_file_path)
	elif translation_mode == Mode.XML_AND_VM:
		translate_vm_xml(input_file_path)


# ============= Various Jack Compilation Methods ================


def translate_vm_xml(input_file_path):
	"""
	Compile given file path into vm file and xml file
	:param input_file_path: The path to our file
	"""
	translate_xml(input_file_path)
	translate_vm(input_file_path)


def translate_vm(input_file_path):
	"""
	Compile given file path into vm file
	:param input_file_path: The path to our file
	"""
	# Create a JackTokenizer from the Xxx.jack input file
	tokenizer = JackTokenizer(input_file_path)
	# Create an output file called Xxx.vm and prepare it for writing
	out_path = input_file_path[:JACK_SUFFIX_LENGTH] + VM_FILE_SUFFIX
	out_file = open(out_path, WRITE_PERMISSIONS)
	# Create a VMWriter object for the compilation engine
	vmw = VMWriter(out_file)
	# Create a compilation engine using the tokenizer to compile into the output file
	engine = CompilationEngine(tokenizer, out_file, vmw)
	# Use the CompilationEngine to compile the input JackTokenizer into the output file
	engine.compile_class()
	out_file.close()


def translate_xml(input_file_path):
	"""
	Compile given file path into xml file
	:param input_file_path: The path to our file
	"""
	# Create a JackTokenizer from the Xxx.jack input file
	tokenizer = JackTokenizer(input_file_path)
	# Create an output file called Xxx.xml and prepare it for writing
	out_path = input_file_path[:JACK_SUFFIX_LENGTH] + XML_FILE_SUFFIX
	out_file = open(out_path, WRITE_PERMISSIONS)
	# Create a compilation engine using the tokenizer to compile into the output file
	engine = CompilationEngine(tokenizer, out_file)
	# Use the CompilationEngine to compile the input JackTokenizer into the output file
	engine.xml_compile_class()
	out_file.close()


def translate_file(arg, translation_mode=Mode.VM_ONLY):
	"""
	Translates single file in given file path to specified target language output file.
	This method ignores files not ending with a .jack suffix and throws exceptions if the files
	do not exist (i.e given a path but it does not represent an actual .jack file).
	:param arg: The path to our file
	:param translation_mode: The language we want to translate to (default only VM)
	"""
	# check if the file indeed is a .jack file
	if not arg.endswith(JACK_FILE_SUFFIX):
		return
	# check if the .jack file even exists
	if not os.path.exists(arg):
		print(FILE_DOES_NOT_EXIST.format(arg))
		exit(ERROR_OCCURRED)
	# Import jack file into a data structure and compile it into xml file
	run_single_analyze(arg, translation_mode)


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
	2. Create an output file called Xxx.vm and prepare it for writing.
	3. Use the CompilationEngine to compile the input JackTokenizer into the output file.
	"""
	for i in range(1, len(sys.argv)):
		handle_arg(sys.argv[i])

# Call the main function
main()
