/**
 * This class' objects represent blocks of assembly code translated from VM code.
 */
public class AssemblyBlock {

	private static final String COMMENT_PREFIX = "// ";
	private static final String NEWLINE = "\n";
	private String codeBlock;

	/**
	 * Constructor for the AssemblyBlock class, receives a line and a code and creates a usable version of
	 * them.
	 *
	 * @param vmCode       The VM version of this code.
	 * @param assemblyCode The Assembly version of this code.
	 */
	public AssemblyBlock(String vmCode, String assemblyCode) {
		this.codeBlock = COMMENT_PREFIX + vmCode + NEWLINE + assemblyCode;
		/*
		 * Each block of assembly code will look like this:
		 * // the VM line of code which this assembly code represents
		 * The actual assembly code
		 */
	}

	public String getCode() {
		return this.codeBlock;
	}
}
