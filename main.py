#!/usr/bin/python3
# -*- coding: utf-8 -*-

import serial
import time
import threading
import socket
import json

acc = 0
p_button = 0
gear = 'N'
data = {}
clients = []

portA = '/dev/ttyUSB0'
portB = '/dev/ttyUSB1'
baud = 9600

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", 9999))
sock.listen(1)

def receiverthread():
    global clients

    while True:
        client, client_addr = sock.accept()
        print(f'New Client: {client_addr}')
        clients.append(client)

def senderthread():
    global acc
    global p_button
    global gear
    global data
    global clients

    while True:
        for client in clients:
            data['accel'] = acc
            data['P'] = p_button
            data['gear'] = gear
            client.sendall(bytes(json.dumps(data), encoding="utf-8"))
            time.sleep(1/15)

def serialthread(ser):
    global acc
    global p_button
    global gear

    line = []
    while True:
        for c in ser.read():
            if c == 10:
                text = ''.join(line).strip()
                try:
                    if text[0] == 'A':
                        text = text[1:]
                        if text.isnumeric():
                            acc = int(text)
                        else:
                            print(text)
                    elif text[0] == 'D':
                        text = text[1:]
                        temp = text.split('/')
                        p_button = int(temp[0])
                        gear = temp[1]
                except IndexError:
                    pass
                del line[:]
            else:
                line.append(chr(c))

if __name__ == "__main__":
    serA = serial.Serial(portA, baud, timeout=0)
    serial_threadA = threading.Thread(target=serialthread, args=(serA,))
    serial_threadA.start()

    serB = serial.Serial(portB, baud, timeout=0)
    serial_threadB = threading.Thread(target=serialthread, args=(serB,))
    serial_threadB.start()

    receiver_thread = threading.Thread(target=receiverthread(), args=())
    receiver_thread.start()

    sender_thread = threading.Thread(target=senderthread(), args=())
    sender_thread.start()
