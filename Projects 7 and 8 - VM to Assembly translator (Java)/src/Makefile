###############################################################################
#
# Makefile for Java solution to Nand ex 8
#
# Students:
# Idan Gabay, ID 312415706, idan.gabay@mail.huji.ac.il
# David Nir, ID 203487293, david.nir1@mail.huji.ac.il
#
###############################################################################


# The sources for the program
SRCS = main.java Parser.java VmCommand.java ArithmeticBooleanCommand.java MemoryAccessCommand.java \
AssemblyBlock.java VmSyntaxException.java VmToAssemblyFileWriter.java FlowControlCommand.java \
FunctionCommand.java VmInit.java

# Constants and flags
JAVAC=javac
EXEC=VMtranslator
TAR=tar
TARFLAGS=cvf
TARNAME=project8.tar
TARSRCS=$(SRCS) $(EXEC) README Makefile

# Rules/Recipes

all: compile

compile:
	$(JAVAC) $(JAVACFLAGS) $(SRCS)
	chmod +x $(EXEC)

# convenience
tar:
	$(TAR) $(TARFLAGS) $(TARNAME) $(TARSRCS)

# after cleaning
clean:
	rm -f *.class *~
