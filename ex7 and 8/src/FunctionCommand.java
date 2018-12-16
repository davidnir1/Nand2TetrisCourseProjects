/**
 * This class represents a function command.
 */
class FunctionCommand extends VmCommand {

	/*
	todo This class now creates objects which hold our data properly
	todo The objects also hold the correct type enum
	todo We need to create translation methods (into assemblyBlocks)
	todo use "usefulNotes" carefully, this is extremely confusing
	todo once this is complete, we can run the tests in the "FunctionCalls"
	todo WOLOLO~~...... AIOOOO-IOOO~~IOOOO.....WOLOLO......
	 */

	private static final String SYNTAX_PROBLEM_IN_LINE = "Problem with syntax in line ";
	private static final String PUSH_D_INTO_STACK = "@SP\nA=M\nM=D\n@SP\t// SP++\nM=M+1\n";
	private static final int RETURN_STATEMENT = 1;
	private static final int DECLARATION_OR_CALL = 3;
	private static final int FUNC_NAME = 1;
	private static final int N_ARGS = 2;
	private static final String RETURN_COMMAND = "return";
	private static final String FUNCTION_COMMAND = "function";
	private static final String CALL_COMMAND = "call";
	private String line; // Original code line
	private String funcName; // Function name
	private String nArgs; // The number in the end of the command
	// note - if the command is a return, funcName and nArgs stay unused
	private String callerFunc;
	private CommandType type;

	/**
	 * Functions possible commands
	 */
	private enum CommandType {
		DECLARATION,
		CALL,
		RETURN
	}

	/**
	 * Receives a single line and assign it to the current object.
	 * Line syntax is:
	 * 3 components means it's a declaration or a call
	 * 1 component means it's a return
	 *
	 * @param line Original line code
	 * @throws VmSyntaxException If given line didn't match any known type
	 */
	FunctionCommand(String line) throws VmSyntaxException {
		this.line = line; // assumes valid input
		String[] components = line.split(" ");
		setCommandType(components);
		if (components.length == 3) { // if it's a call or declaration
			this.funcName = components[FUNC_NAME];
			this.nArgs = components[N_ARGS];
		}
	}

	/**
	 * @param callerFunc Caller function
	 */
	void setParentFunction(String callerFunc) {
		this.callerFunc = callerFunc;
	}

	/**
	 * @return True if current line is a function declaration
	 */
	boolean newFunction() {
		return this.type == CommandType.DECLARATION;
	}

	/**
	 * @return Function name
	 */
	String getFuncName() {
		return this.funcName;
	}

	/**
	 * Receives a line components array, and assign current command type based on it first index.
	 *
	 * @param components An array of command line components
	 * @throws VmSyntaxException If given line didn't match any known type
	 */
	private void setCommandType(String[] components) throws VmSyntaxException {
		switch (components.length) {
			case RETURN_STATEMENT:
				if (components[0].equals(RETURN_COMMAND)) {
					this.type = CommandType.RETURN;
					return;
				}
			case DECLARATION_OR_CALL:
				if (components[0].equals(FUNCTION_COMMAND)) {
					this.type = CommandType.DECLARATION;
					return;
				} else if (components[0].equals(CALL_COMMAND)) {
					this.type = CommandType.CALL;
					return;
				}
		}
		// the line didn't match any known type, so throw an exception
		throw new VmSyntaxException(SYNTAX_PROBLEM_IN_LINE + this.line);
	}

	@Override
	AssemblyBlock getAssemblyBlock() throws VmSyntaxException {
		switch (this.type) {
			case DECLARATION:
				return new AssemblyBlock(this.line, getDeclarationCode());
			case CALL:
				return new AssemblyBlock(this.line, getCallCode());
			case RETURN:
				return new AssemblyBlock(this.line, this.getReturnCode());
		}
		// this line should be unreachable
		throw new VmSyntaxException(SYNTAX_PROBLEM_IN_LINE + line);
	}

