from multiprocessing import Process, Queue
import os
from socket import *
import sys
from Tkinter import *

class MessageApp():
    def __init__(self, root, queue, port=13000):
        # initialize gui
        self.root = root
        self.root.wm_title("Messenger")
        self.root.resizable(width=FALSE,height=FALSE)
        self.root.geometry('{}x{}'.format(460,340))
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.msgs = Text(self.root)
        self.msgs.place(x=10,y=10,height=290,width=260)
        self.msgs.config(state=DISABLED)
        self.inpt = Entry(root)
        self.inpt.place(x=10,y=310,width=200)
        self.inpt.bind('<Return>', self.send)
        self.send_btn = Button(root, text='Send',command=self.send)
        self.send_btn.grid(sticky=W,pady=4)
        self.send_btn.place(x=220,y=310,width=50, height=20)
        self.ip_list = Text(self.root)
        self.ip_list.place(x=300,y=10,height=250,width=150)
        self.ip_list.config(state=DISABLED)
        Label(root, text='Name:').place(x=300,y=290)
        Label(root, text='IP:').place(x=300,y=270)
        self.ip_inpt = Entry(root)
        self.ip_inpt.place(x=350,y=270,width=100)
        self.nm_inpt = Entry(root)
        self.nm_inpt.place(x=350,y=290,width=100)
        self.ip_butn = Button(root, text='Add',command=self.add_ip)
        self.ip_butn.grid(sticky=W,pady=4)
        self.ip_butn.place(x=300,y=310,width=150, height=20)       
        self.count = 0
        
        # config udp socket for sending messages
        self.send_port = port
        self.send_addr = {}
        self.send_sock = socket(AF_INET, SOCK_DGRAM)
        self.msg_queue = queue
        
    def recv(self):
        buff = 1024
        while not self.msg_queue.empty():
            (data, addr) = self.msg_queue.get()
            try:
                self.add_msg(self.msgs, self.send_addr[addr[0]] + ": " + data)
            except KeyError:
                self.add_msg(self.msgs, addr[0] + ": " + data)
        self.root.after(1000, self.recv)
    
    def start(self):
        self.root.after(1000, self.recv)
        self.root.mainloop()
        
    def add_msg(self, txt_box, text):
        txt_box.config(state=NORMAL)
        if self.count > 21:
            txt_box.delete('1.0', '2.0')
        self.count += 1
        txt_box.insert(INSERT, text + "\n")
        txt_box.config(state=DISABLED)
        
    def send(self, text=''):
        self.add_msg(self.msgs, "YOU: " + self.inpt.get())
        for addr in self.send_addr.keys():
            self.send_sock.sendto(self.inpt.get(), (addr, self.send_port))
        self.inpt.delete(0, 'end')        

    def add_ip(self):
        if self.ip_inpt.get().count('.') == 3:
            self.add_msg(self.ip_list, self.nm_inpt.get())
            name = self.nm_inpt.get() if self.nm_inpt.get() is not '' else self.ip_inpt.get()
            self.send_addr[self.ip_inpt.get()] = name
            self.ip_inpt.delete(0, 'end')  
            self.nm_inpt.delete(0, 'end')
            
    def exit(self):
        sys.exit(0)
        
        
def msg_listen(queue, port=13000):
    buff = 1024
    recv_sock = socket(AF_INET, SOCK_DGRAM)
    recv_sock.bind(('', port))
    while True:
        (data, addr) = recv_sock.recvfrom(buff)
        queue.put((data,addr))

    
def msgr_init(queue):
    root = Tk()
    messenger = MessageApp(root, queue)
    messenger.start()
  
  
# ------- Terminal Messenger -------  
def term_receive(buff=1024, port=13000):
    UDPSock = socket(AF_INET, SOCK_DGRAM)
    UDPSock.bind(('', port))
    while True:
        (data, addr) = UDPSock.recvfrom(buff)
        print (addr[0] + ' - ' + data)
    UDPSock.close()
       
        
def term_send(host, buff=1024, port=13000):
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
    if '--no-gui' in sys.argv:
        p = Process(target=term_receive)
        p.start()
        for arg in sys.argv:
            if arg.count('.') == 3:
                term_send(arg)
                break
    else:
        msg_queue = Queue()
        msg_read = Process(target=msg_listen, args=(msg_queue,))
        msg_read.start()
        msg_proc = Process(target=msgr_init, args=(msg_queue,))
        msg_proc.start()
