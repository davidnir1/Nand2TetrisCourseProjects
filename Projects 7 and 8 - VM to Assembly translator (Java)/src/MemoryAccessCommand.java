import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;

/**
 * This class' objects represent memory access commands from VM files.
 * Currently there are two types of commands, PUSH and POP.
 */
public class MemoryAccessCommand extends VmCommand {

	// Error messages
	private static final String BAD_SYNTAX_PROBLEM = "Bad syntax - could not create an assembly block for ";
	private static final String BAD_SYNTAX_CONSTANT_POP = "Bad Syntax - popping into constant ";
	private static final String ERR_UNKNOWN_MEMORY_SEGMENT = "Unknown memory segment: ";
	private static final String BAD_SYNTAX = "Bad syntax: ";
	// General constants
	private static final String SPACE_CHAR = " ";
	private static final String PUSH_PREFIX = "push";
	private static final int DEST_INDEX = 1;
	private static final int DATA_INDEX = 2;
	private static final int CORRECT_NUM_OF_COMPONENTS = 3;
	private static final String NEWLINE = "\n";
	// Special destinations
	private static final String POINTER_DEST = "pointer";
	private static final String TEMP_DEST = "temp";
	private static final String CONST_DEST = "constant";
	private static final String STATIC_DEST = "static";
	// Constant assembly commands
	private static final String PUSH_OUT_SUFFIX = "@SP\t// SP=D\nA=M\nM=D\n@SP\t//SP++\nM=M+1\n";
	private static final String A_INST_SUFF = "@";
	private static final String ASSIGN_D_FROM_MEM = "D=M\n";
	private static final String ASSIGN_D_FROM_CONST = "D=A\n";
	private static final String INC_D_BY_CONST = "D=D+A\n";
	private static final String ASSIGN_D_FROM_A_ADDRESS = "A=D\nD=M\n";
	private static final String DECREMENT_STACK_POINTER = "@SP\t// SP--\nM=M-1\n@";
	private static final String ASSIGN_R13_FROM_D = "@R13\nM=D\n";
	private static final String COPY_STACK_TOP_INTO_ADDRESS_STORED_IN_R13 = "A=M\nD=M\n@R13\nA=M\nM=D\n";

	// We define enums for the types to support any future command types we might add
	private enum CommandType {
		PUSH,
		POP
	}

	// This map is shared by all objects in this class, and is used to translate destinations into usable
	// pointers, so that it's easier and faster to write Assembly code.
	// This map is also initiated statically to conserve memory and shorten run time.
	private static HashMap<String, String> destinationMap;
	static {
		destinationMap = new HashMap<>();
		destinationMap.put("local", "LCL");
		destinationMap.put("argument", "ARG");
		destinationMap.put("this", "THIS");
		destinationMap.put("that", "THAT");
		destinationMap.put("pointer", "3");
		destinationMap.put("temp", "5");
	}

	private CommandType type; // the type of command
	private String line; // this is a copy of the original line, used for documentation in translation
	private String dest; // this will be the destination
	private String data; // this will be the data
	private String filePath; // this is used for static

	/**
	 * Constructor for the MemoryAccessCommand class.
	 * Receives a line and a file's path and initializes everything accordingly.
	 *
	 * @param line     The actual VM code from the file
	 * @param filePath The file's path (used in commands with static destinations)
	 * @throws VmSyntaxException When there is some unknown syntax in the command
	 */
	public MemoryAccessCommand(String line, String filePath) throws VmSyntaxException {
		this.line = line;
		this.filePath = filePath;
		// break up the line into the 3 components we need
		String[] components = line.split(SPACE_CHAR);
		// case: the line's syntax is unfamiliar, meaning it has more than 3 parts.
		if (components.length != CORRECT_NUM_OF_COMPONENTS)
			throw new VmSyntaxException(BAD_SYNTAX + line);
		//Note: components[0] is push or pop
		//components[1] should be the destination (for example "constant")
		//components[2] should be the data
		this.dest = components[DEST_INDEX];
		this.data = components[DATA_INDEX];
		setType(); // set this object's type according to the inputs
	}

