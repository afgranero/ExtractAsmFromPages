# the code here is in the format disassember, ...
# ... it must be normalized by code to generate compilable in jsasmplus and z80asm
MC_TRS80_M1_L1_0098= """
;----------------------------------------------------------------------------------------------------------------------------------;
; Missing code part adapted from https://github.com/andyv/level1/blob/master/level1.src                                            ;
;----------------------------------------------------------------------------------------------------------------------------------;

;----------------------------------------------------------------------------------------------------------------------------------;
;                                                                                                                                  ;
; Continuation of RST 08H                                                                                                          ;
;                                                                                                                                  ;
;----------------------------------------------------------------------------------------------------------------------------------;

0098H   INC HL                  ; Point to offset
0099H   JR Z,00A2H              ; Got match, consume char at DE
009BH   PUSH BC                 ; Take alternate branch
009CH   LD C,(HL)               ; BC = offset
009DH   LD B,00H
009FH   ADD HL,BC               ; Branch address
00A0H   POP BC                  ; Restore BC
00A1H   DEC DE                  ; Do not consume char at DE
00A2H   INC DE
00A3H   INC HL
00A4H   EX (SP),HL              ; return to HL
00A5H   RET

        ;--------------------------------------------------------------------------------------------------------------------------;
        ; Parse floating point constant                                                                                            ;
        ;                                                                                                                          ;
        ; Bit 0 of B is 'Seen decimal point'                                                                                       ;
        ; Bit 1 of B is 'Seen exponent minus sign'                                                                                 ;
        ; Bit 5 of B is 'Seen digits in exponent'                                                                                  ;
        ; Bit 6 of B is 'Seen a digit'                                                                                             ;
        ; Bit 7 of B is 'Large number of digits'                                                                                   ;
        ;                                                                                                                          ;
        ; C = number of digits past the DP                                                                                         ;
        ; Returns with Z set if found a valid number                                                                               ;
        ;--------------------------------------------------------------------------------------------------------------------------;

00A6H   CALL 0155H              ; Zero C':HL' accumulator
00A9H   LD B,00H
00ABH   LD C,B                  ; Weird way of loading BC=0
00ACH   RST 28H
00ADH   CALL 00B2H
00B0H   JR 00ADH                ; Infinite digit loop

        ;--------------------------------------------------------------------------------------------------------------------------;
        ; Parse next digit of FP number.  Called from an infinite loop.                                                            ;
        ;--------------------------------------------------------------------------------------------------------------------------;

00B2H   CALL 008CH              ; Parse digit
00B5H   JR C,00D7H              ; No digit
00B7H   SET 6,B
00B9H   BIT 7,B
00BBH   JR NZ,00D2H             ; Large number, ignore digits
00BDH   CALL 00C5H
00C0H   BIT 0,B
00C2H   RET Z
00C3H   DEC C
00C4H   RET

00C5H   CALL 015EH              ; Accumulate a digit
00C8H   RET Z                   ; Accumulator still small
00C9H   EXX
00CAH   LD H,D
00CBH   LD L,E
00CCH   EX AF,AF'
00CDH   LD C,A
00CEH   EXX
00CFH   SET 7,B                 ; Flag number as 'large'
00D1H   POP AF                  ; Pop 1st level return address

        ;--------------------------------------------------------------------------------------------------------------------------;
        ; For large number, only keep track of digits past DP.                                                                     ;
        ;--------------------------------------------------------------------------------------------------------------------------;

00D2H   BIT 0,B
00D4H   RET NZ
00D5H   INC C
00D6H   RET

        ;--------------------------------------------------------------------------------------------------------------------------;
        ; Didn't find a digit                                                                                                      ;
        ;--------------------------------------------------------------------------------------------------------------------------;

00D7H   RST 08H
00D8H   DEFB '.'
00D9H   DEFB 05H                ; TARGET 00DFH (AFG note: relative jump)

00DAH   BIT 0,B
00DCH   SET 0,B
00DEH   RET Z                   ; Already seen DP, give up

00DFH   POP AF
00E0H   BIT 6,B
00E2H   RET Z                   ; Return if no digits seen
00E3H   LD L,18H
00E5H   LD H,00H
00E7H   PUSH BC
00E8H   PUSH DE
00E9H   EXX
00EAH   CALL 0E00H              ; Normalize C':H':L'
00EDH   LD BC,000AH             ; Push a pair of floats   
00F0H   ADD IX,BC
00F2H   POP DE
00F3H   LD BC,00FBH
00F6H   PUSH BC
00F7H   PUSH DE
00F8H   JP 0D0FH                ; Store regs to FP stack top

00FBH   POP BC
00FCH   PUSH DE
00FDH   RST 08H, 
00FEH   DEFB 'E'
00FFH   DEFB 1CH                ; TARGET 011CH (AFG note: relative jump)
0100H   RST 08H
0101H   DEFB '+'
0102H   DEFB 02H                ; TARGET 0105H (AFG note: relative jump)
0103H   JR 010AH

0105H   RST 08H
0106H   DEFB '-'
0107H   DEFB 02H                ; TARGET 010AH (AFG note: relative jump)
0108H   SET 1,B

;----------------------------------------------------------------------------------------------------------------------------------;
; End of missing part.                                                                                                             ;
;----------------------------------------------------------------------------------------------------------------------------------;
"""

