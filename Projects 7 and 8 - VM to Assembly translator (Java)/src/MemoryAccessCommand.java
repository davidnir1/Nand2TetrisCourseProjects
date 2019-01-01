import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;

/**
 * This class' objects represent memory access commands from VM files.
 * Currently there are two types of commands, PUSH and POP.
 */
public class MemoryAccessCommand extends VmCommand {

	private static final String SPACE_CHAR = " ";
	private static final String PUSH_PREFIX = "push";
	private static final String BAD_SYNTAX_PROBLEM = "Bad syntax - could not create an assembly block for ";
	private static final String BAD_SYNTAX_CONSTANT_POP = "Bad Syntax - popping into constant ";
	private static final String ERR_UNKNOWN_MEMORY_SEGMENT = "Unknown memory segment: ";
	private static final String BAD_SYNTAX = "Bad syntax: ";
	private static final int DEST_INDEX = 1;
	private static final int DATA_INDEX = 2;
	private static final int CORRECT_NUM_OF_COMPONENTS = 3;
	private static final String NEWLINE = "\n";
	private static final String PUSH_OUT_SUFFIX = "@SP\t// SP=D\nA=M\nM=D\n@SP\t//SP++\nM=M+1\n";

	// We define enums for the types to support any future command types we might add
	private enum CommandType {
		PUSH,
		POP
	}

	// This map is shared by all objects in this class, and is used to translate destinations into usable
	// pointers, so that it's easier and faster to write Assembly code.
	// This map is also initiated statically to conserve memory.
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
		String output = "@";
		boolean isPointer = !(dest.equals("pointer") || dest.equals("temp"));
		// prepare the value in dest to copy into the stack
		if (dest.equals("constant")) {
			output += data + " // D=" + data + "\n";
			output += "D=A\n";
		} else {
			if (dest.equals("static")) {
				ptr = getStaticFileName() + "." + data;
				output += ptr + "\t//D=" + ptr + "\n";
				output += "D=M\n";
			} else {
				ptr = destinationMap.get(dest);
				if (ptr == null)
					throw new VmSyntaxException(ERR_UNKNOWN_MEMORY_SEGMENT + this.dest);
				output += ptr + " // D=" + ptr + "+" + data + "\n";
				output += isPointer ? "D=M\n" : "D=A\n";
				output += "@" + data + "\n";
				output += "D=D+A\n";
				output += "A=D\nD=M\n";
			}
		}
		output += PUSH_OUT_SUFFIX;
		return output;
	}


	private String getPopCode(String dest, String index) throws VmSyntaxException {
		String ptr;
		// sp --
		String output = "@SP\t// SP--\nM=M-1\n@";
		boolean isPointer = !(dest.equals("pointer") || dest.equals("temp"));
		// throw an exception since this is not an allowed command
		if (dest.equals("constant"))
			throw new VmSyntaxException(BAD_SYNTAX_CONSTANT_POP + this.line + "\n");
			// put the address of dest in R13 to prepare for copying from the stack
		else {
			if (dest.equals("static")) {
				ptr = getStaticFileName() + "." + data;
				output += ptr + "\t//D=" + ptr + "\n";
				output += "D=A\n";
				output += "@R13\nM=D\n";
			} else {
				ptr = destinationMap.get(dest);
				if (ptr == null)
					throw new VmSyntaxException(ERR_UNKNOWN_MEMORY_SEGMENT + this.dest);
				output += ptr + "\t// R13=" + ptr + "+" + index + "\n";
				output += (isPointer) ? "D=M" : "D=A";
				output += "\n@" + index + "\nD=D+A\n@R13\nM=D\n";
			}
		}
		// actually copy the value into our destination
		output += "@SP\t//" + ptr + "=SP\nA=M\nD=M\n@R13\nA=M\nM=D\n";
		return output;
	}
}

