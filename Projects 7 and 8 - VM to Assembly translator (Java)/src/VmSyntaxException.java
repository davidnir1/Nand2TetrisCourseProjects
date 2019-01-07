/**
 * An exception class which is thrown whenever there's a syntax problem with the VM code.
 */
public class VmSyntaxException extends Exception {

	private static final long serialVersionUID = 1L;

	public VmSyntaxException(String msg){
		super(msg);
	}

}