MC_TRS80_M1_L1_032B = """032BH   DEFB 84H, 52H           ; AFG note: this data was ommited in the original

"""

MC_TRS80_M1_L1_0336 = """
"""

MC_TRS80_M1_L1_0EBD = """
;----------------------------------------------------------------------------------------------------------------------------------;
; Missing code part adapted from https://github.com/andyv/level1/blob/master/level1.src                                            ;
;----------------------------------------------------------------------------------------------------------------------------------;

;----------------------------------------------------------------------------------------------------------------------------------;
;                                                                                                                                  ;
; Parse an integer, requiring digits.                                                                                              ;
;                                                                                                                                  ;
;----------------------------------------------------------------------------------------------------------------------------------;

0EBDH   CALL OEC4H
0EC0H   RET NZ
0EC1H   JP 08C9H                ; Throw a WHAT

;----------------------------------------------------------------------------------------------------------------------------------;
; End of missing part.                                                                                                             ;
;----------------------------------------------------------------------------------------------------------------------------------;
"""

MISSING_CODE = {
    # TRS-80 - Level 1 ROM Disassembled.html/TRS-80 - Level 1 ROM Disassembled.html
    '33e2ac3b3c6417fd9307feb68f4c7e2c965ce34b54b46fc8b274b39282eef019':
        {
            '0098H': MC_TRS80_M1_L1_0098,
            '032BH': MC_TRS80_M1_L1_032B,
            '0336H': MC_TRS80_M1_L1_0336,
            '0EBDH': MC_TRS80_M1_L1_0EBD,
        },
    # TRS-80 - Model I - Level 2/Model I ROM Explained - Part 1.html
    '76337e787a728184b3f5a8af89bedcb8ade1ad79937809d05302f4951f007676': 
        {},
    # TRS-80 - Model I - Level 2/Model I ROM Explained - Part 2.html
    'ecc98da804913d11f43d7f9f5bc911841020af954a877c728891bd7f1013852b':
        {},
    # TRS-80 - Model I - Level 2/Model I ROM Explained - Part 3.html
    'a9e56a939c987889be77c22b331974105b7aabc700f8d541d84560653e5f95a8':
        {},
    # Model III ROM Explained - Part 1.html
    '0f2f2135b06b067b3ec6d751ead77d2801902272563ca3ae53bc8a890298089d':
        {},
    # Model III ROM Explained - Part 1.html/Model III ROM Explained - Part 2.html
    'c4003dbe2e36707400a47c1f28d80ebaca5f7812b34014c3fb3f062c5273e48f':
        {},
    # Model III ROM Explained - Part 1.html/Model III ROM Explained - Part 3.html
    'c73cf199246f061c047c108e6d1f375dd292f2b243b6d96859f37d94d2b607e6':
        {},
    # Model III ROM Explained - Part 1.html/Model III ROM Explained - Part 4.html
    'dbabc65bdfb220c4d44a6f6ca8e9bad4ba8416c6885990e275908a7cc935111e':
        {},
    }

SKIP = 'skip'
SUBSTITUTE = 'substitute'
INSERT_NEXT = 'insert next'

