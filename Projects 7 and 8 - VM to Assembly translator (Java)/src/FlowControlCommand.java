/**
 * This class represents a single flow control command, such as "goto".
 */
class FlowControlCommand extends VmCommand {

	// Error messages
	private static final String SYNTAX_PROBLEM_IN_LINE = "Syntax problem in flow control command: ";
	// General constants
	private static final int COMMAND = 0;
	private static final int LABEL_NAME = 1;
	private static final int EXPECTED_NUM_OF_WORDS = 2;
	private static final String SPACE_SEPARATOR = " ";
	private static final String LABEL_COMMAND = "label";
	private static final String GOTO_COMMAND = "goto";
	private static final String IF_GOTO_COMMAND = "if-goto";
	// Constant Assembly code
	private static final String UNCONDITIONAL_JUMP = "0;JMP\n";
	private static final String STACK_POINTER_DECREMENT = "@SP\t// SP--\nM=M-1\n";
	private static final String ASSIGN_D_FROM_STACK_TOP = "A=M\t// D=*SP\nD=M\n";
	private static final String JUMP_TO_D_IF_NOT_ZERO = "D;JNE\n";

	// Fields which are used throughout the operation of objects from this class
	private String line, prefix, targetLabel;
	private CommandType type;
	// we hold this field in case we want to support nested functions in the future
	private String parentFunction;

	/**
	 * Flow control possible commands
	 */
	private enum CommandType {
		LABEL,
		GOTO,
		IF_GOTO
	}

	/**
	 * Receives a single line and a function name and assign them to the current object.
	 * Line syntax is:
	 * components[0] = label/goto/if-goto
	 * components[1] = label name
	 *
	 * @param line         The current code line
	 * @param functionName The function name
	 * @throws VmSyntaxException in case line syntax is wrong
	 */
	FlowControlCommand(String line, String functionName) throws VmSyntaxException {
		this.line = line;
		String[] components = line.split(SPACE_SEPARATOR);
		if (components.length > EXPECTED_NUM_OF_WORDS)
			throw new VmSyntaxException(SYNTAX_PROBLEM_IN_LINE + line);
		this.prefix = components[COMMAND];
		this.targetLabel = components[LABEL_NAME]; // generate a function unique label name
		this.parentFunction = functionName;
		setCommandType();
	}

	/*
	 * Set the current command type based on the given prefix.
	 * Throws VmSyntaxException in case we encounter an unknown command type
	 */
	private void setCommandType() throws VmSyntaxException {
		switch (this.prefix) {
			case LABEL_COMMAND:
				this.type = CommandType.LABEL;
				break;
			case GOTO_COMMAND:
				this.type = CommandType.GOTO;
				break;
			case IF_GOTO_COMMAND:
				this.type = CommandType.IF_GOTO;
				break;
			default:
				throw new VmSyntaxException(SYNTAX_PROBLEM_IN_LINE + this.line);
		}
	}

	@Override
	AssemblyBlock getAssemblyBlock() {
		String assemblyCode = getAssemblyInstructions();
		return new AssemblyBlock(this.line, assemblyCode);
	}

	/*
	 * Assumes the current type is properly initiated because of constructor.
	 * Returns an assembly code string of the current command type (label, goto or if-goto)
	 */
	private String getAssemblyInstructions() {
		String output = "";
		switch (this.type) { //
			case LABEL:
				return getAssemblyLabelCode();
			case GOTO:
				return getAssemblyGotoCode();
			case IF_GOTO:
				return getAssemblyIfGotoCode();
		}
		return output;
	}

	/*
	 * Returns an assembly code string of the label label declaration:
	 * "(label)"
	 */
	private String getAssemblyLabelCode() {
		return "("+this.targetLabel + ")\n";
	}

	/*
	 * Returns an assembly code string of the goto command type:
	 * "@label"
	 * "0:JMP"
	 */
	private String getAssemblyGotoCode() {
		String output = "@" + this.targetLabel + "\n"; // the a instruction to point at the label
		output += UNCONDITIONAL_JUMP; // unconditional jump to the label
		return output;
	}

	/*
	 * Returns an assembly code string of the if-goto command type.
	 * The command pop the last item in the stack.
	 * if this item is not 0, we jump to the label, otherwise do nothing.
	 */
	private String getAssemblyIfGotoCode() {
		String output = STACK_POINTER_DECREMENT;
		output += ASSIGN_D_FROM_STACK_TOP;
		output += "@" + this.targetLabel + "\n"; // A = location of the target label
		output += JUMP_TO_D_IF_NOT_ZERO;
		return output;
	}
}
