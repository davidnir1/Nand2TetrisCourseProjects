# Nand2TetrisCourseProjects
This is a repository which holds projects from the Nand2Tetris course.  
In the first part of the course we built the HACK computer platform - a 16 bit computer, from the first NAND gates all the
way up to the actual CPU, RAM, etc.  

In the second part of the course we built a compiler which compiles JACK code (an abstract language described and used in
the course, which is similar to Java) into (eventually) HACK machine language.  
We built the compiler using Python and Java as our main tools.  


This repository holds all of our chip implementations (which together make the HACK platform) and projects 6-12 (which together make the JACK compiler, VM to Assembly translator and the Assembler).  

What we built in this second part of the course (ordered from the highest level to the lowest):
    
  Crucial implementations of JACK operating system classes (project 12):
    Here we implemented a few extremely efficient classes which provide the very basic operations required by a JACK programmer, such as:
      Math operations (multiplication, division, etc)
      Memory operations (heap allocation, memory poking, etc)
      Screen manipulations (pixel drawing, verious basic shape drawing, etc)
      Output class (provides support for the JACK text)
      etc..
      
  A JACK to HACK VM compiler (projects 10-11):
    This component understands and translates JACK code and translates it into HACK VM code which is usable in any HACK VM supporting         Machine.
    
  Our very own Snake game implementation (project 9):
    Here we built our own version of the Snake game in the JACK language, which we eventually ran using our own compiler and OS.
  
  A VM to Assembly translator (projects 7-8):
    This component translates VM code into Assembly code, which can then be used to generate machine language code for the HACK             platform.
    
  An Assembly to Machine Language translator (project 6):
    This component translates Assembly code into HACK Machine Language which can be ran on the HACK platform we built in part 1 of  
    The nand2tetris course.
  
Nand2Tetris is a free internet course, recommended to every person who wants to gain deep understanding of how computer systems work.

Course website:
https://www.nand2tetris.org/
  
David Nir and Idan Gabay.
