skip_list = {
    # TRS-80 - Level 1 ROM Disassembled.html/TRS-80 - Level 1 ROM Disassembled.html
    '33e2ac3b3c6417fd9307feb68f4c7e2c965ce34b54b46fc8b274b39282eef019':
        {
            '0155H': (2, 'skip',        '015EH'),           # entire session was repeated including title
            '0249H': (2, 'substitute',  '0254H'),           # adddress is wrong repeating a previous one
            '0251H': (1, 'substitute',  '0252H'),           # address wrong
            '0287H': (1, 'substitute',  '02B7H'),           # address wrong
            '0329H': (1, 'insert next', '032AH|DEFW 8452'), # a data word was ommited
            '04ECH': (2, 'substitute',  '04EDH'),           # address repeated instead of incremented
            '0501H': (2, 'substitute',  '0502H'),           # address repeated instead of incremented
            '06AAH': (2, 'substitute',  '06ACH'),           # address repeated instead of incremented
            '0842H': (2, 'skip',        '0858H'),           # an entire session was repeated includinG title
            '08BAH': (1, 'substitute',  '08B3H'),           # address wrong
            '08D4H': (2, 'substitute',  '08D5H'),           # address repeated instead of incremented
            '0A89H': (2, 'substitute',  '0A8AH'),           # address repeated instead of incremented
            '0AB1H': (2, 'substitute',  '0AB2H'),           # address repeated instead of incremented
            '0E4AH': (2, 'substitute',  '0E4BH'),           # address repeated instead of incremented
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