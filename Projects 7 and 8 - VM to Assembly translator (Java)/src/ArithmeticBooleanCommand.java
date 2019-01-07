/**
 * This class represents an arithmetic or boolean VM command.
 * A VM command can be {add, sub, neg, eq, gt, lt, and, or, not}
 */
class ArithmeticBooleanCommand extends VmCommand {
	// line will hold the current VM command.
	// This class assumes the parser already removed all comments and spaces.
	private String line;
	private String funcName;
	// Allowed commands syntax
	private static final String ADD = "add";
	private static final String SUB = "sub";
	private static final String NEG = "neg";
	private static final String EQ = "eq";
	private static final String GT = "gt";
	private static final String LT = "lt";
	private static final String AND = "and";
	private static final String OR = "or";
	private static final String NOT = "not";
	// Error strings
	private static final String NOT_A_VALID_BOOLEAN_COMMAND = "Not a valid boolean command";
	private static final String BAD_SYNTAX = "Boolean arithmetic commands should not get arguments.";
	// Stack access
	private static final String POP_TO_D = "@SP\nAM=M-1\nD=M\n";
	private static final String PROMOTE_SP = "@SP\nM=M+1\n";
	private static final String POP_AGAIN_AND_ADD_TO_D = "A=A-1\nM=M+D\n";
	private static final String POP_AGAIN_AND_SUB = "A=A-1\nD=M-D\n";
	// Bitwise operations
	private static final String BITWISE_OR_D_M = "A=A-1\nM=D|M\n";
	private static final String BITWISE_AND_D_M = "A=A-1\nM=D&M\n";
	private static final String BITWISE_NOT_D = "M=!D\n";
	// Is Equal
	private static final String IS_EQ = "@%2$s$EQ_%1$d\nD;JEQ\n@%2$s$NEQ_%1$d\n0;JMP\n(%2$s$EQ_%1$d)\nD=-1\n" +
			"@%2$s$NEXT_%1$d\n0;JMP\n(%2$s$NEQ_%1$d)\nD=0\n(%2$s$NEXT_%1$d)\n";
	// Some string for both GT and LT
	private static final String COPY_D_TO_R13 = "@R13\nM=D\n";
	private static final String POP_TO_R14 = "@SP\nA=M-1\nD=M\n@R14\nM=D\n";
	private static final String TRUE_FALSE = "(%2$s$TRUE_%1$d)\nD=-1\n@%2$s$NEXT_%1$d\n0;JMP\n" +
			"(%2$s$FALSE_%1$d)\nD=0\n(%2$s$NEXT_%1$d)\n";
	// Is Greater Than (include consideration of an overflow)
	private static final String GT_DIFF_SIGN = "@R14\nD=M\n@%2$s$YLE_%1$d\nD;JGT\n@%2$s$YGT_%1$d\nD;JLE\n" +
			"(%2$s$YLE_%1$d)\n@R13\nD=M\n@%2$s$TRUE_%1$d\nD;JLE\n@%2$s$ELSE_%1$d\n0;JMP\n(%2$s$YGT_%1$d)\n" +
			"@R13\nD=M\n@%2$s$FALSE_%1$d\nD;JGT\n";
	private static final String GT_SAME_SIGN = "(%2$s$ELSE_%1$d)\n@R14\nD=M\n@R13\nD=D-M\n" +
			"@%2$s$FALSE_%1$d\nD;JLE\n";
	private static final String IS_GT = COPY_D_TO_R13 + POP_TO_R14 + GT_DIFF_SIGN + GT_SAME_SIGN + TRUE_FALSE;
	// Is Less Than (include consideration of an overflow)
	private static final String LT_DIFF_SIGN = "@R14\nD=M\n@%2$s$YGE_%1$d\nD;JLT\n@%2$s$YLT_%1$d\n" +
			"D;JGE\n(%2$s$YGE_%1$d)\n@R13\nD=M\n@%2$s$TRUE_%1$d\nD;JGE\n@%2$s$ELSE_%1$d\n0;JMP\n" +
			"(%2$s$YLT_%1$d)\n@R13\nD=M\n@%2$s$FALSE_%1$d\nD;JLT\n";
	private static final String LT_SAME_SIGN = "(%2$s$ELSE_%1$d)\n@R14\nD=M\n@R13\nD=D-M\n" +
			"@%2$s$FALSE_%1$d\nD;JGE\n";
	private static final String IS_LT = COPY_D_TO_R13 + POP_TO_R14 + LT_DIFF_SIGN + LT_SAME_SIGN + TRUE_FALSE;
	// Others
	private static final String NEG_D = "@0\nD=A-D\nA=M\nM=D\n";
	private static final String ASSIGN_D_TO_M = "M=D\n";
	private static final String PUSH_D = "@SP\nA=M-1\nM=D\n";
	private static final String SPACES_REGEX = "\\s+";


	/**
	 * Retrieves a single VM command and make sure it has the right syntax.
	 *
	 * @param line     A VM command line (without comments or spaces)
	 * @param funcName The function name that used current arithmetic boolean command
	 * @throws VmSyntaxException In case the command has a bad syntax
	 */
	ArithmeticBooleanCommand(String line, String funcName) throws VmSyntaxException {
		// Assumes the parser already removed all comments and spaces
		String[] splited = line.split(SPACES_REGEX);
		if (splited.length != 1) {
			throw new VmSyntaxException(BAD_SYNTAX);
		}
		this.line = line;
		this.funcName = funcName;
	}

	// Retrieves a single VM command and return the right assembly translation of it.
	@Override
	AssemblyBlock getAssemblyBlock() throws VmSyntaxException {
		String outputCommand = POP_TO_D;
		// y is the topmost operand in the stack, x is right beneath him
		switch (line) {
			case ADD: // x + y
				outputCommand += POP_AGAIN_AND_ADD_TO_D;
				break;
			case SUB: // x - y
				outputCommand += POP_AGAIN_AND_SUB + ASSIGN_D_TO_M;
				break;
			case NEG: // -y
				outputCommand += NEG_D + PROMOTE_SP;
				break;
			case EQ: // -1 (true) if x == y, 0 (false) otherwise
				outputCommand += POP_AGAIN_AND_SUB + String.format(IS_EQ, counter, funcName) + PUSH_D;
				counter += 1;
				break;
			case GT: // -1 (true) if x > y, 0 (false) otherwise
				outputCommand += String.format(IS_GT, counter, funcName) + PUSH_D;
				counter += 1;
				break;
			case LT: // -1 (true) if x < y, 0 (false) otherwise
				outputCommand += String.format(IS_LT, counter, funcName) + PUSH_D;
				counter += 1;
				break;
			case AND: // x And y
				outputCommand += BITWISE_AND_D_M;
				break;
			case OR: // x Or y
				outputCommand += BITWISE_OR_D_M;
				break;
			case NOT: // Not y
				outputCommand += BITWISE_NOT_D + PROMOTE_SP;
				break;
			default: // Not a valid boolean command
				throw new VmSyntaxException(NOT_A_VALID_BOOLEAN_COMMAND);
		}
		return new AssemblyBlock(line, outputCommand);
	}
}