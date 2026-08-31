import customtkinter as ctk
import map_view
import get_adsb
from PIL import Image, ImageTk
import sys, os

def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return filename

PLANE_IMAGE = Image.open(resource_path("plane.png"))
PLANE_IMAGE_BLUE = Image.open(resource_path("plane_color_blue.png"))

BG_BLUE = "#030d40"
FRAME_BLUE = "#031153"
INSIDE_FRAME_BLUE = "#142476"
LIGHT_BLUE = "#62a9e4"

class SimpleFrame(ctk.CTkFrame):
    def __init__(self, master, tag):
        super().__init__(master, corner_radius=15, fg_color=INSIDE_FRAME_BLUE,
                         width=165, height=60, bg_color=FRAME_BLUE)
        self.grid_propagate(False)

        self.text = None
        self.label_tag = ctk.CTkLabel(master=self, text=tag, font=("Arial", 10), text_color="grey",
                                      anchor=ctk.W)
        self.label_info = ctk.CTkLabel(master=self, text=self.text, 
                                  font=("Arial Black", 20), text_color=LIGHT_BLUE, anchor=ctk.W)

        self.label_tag.grid(row=0, column=0, sticky=ctk.W, padx=10)
        self.label_info.grid(row=1, column=0, sticky=ctk.W, padx=10)

    def place_frame(self, text, x, y):
        self.text = text
        self.label_info.configure(text=text)
        self.place(x=x, y=y, anchor=ctk.W)

class MapFrame(ctk.CTkFrame):
    def __init__(self, master, map_width, map_height):
        super().__init__(master, corner_radius=15, fg_color = BG_BLUE, bg_color=BG_BLUE)
        self.pack_propagate(False)

        self.city = "London"
        self.map = map_view.create_map_widget(self, map_width, map_height)
        self.map.grid(row=0, column=0)
        self.map.set_address(self.city)
        self.map.set_zoom(0)

class InfoFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, width=630, height=240, fg_color=FRAME_BLUE, corner_radius=15, bg_color=BG_BLUE)
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.plane_frame = ctk.CTkFrame(self, width=200, height=200, fg_color='transparent',
                                        corner_radius=15, bg_color='transparent')
        self.plane_image_label = ctk.CTkLabel(master=self.plane_frame, text="", corner_radius=15,
                                              fg_color='transparent', bg_color='transparent',
                                              anchor=ctk.CENTER)

        self.label_no_aircraft = ctk.CTkLabel(self, text="NO AIRCRAFT\n SELECTED", 
                                              text_color="#595757", font=("Arial Black", 50))
        self.label_no_aircraft.pack(anchor=ctk.CENTER, expand=True)

        self.flightnumber_frame = SimpleFrame(self, "CALLSIGN")
        self.aircraft_type_frame = SimpleFrame(self, "AIRCRAFT TYPE")
        self.registration_frame = SimpleFrame(self, "REGISTRATION")
        self.alt_baro_frame = SimpleFrame(self, "ALT BARO")
        self.groundspeed_frame = SimpleFrame(self, "GROUND SPEED")
        self.track_frame = SimpleFrame(self, "TRACK")

    def show_info(self, flight_number, aircraft_type, registration, alt_baro, track, track_formatted,
                  ground_speed):
        if self.label_no_aircraft.winfo_ismapped():
            self.label_no_aircraft.pack_forget()

        self.plane_image = PLANE_IMAGE_BLUE.resize((190, 190))
        self.plane_image = self.plane_image.rotate(-int(track), expand=True)
        self.plane_image = ImageTk.PhotoImage(self.plane_image)
        self.plane_image_label.configure(image=self.plane_image)

        self.plane_image_label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
        self.plane_frame.place(x=120, y=120, anchor=ctk.CENTER)

        self.flightnumber_frame.place_frame(flight_number, 260, 50)
        self.aircraft_type_frame.place_frame(aircraft_type, 260, 120)
        self.registration_frame.place_frame(registration, 260, 190)

        self.alt_baro_frame.place_frame(alt_baro, 445, 50)
        self.groundspeed_frame.place_frame(ground_speed, 445, 120)
        self.track_frame.place_frame(track_formatted, 445, 190)

    def update_info(self, plane):
        self.flightnumber_frame.label_info.configure(text=plane.flight_number)
        self.aircraft_type_frame.label_info.configure(text=plane.aircraft_type)
        self.registration_frame.label_info.configure(text=plane.registration)

        self.alt_baro_frame.label_info.configure(text=plane.alt_baro)
        self.groundspeed_frame.label_info.configure(text=plane.ground_speed)
        self.track_frame.label_info.configure(text=plane.track_formatted)

