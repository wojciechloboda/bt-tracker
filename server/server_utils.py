
import socket
import threading
import time
from queue import Queue
import struct
import numpy as np
# from filterpy.kalman import KalmanFilter
from tkinter import *
from kalman import *
from config import *

receivers = {}
connected_receivers = 0

def get_new_id():
    global connected_receivers
    connected_receivers += 1
    return connected_receivers 

class ReceiverThread(threading.Thread):
    def __init__(self, client_socket, on_add_device, on_remove_device, on_device_dist_change, beacon_name):
        threading.Thread.__init__(self)
        self.shouldRun = True
        self.on_add_device = on_add_device
        self.on_remove_device = on_remove_device
        self.on_device_dist_change = on_device_dist_change
        self.client_socket = client_socket
        self.beacon_name = beacon_name

    def terminate(self):
        self.shouldRun = False

    def run(self):
        rec_id = get_new_id()
        kf = KalmanFilter(R=0.01, Q=2)
        try:
            chunk = self.client_socket.recv(MSG_SIZE)
            t, payload = struct.unpack("Bi", chunk)
            if t != 1:
                print("bad msg from receiver")
                return
            
            chunk = struct.pack("B50s", 1, self.beacon_name.encode('utf-8') + b'\x00')
            self.client_socket.send(chunk)

            receivers[rec_id] = Receiver(0, 0)
            print("CONNECTED TO TRACKER: ", rec_id)
            self.on_add_device(rec_id)
            while self.shouldRun:
                try:
                    chunk = self.client_socket.recv(MSG_SIZE)
                    if len(chunk) == 8:
                        t, payload = struct.unpack("Bi", chunk)
                        payload = kf.filter(payload)
                        receivers[rec_id].data_queue.put(payload) 
                        self.on_device_dist_change(rec_id, payload)
                except socket.timeout:
                    pass
        except (socket.error, ConnectionResetError, Exception):
            print(f"receiver {rec_id} socket error, terminating connection")
            del receivers[rec_id]
        finally:
            self.on_remove_device(rec_id)

class Receiver:
    def __init__(self, x, y):
        self.x = x #position in meters
        self.y = y
        self.data_queue = Queue()

class AcceptConThread(threading.Thread):
    def __init__(self, on_add_device, on_remove_device, on_device_dist_change, beacon_name):
        threading.Thread.__init__(self)
        self.on_add_device = on_add_device
        self.on_remove_device = on_remove_device
        self.on_device_dist_change = on_device_dist_change
        self.should_run = True
        self.rec_threads = []
        self.beacon_name = beacon_name

    def terminate(self):
        self.should_run = False

    def run(self):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((HOST, SERVER_PORT))
            server_socket.listen(MAX_REC)
            server_socket.settimeout(0.1)
            server_socket.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 2000, 500))
            # client_socket.settimeout(0.2)

            while self.should_run:
                try:
                    client_socket, _ = server_socket.accept()
                    client_socket.settimeout(0.1)
                    print("GOT CONNECTION FROM CLIENT")
                    rec_t = ReceiverThread(client_socket, self.on_add_device, self.on_remove_device, self. on_device_dist_change, self.beacon_name)
                    rec_t.start()
                    self.rec_threads.append(rec_t)
                except TimeoutError:
                    pass
            for rec in self.rec_threads:
                rec.terminate()
                if rec.alive():
                    rec.join(0.1)
        except (socket.error, ConnectionResetError, Exception):
            print("server socket exception")

if __name__ == '__main__':
    try:
        accept_conn_thread = AcceptConThread(None, None)
        accept_conn_thread.start()
    except:
        pass
    finally:
        accept_conn_thread.terminate()
        accept_conn_thread.join()
