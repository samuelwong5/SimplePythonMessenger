from multiprocessing import Process, Queue
import os
from socket import *
import sys
from Tkinter import *


class Messenger():
    def __init__(self, queue, port=13000):
        self.main_msg_queue = queue  # Queue for all messages
        self.port = port             # Port configuration
        self.contact_dict = {}
        # self.contact_dict = {'172.27.19.126' : [None, 'TestServer']}
        
        # Initialize GUI
        self.root = Tk()
        self.root.wm_title('Contacts')
        self.root.resizable(width=FALSE,height=FALSE)
        self.root.geometry('{}x{}'.format(200,420))
        Label(self.root, text='Contacts:').place(x=10,y=10)
        self.contact_lb = Listbox(self.root)
        self.contact_lb.place(x=10,y=30,height=310,width=180)
        # self.contact_lb.insert(1, "TestServer")
        self.contact_lb.bind('<Double-1>', self.open_chat_window)
        Label(self.root, text='IP:').place(x=10,y=350)
        Label(self.root, text='Name:').place(x=10,y=370)
        self.ip_inpt = Entry(self.root)
        self.ip_inpt.place(x=60,y=350,width=100)
        self.nm_inpt = Entry(self.root)
        self.nm_inpt.place(x=60,y=370,width=100)
        self.ip_butn = Button(self.root, text='Add',command=self.contact_add)
        self.ip_butn.grid(sticky=W,pady=4)
        self.ip_butn.place(x=10,y=390,width=150, height=20)   
        self.root.after(1000, self.receive_message)
        self.root.mainloop() 
        
    def receive_message(self, buff=1024):
        while not self.main_msg_queue.empty():
            (data, addr) = self.main_msg_queue.get()
            try:
                q = self.contact_dict[addr[0]][0]
                if q is not None:
                    q.put((data,addr))
            except KeyError:
                pass 
        self.root.after(1000, self.receive_message)    
        
    def open_chat_window(self, event):
        contact_name = self.contact_lb.selection_get()
        for k,v in self.contact_dict.iteritems():
            if v[1] == contact_name:
                new_queue = Queue()
                self.contact_dict[k][0] = new_queue
                MessageChatWindow(Tk(), new_queue, k, contact_name, self.port)
        
    def contact_add(self):
        if self.ip_inpt.get().count('.') == 3:
            name = self.nm_inpt.get() if self.nm_inpt.get() is not '' else self.ip_inpt.get()
            self.contact_lb.insert('end', name)
            self.contact_dict[self.ip_inpt.get()] = [None, name]
            self.ip_inpt.delete(0, 'end')  
            self.nm_inpt.delete(0, 'end')    

            
class MessageChatWindow():
    def __init__(self, root, queue, addr, name='', port=13000):
        # Initialize GUI
        self.root = root
        self.root.wm_title('Messenger ' + ('- ' + name if name != '' else ''))
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
        self.name = name if name != '' else addr
        
        # UDP socket for sending messages
        self.send_port = port
        self.send_addr = addr
        self.send_sock = socket(AF_INET, SOCK_DGRAM)
        self.msg_queue = queue
        
        # Callback for receiving messages
        self.root.after(1000, self.recv)
        self.root.mainloop()
        
    def recv(self):
        buff = 1024
        while not self.msg_queue.empty():
            (data, addr) = self.msg_queue.get()
            try:
                self.add_msg(self.msgs, self.name + ": " + data)
            except KeyError:
                self.add_msg(self.msgs, addr[0] + ": " + data)
        self.root.after(1000, self.recv)
        
    def add_msg(self, txt_box, text):
        txt_box.config(state=NORMAL)
        if self.count > 21:
            txt_box.delete('1.0', '2.0')
        self.count += 1
        txt_box.insert(INSERT, text + "\n")
        txt_box.config(state=DISABLED)
        
    def send(self, text=''):
        self.add_msg(self.msgs, "YOU: " + self.inpt.get())
        self.send_sock.sendto(self.inpt.get(), (self.send_addr, self.send_port))
        self.inpt.delete(0, 'end')        
            
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
    msgr = Messenger(queue)
  
  
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
