#!/usr/bin/python3
# -*- coding: utf-8 -*-

import serial
import time
import threading
import socket
import json
import glob


def serial_ports():
    ports = glob.glob('/dev/tty[A-Za-z]*')

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
data = {}
clients = []

baud = 9600

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", 9999))
sock.listen(1)

def receiverthread():
    global clients

    while True:
        client, client_addr = sock.accept()
        print(f'New Client: {client_addr}')
        clients.append((client, client_addr))

def senderthread():
    global acc
    global p_button
    global gear
    global data
    global clients

    while True:
        for c in clients:
            client, client_addr = c
            data['accel'] = acc
            data['P'] = p_button
            data['gear'] = gear
            try:
                client.sendall(bytes(json.dumps(data), encoding="utf-8"))
            except:
                print(f'Client Left: {client_addr}')
                clients.remove(client)
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
    try:
        for port in serial_ports():
            ser = serial.Serial(port, baud, timeout=0)
            serial_thread = threading.Thread(target=serialthread, args=(ser,))
            serial_thread.daemon = True
            serial_thread.start()

        receiver_thread = threading.Thread(target=receiverthread, args=())
        receiver_thread.daemon = True
        receiver_thread.start()

        sender_thread = threading.Thread(target=senderthread, args=())
        sender_thread.daemon = True
        sender_thread.start()

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        print('closing')
        sock.close()