class Plane():
    def __init__(self, data):
        self.marker = None

        self.flight_number = data['flight'].strip()
        self.aircraft_type = data['t']
        self.registration = data['r']
        self.alt_baro = str(data['alt_baro']) + "ft"
        self.track = data['track']
        self.track_formatted = str(data['track']) + '°'
        self.ground_speed = str(data['gs']) + "kts"
        self.lat = data['lat']
        self.lon = data['lon']

        self.icon = PLANE_IMAGE.rotate(-int(self.track), expand=True).resize((25, 25))
        self.icon = ImageTk.PhotoImage(self.icon)

    def update(self, data):
        try:
            self.alt_baro = str(data['alt_baro']) + "ft"
            self.ground_speed = str(data['gs']) + "kts"
            self.track = data['track']
            self.track_formatted = str(data['track']) + '°'
            self.lat = data['lat']
            self.lon = data['lon']
        except KeyError:
            pass

class App():
    def __init__(self):
        self.app = ctk.CTk()
        self.app.geometry("650x820")
        self.app.title("ADSB Radar")
        self.app.configure(fg_color=BG_BLUE, bg_color=BG_BLUE)

        self.app.columnconfigure(0, weight=1)
        self.app.rowconfigure((0, 1, 2), weight=1)

        self.info_frame = InfoFrame(self.app)
        self.map_frame = MapFrame(self.app, 630, 520)

        self.location_frame = ctk.CTkFrame(self.app, width=630, height=40, bg_color=BG_BLUE,
                                           corner_radius=15, fg_color=FRAME_BLUE)
        self.location_entry = ctk.CTkEntry(self.location_frame, width=400, height=30, placeholder_text="ENTER LOCATION HERE FIRST",
                                           fg_color="transparent", bg_color=FRAME_BLUE, placeholder_text_color=LIGHT_BLUE,
                                           text_color=LIGHT_BLUE, font=("Arial", 15), border_color=FRAME_BLUE)
        self.location_frame.grid(row=2, column=0)
        self.location_entry.place(x=10, y=20, anchor=ctk.W)
        self.location_entry.bind("<Return>", self.on_location_enter)      

        self.map_frame.grid(row=1, column=0)
        self.info_frame.grid(row=0, column=0)

        self.lat = None
        self.lon = None

        self.plane_obj_list = []
        self.current_planes = []

        self._refreshing = False

    def get_planes(self):
        plane_json_list = get_adsb.get_nearest_planes(self.lat, self.lon, 75)
        if len(plane_json_list) != 0:
    
            current_flights = {data['flight'].strip() for data in plane_json_list if 'flight' in data}
    
            for plane_obj in self.plane_obj_list[:]:
                if plane_obj.flight_number not in current_flights:
                    if plane_obj.marker is not None:
                        plane_obj.marker.delete()
                    self.plane_obj_list.remove(plane_obj)
    
            existing_flights = {plane.flight_number: plane for plane in self.plane_obj_list}
    
            for data in plane_json_list:
                if 'flight' not in data: continue
                flight_num = data['flight'].strip()
    
                if flight_num in existing_flights:
                    existing_flights[flight_num].update(data)
                else:
                    try:
                        self.plane_obj_list.append(Plane(data))
                    except KeyError:
                        pass

            self.current_planes = {plane.flight_number: plane for plane in self.plane_obj_list}

    def place_plane_markers(self):
        for plane in self.plane_obj_list:
            if plane.marker is None:
                plane.marker = self.map_frame.map.set_marker(plane.lat, plane.lon, 
                                                             text=plane.flight_number, icon=plane.icon,
                                                             command=lambda marker, p=plane: self.show_plane_info(p))
            else:
                plane.marker.set_position(plane.lat, plane.lon)
                plane.marker.change_icon(plane.icon)

    def show_plane_info(self, plane):
        self.info_frame.show_info(plane.flight_number, plane.aircraft_type, plane.registration,
                                              plane.alt_baro, plane.track, plane.track_formatted, plane.ground_speed)

    def update_info_frame(self):
        if self.info_frame.flightnumber_frame.text is not None:
            plane = self.current_planes.get(self.info_frame.flightnumber_frame.text)
            print(f"update_info_frame: looking up '{self.info_frame.flightnumber_frame.text}', found: {plane}")
            if plane is not None:
                print(f"  alt_baro={plane.alt_baro}, gs={plane.ground_speed}, track={plane.track_formatted}")
                self.info_frame.update_info(plane)
        else:
            print("update_info_frame: no plane currently selected")

    def on_location_enter(self, event):
        location = self.location_entry.get().strip()
        if location:
            self.map_frame.city = location
            self.map_frame.map.set_address(location)
            self.lat, self.lon = self.map_frame.map.get_position()
            if not self._refreshing:
                self._refreshing = True
                self.refresh_planes()
        
    def refresh_planes(self):
        self.get_planes()
        self.place_plane_markers()
        self.update_info_frame()
        self.app.after(5000, self.refresh_planes)

    def run(self):
        self.app.mainloop()

window = App()
window.run()