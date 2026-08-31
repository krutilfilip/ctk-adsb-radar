import tkintermapview
import math

#calculates the zoom from 0-19 for a specific nautical mile radius
def zoom_for_radius(radius_nm, widget_width_px, lat):
    diameter_m = 2 * radius_nm * 1852
    lat_rad = math.radians(lat)
    z = math.log2(156543.03392 * math.cos(lat_rad) * widget_width_px / diameter_m)
    return max(0, min(19, z))

#creates the map widget
def create_map_widget(root, width, height):
    return tkintermapview.TkinterMapView(root, width=width, height=height, corner_radius=20)