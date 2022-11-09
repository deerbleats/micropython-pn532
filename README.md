# micropython-pn532
#use example
from pn532 import PN532
card = PN532(2,115200) #com_num,freq
card.wakeup()
card.spawncard_number()

