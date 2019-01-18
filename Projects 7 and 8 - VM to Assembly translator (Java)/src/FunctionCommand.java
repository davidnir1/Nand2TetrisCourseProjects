/**
 * This class represents a function command, such as "return" or "call".
 */
class FunctionCommand extends VmCommand {

	// Error message
	private static final String SYNTAX_PROBLEM_IN_LINE = "Problem with syntax in line ";
	// General constants
	private static final int RETURN_STATEMENT = 1;
	private static final int DECLARATION_OR_CALL = 3;
	private static final int FUNC_NAME = 1;
	private static final int N_ARGS = 2;
	private static final int COMMAND_TYPE_COMPONENT = 0;
	private static final String RETURN_COMMAND = "return";
	private static final String FUNCTION_COMMAND = "function";
	private static final String CALL_COMMAND = "call";
	private static final String SPACE_SEPARATOR = " ";
	// Constant Assembly code
	private static final String FUNC_LOOP_LABEL = "$LOOP_";
	private static final String FUNC_END_LOOP_LABEL = "$END_LOOP_";
	private static final String A_INST_PREFIX = "@";
	private static final String ASSIGN_R13_FROM_A = "\nD=A\n@R13\nM=D\n";
	private static final String PUSH_D_INTO_STACK = "@SP\nA=M\nM=D\n@SP\t// SP++\nM=M+1\n";
	private static final String DECREMENT_R13_BY_ONE = "@R13\t// R13--\nM=M-1\nD=M\n";
	private static final String JUMP_IF_D_LESS_THAN_ZERO = "D;JLT\n";
	private static final String END_LOOP_COMMENT = "\t// loop ended\n";
	private static final String PUSH_ZERO_TO_STACK = "D=0\t// push 0\n@SP\nA=M\nM=D\n";
	private static final String INCREMENT_STACK_POINTER = "@SP\t// SP++\nM=M+1\n";
	private static final String UNCONDITIONAL_JUMP = "0;JMP\n";
	private static final String NEXT_ITERATION_COMMENT = "\t// perform another iteration\n";
	private static final String FUNC_RETURN_LABEL = "$RETURN_LABEL_";
	private static final String ASSIGN_D_FROM_A = "D=A\n";
	private static final String PUSH_RETURN_LABEL_COMMENT = "\t// push return label\n";
	private static final String ASSIGN_D_FROM_LCL_ADDRESS = "@LCL\t// push LCL\nD=M\n";
	private static final String ASSIGN_D_FROM_ARG_ADDRESS = "@ARG\t// push ARG\nD=M\n";
	private static final String ASSIGN_D_FROM_THIS_ADDRESS = "@THIS\t// push THIS\nD=M\n";
	private static final String ASSIGN_D_FROM_THAT_ADDRESS = "@THAT\t// push THAT\nD=M\n";
	private static final String SP_MINUS_NARGS_PREFIX = "@SP\t// ARG = SP-";
	private static final String SP_MINUS_NARGS_SUFFIX = "-5\n";
	private static final String ASSIGN_D_FROM_M = "D=M\n";
	private static final String DECREMENT_D_BY_A = "D=D-A\n";
	private static final String DECREMENT_ARG_BY_5 = "@5\nD=D-A\n@ARG\nM=D\n";
	private static final String ASSIGN_LCL_BY_STACK_POINTER = "@SP\t// LCL=SP\nD=M\n@LCL\nM=D\n";
	private static final String GOTO_COMMENT = "\t// goto ";
	private static final String ASSIGN_R13_FROM_LCL = "@LCL\nD=M\n@R13\nM=D\n";
	private static final String ASSIGN_R14_FROM_LAST_FRAME_END_ADDRESS = "@5\nD=A\n@R13\nD=M-D\nA=D\nD=M\n@R14\nM=D\n";
	private static final String POP_STACK_INTO_ARG_ADDRESS = "@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n";
	private static final String ASSIGN_STACK_FROM_ARG_PLUS1 = "@ARG\nD=M+1\n@SP\nM=D\n";
	private static final String ASSIGN_THAT_CURRENT_FRAME_INDEX = "@1\nD=A\n@R13\nD=M-D\nA=D\nD=M\n@THAT\nM=D\n";
	private static final String ASSIGN_THIS_CURRENT_FRAME_INDEX = "@2\nD=A\n@R13\nD=M-D\nA=D\nD=M\n@THIS\nM=D\n";
	private static final String ASSIGN_ARG_CURRENT_FRAME_INDEX = "@3\nD=A\n@R13\nD=M-D\nA=D\nD=M\n@ARG\nM=D\n";
	private static final String ASSIGN_LCL_CURRENT_FRAME_INDEX = "@4\nD=A\n@R13\nD=M-D\nA=D\nD=M\n@LCL\nM=D\n";
	private static final String JUMP_TO_THE_TARGET_FRAME = "@R14\nA=M\n0;JMP\n";
	private static final String R13_NARGS_COMMENT = "\t// R13=";

