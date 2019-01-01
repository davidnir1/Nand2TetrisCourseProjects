/**
 * This class' objects represent VM commands from .vm files such as "push constant 5".
 * We use this hierarchy to support additional types of commands in the future.
 * Each object from this class will be able to generate assembly code from it's own vm code.
 */
abstract public class VmCommand {
	protected static int counter = 0;

	/**
	 * Method which handles the translation of the VM command to Assembly and returns an AssemblyBlock
	 * object representing the Assembly version of the current VM command.
	 * @return AssemblyBlock object
	 * @throws VmSyntaxException if there was a problem with syntax while translating into Assembly.
	 */
	abstract AssemblyBlock getAssemblyBlock() throws VmSyntaxException;

}
