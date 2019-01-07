// quick assembly program which shows the last key pressed in R1

//the main loop
(LOOP)
	//check if keypress is "not zero"
	@KBD
	D=M
	// we store the key code in R1 ONLY IF A KEY WAS PRESSED
	// this will allow us to "store" the last key pressed
	@RECORD
	D;JNE 
	// no key pressed, keep checking
	@LOOP
	0;JMP
	
// copy the code of the pressed key into R1
(RECORD)
	@KBD
	D=M
	@R1
	M=D
	@LOOP
	0;JMP