	private String line; // Original code line
	private String funcName; // Function name
	private String nArgs; // The number in the end of the command
	// callerFunc is maintained in case we want to support nested functions in the future
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
		String[] components = line.split(SPACE_SEPARATOR);
		setCommandType(components);
		if (components.length == 3) { // if it's a call or declaration, we maintain funcName
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

	/*
	 * Receives a line components array, and assign current command type based on it first index.
	 *
	 * Param components is an array of command line components.
	 * Throws VmSyntaxException if given line didn't match any known type.
	 */
	private void setCommandType(String[] components) throws VmSyntaxException {
		String commandType = components[COMMAND_TYPE_COMPONENT];
		switch (components.length) {
			case RETURN_STATEMENT:
				if (commandType.equals(RETURN_COMMAND)) {
					this.type = CommandType.RETURN;
					return;
				}
			case DECLARATION_OR_CALL:
				if (commandType.equals(FUNCTION_COMMAND)) {
					this.type = CommandType.DECLARATION;
					return;
				} else if (commandType.equals(CALL_COMMAND)) {
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

	/*
	 * This function returns a translation of a function declaration.
	 * The pseudo code for command "function myFunc nArgs" will be:
	 * Repeat nArgs times:
	 * push 0
	 * Returns string holding a translation of a declaration command into assembly.
	 */
	private String getDeclarationCode() {
		String loopLabel = this.funcName + FUNC_LOOP_LABEL + counter;
		String endLoopLabel = this.funcName + FUNC_END_LOOP_LABEL + counter++;
		// (f)
		String output = "(" + this.funcName + ")\n";
		// R13 = nArgs
		output += A_INST_PREFIX + this.nArgs + R13_NARGS_COMMENT + this.nArgs + ASSIGN_R13_FROM_A;
		// loop label
		output += "(" + loopLabel + ")\n";
		// R13 --
		output += DECREMENT_R13_BY_ONE;
		// check end loop, jump if needed
		output += A_INST_PREFIX + endLoopLabel + END_LOOP_COMMENT + JUMP_IF_D_LESS_THAN_ZERO;
		// push 0 to stack
		output += PUSH_ZERO_TO_STACK;
		// SP++
		output += INCREMENT_STACK_POINTER;
		// Jump to next iteration
		output += A_INST_PREFIX + loopLabel + NEXT_ITERATION_COMMENT + UNCONDITIONAL_JUMP;
		// create end of loop label
		output += "(" + endLoopLabel + ")\n";
		return output;
	}

	/*
	 * Function which returns an assembly translation of a call command.
	 * Returns string with assembly translation of a call command.
	 */
	private String getCallCode() {
		String returnLabel = this.funcName + FUNC_RETURN_LABEL + counter++;
		// D = return label
		String output = A_INST_PREFIX + returnLabel + PUSH_RETURN_LABEL_COMMENT + ASSIGN_D_FROM_A;
		// push D
		output += PUSH_D_INTO_STACK;
		// D = LCL
		output += ASSIGN_D_FROM_LCL_ADDRESS;
		// push D
		output += PUSH_D_INTO_STACK;
		// D = ARG
		output += ASSIGN_D_FROM_ARG_ADDRESS;
		// push D
		output += PUSH_D_INTO_STACK;
		// D = THIS
		output += ASSIGN_D_FROM_THIS_ADDRESS;
		// push D
		output += PUSH_D_INTO_STACK;
		// D = THAT
		output += ASSIGN_D_FROM_THAT_ADDRESS;
		// push D
		output += PUSH_D_INTO_STACK;
		// ARG = SP-nArgs
		output += SP_MINUS_NARGS_PREFIX + this.nArgs + SP_MINUS_NARGS_SUFFIX;
		output += ASSIGN_D_FROM_M +A_INST_PREFIX + this.nArgs +"\n"+ DECREMENT_D_BY_A;
		// ARG = ARG-5
		output += DECREMENT_ARG_BY_5;
		// LCL = SP
		output += ASSIGN_LCL_BY_STACK_POINTER;
		// jump to function label
		output += A_INST_PREFIX + this.funcName + GOTO_COMMENT + this.funcName + "\n"+UNCONDITIONAL_JUMP;
		// create a return label
		output += "(" + returnLabel + ")\n";
		return output;
	}

	/*
	 * Function which returns an assembly translation of a return command.
	 * Return string with assembly translation of a return command
	 */
	private String getReturnCode() {
		// FRAME (Temp Var R13) = LCL
		String output = ASSIGN_R13_FROM_LCL;
		// RET (TEMP Var R14) = *(FRAME-5)
		output += ASSIGN_R14_FROM_LAST_FRAME_END_ADDRESS;
		// *ARG = pop()
		output += POP_STACK_INTO_ARG_ADDRESS;
		// SP = ARG + 1
		output += ASSIGN_STACK_FROM_ARG_PLUS1;
		// THAT = *(FRAME-1)
		output += ASSIGN_THAT_CURRENT_FRAME_INDEX;
		// THIS = *(FRAME-2)
		output += ASSIGN_THIS_CURRENT_FRAME_INDEX;
		// ARG = *(FRAME-3)
		output += ASSIGN_ARG_CURRENT_FRAME_INDEX;
		// LCL = *(FRAME-4)
		output += ASSIGN_LCL_CURRENT_FRAME_INDEX;
		// goto *(FRAME-5)
		output += JUMP_TO_THE_TARGET_FRAME;
		return output;
	}

}