/**
 * Small VmCommand subclass which helps with the bootsrap generation.
 */
public class VmInit extends VmCommand {

	private static final String BOOTSTRAP_TITLE = "SP=256";
	private static final String BOOTSTRAP_CODE = "@256\nD=A\n@SP\nM=D\n";

	@Override
	AssemblyBlock getAssemblyBlock() throws VmSyntaxException {
		return new AssemblyBlock(BOOTSTRAP_TITLE, BOOTSTRAP_CODE);
	}
}
