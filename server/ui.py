
import tkinter as tk
from server_utils import *
from config import *

def clamp(value, min, max):
    if value < min:
        return min
    if value > max:
        return max
    return value

class MapMarker():
    def __init__(self, canvas, x, y, rad, color, id):
        self.canvas = canvas
        self.color = color
        self.x = x
        self.y = y
        self.oval = canvas.create_oval(
            x - rad,
            y - rad,
            x + rad,
            y + rad,
            outline=color,
            fill=color,
            # width=5,
            tags=("token",)
        )
        self.oval_label = canvas.create_text((x, y - rad), text=f'ID: {id}', anchor='s')
        self.canvas.tag_raise(self.oval_label)
        self.focus_marker = None
        self.length_indicator = []
        self.dist = 0
        self.dist_indicator = None
        self.focused = False

    #delta is one meter is real life
    def create_length_indicator(self, delta_r, color):
        for m in range(1, 10):
            self.length_indicator.append(
                self.canvas.create_oval(
                self.x - m * delta_r,
                self.y - m * delta_r,
                self.x + m * delta_r,
                self.y + m * delta_r,
                outline=color,
                fill='',
                # width=OUTLINE_WIDTH,
            ))
            self.canvas.tag_lower(self.length_indicator[-1])

    def create_dist_indicator(self, color):
        self.dist_indicator = self.canvas.create_oval(
                self.x - self.dist * PIXELS_TO_METER,
                self.y - self.dist * PIXELS_TO_METER,
                self.x + self.dist * PIXELS_TO_METER,
                self.y + self.dist * PIXELS_TO_METER,
                outline=color,
                fill='',
                width = OUTLINE_WIDTH,
            )
        self.canvas.tag_lower(self.dist_indicator)

    def destroy(self):
        self.canvas.delete(self.oval)
        self.canvas.delete(self.oval_label)
        for ind in self.length_indicator:
            self.canvas.delete(ind)
        self.length_indicator = []
        if self.dist_indicator:
            self.canvas.delete(self.dist_indicator)

    def update_device_dist(self, dist):
        self.dist = dist
        if self.focused:
            if self.dist_indicator:
                self.canvas.delete(self.dist_indicator)
            self.create_dist_indicator('red')


    def focus(self) :
        self.canvas.itemconfig(self.oval, outline=OUTLINE_COLOR)
        self.create_length_indicator(PIXELS_TO_METER, 'black')
        self.create_dist_indicator('red')
        self.focused = True
    
    def unfocus(self):
        self.canvas.itemconfig(self.oval, outline=self.color)
        for ind in self.length_indicator:
            self.canvas.delete(ind)
        self.length_indicator = []
        if self.dist_indicator:
            self.canvas.delete(self.dist_indicator)
        self.focused = False

    def move(self, delta_x, delta_y):
        self.x += delta_x
        self.y += delta_y
        self.canvas.move(self.oval, delta_x, delta_y)
        self.canvas.move(self.oval_label, delta_x, delta_y)
        if self.dist_indicator: 
            self.canvas.move(self.dist_indicator, delta_x, delta_y)
        # if self.focus_marker:
        #     self.canvas.move(self.focus_marker, delta_x, delta_y)

        for ind in self.length_indicator:
            self.canvas.move(ind, delta_x, delta_y)

class BeaconMarker():
    def __init__(self, canvas):
        self.canvas = canvas
        # self.beacon_oval = None
        # self.beacon_oval_bif
        
    def update(self, x, y, rad):
        self.canvas.delete('beacon')
        self.beacon_oval = self.canvas.create_oval(
            x - MARKER_RADIUS,
            y - MARKER_RADIUS,
            x + MARKER_RADIUS,
            y + MARKER_RADIUS,
            fill='green',
            tags=('beacon',))

        self.beacon_oval_big = self.canvas.create_oval(
            x - rad,
            y - rad,
            x + rad,
            y + rad,
            fill='',
            width=OUTLINE_WIDTH,
            tags=('beacon',))
        
    def destroy(self):
        self.canvas.delete('beacon')

class Map(tk.Frame):
    def __init__(self, parent, width, height):
        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, width=width, height=height, background="white", highlightthickness=1, highlightbackground="black")
        self.canvas.pack(fill='both')
        self._drag_data = {"x": 0, "y": 0, "item": None}

        self.canvas.tag_bind("token", "<ButtonPress-1>", self.drag_start)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self.drag_stop)
        self.canvas.tag_bind("token", "<B1-Motion>", self.drag)

        self.markers = {}

        # self.beacon_oval = None
        # self.updateBeacon = None
        self.beacon = BeaconMarker(self.canvas)

    def update_beacon_marker(self, x, y, rad, color):
        self.beacon.update(x, y, rad)
        # self.canvas.delete("beacon")
        # self.beacon_oval = self.canvas.create_oval(
        #     x - rad,
        #     y - rad,
        #     x + rad,
        #     y + rad,
        #     fill=color,
        #     width=OUTLINE_WIDTH,
        #     tags=("beacon",))
        
    def destroy_beacon_marker(self):
        # self.canvas.delete("beacon")
        self.beacon.destroy()

    def update_device_dist(self, id, dist):
        self.markers[id].update_device_dist(dist)

    def focus(self, id):
        if id in self.markers:
            self.markers[id].focus()

    def unfocus(self, id):
        if id in self.markers:
            self.markers[id].unfocus()

    def get_marker_position(self, id):
        if id in self.markers:
            return self.markers[id].x, self.markers[id].y
        return 100, 100
        
    def create_marker(self, x, y, color, id):
        self.markers[id] = MapMarker(self.canvas, x, y, MARKER_RADIUS, color, id)

    def remove_marker(self, id):
        if id in self.markers:
            self.markers[id].destroy()
            del self.markers[id]
            
            # self.canvas.delete(self.markers[id].oval)

    def drag_start(self, event):
        current_marker = self.canvas.find_closest(event.x, event.y)[0]
        # current_marker = None
        # for cm in self.canvas.find_closest(event.x, event.y):
        #     print(self.canvas.gettags(cm))
        #     if 'token' in self.canvas.gettags(cm):
        #         current_marker = cm
        #         break

        if not current_marker:
            return
        
        for key in self.markers:
            if self.markers[key].oval == current_marker:
                self._drag_data['item'] = self.markers[key]
                break
        
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def drag_stop(self, event):
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def drag(self, event):
        if not self._drag_data["item"]:
            return
        
        item = self._drag_data["item"]
        x0, y0, _, _ = self.canvas.coords(item.oval) # potenial bug
        if clamp(event.x, 0, self.canvas.winfo_width()) != event.x or clamp(event.y, 0, self.canvas.winfo_height()) != event.y: 
            self.drag_stop(None)
            return

        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]

        new_x = x0 + delta_x
        new_y = y0 + delta_y

        new_x = clamp(new_x, 0, self.winfo_width() - 2 * MARKER_RADIUS)
        new_y = clamp(new_y, 0, self.winfo_height() - 2 * MARKER_RADIUS)

        # self.canvas.move(self._drag_data["item"].oval, new_x - x0, new_y - y0)# here magic
        item.move(new_x - x0, new_y - y0)

        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        if self.updateBeacon:
            self.updateBeacon()


