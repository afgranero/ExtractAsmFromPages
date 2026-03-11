; test if IX, IY offsets can be hexadeximal
 RES 7,(IX-1)
 RES 7,(IX+127)
 RES 7,(IX+128)
 RES 7,(IX+FFH)
 RES 7,(IX+FF)
 RES 7,(IX+0FF)