	/**
	 * This function returns a translation of a function declaration.
	 * The pseudo code for command "function myFunc nArgs" will be:
	 * Repeat nArgs times:
	 * push 0
	 *
	 * @return String holding a translation of a declaration command into assembly
	 */
	private String getDeclarationCode() {
		String loopLabel = this.funcName + "$LOOP_" + counter;
		String endLoopLabel = this.funcName + "$END_LOOP_" + counter++;
		// (f)
		String output = "(" + this.funcName + ")\n";
		// R13 = nArgs
		output += "@" + this.nArgs + "\t// R13=" + this.nArgs + "\nD=A\n@R13\nM=D\n";
		// loop label
		output += "(" + loopLabel + ")\n";
		// R13 --
		output += "@R13\t// R13--\nM=M-1\nD=M\n";
		// check end loop, jump if needed
		output += "@" + endLoopLabel + "\t// loop ended\nD;JLT\n";
		// push 0 to stack
		output += "D=0\t// push 0\n@SP\nA=M\nM=D\n";
		// SP++
		output += "@SP\t// SP++\nM=M+1\n";
		// Jump to next iteration
		output += "@" + loopLabel + "\t// perform another iteration\n0;JMP\n";
		// end of loop label
		output += "(" + endLoopLabel + ")\n";
		return output;
	}

	/**
	 * Function which returns an assembly translation of a call command.
	 *
	 * @return String with assembly translation of a call command
	 */
	private String getCallCode() {
		String returnLabel = this.funcName + "$" + "RETURN_LABEL_" + counter++;
		// D = return label
		String output = "@" + returnLabel + "\t// push return label\nD=A\n";
		// push D
		output += PUSH_D_INTO_STACK;
		// D = LCL
		output += "@LCL\t// push LCL\nD=M\n";
		// push D
		output += PUSH_D_INTO_STACK;
		// D = ARG
		output += "@ARG\t// push ARG\nD=M\n";
		// push D
		output += PUSH_D_INTO_STACK;
		// D = THIS
		output += "@THIS\t// push THIS\nD=M\n";
		// push D
		output += PUSH_D_INTO_STACK;
		// D = THAT
		output += "@THAT\t// push THAT\nD=M\n";
		// push D
		output += PUSH_D_INTO_STACK;
		// ARG = SP-nArgs
		output += "@SP\t// ARG = SP-" + this.nArgs + "-5\nD=M\n@" + this.nArgs + "\nD=D-A\n";
		// ARG = ARG-5
		output += "@5\nD=D-A\n@ARG\nM=D\n";
		// LCL = SP
		output += "@SP\t// LCL=SP\nD=M\n@LCL\nM=D\n";
		// jump to function label
		output += "@" + this.funcName + "\t// goto " + this.funcName + "\n0;JMP\n";
		// create a return label
		output += "(" + returnLabel + ")\n";
		return output;
	}

	/**
	 * Function which returns an assembly translation of a return command.
	 *
	 * @return String with assembly translation of a return command
	 */
	private String getReturnCode() {
		// FRAME (Temp Var R13) = LCL
		String output = "@LCL\nD=M\n@R13\nM=D\n";
		// RET (TEMP Var R14) = *(FRAME-5)
		output += "@5\nD=A\n@R13\nD=M-D\nA=D\nD=M\n@R14\nM=D\n";
		// *ARG = pop()
		output += "@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n";
		// SP = ARG + 1
		output += "@ARG\nD=M+1\n@SP\nM=D\n";
		// THAT = *(FRAME-1)
		output += "@1\nD=A\n@R13\nD=M-D\nA=D\nD=M\n@THAT\nM=D\n";
		// THIS = *(FRAME-2)
		output += "@2\nD=A\n@R13\nD=M-D\nA=D\nD=M\n@THIS\nM=D\n";
		// ARG = *(FRAME-3)
		output += "@3\nD=A\n@R13\nD=M-D\nA=D\nD=M\n@ARG\nM=D\n";
		// LCL = *(FRAME-4)
		output += "@4\nD=A\n@R13\nD=M-D\nA=D\nD=M\n@LCL\nM=D\n";
		// goto *(FRAME-5)
		output += "@R14\nA=M\n0;JMP\n";
		return output;
	}

}