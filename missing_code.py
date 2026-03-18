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