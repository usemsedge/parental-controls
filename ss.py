from tkinter import *
import socket
import select
import sys
import _thread


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  


IP = socket.gethostbyname(socket.gethostname())
PORT = 31415

server.bind((IP, PORT))
server.listen(1)


def cthread(con, ad):

    while True:
        try:
            message = con.recv(2048) #cliwnt sent message
            if message:
                print(message)
            else:
                pass
        except:
            continue


class thing(Tk):
    def __init__(self, server, *args, **kwargs):
        self.server = server
        super().__init__(*args, **kwargs)

        self.entry = Entry(self)
        self.entry.grid()

        self.entry.bind('<Return>', self.send)

    def send(self, event=None, message=None):
        if message:
            thing_to_send = message #python did stuff should not be printe
        else:
            thing_to_send = self.entry.get()
            print(thing_to_send) #user inputted stuff
            
        try:
            self.client.send(bytes(thing_to_send, 'utf-8'))
        except:
            self.client = 0
            print('Client disconnected' + self.ad[0])
            self.ad = 0
            return False
        self.entry.delete(0, END)
        return True

    def main(self):
        while True:
            print('trying to accept')
            con, ad = server.accept() 
            print('accepted at ' + str(ad[0]))
            
            self.client = con
            self.ad = ad
            _thread.start_new_thread(cthread, (con, ad))

            while True:
                self.update()
                if not self.client:
                    break

            
e = thing(server)
e.main()



