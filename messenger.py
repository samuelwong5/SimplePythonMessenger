from multiprocessing import Process, Queue
import os
from socket import *
import sys
from Tkinter import *

class MessageApp():
    def __init__(self, root, host, queue, port=13000):
        # initialize gui
        self.root = root
        self.root.wm_title("Messenger")
        self.root.resizable(width=FALSE,height=FALSE)
        self.root.geometry('{}x{}'.format(280,340))
        self.msgs = Text(self.root)
        self.msgs.place(x=10,y=10,height=290,width=260)
        self.msgs.config(state=DISABLED)
        self.inpt = Entry(root)
        self.inpt.place(x=10,y=310,width=200)
        self.inpt.bind('<Return>', self.send)
        self.send_btn = Button(root, text='Send',command=self.send)
        self.send_btn.grid(sticky=W,pady=4)
        self.send_btn.place(x=220,y=310,width=50, height=20)
        self.count = 0
        
        # config udp socket for sending messages
        self.send_addr = (host, port)
        self.send_sock = socket(AF_INET, SOCK_DGRAM)
        self.msg_queue = queue
        
    def recv(self):
        buff = 1024
        while not self.msg_queue.empty():
            (data, addr) = self.msg_queue.get()
            self.add_msg(addr[0] + ": " + data)
        self.root.after(1000, self.recv)
    
    def start(self):
        self.root.after(1000, self.recv)
        self.root.mainloop()
        
    def add_msg(self, text):
        self.msgs.config(state=NORMAL)
        if self.count > 21:
            self.msgs.delete('1.0', '2.0')
        self.count += 1
        self.msgs.insert(INSERT, text + "\n")
        self.msgs.config(state=DISABLED)
        
    def send(self, text=''):
        self.add_msg("YOU: " + self.inpt.get())
        self.send_sock.sendto(self.inpt.get(), self.send_addr)
        self.inpt.delete(0, 'end')        

        
def msg_listen(queue, port=13000):
    buff = 1024
    recv_sock = socket(AF_INET, SOCK_DGRAM)
    recv_sock.bind(('', port))
    while True:
        (data, addr) = recv_sock.recvfrom(buff)
        queue.put((data,addr))

    
def msgr_init(target, queue):
    root = Tk()
    messenger = MessageApp(root, '172.27.19.126', queue)
    messenger.start()
  
  
# ------- Terminal Messenger -------  
def term_receive(port=13000):
    UDPSock = socket(AF_INET, SOCK_DGRAM)
    UDPSock.bind(('', port))
    while True:
        (data, addr) = UDPSock.recvfrom(buff)
        print (addr[0] + data)
    UDPSock.close()
       
        
def term_send(host, port=13000):
    addr = (host, port)
    UDPSock = socket(AF_INET, SOCK_DGRAM)
    while True:
        data = raw_input("")
        UDPSock.sendto(data, addr)
        if data == "exit":
            break
    UDPSock.close()
    p.terminate()
    p.join()
# ----------------------------------

if __name__ == "__main__":    
    if len(sys.argv)<2:
        print("Missing argument: target_ip")
        sys.exit(-1)
    if '--no-gui' in sys.argv:
        p = Process(target=term_receive)
        p.start()
        for a in sys.argv:
            if a.count('.') == 3:
                term_send(a)
                break
    else:
        msg_queue = Queue()
        msg_proc = None
        for a in sys.argv:
            if a.count('.') == 3:
                msg_proc = Process(target=msgr_init, args=(a, msg_queue))
                break
        msg_proc.start()
        msg_listen(msg_queue)
