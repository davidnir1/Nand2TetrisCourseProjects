import java.io.*;
import java.io.FileWriter;
import java.util.ArrayList;

/**
 * Class which is responsible for managing the entire process, from reading the input file to writing the
 * output file.
 */
public class VmToAssemblyFileWriter {


	private static final String VM_FILE_SUFFIX = ".vm";
	private static final String ASM_FILE_SUFFIX = ".asm";
	private static final int ERROR_CODE = -1;
	private static final String FILE_NOT_EXIST_PREFIX = "ERROR: file ";
	private static final String FILE_NOT_EXIST_SUFFIX = " does not exist.";
	private static final String CALL_SYS_INIT_0 = "call Sys.init 0";
	private static final String SYS_INIT = "Sys.init";

	/**
	 * Method which receives an input path and starts the process, which in the end will create an output
	 * file which will hold the assembly version of the VM commands inside the input file or directory.
	 *
	 * @param inputPath The path to the file or directory we are translating
	 * @throws VmSyntaxException - If there are syntax problems
	 * @throws IOException       - If there are reading or writing problems
	 */
	public void translateInput(String inputPath) throws VmSyntaxException, IOException {
		File f = new File(inputPath);
		// verify that the path exists
		if (!f.exists()) {
			System.err.println(FILE_NOT_EXIST_PREFIX + inputPath + FILE_NOT_EXIST_SUFFIX);
			System.exit(ERROR_CODE);
		}
		// case: the path leads to a file and it is indeed a .vm file
		if (f.isFile() && isVmFile(inputPath))
			translateFile(inputPath);
			// case: the path leads to a directory
		else if (f.isDirectory())
			translateFolder(inputPath);
	}

	/*
	 * Method which receives a path to a VM file and returns a path to an asm file in the same directory
	 * with the same name.
	 */
	private String getAsmPath(String vmPath) {
		int dotIndex = vmPath.lastIndexOf(VM_FILE_SUFFIX);
		return vmPath.substring(0, dotIndex) + ASM_FILE_SUFFIX;
	}

	/*
	 * Method which receives a path to a folder, and translates all of the .vm files inside it into a
	 * single <folder name>.asm file inside that directory.
	 */
	private void translateFolder(String inputPath) throws VmSyntaxException, IOException {
		File folder = new File(inputPath);
		// get a list of all the files inside the directory
		File[] fileList = folder.listFiles();
		// prepare the path of the output file
		String outputPath = inputPath + File.separator + folder.getName() + ASM_FILE_SUFFIX;
		// sanity check to see if the directory is empty
		if (fileList == null)
			return;
		// prepare an assemblyBlock array list which will be used for file writing
		ArrayList<AssemblyBlock> assemblyBlocks = new ArrayList<>();
		for (File aFileList : fileList) {
			String path = aFileList.getAbsolutePath();
			if (path.endsWith(VM_FILE_SUFFIX)) {
				// add the assembly commands related to the current file
				getAssemblyCommands(path, assemblyBlocks);
			}
		}
		// write everything into the output file
		writeToFile(assemblyBlocks, outputPath);
	}

	/*
	 * Method which receives a path to a .vm file and handles it's translation and writing into the output
	 * file.
	 */
	private void translateFile(String inputPath) throws VmSyntaxException, IOException {
		// create an array list with the assembly blocks extracted from the input file
		ArrayList<AssemblyBlock> assemblyBlocks = new ArrayList<>();
		getAssemblyCommands(inputPath, assemblyBlocks);
		// generate an output path
		String outputPath = getAsmPath(inputPath);
		// write the output file
		writeToFile(assemblyBlocks, outputPath);
	}

	/*
	 * Method which receives a list of assembly blocks and a path to an output file, and writes all of the
	 * blocks into the output file.
	 */
	private void writeToFile(ArrayList<AssemblyBlock> assemblyBlocks, String outputPath) throws
			IOException {
		FileWriter fw = new FileWriter(outputPath);
		BufferedWriter bfw = new BufferedWriter(fw);
		for (AssemblyBlock assemblyBlock : assemblyBlocks)
			bfw.write(assemblyBlock.getCode());
		bfw.close();
	}

	/*
	 * Method which receives a path to an .vm file and an array list of assembly blocks, and adds the
	 * blocks which are generated from the file to the given array.
	 */
	private void getAssemblyCommands(String inputPath, ArrayList<AssemblyBlock> assemblyBlocks) throws
			VmSyntaxException {
		// generate an array list of new vm commands from the input file
		Parser parse = new Parser();
		ArrayList<VmCommand> vmCommands = parse.getVmCommandsFromFile(inputPath);
		// add bootsrap code
		assemblyBlocks.add(new VmInit().getAssemblyBlock());
		FunctionCommand initBlock = new FunctionCommand(CALL_SYS_INIT_0);
		initBlock.setParentFunction(SYS_INIT);
		assemblyBlocks.add(initBlock.getAssemblyBlock());
		// add the assembly block version of each vm command to the given assembly block array
		for (VmCommand vmCommand : vmCommands) {

			assemblyBlocks.add(vmCommand.getAssemblyBlock());
		}
	}

	/*
	 * Method which receives a file's name and returns true if it ends with .vm, false otherwise.
	 */
	private boolean isVmFile(String fileName) {
		return fileName.endsWith(VM_FILE_SUFFIX);
	}
}


