; Testing DEFs sintaxes
 DEFB "TEST0", 0DH
 DEFM "TEST1"
 DEFB 0DH
 DEFM "TEST2" + 0DH ; fails: test7.asm(5): error: Unexpected: + 0DH
 DEFM "TEST3", 0DH
 DEFB "X"

