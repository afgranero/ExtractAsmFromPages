; testing if  ORG works: this time it should issue a warning skip a byte
 ORG 0000H
 DEFB 01H, 02H
 ORG 0003H
 DEFW 0102H
