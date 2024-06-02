import tkinter as tk
from server_utils import *
from device_state import DeviceStateUI
from ui import *

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)

        self.device_list = DeviceList(self.root, 200, 400)
        self.device_list.grid(row=0, column=0)

        self.map = Map(self.root, 400, 400)
        self.map.grid(row=0, column=1)

        self.state = DeviceStateUI(self.map, self.device_list)

        self.bottom_frame = tk.Frame(self.root, width=600, height=50)
        self.bottom_frame.grid(row=1, column=0, columnspan=2)

        self.bottom_frame.pack_propagate(0)

        tk.Label(self.bottom_frame, text = 'Beacon name:').grid(row=0, column=0)
        self.beacon_name_en = tk.Entry(self.bottom_frame)
        self.beacon_name_en.grid(row=0, column=1)

        self.btn = tk.Button(self.bottom_frame, text = 'start server', command = self.run_server) 
        self.btn.grid(row=0, column=2)

        self.btn_tri = tk.Button(self.bottom_frame, text = 'toggle beacon', command = self.state.toggle_beacon)
        self.btn_tri.grid(row=0, column=3)

        self.accept_conn_thread = AcceptConThread(self.state.add_device, self.state.remove_device, self.state.update_device_dist, "DEAFULT")
    
        #mocked
        self.state.add_device(10)
        self.state.update_device_dist(10, -77)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.mainloop()

    def terminate_server(self):
        print('terminating server...')
        self.accept_conn_thread.terminate()
        if self.accept_conn_thread.is_alive():
            self.accept_conn_thread.join(0.2)

    def run_server(self):
        print('running server...')
        self.accept_conn_thread.daemon = True
        self.accept_conn_thread.beacon_name = self.beacon_name_en.get()
        self.accept_conn_thread.start()

    def on_closing(self):
        print('terminating server')
        self.terminate_server()
        self.root.destroy()

if __name__ == "__main__":
    App()
