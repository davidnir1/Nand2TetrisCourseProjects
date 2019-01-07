import java.io.*;
import java.util.ArrayList;


/**
 * Class which is responsible for reading a file and extracting a list of VmCommand objects from it.
 */
public class Parser {

	private static final int ERROR_CODE = -1;
	private static final String ERR_READER_CLOSE = "Error closing file reader";
	private static final String COMMENT_PREFIX = "//";
	private static final String SYNTAX_ERROR_UNKNOWN_COMMAND = "Syntax error: unknown command ";
	private static final String ERR_READ_FILE = "ERROR: problem while reading from file ";
	private static final int NOT_FOUND_INDEX = -1;
	private static final String BUFFERED_READER_ERR = "ERROR: problem with buffered reader";

	private FileReader fileReader;
	private BufferedReader bufferedReader;
	private ArrayList<String> inputLines; // the lines read from file will go here
	private ArrayList<VmCommand> outputVmCommands; // the Vm commands extracted from the file
	private String currentFunction = "DEFAULT_PARENT_FUNC_NAME";
	private String currentFile = "DEFAULT_FILE";


	/**
	 * Basic constructor for the Parser class, initializes the data structures used by the class.
	 */
	public Parser() {
		this.inputLines = new ArrayList<>();
		this.outputVmCommands = new ArrayList<>();
	}

	/**
	 * Method which receives a path to a file and returns an array list of VmCommand objects, each
	 * representing a single VM command in the file.
	 *
	 * @param filePath The path to the file we are working on
	 * @return Array list of VmCommand objects
	 */
	public ArrayList<VmCommand> getVmCommandsFromFile(String filePath) {
		// returns the lines pulled from the file as an array list
		// load the file we are working on
		loadFile(filePath);
		// load the lines from the file into an array list
		extractLinesFromFile();
		// close the readers as we don't need them anymore
		closeReaders();
		// translate each line into a vm command
		try {
			generateVmCommandList(filePath);
		} catch (VmSyntaxException vmse) { // there was a syntax problem while parsing the file
			System.err.println(vmse.getMessage());
			System.exit(ERROR_CODE);
		}
		return this.outputVmCommands;
	}

	/*
	 * Method which receives a path to a file and populates this object's VmCommand list with VmCommand
	 * objects from the lines previously extracted from the file.
	 */
	private void generateVmCommandList(String filePath) throws VmSyntaxException {
		VmCommand currentCommand;
		for (String inputLine : this.inputLines) {
			// extract a VmCommand object from the current line
			currentCommand = createVmCommand(inputLine, filePath);
			this.outputVmCommands.add(currentCommand);
		}
	}

	/*
	 * Method which receives a line from a file and returns true if it represents a memory access command.
	 */
	private boolean MemoryAccess(String line) {
		return line.startsWith("push") || line.startsWith("pop");
	}

	/*
	 * Method which receives a line from a file and returns true if it represents an arithmetic or boolean
	 * command.
	 */
	private boolean ArithmeticBoolean(String line) {
		return line.startsWith("add") || line.startsWith("sub") || line.startsWith("neg") || line.startsWith("eq") ||
				line.startsWith("gt") || line.startsWith("lt") || line.startsWith("and") || line.startsWith("or") ||
				line.startsWith("not");
	}

	/*
	 * Method which receives a line from a file and returns true if it represents a flow control
	 * command.
	 */
	private boolean FlowControl(String line) {
		return line.startsWith("label") || line.startsWith("goto") || line.startsWith("if-goto");
	}

	private boolean FunctionCommand(String line){
		return line.startsWith("function") || line.startsWith("call") || line.startsWith("return");
	}




	/*
	 * Method which receives a line and returns a stripped version of it, removing anything which starts
	 * with "//" (comments) and whitespaces.
	 */
	private String removeCommentsAndSpaces(String line) {
		String output = line;
		int commentIndex = line.indexOf(COMMENT_PREFIX); // find the prefix of the comment
		if (commentIndex != NOT_FOUND_INDEX) // verify that there actually is a comment in this line
			output = line.substring(0, commentIndex);
		output = output.trim(); // remove any whitespaces
		return output;
	}

	private FunctionCommand getFunctionCommand(String line) throws VmSyntaxException{
		FunctionCommand output;
		output = new FunctionCommand(line);
		if(output.newFunction()) { // if a new function is declared
			this.currentFunction = this.currentFile+"."+output.getFuncName();
		}else
			output.setParentFunction(this.currentFunction);
		return output;
	}

	/*
	 * Method which receives a line from a file and the file's path, and returns a single VmCommand object
	 * which represents the VM command in the given line.
	 * Throws a VmSyntaxException if there's a syntax problem in the line.
	 */
	private VmCommand createVmCommand(String line, String filePath) throws VmSyntaxException {
		String trimmedLine = removeCommentsAndSpaces(line);
		// if it's a function related command
		if(FunctionCommand(trimmedLine))
			return getFunctionCommand(trimmedLine);
		// if it's a flow control command
		if (FlowControl(trimmedLine))
			return new FlowControlCommand(trimmedLine,this.currentFunction);
		// if it's a memory access command
		if (MemoryAccess(trimmedLine))
			return new MemoryAccessCommand(trimmedLine, filePath);
		// if it's an arithmetic boolean command
		if (ArithmeticBoolean(trimmedLine))
			return new ArithmeticBooleanCommand(trimmedLine, this.currentFunction);
		// throw an exception since we encountered an unknown syntax line
		throw new VmSyntaxException(SYNTAX_ERROR_UNKNOWN_COMMAND + line);
	}

	/*
	 * Method which uses the object's bufferedReader to read from the file it was initiated with and
	 * populates the array list of lines with lines from the file.
	 * Ignores whitespace lines and comment lines.
	 */
	private void extractLinesFromFile() {
		// this goes over the file and copies the strings it finds into the array list of strings we have
		if (this.bufferedReader == null) // sanity check
		{
			System.err.println(BUFFERED_READER_ERR);
			System.exit(ERROR_CODE);
		}
		String line, trimmedLine;
		try {
			// attempt to read a line from the file
			while ((line = bufferedReader.readLine()) != null) {
				trimmedLine = line.trim(); // remove leading and trailing whitespaces altogether
				// if it's not a comment or whitespace line
				if (!(trimmedLine.startsWith(COMMENT_PREFIX)) && !trimmedLine.isEmpty())
					this.inputLines.add(trimmedLine);
			}
		} catch (IOException ioe) {
			System.err.println(ERR_READ_FILE);
			System.exit(ERROR_CODE);
		}
	}

	/*
	 * Method which attempts to close the reader objects used by this object.
	 */
	private void closeReaders() {
		// closes the input streams
		try {
			if (this.bufferedReader != null) // this will close fileReader as well
				this.bufferedReader.close();
			else if (this.fileReader != null) // in case something weird happened and we have no bufferedReader
				this.fileReader.close();
		} catch (IOException ioe) {
			System.err.println(ERR_READER_CLOSE);
			System.exit(ERROR_CODE);
		}
	}

	/*
	 * Method which receives a path to a file and initiates the object's readers with it.
	 */
	private void loadFile(String filePath) {
		// get the name of the file
		File file = new File(filePath);
		this.currentFile = file.getName();
		this.currentFile = this.currentFile.substring(0,this.currentFile.indexOf(".vm"));
		// loads a file into the readers, after this is done we should have a buffered reader ready
		try {
			this.fileReader = new FileReader(filePath);
			this.bufferedReader = new BufferedReader(fileReader);
		} catch (IOException ioe) {
			System.err.println(ERR_READ_FILE + filePath);
		}

	}
}
