from machine import UART
import time
import json
import _thread
from machine import Pin


WAKEUP = b"\x55\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x03\xfd\xd4\x14\x01\x17\x00"
SCANCARD = b"\x00\x00\xFF\x04\xFC\xD4\x4A\x02\x00\xE0\x00"
door_state = False

class PN532():
    def __init__(self,uart,freq):
        self.uart = uart
        self.freq = freq
        self.UART = UART(self.uart,self.freq)
        self.uartinit = self.UART.init(self.freq,bits = 8,parity = None,stop = 1)
    def write_cmd(self,cmd):
        self.UART.write(cmd)
        time.sleep(0.1)

    def read_cmd(self):
        return(self.UART.read())
        time.sleep(0.1)
    
    def wakeup(self,test = None):
        self.write_cmd(WAKEUP)
        time.sleep(0.1)
    
    def searchcard(self,test = None):
        self.write_cmd(SCANCARD)
        time.sleep(0.1)
        self.cardnumber = self.read_cmd()
        return self.cardnumber
    
    def the_verify(self):
        global verify_data
        verify = open("cardnumber.txt")
        verify_data = json.loads(verify.read())
        return verify_data

    def spawncard_number(self):
        card_data = self.searchcard()
        time.sleep(0.2)
        if len(card_data) > 6:
            part_a = str(hex(card_data[19])).lstrip("0").lstrip("x")
            if len(part_a) == 2:
                #return part_a
                pass
            else:
                part_a = "0"+part_a
                #return part_a
            part_b = str(hex(card_data[20])).lstrip("0").lstrip("x")
            if len(part_b) ==2 :
                #return part_b
                pass
            else:
                part_b = "0"+part_b   
                #return part_b
            part_c = str(hex(card_data[21])).lstrip("0").lstrip("x")
            if len(part_c) ==2 :
                #return part_c
                pass
            else:
                part_c = "0"+part_c
                #return part_c
            part_d = str(hex(card_data[22])).lstrip("0").lstrip("x")
            if len(part_d) ==2 :
                #return part_d
                pass
            else:
                part_d = "0"+part_d
                #return part_d
            finalnumber = part_a + part_b + part_c + part_d
            return(finalnumber)
    
    def filter(self):
        import socket
        import time
        host = "192.168.5.185"
        port = 8008
        def socket_connect():
            global s
            
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.connect((host,port))
        def socket_close():
            s.close()
        def send_equipment_num():
            s.send("0002")
        def send_card(name):
            s.send(name)
        
        try:
            card_data = self.searchcard()
            time.sleep(0.2)
            if len(card_data) > 6:
                part_a = str(hex(card_data[19])).lstrip("0").lstrip("x")
                if len(part_a) == 2:
                    #return part_a
                    pass
                else:
                    part_a = "0"+part_a
                    #return part_a
                part_b = str(hex(card_data[20])).lstrip("0").lstrip("x")
                if len(part_b) ==2 :
                    #return part_b
                    pass
                else:
                    part_b = "0"+part_b   
                    #return part_b
                part_c = str(hex(card_data[21])).lstrip("0").lstrip("x")
                if len(part_c) ==2 :
                    #return part_c
                    pass
                else:
                    part_c = "0"+part_c
                    #return part_c

                part_d = str(hex(card_data[22])).lstrip("0").lstrip("x")
                if len(part_d) ==2 :
                    #return part_d
                    pass
                else:
                    part_d = "0"+part_d
                    #return part_d
                finalnumber = part_a + part_b + part_c + part_d
                if finalnumber in self.the_verify().keys():
                    global door_state
                    door_state = True
                    try:
                        username = self.the_verify()[finalnumber]
                        socket_connect()
                        time.sleep(0.2)
                        print(str(username))
                        pla = "pla"
                        test_dict = pla,"{"+'"'+"name"+'"'+":"+'"'+username+'"'+"}"
                        s.send(test_dict[1])

                        time.sleep(0.2)
                        socket_close()
                        print("welcome%s"%(username))
                        door_state = False
                    except BaseException as e :
                        pass
                else:
                    print("invader")
                #for finalnumber in 

            else:
                pass
        except BaseException as e:
            #print(e)
            self.wakeup()
            pass
                
            

            """
            num = str(hex(test[19])).lstrip("0").lstrip("x")+str(hex(test[20])).lstrip("0").lstrip("x")+str(hex(test[21])).lstrip("0").lstrip("x")+str(hex(test[22])).lstrip("0").lstrip("x")
            """

def the_door_state(threadName,delay):
    try:
        from machine import Pin
        import time
        led = Pin(2,Pin.OUT)
        led.off()
        global door_state
        door_state = False
        delay = delay+1
        while True:
            if door_state:
                led.on()
                print("door is open")
                time.sleep(5)
                led.off()
                door_state = False
            else:
                continue

    except BaseException as e:
        
        
        pass


if __name__ == "__main__":
        from pn532_test import PN532
        from pn532_test import the_door_state
        import _thread
        def do_connect():
            import network
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            if not wlan.isconnected():
                print('connecting to network...')
                wlan.connect('Test', '12345678')
                while not wlan.isconnected():
                    pass
            print('network config:', wlan.ifconfig())
        card = PN532(2,115200)
        card.wakeup()
        do_connect()
        _thread.start_new_thread(the_door_state,("test1",1))
        
        while True:
            card.filter()


