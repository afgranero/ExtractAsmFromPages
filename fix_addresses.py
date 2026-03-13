SKIP = 'skip'
SUBSTITUTE = 'substitute'
INSERT_NEXT = 'insert next'

FIX_LIST = {
    # TRS-80 - Level 1 ROM Disassembled.html/TRS-80 - Level 1 ROM Disassembled.html
    '33e2ac3b3c6417fd9307feb68f4c7e2c965ce34b54b46fc8b274b39282eef019':
        {
            '0155H': (2, SKIP,          '015EH', ''),           # entire session was repeated including title
            '0249H': (2, SUBSTITUTE,    '0254H', ''),           # adddress is wrong repeating a previous one
            '0251H': (1, SUBSTITUTE,    '0252H', ''),           # address wrong
            '0287H': (2, SUBSTITUTE,    '02B7H', ''),           # address wrong
            '0329H': (1, INSERT_NEXT,   '032BH', 'DEFW 8452H'), # data word was ommited
            '04ECH': (2, SUBSTITUTE,    '04EDH', ''),           # address repeated instead of incremented
            '0501H': (2, SUBSTITUTE,    '0502H', ''),           # address repeated instead of incremented
            '0580H': (1, SKIP,          '0581H', ''),           # this one is complicated, not an error ...
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
            '06AAH': (2, SUBSTITUTE,    '06ACH', ''),           # address repeated instead of incremented
            '0768H': (1, SKIP,          '0769H', ''),           # a RLCA instruction is in fact the high ...
                                                                # ... order byte of the address of the ...
                                                                # ... previous instruction in little endian ...
                                                                # ... format repeated, probably because the ...
                                                                # ... disassembler misinterpreted the two ... 
                                                                # ... data bytes after the RST 08 and on ... 
                                                                # ... correcting manuallly it was left there
            '07E7H': (1, SKIP,          '07E8H', ''),           # same as the previous one
            '0806H': (1, SKIP,          '0807H', ''),           # a EX AF, AF' instruction is in fact the high ...
                                                                # ... order byte of the address of the ...
                                                                # ... previous instruction in little endian ...
                                                                # ... format reapeated, again probably because of ...
                                                                # ... a misinterpretation by the disassdembler ,,,
                                                                # ... and the person correcting it.
            '0842H': (1, SKIP,          '0842H', ''),           # entire session was repeated including title
            '08BAH': (1, SUBSTITUTE,    '08B3H', ''),           # address wrong
            '08D4H': (2, SUBSTITUTE,    '08D5H', ''),           # address repeated instead of incremented
            '0A89H': (2, SUBSTITUTE,    '0A8AH', ''),           # address repeated instead of incremented
            '0AB1H': (2, SUBSTITUTE,    '0AB2H', ''),           # address repeated instead of incremented
            '0E4AH': (2, SUBSTITUTE,    '0E4BH', ''),           # address repeated instead of incremented
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

def fix_address(address, hash, type="code"):
    # this is not one of the expected files: do nothing
    if hash not in FIX_LIST:
        return None, address, None

    fix_elements = FIX_LIST[hash]

    # initialize the attributes on the first time
    if type not in fix_address.count_addresseses:
        fix_address.count_addresseses[type] = {}

    if type not in fix_address.address_stop_skipping:
        fix_address.address_stop_skipping[type] = {}
        
    # even if it os not an address of interest the function can still be on SKIP state
    if fix_address.address_stop_skipping[type] != {}:
        if fix_address.address_stop_skipping[type] == address:
            # skiping part ended return to normal
            fix_address.address_stop_skipping[type] = {}
            return None, address, None
        else:
            # it is on SKIP state: skip
            return SKIP, address, None

    if address not in fix_elements:
        return None, address, None

    # can only reach this point if it is an address of interest

    # count ocurrencies of the address
    if address not in fix_address.count_addresseses[type]:
        fix_address.count_addresseses[type][address] = 1
    else:
        fix_address.count_addresseses[type][address] += 1

    count, action, new_address, extra = fix_elements[address]
    if count == fix_address.count_addresseses[type][address]:
        # the address has the necessary count
        # TODO here we can use a switch
        if action == SKIP:
            fix_address.address_stop_skipping[type] = new_address
            return SKIP, None, None
        elif action == SUBSTITUTE:
            return SUBSTITUTE, new_address, None
        elif action == INSERT_NEXT:
            return INSERT_NEXT, new_address, extra
    else:
        return None, address, None

fix_address.count_addresseses = {}
fix_address.address_stop_skipping = {}