FIX_LIST = {
    # TRS-80 - Level 1 ROM Disassembled.html/TRS-80 - Level 1 ROM Disassembled.html
    '33e2ac3b3c6417fd9307feb68f4c7e2c965ce34b54b46fc8b274b39282eef019':
        {
            '0155H': (2, SKIP,          '015EH'),           # entire session was repeated including title
            '0249H': (2, SUBSTITUTE,    '0254H'),           # adddress is wrong repeating a previous one
            '0251H': (1, SUBSTITUTE,    '0252H'),           # address wrong
            '0287H': (2, SUBSTITUTE,    '02B7H'),           # address wrong
            '0329H': (1, INSERT_NEXT,   '032BH'),           # data word was ommited in the original
            '0336H': (1, INSERT_NEXT,   '0336H'),           # add a line for better grouping
            '04ECH': (2, SUBSTITUTE,    '04EDH'),           # address repeated instead of incremented
            '0501H': (2, SUBSTITUTE,    '0502H'),           # address repeated instead of incremented
            '0580H': (1, SKIP,          '0581H'),           # this one is complicated, not an error ...
                                                            # ... when entering a routine by 0560H and ...
                                                            # ... following code flow it executes ...
                                                            # ... 057FH 3E 09  LD A,09H ...
                                                            # ... 0581H 7E     LD A,(HL) ...
                                                            # ... what seems to make no sense as the ...
                                                            # ... A register is loaded with one value ...
                                                            # ... and with another one next, but ...
                                                            # ... there are several places that jump to ...
                                                            # ... address  0580H that is in the middle of ...
                                                            # ... the instruction 057FH 3E 09  LD A,09H ...
                                                            # ... that has two bytes, more peciselly the 09H 
                                                            # ... that is the opcode of:
                                                            # ... 0580H 09     ADD HL,BC ...
                                                            # ... this way the useless instruction at 057FH ... 
                                                            # ... becomes another, but just when the ...
                                                            # ... code jumps to 0580H, it seems like a ...
                                                            # ... clever way to save a few bytes with ... 
                                                            # ... conditionals or repeating code ...
                                                            # ... but if this instruction is explicited ...
                                                            # ... in the assembler we get a warning for ... 
                                                            # ... 'ORG does not pad output file to reach ...
                                                            # ... target address, bytes skipped: -1' ...
                                                            # ... in some assemblers like jsasmplus.
            '06AAH': (2, SUBSTITUTE,    '06ACH'),           # address repeated instead of incremented
            '0768H': (1, SKIP,          '0769H'),           # a RLCA instruction is in fact the high ...
                                                            # ... order byte of the address of the ...
                                                            # ... previous instruction in little endian ...
                                                            # ... format repeated, probably because the ...
                                                            # ... disassembler misinterpreted the two ... 
                                                            # ... data bytes after the RST 08 and on ... 
                                                            # ... correcting manuallly it was left there
            '07E7H': (1, SKIP,          '07E8H'),           # same as the previous one
            '0806H': (1, SKIP,          '0807H'),           # a EX AF, AF' instruction is in fact the high ...
                                                            # ... order byte of the address of the ...
                                                            # ... previous instruction in little endian ...
                                                            # ... format reapeated, again probably because of ...
                                                            # ... a misinterpretation by the disassdembler ,,,
                                                            # ... and the person correcting it.
            '0842H': (1, SKIP,          '0842H'),           # entire session was repeated including title
            '08BAH': (1, SUBSTITUTE,    '08B3H'),           # address wrong
            '08D4H': (2, SUBSTITUTE,    '08D5H'),           # address repeated instead of incremented
            '0097H': (1, INSERT_NEXT,   '0098H'),           # missing section in the original
            '0A89H': (2, SUBSTITUTE,    '0A8AH'),           # address repeated instead of incremented
            '0AB1H': (2, SUBSTITUTE,    '0AB2H'),           # address repeated instead of incremented
            '0E4AH': (2, SUBSTITUTE,    '0E4BH'),           # address repeated instead of incremented
            '0EB9H': (1, INSERT_NEXT,   '0EBDH'),           # missing section in the original
        },
    # TRS-80 - Model I - Level 2/Model I ROM Explained - Part 1.html
    '76337e787a728184b3f5a8af89bedcb8ade1ad79937809d05302f4951f007676': 
        {},
    # TRS-80 - Model I - Level 2/Model I ROM Explained - Part 2.html
    'ecc98da804913d11f43d7f9f5bc911841020af954a877c728891bd7f1013852b':
        {},
    # TRS-80 - Model I - Level 2/Model I ROM Explained - Part 3.html
    'a9e56a939c987889be77c22b331974105b7aabc700f8d541d84560653e5f95a8':
        {},
    # Model III ROM Explained - Part 1.html
    '0f2f2135b06b067b3ec6d751ead77d2801902272563ca3ae53bc8a890298089d':
        {},
    # Model III ROM Explained - Part 1.html/Model III ROM Explained - Part 2.html
    'c4003dbe2e36707400a47c1f28d80ebaca5f7812b34014c3fb3f062c5273e48f':
        {},
    # Model III ROM Explained - Part 1.html/Model III ROM Explained - Part 3.html
    'c73cf199246f061c047c108e6d1f375dd292f2b243b6d96859f37d94d2b607e6':
        {},
    # Model III ROM Explained - Part 1.html/Model III ROM Explained - Part 4.html
    'dbabc65bdfb220c4d44a6f6ca8e9bad4ba8416c6885990e275908a7cc935111e':
        {},
    }
