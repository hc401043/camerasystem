import serial as sr
import time
import threading as th

class Bluetooth:
    def __init__(self,port,speed):
        self.data=""
        self.ser=-1
        self.wtime=5
        self.sending=False
        self.port = port
        self.speed = speed

        self.red = [-1]*2
        self.green = [-1]*2
        self.blue = [-1]*2
        self.yellow = [-1]*2
        self.black = [-1]*2
        self.redidx = 0
        self.greenidx = 0
        self.blueidx = 0
        self.yellowidx = 0
        self.blackidx = 0

        self.bonus = 0
        self.debug_str = ""
    
    def reset_blockinfo(self):
        self.red = [-1]*2
        self.green = [-1]*2
        self.blue = [-1]*2
        self.yellow = [-1]*2
        self.black = [-1]*2
        self.redidx = 0
        self.greenidx = 0
        self.blueidx = 0
        self.yellowidx = 0
        self.blackidx = 0

    def open_comport(self):
        try :
            self.ser = sr.Serial(self.port,self.speed)
            return True
        except sr.SerialException:
            print("ポートが開けないようです") 
            return False

    def close_comport(self):
        self.ser.close()


    def send_thread(self):
        while self.sending:
            self.set_dataln(self.make_sendstr())
            print("senddata:",self.data)
            self.ser.write(self.data)
            time.sleep(self.wtime)

    def start_send_thread(self):
        self.sending=True
        bt_th = th.Thread(target=self.send_thread)
        bt_th.setDaemon(True)
        bt_th.start()

    def stop_send_thread(self):
        self.sending = False

    def set_dataln(self,dat):
        udata =  dat
        self.data = udata.encode()

    def set_red(self,no):
        if self.redidx==2: self.redidx=0
        if self.red[(self.redidx+1)%2]==no: return
        self.red[self.redidx]=no
        self.redidx=self.redidx+1
    def set_green(self,no):
        if self.greenidx==2: self.greenidx=0
        if self.green[(self.greenidx+1)%2]==no: return
        self.green[self.greenidx]=no
        self.greenidx=self.greenidx+1
    def set_blue(self,no):
        if self.blueidx==2: self.blueidx=0
        if self.blue[(self.blueidx+1)%2]==no: return
        self.blue[self.blueidx]=no
        self.blueidx=self.blueidx+1
    def set_yellow(self,no):
        if self.yellowidx==2: self.yellowidx=0
        if self.yellow[(self.yellowidx+1)%2]==no: return
        self.yellow[self.yellowidx]=no
        self.yellowidx=self.yellowidx+1
    def set_black(self,no):
        if self.blackidx==2: self.blackidx=0
        if self.black[(self.blackidx+1)%2]==no: return
        self.black[self.blackidx]=no
        self.blackidx=self.blackidx+1

    def make_sendstr(self):
        if self.debug_str!="":
            return self.debug_str

        data = ""
        cmd = ['R','G','B','Y','K','x']
        value=0
        if self.red[0]!=-1:
            value = self.red[0]
        if self.red[1]!=-1:
            value = value*100 + self.red[1]
        if value!=0:    
            data = data+ cmd[0]+str(value)+'\n'

        value=0
        if self.green[0]!=-1:
            value = self.green[0]
        if self.green[1]!=-1:
            value = value*100 + self.green[1]
        if value!=0:    
            data = data+ cmd[1]+str(value)+'\n'

        value=0
        if self.blue[0]!=-1:
            value = self.blue[0]
        if self.blue[1]!=-1:
            value = value*100 + self.blue[1]
        if value!=0:    
            data = data+ cmd[2]+str(value)+'\n'

        value=0
        if self.yellow[0]!=-1:
            value = self.yellow[0]
        if self.yellow[1]!=-1:
            value = value*100 + self.yellow[1]
        if value!=0:    
            data = data+ cmd[3]+str(value)+'\n'

        value=0
        if self.black[0]!=-1:
            value = self.black[0]
        if self.black[1]!=-1:
            value = value*100 + self.black[1]
        if value!=0:    
            data = data+ cmd[4]+str(value)+'\n'
        
        #self.bonus = 7 
        data=data+cmd[5]+str(self.bonus)+'\n'


        #data = "R106\nx9\n";
        return data



    def set_wtime(self,t):
        self.wtime = t