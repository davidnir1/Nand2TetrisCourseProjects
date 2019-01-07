import java.io.IOException;


public class main {

	private static final String ERR_INV_NUM_ARGS = "ERROR: Invalid number of parameters";
	private static final int ERROR_CODE = -1;

	/**
	 * The main function for the VM to Assembly translator.
	 * This function will verify that there are inputs and start the process for each input.
	 * If for any reason, something fails, we exit with code -1, otherwise with code 0.
	 */
	public static void main(String[] args) {
		if (args.length < 1) { // check that we have arguments
			System.err.println(ERR_INV_NUM_ARGS);
			return;
		}
		try {
			// iterate over the inputs, handling each
			for (String inputPath : args) {
				// translate the current arg and create an output file for it
				VmToAssemblyFileWriter vmtaFileWriter = new VmToAssemblyFileWriter();
				vmtaFileWriter.translateInput(inputPath);
			}
			// if there was a problem with reading/writing a file or some syntax problems
		} catch (IOException | VmSyntaxException exc) {
			System.err.println(exc.getMessage());
			System.exit(ERROR_CODE);
		}
	}
}

