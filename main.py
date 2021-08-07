#!/usr/bin/python3
# -*- coding: utf-8 -*-
from MonitoringClient.MonitoringClient import MonitoringClient
import serial
import time
import threading
import socket
import json
import glob


def serial_ports():
    ports = glob.glob('/dev/tty[A-Za-z]*')
    # ports = ['COM%s' % (i + 1) for i in range(256)]

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

acc = 0
p_button = 0
gear = 'N'
change_gear = 'N'

baud = 9600

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", 9999))
sock.listen(1)

def acceptionthread():
    global sock
    while True:
        c = sock.accept()
        print(f'New Client: {c[1]}')

        receiver_thread = threading.Thread(target=receiverthread, args=(c,))
        receiver_thread.daemon = True
        receiver_thread.start()

        sender_thread = threading.Thread(target=senderthread, args=(c,))
        sender_thread.daemon = True
        sender_thread.start()


def receiverthread(c):
    global change_gear
    client, client_addr = c
    while True:
        try:
            data = client.recv(1024)
            if not len(data):
                raise ValueError
            data = data.decode()
            if data[0] in ['R','N','D']:
                change_gear = data[0]
        except:
            print(f'RClient Left: {client_addr}')
            break


def senderthread(c,):
    global acc
    global p_button
    global gear

    client, client_addr = c
    while True:
        data = {}
        data['accel'] = acc
        data['P'] = p_button
        data['gear'] = gear
        #print(data)
        try:
            client.sendall(bytes(json.dumps(data), encoding="utf-8"))
        except:
            print(f'SClient Left: {client_addr}')
            break
        time.sleep(1/15)

def serialthread(ser):
    global acc
    global p_button
    global gear
    global change_gear

    line = []
    dial = False
    while True:
        if dial:
            if gear != change_gear:
                ser.write(change_gear.encode())
                gear = change_gear
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
                        dial = True
                        text = text[1:]
                        temp = text.split('/')
                        p_button = int(temp[0])
                        gear = temp[1]
                        change_gear = temp[1]
                except IndexError:
                    pass
                del line[:]
                ser.reset_input_buffer()
            else:
                line.append(chr(c))


def setMC(MC):
    global acc
    global p_button
    global gear

    while True:
        MC.set('accel', acc)
        MC.set('P', p_button)
        MC.set('gear', gear)


if __name__ == "__main__":
    for port in serial_ports():
        print(port)
        ser = serial.Serial(port, baud, timeout=0)
        serial_thread = threading.Thread(target=serialthread, args=(ser,))
        serial_thread.daemon = True
        serial_thread.start()

    MC = MonitoringClient('http://34.64.189.234/post.php')
    setMC = threading.Thread(target=setMC, args=(MC,))
    setMC.daemon = True
    setMC.start()

    acception_thread = threading.Thread(target=acceptionthread(), args=())
    acception_thread.daemon = True
    acception_thread.start()

    sock.close()
