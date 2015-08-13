from multiprocessing import Process
import os
from socket import *
import sys


host = "172.0.0.1" # set to IP address of target computer
port = 13000       # default port
buff = 1024        # default received message buffer size  



def receive():
    UDPSock = socket(AF_INET, SOCK_DGRAM)
    UDPSock.bind(('', port))
    while True:
        (data, addr) = UDPSock.recvfrom(buff)
        print "[RECV] " + data
    UDPSock.close()
       
        
def send():
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

    
if __name__ == "__main__":  
    if len(sys.argv)>1:
        host = sys.argv[1]
    p = Process(target=receive)
    p.start()
    send()