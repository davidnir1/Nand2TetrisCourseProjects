/**
 * This class represents a flow control command.
 */
class FlowControlCommand extends VmCommand {

	private static final String SYNTAX_PROBLEM_IN_LINE = "Syntax problem in flow control command: ";
	private static final int COMMAND = 0;
	private static final int LABEL_NAME = 1;
	private static final String LABEL_COMMAND = "label";
	private static final String GOTO_COMMAND = "goto";
	private static final String IF_GOTO_COMMAND = "if-goto";
	private String line, prefix, targetLabel;
	private CommandType type;
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
		String[] components = line.split(" ");
		if (components.length > 2)
			throw new VmSyntaxException(SYNTAX_PROBLEM_IN_LINE + line);
		this.prefix = components[COMMAND];
		this.targetLabel = components[LABEL_NAME]; // generate a function unique label name
		this.parentFunction = functionName;
				setCommandType();
	}

	/**
	 * Set the current command type based on the given prefix.
	 *
	 * @throws VmSyntaxException in case we encounter an unknown command type
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

	/**
	 * Assumes the current type is properly initiated because of constructor
	 *
	 * @return An assembly code string of the current command type (label, goto or if-goto)
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

	/**
	 * @return An assembly code string of the label label declaration:
	 * "(label)"
	 */
	private String getAssemblyLabelCode() {
		return "("+this.targetLabel + ")\n";
	}

	/**
	 * @return An assembly code string of the goto command type:
	 * "@label"
	 * "0:JMP"
	 */
	private String getAssemblyGotoCode() {
		String output = "@" + this.targetLabel + "\n"; // the a instruction to point at the label
		output += "0;JMP\n"; // unconditional jump to the label
		return output;
	}

	/**
	 * @return An assembly code string of the if-goto command type.
	 * The command pop the last item in the stack.
	 * if this item is not 0, we jump to the label, otherwise do nothing
	 * "@SP"
	 * "M=M-1"
	 * "A=M"
	 * "D=M"
	 * "@label"
	 * "D;JNE"
	 */
	private String getAssemblyIfGotoCode() {
		String output = "@SP\t// SP--\n";
		output += "M=M-1\n";
		output += "A=M\t// D=*SP\nD=M\n";
		output += "@" + this.targetLabel + "\n";
		output += "D;JNE\n";
		return output;
	}
}