class DeviceList(tk.Frame):
    def __init__(self, parent, width, height):
        tk.Frame.__init__(self, parent, width=width, height=height)

        tk.Frame.pack_propagate(self, 0)

        self.left_frame_label = tk.Label(self, text='Connected Devices:')
        self.left_frame_label.pack(side=tk.TOP)

        self.device_container = tk.Frame(self)
        self.device_container.pack(side=tk.TOP)

        self.selected_device_frames = {}

        # self.show_device_options(0)

        self.devices = {}

    def onSetParams(self, id, rssi_en, n_en, onDeviceSetParams):
        try:
            rssi = int(rssi_en.get())
            n = int(n_en.get())
            print(f'GOT: {rssi}, {n}')
            onDeviceSetParams(id, rssi, n)
        except ValueError:
            pass

    def show_device_options(self, id, onDeviceSetParams, getDeviceParams):
        selected_device_frame = tk.Frame(self)
        selected_device_frame.pack(side=tk.BOTTOM)
        self.selected_device_frames[id] = selected_device_frame
        # self.selected_device_frame.pack_propagate(0)

        selected_device_label = tk.Label(selected_device_frame, text=f'selected device id: {id}')
        selected_device_label.pack(side=tk.TOP)

        rssi, n = getDeviceParams(id) 

        rssi_frame = tk.Frame(selected_device_frame)
        rssi_frame.pack(fill='x', side=tk.TOP)
        tk.Label(rssi_frame, text=f'RSSI at 1m: ').pack(side=tk.LEFT)
        rssi_en = tk.Entry(rssi_frame)
        rssi_en.pack(fill='x', side=tk.RIGHT)
        rssi_en.insert(0, f'{rssi}')

        n_frame = tk.Frame(selected_device_frame)
        n_frame.pack(fill='x', side=tk.TOP)
        tk.Label(n_frame, text=f'N: ').pack(side=tk.LEFT)
        n_en = tk.Entry(n_frame)
        n_en.pack(side=tk.RIGHT)
        n_en.insert(0, f'{n}')

        set_btn = tk.Button(selected_device_frame, text = 'set params', command=lambda: self.onSetParams(id, rssi_en, n_en, onDeviceSetParams))
        set_btn.pack(fill='x', side=tk.TOP)

    def hide_device_options(self, id):
        if id in self.selected_device_frames:
            self.selected_device_frames[id].destroy()
            del self.selected_device_frames[id]

    def update_device_label(self, id, text):
        if id in self.devices:
            self.devices[id].update_device_label(text)

    def add_device(self, text, id, onFocus, onUnfocus):
        device_label = DeviceLabel(self.device_container, 200, 20, text, id, onFocus, onUnfocus)
        device_label.pack()
        self.devices[id] = device_label

    def focus(self, id, onDeviceSetParams, getDeviceParams):
        if id in self.devices:
            self.devices[id].focus()
            self.show_device_options(id, onDeviceSetParams, getDeviceParams)

    def unfocus(self, id):
        if id in self.devices:
            self.devices[id].unfocus()
            self.hide_device_options(id)

    def remove_device(self, id):
        if id in self.devices:
            self.devices[id].destroy()
            self.hide_device_options(id)
            del self.devices[id]


class DeviceLabel(tk.Frame):
    def __init__(self, parent, width, height, text, id, onFocus, onUnfocus):
        tk.Frame.__init__(self, parent, width=width, height=height)
        tk.Frame.pack_propagate(self, 0)

        # b = tk.Button(self, text=text)
        self.label = tk.Label(self, text=text, bg='white', borderwidth=5)
        self.label.bind('<Button-1>', self.on_click)


        # frame1.bind('<Leave>', exit_)
        self.label.pack(fill=tk.BOTH, expand=1)
        self.clicked = False
        self.onFocus = onFocus
        self.onUnfocus = onUnfocus
        self.id = id

    def update_device_label(self, text):
        self.label.config(text=text)

    def on_click(self, event):
        self.clicked = not self.clicked
        if self.clicked:
            self.onFocus(self.id)
        else:
            self.onUnfocus(self.id)
        pass
        
    def focus(self):
        self.label.config(bg='grey')

    def unfocus(self):
        self.label.config(bg='white')