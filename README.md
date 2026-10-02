# micropython-pn532
#use example
\
from pn532 import PN532\
card = PN532(2,115200) #com_num,freq\
card.wakeup()\
card.spawncard_number()

## Compatibility and host tests

UID formatting is shared by `spawncard_number` and `filter`. It still reads
positions 19–22 and produces the same lowercase, padded hexadecimal text.
UART commands, all delays, authorization-file lookups, socket text, and
`door_state` updates are unchanged. No live network or door is exercised by
the tests.

Run `python3 -B -m unittest discover -s tests -v` from this directory.
The fake UART/socket tests cover all byte values, short/None responses, known
and unknown cards, wakeup fallback, and connection failure. They do not
validate MicroPython sockets, UART framing, real NFC cards or thread timing.

Existing limitations are deliberately retained: short frames can raise an
index error; `None` can raise a type error; a failed socket connection after
authorization leaves `door_state` true. The main example imports `pn532_test`
although the supplied file is `pn532.py`. These require separate behavior
changes and hardware review, rather than being silently fixed in a refactor.
