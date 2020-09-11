# -*- coding: utf-8 -*-
import json
import pyautogui

key_codes = {
    'f1':16777264,
    'ctrl': 16777249,
    'shift':16777248,
    'capslock':16777252,
    'tab':16777217,
    'esc':16777216,
    'win':16777250,
    'alt':16777251,
    #'win-left':16777301,
    'enter':16777220,
    'escape':16777219,
    'left':16777234,
    'right':16777236,
    'up':16777235,
    'down':16777237,
    'insert':16777222,
    'home':16777232,
    'pageup':16777238,
    'delete':16777223,
    'end':16777233,
    'pagedown':16777239,
    'pause':16777224,
    'scrolllock':16777254,
    'prtscr':16777284,#?
}

def get_mouse_type(cmd):
    if cmd == 'l':
        return 'left'
    elif cmd == 'r':
        return 'right'
    elif cmd == 'm':
        return 'middle'
    elif cmd == 'f':
        return 'forward'
    elif cmd == 'b':
        return 'back'

def get_key_type(cmd):
    if cmd < 100000:
        if True:#try:
            key = chr(cmd)
            return key
        #except:
        #    print('error', cmd)
    else:
        for item in key_codes.keys():
            if cmd == key_codes[item]:
                key = item
                return key
        print('Unknow', cmd)

def parse_mouse(mouse_dict):
    for item in mouse_dict['move']:
        pyautogui.moveTo(item[0], item[1], duration=0.01)
    for item in mouse_dict['press']:
        pyautogui.mouseDown(button=get_mouse_type(item[0]), x=item[1], y=item[2])
    for item in mouse_dict['release']:
        pyautogui.mouseUp(button=get_mouse_type(item[0]), x=item[1], y=item[2])
    for item in mouse_dict['wheel']:
        if abs(item) > 0: pyautogui.scroll(item)

def parse_keyboard(keyboard_dict):
    for item in keyboard_dict['press']:
        key = get_key_type(item)
        pyautogui.keyDown(key)
    for item in keyboard_dict['release']:
        key = get_key_type(item)
        pyautogui.keyUp(key)

def parse_cmd(cmd_dict):
    pass


import socket
from PIL import ImageGrab
import cv2
import numpy as np
import threading

ip = '127.0.0.1'
keybord_port = 23333
mouse_port = 23332
vision_port = 23331
keybord_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mouse_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
vision_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
keybord_socket.bind((ip, keybord_port))
mouse_socket.bind((ip, mouse_port))


width = 320
height = 240

def keybord_loop():
    while True:
        data, addr = keybord_socket.recvfrom(65535)
        keyboard_dict = json.loads(data.decode('utf-8'))
        parse_keyboard(keyboard_dict)

def mouse_loop():
    while True:
        data, addr = mouse_socket.recvfrom(65535)
        mouse_dict = json.loads(data.decode('utf-8'))
        parse_mouse(mouse_dict)

def vision_loop():
    while True:
        raw_img = ImageGrab.grab()
        resize_img = raw_img.resize((width,height))
        img = np.array(resize_img)
        ret, jpeg = cv2.imencode('.jpg', img)
        data = jpeg.tobytes()
        vision_socket.sendto(data, (ip, vision_port))

vision_thread = threading.Thread(target=vision_loop, args=())
keybord_thread = threading.Thread(target=keybord_loop, args=())
mouse_thread = threading.Thread(target=mouse_loop, args=())

vision_thread.start()
keybord_thread.start()
mouse_thread.start()

"""
while True:
    mouse_dict = {
        'move':[],
        'press':[],
        'release':[],
        'wheel':[],
    }
    keyboard_dict = {
        'press': [70],
        'release': [70],
    }
    cmd_dict = {
        'width':0,
        'height':0,
    }

    parse_mouse(mouse_dict)
    parse_keyboard(keyboard_dict)
    break
    mouse_dict = {
        'move':[],
        'press':[],
        'release':[],
        'wheel':[1., 1., 1., 1.],
    }
    parse_mouse(mouse_dict)
    break
"""