from easy_trilateration.model import *  
from easy_trilateration.least_squares import easy_least_squares 
from kalman import KalmanFilter  
from config import *

class Device():
    def __init__(self, rssi_at_1m, n, text):
        self.rssi_at_1m = rssi_at_1m
        self.n = n
        self.last_x = 100
        self.last_y = 100
        self.last_dist = 0
        self.text = text


class DeviceStateUI():
    def __init__(self, map, device_list):
        self.focused_id = None
        self.device_dict = {}
        self.map = map
        self.device_list = device_list
        self.connected_devices = {}
        self.focused = set()
        self.draw_beacon = False
        self.map.updateBeacon = self.update_beacon

    def add_device(self, id):
        # self.connected_devices[id] = {'rssi': DEFAULT_RSSI_AT_1_M, 'n': DEFAULT_N}
        self.connected_devices[id] = Device(DEFAULT_RSSI_AT_1_M, DEFAULT_N, f'ESP32 ID: {id}')
        # self.connected_dist[id] = 0
        # text_var = tk.StringVar(text + 'dist: ' + self.connected_dist[id]) 
        self.device_list.add_device(self.connected_devices[id].text, id, self.onDeviceFocus, self.onDeviceUnfocus)
        self.map.create_marker(self.connected_devices[id].last_x, self.connected_devices[id].last_y, 'blue', id)

    def remove_device(self, id):
        if id in self.connected_devices:
            del self.connected_devices[id]
        # self.connected.remove(id)
        self.device_list.remove_device(id)
        self.map.remove_marker(id)

    def update_device_dist(self, id, rssi):
        dist = self.rssi_to_meters(id, rssi)
        self.connected_devices[id].last_dist = dist
        self.connected_devices[id].text = f'ESP32 ID: {id}, rssi: {rssi:0.2f}, dist: {dist:0.2f}'
        # print(f'GOT rssi: {rssi}, meters:{dist}')
        self.device_list.update_device_label(id, self.connected_devices[id].text)
        self.map.update_device_dist(id, dist)

        self.update_beacon()

    def onDeviceFocus(self, deviceId):
        self.focused.add(deviceId)
        self.device_list.focus(deviceId, self.onDeviceSetParams, self.getDeviceParams)
        self.map.focus(deviceId)

    def onDeviceUnfocus(self, deviceId):
        self.focused.remove(deviceId)
        self.device_list.unfocus(deviceId)
        self.map.unfocus(deviceId)

    def onDeviceSetParams(self, id, rssi, n): #musi byc int
        if id in self.connected_devices:
            self.connected_devices[id].rssi_at_1m = rssi
            self.connected_devices[id].n = n
    
    def getDeviceParams(self, id):
        if id in self.connected_devices:
            return self.connected_devices[id].rssi_at_1m, self.connected_devices[id].n
        return DEFAULT_RSSI_AT_1_M, DEFAULT_N

    def rssi_to_meters(self, id, rssi):
        return 10 ** ((self.connected_devices[id].rssi_at_1m - rssi)/(10 * self.connected_devices[id].n))
    
    def show_beacon(self):
        self.draw_beacon = True
        self.update_beacon()

    def hide_beacon(self):
        self.draw_beacon = False
        self.map.destroy_beacon_marker()

    def update_beacon(self):
        if not self.draw_beacon:
            return 
        
        for id in self.connected_devices:
            x, y = self.map.get_marker_position(id)
            self.connected_devices[id].last_x = x
            self.connected_devices[id].last_y = y
                    
        circles = [Circle(dev.last_x, dev.last_y, dev.last_dist * PIXELS_TO_METER) for dev in self.connected_devices.values()]
        print(circles)
        result, _ = easy_least_squares(circles)
        self.map.destroy_beacon_marker()
        self.map.update_beacon_marker(result.center.x, result.center.y, result.radius, 'green')

    def toggle_beacon(self):
        if self.draw_beacon:
            self.hide_beacon()
        else:
            self.show_beacon()