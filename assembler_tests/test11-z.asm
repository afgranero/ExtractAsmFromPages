; testing if relative jumps specified as abolute addresses are detected as error if jumps outside the program
 ORG 0000H
 JR 0006H
 ORG 0002H
 NOP
 ORG 0003H
 NOP
 ORG 0004H
 NOP
 ORG 0005H
 NOP