	/*
	 * Method which sets the type of this object according to it's fields.
	 */
	private void setType() {
		if (this.line.startsWith(PUSH_PREFIX)) {
			this.type = CommandType.PUSH;
		} else
			this.type = CommandType.POP;
	}

	@Override
	public AssemblyBlock getAssemblyBlock() throws VmSyntaxException {

		switch (this.type) {
			case PUSH:
				return new AssemblyBlock(this.line, getPushCode(this.dest, this.data));
			case POP:
				return new AssemblyBlock(this.line, getPopCode(this.dest, this.data));
		}
		throw new VmSyntaxException(BAD_SYNTAX_PROBLEM + this.line + NEWLINE);
	}

	/*
	 * Method which returns the correct pointer created from the file's name.
	 * It is used when translating a static destination command.
	 */
	private String getStaticFileName() {
		Path fPath = Paths.get(this.filePath);
		String fileName = fPath.getFileName().toString();
		// check if the file has an extension and remove it if so
		int extensionIndex = fileName.lastIndexOf('.');
		if (extensionIndex >= 0)
			fileName = fileName.substring(0, extensionIndex);
		return fileName;
	}

	/*
	 * Method which receives a destination and data input and generates Assembly code which translates into
	 * a push command.
	 */
	private String getPushCode(String dest, String data) throws VmSyntaxException {
		String ptr;
		String output = A_INST_SUFF;
		boolean isPointer = !(dest.equals(POINTER_DEST) || dest.equals(TEMP_DEST));
		// prepare the value in dest to copy into the stack
		if (dest.equals(CONST_DEST)) {
			output += data + " // D=" + data + "\n";
			output += ASSIGN_D_FROM_CONST;
		} else {
			if (dest.equals(STATIC_DEST)) {
				ptr = getStaticFileName() + "." + data;
				output += ptr + "\t//D=" + ptr + "\n";
				output += ASSIGN_D_FROM_MEM;
			} else {
				ptr = destinationMap.get(dest);
				if (ptr == null)
					throw new VmSyntaxException(ERR_UNKNOWN_MEMORY_SEGMENT + this.dest);
				output += ptr + " // D=" + ptr + "+" + data + "\n";
				output += isPointer ? ASSIGN_D_FROM_MEM : ASSIGN_D_FROM_CONST;
				output += A_INST_SUFF + data + "\n";
				output += INC_D_BY_CONST;
				output += ASSIGN_D_FROM_A_ADDRESS;
			}
		}
		output += PUSH_OUT_SUFFIX;
		return output;
	}

	/*
	 * Method which receives a destination and data input and generates Assembly code which translates into
	 * a pop command.
	 */
	private String getPopCode(String dest, String index) throws VmSyntaxException {
		String ptr;
		// sp --
		String output = DECREMENT_STACK_POINTER;
		boolean isPointer = !(dest.equals(POINTER_DEST) || dest.equals(TEMP_DEST));
		// throw an exception since this is not an allowed command
		if (dest.equals(CONST_DEST))
			throw new VmSyntaxException(BAD_SYNTAX_CONSTANT_POP + this.line + NEWLINE);
			// put the address of dest in R13 to prepare for copying from the stack
		else {
			if (dest.equals(STATIC_DEST)) {
				ptr = getStaticFileName() + "." + data;
				output += ptr + "\t//D=" + ptr + "\n";
				output += ASSIGN_D_FROM_CONST;
				output += ASSIGN_R13_FROM_D;
			} else {
				ptr = destinationMap.get(dest);
				if (ptr == null)
					throw new VmSyntaxException(ERR_UNKNOWN_MEMORY_SEGMENT + this.dest);
				output += ptr + "\t// R13=" + ptr + "+" + index + "\n";
				output += (isPointer) ? ASSIGN_D_FROM_MEM : ASSIGN_D_FROM_CONST;
				output += A_INST_SUFF + index + "\n"+INC_D_BY_CONST+ASSIGN_R13_FROM_D;
			}
		}
		// actually copy the value into our destination (the destination's address is stored inside R13)
		output += "@SP\t//" + ptr + "=SP\n"+ COPY_STACK_TOP_INTO_ADDRESS_STORED_IN_R13;
		return output;
	}
}

